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
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

HOST = os.environ.get("AGENT_HOST", "127.0.0.1")
PORT = int(os.environ.get("AGENT_PORT", "8765"))
OLLAMA = os.environ.get("AGENT_OLLAMA", "http://127.0.0.1:11434")
MODEL = os.environ.get("AGENT_MODEL", "qwen3-4b-local:latest")

# 每类结果的命中上限，避免同方向刷屏
CATS = ["misc", "crypto", "web", "pwn", "reverse",
        "forensics", "mobile", "hardware", "osint", "ai", "blockchain"]

_KB = None
_KB_LOCK = threading.Lock()


def get_kb():
    """惰性初始化 KB（首次搜索时加载嵌入模型，约 1-2 秒）。"""
    global _KB
    if _KB is None:
        with _KB_LOCK:
            if _KB is None:
                from kb.config import Config
                from kb.rag import KB
                _KB = KB(Config.load())
    return _KB


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
    q = (req.get("q") or "").strip()
    if not q:
        return {"hits": [], "ms": 0}
    cat = req.get("category") or None
    k = int(req.get("top_k") or 8)
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
    p = (kb.cfg.kb_dir / path).resolve()
    try:
        p.relative_to(kb.cfg.kb_dir.resolve())
    except ValueError:
        return {"body": "", "error": "路径越界"}
    if not p.exists():
        return {"body": "", "error": "文件不存在"}
    return {"path": path, "body": p.read_text(encoding="utf-8", errors="replace")}


ASK_SYSTEM = (
    "你是 CTF 解题助手。用户给了一段知识库内容和一个问题。\n"
    "要求：\n"
    "1) 先用一句话说明这类题的判断依据；\n"
    "2) 给出 3-5 步可执行的解题步骤；\n"
    "3) 如果涉及脚本，给出可直接运行或稍改即可用的代码。\n"
    "只依据给定的知识库内容，不要编造工具选项或不存在的语法。"
    "内容不足以回答时明说「知识库未覆盖」。用中文。"
)


def _ask_stream(q: str, paths: list[str]):
    """生成 SSE 事件流（yield 字符串）。"""
    import requests

    kb = get_kb()
    parts = []
    for path in paths[:3]:
        p = (kb.cfg.kb_dir / path).resolve()
        if not p.exists():
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        if t.startswith("---"):
            e = t.find("\n---", 3)
            if e != -1:
                t = t[e + 4:]
        parts.append(f"【{path}】\n{t[:2600]}")

    if not parts:
        yield 'data: {"t":"err","v":"没有可用的知识库内容"}\n\n'
        return

    user = ("【知识库内容】\n" + "\n\n".join(parts) +
            f"\n\n【问题】\n{q}\n\n"
            "请给出：判断依据 → 解题步骤 → 可运行脚本。")

    payload = {
        "model": MODEL,
        "messages": [{"role": "system", "content": ASK_SYSTEM},
                     {"role": "user", "content": user}],
        "stream": True,
        "options": {"num_ctx": 8192, "num_predict": 900, "temperature": 0.2},
    }
    t0 = 0.0
    ntok = 0
    try:
        import time
        t0 = time.time()
        with requests.post(f"{OLLAMA}/api/chat", json=payload,
                           stream=True, timeout=300) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line:
                    continue
                try:
                    j = json.loads(line)
                except json.JSONDecodeError:
                    continue
                piece = (j.get("message") or {}).get("content") or ""
                if piece:
                    ntok += 1
                    yield "data: " + json.dumps({"t": "tok", "v": piece},
                                                ensure_ascii=False) + "\n\n"
                if j.get("done"):
                    dt = max(1e-6, time.time() - t0)
                    ec = j.get("eval_count") or ntok
                    info = f"{ec} tok · {ec/dt:.1f} tok/s"
                    yield "data: " + json.dumps(
                        {"t": "done", "info": info}, ensure_ascii=False) + "\n\n"
    except Exception as e:  # noqa: BLE001
        yield "data: " + json.dumps(
            {"t": "err", "v": f"{type(e).__name__}: {e}"},
            ensure_ascii=False) + "\n\n"


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
            st = FtsIndex(get_kb().cfg.index_dir / "fts.db").stats()
            self._json(st)
        except Exception as e:
            self._json({"docs": 0, "chunks": 0, "categories": {},
                        "error": f"{type(e).__name__}: {e}"})

    def _health(self):
        import requests
        try:
            r = requests.get(f"{OLLAMA}/api/tags", timeout=4)
            r.raise_for_status()
            names = [m["name"] for m in r.json().get("models", [])]
            model = MODEL if MODEL in names else (names[0] if names else "-")
            kb = get_kb()
            n = sum(1 for _ in kb.cfg.kb_dir.rglob("*.md"))
            self._json({"ok": bool(names), "model": model, "models": names,
                        "docs": n, "ollama": OLLAMA})
        except Exception as e:  # noqa: BLE001
            self._json({"ok": False, "error": f"模型不可达: {e}", "docs": 0})

    def do_POST(self):
        u = urlparse(self.path)
        n = int(self.headers.get("Content-Length", "0") or 0)
        try:
            req = json.loads(self.rfile.read(n) or b"{}")
        except Exception:  # noqa: BLE001
            self._json({"error": "bad json"}, 400)
            return

        if u.path == "/api/search":
            try:
                self._json(api_search(req))
            except Exception as e:  # noqa: BLE001
                self._json({"hits": [], "error": f"{type(e).__name__}: {e}"}, 500)
            return

        if u.path == "/api/ask":
            q = (req.get("q") or "").strip()
            paths = req.get("paths") or []
            if not q or not paths:
                self._json({"error": "需要 q 和 paths"}, 400)
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "close")
            self.end_headers()
            try:
                for chunk in _ask_stream(q, paths):
                    self.wfile.write(chunk.encode("utf-8"))
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
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
