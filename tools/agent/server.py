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
  POST /api/hint         {path, question} -> 方向建议（附件侦察 + 小模型）

启动：python tools/agent/server.py
"""
from __future__ import annotations

import json
import os
import re
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

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
MAX_QUERY_CHARS = 2000              # 问题/搜索词
MAX_TOP_K = 50
MAX_PATHS = 3                       # /api/ask 最多读几篇
MAX_DOC_BYTES = 1024 * 1024         # 单篇 Markdown 上限
MAX_PER_DOC_CHARS = 2600            # 送进模型的单篇字符上限
MAX_CONTEXT_CHARS = 12000           # 送进模型的总字符上限
MAX_PATH_CHARS = 500

# 每类结果的命中上限，避免同方向刷屏
CATS = ["misc", "crypto", "web", "pwn", "reverse",
        "forensics", "mobile", "hardware", "osint", "ai", "blockchain"]

_KB = None
_KB_LOCK = threading.Lock()
# /api/ask 串行：4GB 显存下并发生成会互相挤爆。忙碌时直接拒绝，不排队。
_ASK_LOCK = threading.Lock()


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


def api_search(req: dict) -> dict:
    import time
    if not isinstance(req, dict):
        raise BadRequest("请求体必须是 JSON 对象")
    q = _check_query(req.get("q", ""))
    cat = _check_category(req.get("category"))
    k = _check_top_k(req.get("top_k"))
    if not q:
        return {"hits": [], "ms": 0, "query": "", "category": cat}
    kb = get_kb()
    t0 = time.time()
    hits = kb.search(q, top_k=k, category=cat)
    ms = round((time.time() - t0) * 1000, 1)

    out, graph = [], []
    for h in hits:
        gv = getattr(h, "graph_via", None)
        item = {
            "title": h.title, "category": h.category, "path": h.doc_path,
            "score": round(float(h.score or 0), 5),
            "snippet": _snip(h.doc_path, h.category, h.title),
        }
        if gv:
            item["graph_via"] = gv
            graph.append({"title": h.title, "path": h.doc_path, "via": gv})
        # 图谱补进来的条目放到 graph 里，主结果只留词面/向量命中的
        if gv:
            continue
        out.append(item)

    # 若全部都是图谱命中（极少见），至少给一条
    if not out and graph:
        out.append({"title": graph[0]["title"], "category": "",
                    "path": graph[0]["path"], "score": 0,
                    "snippet": "", "graph_via": graph[0]["via"]})

    return {"hits": out, "graph": graph, "ms": ms,
            "query": q, "category": cat}


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

    user = ("【知识库内容】\n" + "\n\n".join(parts) +
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

    def _send(self, code, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
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
            })

    def do_POST(self):
        u = urlparse(self.path)
        try:
            n = int(self.headers.get("Content-Length", "0") or 0)
        except ValueError:
            self._json({"error": "Content-Length 不合法"}, 400)
            return
        if n < 0 or n > MAX_BODY_BYTES:
            self._json({"error": f"请求体过大（上限 {MAX_BODY_BYTES} 字节）"}, 413)
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
