"""CTF 知识库 Web UI —— 搜索引擎样式（单文件，零前端构建）。

设计目标（用户原话）："只是需要思路和一些脚本"。
所以不做聊天窗口，做搜索框：

  输入题面特征 → 立刻出结果卡片 → 每张卡片可"看全文"/"问模型"

端点：
  GET  /                 主页面
  GET  /api/health       健康检查（含模型/索引状态）
  POST /api/search       {q, category, top_k} -> 结果 + 图谱关联
  GET  /api/doc?path=    取某篇全文
  POST /api/ask          {q, paths} -> SSE 流式模型回答
  POST /api/feedback     {query, path, verdict, note} -> 本地 JSONL
  POST /api/analyze?name= 原始字节 -> 附件只读侦察（隔离目录，不执行）
  GET/POST/DELETE /api/workspaces... -> 本地题目工作区（JSON 文件）

启动：python tools/agent/server.py
"""
from __future__ import annotations

import json
import os
import re
import sys
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

# ---- 配置：config.toml 是唯一事实来源，环境变量只做显式覆盖 ----
try:
    from kb.config import Config as _Config

    CFG = _Config.load()
except Exception:  # noqa: BLE001  # 配置坏了也不影响静态页面/错误提示
    CFG = None


def _cfg(section: str, key: str, default):
    if CFG is None:
        return default
    try:
        return CFG.get(section, key, default)
    except Exception:  # noqa: BLE001
        return default


HOST = os.environ.get("AGENT_HOST", "127.0.0.1")
PORT = int(os.environ.get("AGENT_PORT", "8765"))

OLLAMA = (os.environ.get("AGENT_OLLAMA")
          or str(_cfg("ollama", "host", "http://127.0.0.1:11434"))).rstrip("/")
MODEL = (os.environ.get("AGENT_MODEL")
         or str(_cfg("ollama", "model", "qwen2.5-coder-7b")))

# 生成参数统一从 [llm] 读取；AGENT_* 是显式临时覆盖。
NUM_CTX = int(os.environ.get("AGENT_NUM_CTX")
              or _cfg("llm", "n_ctx", 8192))
MAX_TOKENS = int(os.environ.get("AGENT_MAX_TOKENS")
                 or _cfg("llm", "max_tokens", 1200))
TEMPERATURE = float(os.environ.get("AGENT_TEMPERATURE")
                    or _cfg("llm", "temperature", 0.2))
TIMEOUT = int(os.environ.get("AGENT_TIMEOUT")
              or _cfg("llm", "timeout", 300))
KEEP_ALIVE = str(os.environ.get("AGENT_KEEP_ALIVE")
                 or _cfg("llm", "keep_alive", "30m"))
_NUM_GPU = _cfg("llm", "ollama_num_gpu", None)

# ---- 输入/正文边界 ----
MAX_BODY_BYTES = 64 * 1024          # HTTP 请求体
MAX_WORKSPACE_BODY_BYTES = 512 * 1024  # 附件报告附到工作区时可能较大
MAX_QUERY_CHARS = 2000              # 问题/搜索词
MAX_TOP_K = 50
MAX_PATHS = 3                       # /api/ask 最多读几篇
MAX_DOC_BYTES = 1024 * 1024         # 单篇 Markdown 上限
MAX_PER_DOC_CHARS = 2600            # 送进模型的单篇字符上限
MAX_CONTEXT_CHARS = 12000           # 送进模型的总字符上限
MAX_PATH_CHARS = 500
MAX_NOTE_CHARS = 500
FEEDBACK_VERDICTS = {"useful", "useless", "adopted"}
DOC_TYPES = {"topic", "card"}
# 附件侦察：请求体上限与文件名长度；硬上限防止配置写出离谱值。
MAX_ATTACHMENT_NAME = 240
ATTACHMENT_HARD_MAX = 64 * 1024 * 1024
DEFAULT_ATTACHMENT_MAX = 8 * 1024 * 1024

# 每类结果的命中上限，避免同方向刷屏
CATS = ["misc", "crypto", "web", "pwn", "reverse",
        "forensics", "mobile", "hardware", "osint", "ai", "blockchain"]

_KB = None
_KB_LOCK = threading.Lock()
# /api/ask 串行：4GB 显存下并发生成会互相挤爆。忙碌时直接拒绝，不排队。
_ASK_LOCK = threading.Lock()
_FEEDBACK_LOCK = threading.Lock()


class BadRequest(ValueError):
    """客户端输入不合法，返回 400。"""


def _sse(obj: dict) -> str:
    """统一 SSE 帧：data: {json}\\n\\n。"""
    return "data: " + json.dumps(obj, ensure_ascii=False) + "\n\n"


def get_kb():
    """惰性初始化 KB（首次搜索时加载嵌入模型，约 1-2 秒）。"""
    global _KB
    if _KB is None:
        with _KB_LOCK:
            if _KB is None:
                from kb.config import Config
                from kb.rag import KB
                _KB = KB(CFG or Config.load())
    return _KB


def _check_query(q) -> str:
    if not isinstance(q, str):
        raise BadRequest("q 必须是字符串")
    q = q.strip()
    if len(q) > MAX_QUERY_CHARS:
        raise BadRequest(f"问题太长（最多 {MAX_QUERY_CHARS} 字）")
    return q


def _check_top_k(raw) -> int:
    if raw is None or raw == "":
        return int(_cfg("search", "top_k", 8))
    if isinstance(raw, bool) or not isinstance(raw, (int, float, str)):
        raise BadRequest("top_k 必须是整数")
    try:
        k = int(raw)
    except (TypeError, ValueError) as e:
        raise BadRequest("top_k 必须是整数") from e
    if k < 1 or k > MAX_TOP_K:
        raise BadRequest(f"top_k 必须在 1..{MAX_TOP_K} 之间")
    return k


def _check_category(raw):
    if raw in (None, "", "all"):
        return None
    if not isinstance(raw, str) or raw not in CATS:
        raise BadRequest("未知的方向筛选")
    return raw


def _check_doc_type(raw):
    if raw in (None, "", "all"):
        return None
    if not isinstance(raw, str) or raw not in DOC_TYPES:
        raise BadRequest("doc_type 只能是 topic 或 card")
    return raw


def _resolve_kb_file(kb, rel):
    """把相对路径解析到 kb/ 内的 Markdown；越界/非 md/过大一律拒绝。"""
    if not isinstance(rel, str):
        return None, "path 必须是字符串"
    rel = rel.strip().replace("\\", "/")
    if not rel:
        return None, "path 不能为空"
    if len(rel) > MAX_PATH_CHARS:
        return None, "path 太长"
    if rel.startswith("/") or re.match(r"^[A-Za-z]:", rel):
        return None, "路径必须是 kb/ 下的相对路径"
    root = kb.cfg.kb_dir.resolve()
    p = (root / rel).resolve()
    try:
        p.relative_to(root)
    except ValueError:
        return None, "路径越界"
    if p.suffix.lower() != ".md":
        return None, "只允许读取 Markdown"
    if not p.is_file():
        return None, "文件不存在"
    try:
        if p.stat().st_size > MAX_DOC_BYTES:
            return None, f"文件过大（上限 {MAX_DOC_BYTES} 字节）"
    except OSError as e:
        return None, f"文件不可读: {e}"
    return p, None


def _strip_front_matter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:]
    return text


def _collect_sources(kb, paths) -> tuple[list[str], str | None]:
    """读取并截断知识库正文；返回 (parts, error)。"""
    if not isinstance(paths, list):
        return [], "paths 必须是数组"
    if not paths:
        return [], "需要至少一个知识库路径"
    if len(paths) > MAX_PATHS:
        return [], f"最多引用 {MAX_PATHS} 篇资料"
    parts: list[str] = []
    used = 0
    seen: set[str] = set()
    for rel in paths:
        p, err = _resolve_kb_file(kb, rel)
        if err:
            return [], f"{err}: {rel!r}"
        key = str(p)
        if key in seen:
            continue
        seen.add(key)
        try:
            text = _strip_front_matter(p.read_text(encoding="utf-8", errors="replace"))
        except OSError as e:
            return [], f"文件不可读: {e}"
        remain = MAX_CONTEXT_CHARS - used
        if remain <= 0:
            break
        chunk = text[: min(MAX_PER_DOC_CHARS, remain)]
        parts.append(f"【{rel}】\n{chunk}")
        used += len(chunk)
    if not parts:
        return [], "没有可用的知识库内容"
    return parts, None


def _feedback_file() -> Path:
    """反馈落本地 JSONL；显式环境变量可覆盖（便于测试）。"""
    raw = (os.environ.get("AGENT_FEEDBACK_FILE")
           or str(_cfg("feedback", "file", "work/feedback/feedback.jsonl")))
    p = Path(raw)
    return p if p.is_absolute() else (ROOT / p)


def api_feedback(req: dict) -> dict:
    """记录 有用 / 无用 / 采用。只写本地追加文件，不读任意路径。"""
    if not isinstance(req, dict):
        raise BadRequest("请求体必须是 JSON 对象")
    q = _check_query(req.get("query", ""))
    if not q:
        raise BadRequest("需要 query")
    verdict = req.get("verdict")
    if not isinstance(verdict, str) or verdict not in FEEDBACK_VERDICTS:
        raise BadRequest("verdict 必须是 useful / useless / adopted")

    rel = req.get("path", "") or ""
    if not isinstance(rel, str):
        raise BadRequest("path 必须是字符串")
    rel = rel.strip()
    if rel:
        kb = get_kb()
        p, err = _resolve_kb_file(kb, rel)
        if err:
            raise BadRequest(f"{err}: {rel!r}")
        rel = p.relative_to(kb.cfg.kb_dir.resolve()).as_posix()

    note = req.get("note", "") or ""
    if not isinstance(note, str):
        raise BadRequest("note 必须是字符串")
    note = note.strip()
    if len(note) > MAX_NOTE_CHARS:
        raise BadRequest(f"note 太长（最多 {MAX_NOTE_CHARS} 字）")

    from kb.explain import doc_type

    rec = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "query": q,
        "path": rel,
        "doc_type": doc_type(rel) if rel else None,
        "verdict": verdict,
        "note": note,
    }
    f = _feedback_file()
    try:
        f.parent.mkdir(parents=True, exist_ok=True)
        with _FEEDBACK_LOCK:
            with f.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError as e:
        return {"ok": False, "saved": 0, "error": f"反馈写入失败: {e}"}
    return {"ok": True, "saved": 1, "file": str(f)}


# ---------------------------------------------------------------- 附件侦察
def _attachment_max_bytes() -> int:
    """每次读取配置/环境变量，便于测试与临时调小。"""
    raw = (os.environ.get("AGENT_ATTACHMENT_MAX_BYTES")
           or _cfg("attachment", "max_bytes", DEFAULT_ATTACHMENT_MAX))
    try:
        n = int(raw)
    except (TypeError, ValueError):
        n = DEFAULT_ATTACHMENT_MAX
    return max(1, min(n, ATTACHMENT_HARD_MAX))


def _attachment_dir() -> Path:
    raw = (os.environ.get("AGENT_ATTACHMENT_DIR")
           or str(_cfg("attachment", "dir", "work/attachments")))
    p = Path(raw)
    return p if p.is_absolute() else (ROOT / p)


def _check_attachment_name(raw) -> str:
    if raw in (None, ""):
        return "attachment.bin"
    if not isinstance(raw, str):
        raise BadRequest("附件名必须是字符串")
    name = raw.strip()
    if len(name) > MAX_ATTACHMENT_NAME:
        raise BadRequest(f"附件名太长（最多 {MAX_ATTACHMENT_NAME} 字符）")
    return name or "attachment.bin"


def api_analyze(name, data: bytes, workspace_id=None) -> dict:
    """保存到隔离目录并做只读结构化侦察；任何情况下都不执行附件。

    workspace_id 可选：给出时把附件登记为该工作区的「资料收藏」，
    并把时间线事件写入工作区。工作区不存在应在调用前拒绝。
    """
    name = _check_attachment_name(name)
    if not isinstance(data, (bytes, bytearray)) or not data:
        raise BadRequest("附件为空")
    limit = _attachment_max_bytes()
    if len(data) > limit:
        raise BadRequest(f"附件过大（上限 {limit} 字节）")

    from agent.attachment import analyze_upload

    report = analyze_upload(bytes(data), name, _attachment_dir())
    report["ok"] = True
    if workspace_id:
        try:
            kind = report["type"]["kind"]
            size = report["file"]["size"]
            summary = f"附件 {report['file']['name']}（{kind}，{size} 字节）"
            _, entry = _workspace_store().add_entry(
                workspace_id,
                kind="reference",
                title=report["file"]["name"],
                text=summary,
                path=report["file"].get("saved", ""),
                source="analyze",
                attachment={
                    "name": report["file"].get("name"),
                    "saved": report["file"].get("saved"),
                    "sha256": report["file"].get("sha256"),
                    "size": size,
                    "kind": kind,
                },
                report=report,
            )
            report["workspace"] = {"id": workspace_id, "entry_id": entry["id"]}
        except Exception as e:  # noqa: BLE001  # 分析成功优先，登记失败给出可见提示
            report["warnings"].append(f"附件已分析，但写入工作区失败: {e}")
    return report


# ---------------------------------------------------------------- 题目工作区
def _workspace_dir() -> Path:
    raw = (os.environ.get("AGENT_WORKSPACE_DIR")
           or str(_cfg("workspace", "dir", "work/workspaces")))
    p = Path(raw)
    return p if p.is_absolute() else (ROOT / p)


def _workspace_store():
    from agent.workspace import WorkspaceStore

    return WorkspaceStore(_workspace_dir())


def api_workspace_list() -> dict:
    return {"workspaces": _workspace_store().list()}


def api_workspace_get(workspace_id: str) -> dict:
    return {"workspace": _workspace_store().load(workspace_id)}


def api_workspace_create(req: dict) -> dict:
    if not isinstance(req, dict):
        raise BadRequest("请求体必须是 JSON 对象")
    ws = _workspace_store().create(
        req.get("title", ""),
        req.get("category"),
        req.get("id"),
    )
    return {"ok": True, "workspace": ws}


def api_workspace_update(workspace_id: str, req: dict) -> dict:
    if not isinstance(req, dict):
        raise BadRequest("请求体必须是 JSON 对象")
    ws = _workspace_store().update(
        workspace_id,
        title=req.get("title"),
        status=req.get("status"),
        category=req.get("category"),
    )
    return {"ok": True, "workspace": ws}


def api_workspace_add_entry(workspace_id: str, req: dict) -> dict:
    if not isinstance(req, dict):
        raise BadRequest("请求体必须是 JSON 对象")
    ws, entry = _workspace_store().add_entry(
        workspace_id,
        kind=req.get("kind", ""),
        text=req.get("text", ""),
        result=req.get("result"),
        title=req.get("title", ""),
        path=req.get("path", ""),
        url=req.get("url", ""),
        source=req.get("source", ""),
        attachment=req.get("attachment"),
        report=req.get("report"),
        direction=req.get("direction", ""),
        conclusion=req.get("conclusion", ""),
        anchor=req.get("anchor", ""),
    )
    return {"ok": True, "workspace": ws, "entry": entry}


def api_workspace_update_entry(workspace_id: str, entry_id: str,
                               req: dict) -> dict:
    if not isinstance(req, dict):
        raise BadRequest("请求体必须是 JSON 对象")
    ws, entry = _workspace_store().update_entry(
        workspace_id,
        entry_id,
        result=req.get("result"),
        text=req.get("text"),
    )
    return {"ok": True, "workspace": ws, "entry": entry}


def api_workspace_timeline(workspace_id: str) -> dict:
    return {"timeline": _workspace_store().timeline(workspace_id)}


def api_workspace_delete(workspace_id: str) -> dict:
    _workspace_store().delete(workspace_id)
    return {"ok": True}


def api_workspace_delete_entry(workspace_id: str, entry_id: str) -> dict:
    ws = _workspace_store().delete_entry(workspace_id, entry_id)
    return {"ok": True, "workspace": ws}


def api_workspace_export(workspace_id: str, fmt: str,
                         mode: str = "") -> tuple[bytes, str]:
    store = _workspace_store()
    if mode not in ("", "normal", "writeup"):
        raise BadRequest("导出模式只能是 normal 或 writeup")
    if fmt == "json":
        ws = store.load(workspace_id)
        return (json.dumps(ws, ensure_ascii=False, indent=2).encode("utf-8"),
                "application/json; charset=utf-8")
    if fmt not in ("", "md", "markdown"):
        raise BadRequest("导出格式只能是 md 或 json")
    if mode == "writeup":
        kb_root = None
        try:
            # 导出只需要 kb 根目录做存在性校验，不加载模型/索引。
            if _KB is not None:
                kb_root = _KB.cfg.kb_dir
            else:
                from kb.config import Config
                kb_root = Config.load().kb_dir
        except Exception:  # noqa: BLE001  # 无法校验时仍导出，标注“未校验”
            kb_root = None
        text = store.export_writeup(workspace_id, kb_root=kb_root)
    else:
        text = store.export_markdown(workspace_id)
    return text.encode("utf-8"), "text/markdown; charset=utf-8"


# ============================================================== 页面
WEB_DIR = Path(__file__).resolve().parent / "webapp" / "dist"

MIME = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".mjs": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".ico": "image/x-icon",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
    ".ttf": "font/ttf",
    ".map": "application/json; charset=utf-8",
}


def _static(upath: str):
    """按 URL 路径取 dist 下的文件，返回 (bytes, mime) 或 None。"""
    rel = upath.lstrip("/") or "index.html"
    root = WEB_DIR.resolve()
    p = (root / rel).resolve()
    try:
        p.relative_to(root)          # 防目录穿越
    except ValueError:
        return None
    if p.is_file():
        return p.read_bytes(), MIME.get(p.suffix.lower(), "application/octet-stream")
    return None


def _page() -> bytes:
    """首页：从 web/index.html 读，改样式不用动 Python。"""
    p = WEB_DIR / "index.html"
    if p.exists():
        return p.read_bytes()
    return "<h1>页面缺失</h1><p>tools/agent/web/index.html</p>".encode("utf-8")


# ============================================================== 后端
def _snip(doc_path: str, category: str, title: str) -> str:
    """从文档里抽一段最能说明问题的摘要。

    优先「识别信号」章节——那是题面长什么样的描述，最贴近搜索意图。
    """
    import re
    kb = get_kb()
    f = kb.cfg.kb_dir / doc_path
    if not f.exists():
        return ""
    text = f.read_text(encoding="utf-8", errors="replace")
    # 去 front-matter
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:]

    m = re.search(r"#+\s*(?:一、)?识别信号[^\n]*\n(.{20,900}?)(?=\n#|\Z)",
                  text, re.S)
    body = m.group(1) if m else text
    body = re.sub(r"```.*?```", "", body, flags=re.S)
    body = re.sub(r"[ \t]+", " ", body)
    body = re.sub(r"\n{2,}", "\n", body).strip()
    return body[:520]


def _hit_snippet(h, q: str) -> str:
    """命中段落优先用真正命中的 chunk，而不是整篇文档里再猜一段。"""
    text = getattr(h, "best_text", "") or ""
    if text:
        from kb.explain import make_snippet
        snip = make_snippet(text, q)
        if snip:
            return snip
    return _snip(h.doc_path, h.category, h.title)


def _hit_item(h, q: str, context_paths=None) -> dict:
    from kb.applicability import evaluate_conditions
    from kb.explain import doc_type, doc_type_label, match_info

    dtype = doc_type(h.doc_path)
    gv = getattr(h, "graph_via", None)
    item = {
        "title": h.title,
        "category": h.category,
        "path": h.doc_path,
        "score": round(float(h.score or 0), 5),
        "section": getattr(h, "section", "") or "",
        "snippet": _hit_snippet(h, q),
        "doc_type": dtype,
        "doc_type_label": doc_type_label(h.doc_path),
        "match": match_info(h, q),
    }
    try:
        item["applicability"] = evaluate_conditions(
            get_kb().cfg.kb_dir, h.doc_path, q, context_paths or [])
    except Exception as e:  # noqa: BLE001  # 解释失败不影响检索结果
        item["applicability"] = {"status": "unknown", "status_label": "未知",
                                 "conditions": [], "hint": f"适用条件判定失败: {e}",
                                 "trace": {"rules": 0, "requires": 0}}
    if gv:
        item["graph_via"] = gv
    return item


def api_search(req: dict) -> dict:
    import time
    if not isinstance(req, dict):
        raise BadRequest("请求体必须是 JSON 对象")
    q = _check_query(req.get("q", ""))
    cat = _check_category(req.get("category"))
    dtype_filter = _check_doc_type(req.get("doc_type"))
    k = _check_top_k(req.get("top_k"))
    counts = {"topic": 0, "card": 0}
    if not q:
        return {"hits": [], "graph": [], "ms": 0, "query": "",
                "category": cat, "doc_type": dtype_filter, "counts": counts}
    kb = get_kb()
    t0 = time.time()
    hits = kb.search(q, top_k=k, category=cat, doc_type=dtype_filter)
    ms = round((time.time() - t0) * 1000, 1)

    context = [h.doc_path for h in hits]
    out, graph = [], []
    for h in hits:
        item = _hit_item(h, q, context)
        # 图谱补进来的条目放到 graph 里，主结果只留词面/向量命中的
        if item.get("graph_via"):
            graph.append(item)
            continue
        counts[item["doc_type"]] = counts.get(item["doc_type"], 0) + 1
        out.append(item)

    # 若全部都是图谱命中（极少见），至少给一条
    if not out and graph:
        out.append(dict(graph[0]))
        counts[out[0]["doc_type"]] = counts.get(out[0]["doc_type"], 0) + 1

    applic = {"known": 0, "unknown": 0, "unsatisfied": 0}
    for item in out + graph:
        status = (item.get("applicability") or {}).get("status")
        if status in applic:
            applic[status] += 1

    return {"hits": out, "graph": graph, "ms": ms,
            "query": q, "category": cat, "doc_type": dtype_filter,
            "counts": counts, "applicability": applic}


def api_doc(path: str) -> dict:
    kb = get_kb()
    p, err = _resolve_kb_file(kb, path)
    if err:
        return {"body": "", "error": err}
    try:
        body = p.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return {"body": "", "error": f"文件不可读: {e}"}
    return {"path": path, "body": body}


ASK_SYSTEM = (
    "你是 CTF 解题助手。用户给了一段知识库内容和一个问题。\n"
    "要求：\n"
    "1) 先用一句话说明这类题的判断依据；\n"
    "2) 给出 3-5 步可执行的解题步骤；\n"
    "3) 如果涉及脚本，给出可直接运行或稍改即可用的代码。\n"
    "只依据给定的知识库内容，不要编造工具选项或不存在的语法。"
    "内容不足以回答时明说「知识库未覆盖」。用中文。"
)


def _ask_model() -> str:
    """按 /api/tags 的实际名称解析模型（如 qwen2.5-coder-7b -> :local）。"""
    import requests
    try:
        r = requests.get(f"{OLLAMA}/api/tags", timeout=3)
        r.raise_for_status()
        names = [m["name"] for m in r.json().get("models", [])]
        return _pick_model(names)
    except Exception:  # noqa: BLE001
        return MODEL


def _ask_payload(messages: list[dict[str, str]]) -> dict:
    options = {
        "num_ctx": NUM_CTX,
        "num_predict": MAX_TOKENS,
        "temperature": TEMPERATURE,
    }
    if _NUM_GPU is not None:
        options["num_gpu"] = int(_NUM_GPU)
    return {
        "model": _ask_model(),
        "messages": messages,
        "stream": True,
        "keep_alive": KEEP_ALIVE,
        "options": options,
    }


def _ask_stream(q: str, paths: list[str]):
    """生成 SSE 事件流：tok / err / done 三种事件，终态必有一个。"""
    import requests

    kb = get_kb()
    parts, err = _collect_sources(kb, paths)
    if err:
        yield _sse({"t": "err", "v": err})
        return

    # 适用前提由规则确定性判定，不让模型自由发挥；未知/不满足要显式提醒。
    check = ""
    try:
        from kb.applicability import evaluate_paths
        app = evaluate_paths(kb.cfg.kb_dir, paths, q)
        if app.get("hint"):
            check = (
                "\n\n【适用前提检查（规则判定，不是模型推断）】\n"
                + app["hint"]
                + "\n如果关键前提未知或不满足，先在回答开头明确写出「缺少前提：…（unknown）」"
                  "或「不满足：…（unsatisfied）」，不要假设它成立。"
            )
    except Exception as e:  # noqa: BLE001  # 判定失败不影响正常问答
        check = f"\n\n【适用前提检查失败】{type(e).__name__}: {e}"

    user = ("【知识库内容】\n" + "\n\n".join(parts) + check +
            f"\n\n【问题】\n{q}\n\n"
            "请给出：判断依据 → 解题步骤 → 可运行脚本。")
    payload = _ask_payload([
        {"role": "system", "content": ASK_SYSTEM},
        {"role": "user", "content": user},
    ])

    import time
    t0 = time.time()
    ntok = 0
    got_text = False
    finished = False
    r = None
    try:
        r = requests.post(f"{OLLAMA}/api/chat", json=payload,
                          stream=True, timeout=TIMEOUT)
        r.raise_for_status()
        for line in r.iter_lines():
            if not line:
                continue
            try:
                j = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if j.get("error"):
                yield _sse({"t": "err", "v": str(j["error"])})
                finished = True
                return
            piece = (j.get("message") or {}).get("content") or ""
            if piece:
                got_text = True
                ntok += 1
                yield _sse({"t": "tok", "v": piece})
            if j.get("done"):
                finished = True
                if not got_text:
                    yield _sse({"t": "err", "v": "模型没有返回内容。确认本地模型已启动。"})
                    return
                dt = max(1e-6, time.time() - t0)
                ec = j.get("eval_count") or ntok
                info = f"{ec} tok · {ec / dt:.1f} tok/s"
                yield _sse({"t": "done", "info": info})
                return
        if not finished:
            if not got_text:
                yield _sse({"t": "err", "v": "模型返回为空。确认本地模型已启动。"})
            else:
                yield _sse({"t": "done", "info": f"{ntok} tok"})
    except GeneratorExit:
        raise
    except Exception as e:  # noqa: BLE001
        yield _sse({"t": "err", "v": f"{type(e).__name__}: {e}"})
    finally:
        if r is not None:
            try:
                r.close()
            except Exception:  # noqa: BLE001
                pass


def _index_dir() -> Path:
    try:
        return CFG.index_dir if CFG is not None else (ROOT / "index")
    except Exception:  # noqa: BLE001
        return ROOT / "index"


def _index_status() -> dict:
    """索引状态独立于模型状态，health 不得互相冒充。"""
    try:
        from kb.fts import FtsIndex
        st = FtsIndex(_index_dir() / "fts.db").stats()
        docs = int(st.get("docs", 0) or 0)
        return {
            "ok": docs > 0,
            "docs": docs,
            "chunks": int(st.get("chunks", 0) or 0),
            "built_at": st.get("built_at"),
        }
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "docs": 0, "chunks": 0,
                "error": f"{type(e).__name__}: {e}"}


def _pick_model(names: list[str]) -> str:
    if MODEL in names:
        return MODEL
    base = MODEL.split(":")[0].lower()
    for n in names:
        if n.split(":")[0].lower() == base:
            return n
    return names[0] if names else MODEL


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def log_message(self, fmt, *args):    # 静音
        pass

    def _send(self, code, body: bytes, ctype: str, headers=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"),
                   "application/json; charset=utf-8")

    def do_GET(self):
        u = urlparse(self.path)
        if not u.path.startswith("/api/"):
            got = _static(u.path)
            if got:
                self._send(200, got[0], got[1])
                return
            # 单页应用回退：未知路径一律给 index.html
            idx = WEB_DIR / "index.html"
            if idx.is_file():
                self._send(200, idx.read_bytes(), "text/html; charset=utf-8")
                return
            # dist 没构建时，退回单文件简易界面
            legacy = Path(__file__).resolve().parent / "web" / "index.html"
            if legacy.is_file():
                self._send(200, legacy.read_bytes(), "text/html; charset=utf-8")
            else:
                self._send(404, b"UI not built: cd tools/agent/webapp && npm i && npm run build",
                           "text/plain")
            return
        if u.path == "/api/health":
            self._health()
        elif u.path == "/api/stats":
            self._stats()
        elif u.path == "/api/doc":
            qs = parse_qs(u.query)
            self._json(api_doc((qs.get("path") or [""])[0]))
        elif u.path == "/api/workspaces":
            self._workspace_list()
        elif u.path.startswith("/api/workspaces/"):
            self._workspace_get(u)
        else:
            self._send(404, b"not found", "text/plain")

    def _stats(self):
        try:
            from kb.fts import FtsIndex
            st = FtsIndex(_index_dir() / "fts.db").stats()
            self._json(st)
        except Exception as e:  # noqa: BLE001
            self._json({"docs": 0, "chunks": 0, "categories": {},
                        "error": f"{type(e).__name__}: {e}"})

    @staticmethod
    def _workspace_route(path: str):
        prefix = "/api/workspaces/"
        if not path.startswith(prefix):
            return None
        parts = [unquote(p) for p in path[len(prefix):].split("/") if p]
        if not parts:
            return None
        if len(parts) == 1:
            return parts[0], ""
        if len(parts) == 2:
            return parts[0], parts[1]
        if len(parts) == 3 and parts[1] == "entries":
            return parts[0], "entries/" + parts[2]
        return None

    def _workspace_error(self, e):
        from agent.workspace import WorkspaceExists, WorkspaceNotFound

        if isinstance(e, WorkspaceNotFound):
            code = 404
        elif isinstance(e, WorkspaceExists):
            code = 409
        else:
            code = 400
        self._json({"ok": False, "error": str(e)}, code)

    def _workspace_list(self):
        try:
            self._json(api_workspace_list())
        except Exception as e:  # noqa: BLE001
            self._json({"ok": False, "workspaces": [],
                        "error": f"{type(e).__name__}: {e}"}, 500)

    def _workspace_get(self, u):
        from agent.workspace import WorkspaceError

        route = self._workspace_route(u.path)
        if route is None:
            self._json({"ok": False, "error": "not found"}, 404)
            return
        wid, action = route
        qs = parse_qs(u.query)
        try:
            if action == "export":
                fmt = (qs.get("format") or ["md"])[0].lower()
                mode = (qs.get("mode") or [""])[0].lower()
                body, ctype = api_workspace_export(wid, fmt, mode)
                ext = "json" if ctype.startswith("application/json") else "md"
                suffix = "-writeup" if mode == "writeup" else ""
                self._send(200, body, ctype, {
                    "Content-Disposition":
                        f'attachment; filename="{wid}{suffix}.{ext}"',
                })
            elif action == "timeline":
                self._json(api_workspace_timeline(wid))
            elif not action:
                self._json(api_workspace_get(wid))
            else:
                self._json({"ok": False, "error": "not found"}, 404)
        except BadRequest as e:
            self._json({"ok": False, "error": str(e)}, 400)
        except WorkspaceError as e:
            self._workspace_error(e)
        except Exception as e:  # noqa: BLE001
            self._json({"ok": False,
                        "error": f"{type(e).__name__}: {e}"}, 500)

    def _workspace_post(self, u, req):
        from agent.workspace import WorkspaceError

        route = self._workspace_route(u.path)
        if route is None:
            self._json({"ok": False, "error": "not found"}, 404)
            return
        wid, action = route
        try:
            if not action:
                self._json(api_workspace_update(wid, req))
            elif action == "entries":
                self._json(api_workspace_add_entry(wid, req))
            elif action.startswith("entries/"):
                self._json(api_workspace_update_entry(
                    wid, action.split("/", 1)[1], req))
            else:
                self._json({"ok": False, "error": "not found"}, 404)
        except BadRequest as e:
            self._json({"ok": False, "error": str(e)}, 400)
        except WorkspaceError as e:
            self._workspace_error(e)
        except Exception as e:  # noqa: BLE001
            self._json({"ok": False,
                        "error": f"{type(e).__name__}: {e}"}, 500)

    def _analyze(self, u):
        """/api/analyze：原始字节上传，限大小，保存到隔离目录后只读解析。"""
        qs = parse_qs(u.query)
        name = (qs.get("name") or [""])[0]
        workspace = (qs.get("workspace") or [""])[0].strip()
        if workspace:
            from agent.workspace import WorkspaceError

            try:
                _workspace_store().load(workspace)
            except WorkspaceError as e:
                self._workspace_error(e)
                return
        try:
            n = int(self.headers.get("Content-Length", "0") or 0)
        except ValueError:
            self._json({"ok": False, "error": "Content-Length 不合法"}, 400)
            return
        limit = _attachment_max_bytes()
        if n <= 0:
            self._json({"ok": False, "error": "附件为空"}, 400)
            return
        if n > limit:
            self._json({"ok": False,
                        "error": f"附件过大（上限 {limit} 字节）"}, 413)
            return
        try:
            raw = self.rfile.read(n)
        except Exception as e:  # noqa: BLE001
            self._json({"ok": False, "error": f"附件读取失败: {e}"}, 400)
            return
        if len(raw) != n:
            self._json({"ok": False, "error": "附件读取不完整"}, 400)
            return
        try:
            self._json(api_analyze(name, raw, workspace or None))
        except BadRequest as e:
            self._json({"ok": False, "error": str(e)}, 400)
        except Exception as e:  # noqa: BLE001
            self._json({"ok": False,
                        "error": f"{type(e).__name__}: {e}"}, 500)

    def _health(self):
        import requests
        index = _index_status()
        try:
            r = requests.get(f"{OLLAMA}/api/tags", timeout=4)
            r.raise_for_status()
            names = [m["name"] for m in r.json().get("models", [])]
            model = _pick_model(names)
            self._json({
                "ok": bool(names),
                "model_ok": bool(names),
                "index_ok": index["ok"],
                "model": model,
                "models": names,
                "index": index,
                "docs": index.get("docs", 0),
                "ollama": OLLAMA,
                "attachment": {"max_bytes": _attachment_max_bytes()},
            })
        except Exception as e:  # noqa: BLE001
            self._json({
                "ok": False,
                "model_ok": False,
                "index_ok": index["ok"],
                "model": MODEL,
                "models": [],
                "index": index,
                "docs": index.get("docs", 0),
                "error": f"模型不可达: {e}",
                "ollama": OLLAMA,
                "attachment": {"max_bytes": _attachment_max_bytes()},
            })

    def do_POST(self):
        u = urlparse(self.path)
        if u.path == "/api/analyze":
            self._analyze(u)
            return
        try:
            n = int(self.headers.get("Content-Length", "0") or 0)
        except ValueError:
            self._json({"error": "Content-Length 不合法"}, 400)
            return
        if n < 0 or n > (MAX_WORKSPACE_BODY_BYTES
                         if u.path.startswith("/api/workspaces")
                         else MAX_BODY_BYTES):
            limit = (MAX_WORKSPACE_BODY_BYTES
                     if u.path.startswith("/api/workspaces") else MAX_BODY_BYTES)
            self._json({"error": f"请求体过大（上限 {limit} 字节）"}, 413)
            return
        try:
            raw = self.rfile.read(n) if n else b"{}"
            req = json.loads(raw or b"{}")
        except Exception:  # noqa: BLE001
            self._json({"error": "bad json"}, 400)
            return
        if not isinstance(req, dict):
            self._json({"error": "请求体必须是 JSON 对象"}, 400)
            return

        if u.path == "/api/search":
            try:
                self._json(api_search(req))
            except BadRequest as e:
                self._json({"hits": [], "error": str(e)}, 400)
            except Exception as e:  # noqa: BLE001
                self._json({"hits": [], "error": f"{type(e).__name__}: {e}"}, 500)
            return

        if u.path == "/api/feedback":
            try:
                self._json(api_feedback(req))
            except BadRequest as e:
                self._json({"ok": False, "error": str(e)}, 400)
            except Exception as e:  # noqa: BLE001
                self._json({"ok": False, "error": f"{type(e).__name__}: {e}"}, 500)
            return

        if u.path == "/api/workspaces":
            from agent.workspace import WorkspaceError

            try:
                self._json(api_workspace_create(req))
            except WorkspaceError as e:
                self._workspace_error(e)
            except Exception as e:  # noqa: BLE001
                self._json({"ok": False,
                            "error": f"{type(e).__name__}: {e}"}, 500)
            return

        if u.path.startswith("/api/workspaces/"):
            self._workspace_post(u, req)
            return

        if u.path == "/api/ask":
            try:
                q = _check_query(req.get("q", ""))
                paths = req.get("paths")
                if not q:
                    raise BadRequest("需要问题 q")
                if not isinstance(paths, list) or not paths:
                    raise BadRequest("需要至少一个知识库路径")
                if len(paths) > MAX_PATHS:
                    raise BadRequest(f"最多引用 {MAX_PATHS} 篇资料")
            except BadRequest as e:
                self._json({"error": str(e)}, 400)
                return

            # 串行生成：忙碌时立即拒绝，避免显存被打爆。
            if not _ASK_LOCK.acquire(blocking=False):
                self._json({"error": "模型正在处理上一条问题，请稍后再试"}, 429)
                return

            gen = None
            try:
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream; charset=utf-8")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "close")
                self.end_headers()
                gen = _ask_stream(q, paths)
                for chunk in gen:
                    self.wfile.write(chunk.encode("utf-8"))
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                # 客户端断开：关闭生成器，尽量让上游 requests 连接一起释放。
                pass
            finally:
                if gen is not None:
                    try:
                        gen.close()
                    except Exception:  # noqa: BLE001
                        pass
                _ASK_LOCK.release()
            return

        self._json({"error": "not found"}, 404)

    def do_DELETE(self):
        u = urlparse(self.path)
        from agent.workspace import WorkspaceError

        route = self._workspace_route(u.path)
        if route is None:
            self._json({"ok": False, "error": "not found"}, 404)
            return
        wid, action = route
        try:
            if not action:
                self._json(api_workspace_delete(wid))
            elif action.startswith("entries/"):
                self._json(api_workspace_delete_entry(
                    wid, action.split("/", 1)[1]))
            else:
                self._json({"ok": False, "error": "not found"}, 404)
        except WorkspaceError as e:
            self._workspace_error(e)
        except Exception as e:  # noqa: BLE001
            self._json({"ok": False,
                        "error": f"{type(e).__name__}: {e}"}, 500)


def main() -> int:
    print(f"CTF 知识库  http://{HOST}:{PORT}")
    print(f"  模型: {MODEL}")
    print(f"  Ollama: {OLLAMA}")
    print("  首次搜索会加载嵌入模型（约 1-2 秒）")
    srv = ThreadingHTTPServer((HOST, PORT), Handler)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
