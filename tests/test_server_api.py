"""server.py 核心端点的离线测试。

不启动真实 Ollama、不加载嵌入模型：get_kb 用 FakeKB，requests 用 Mock。
"""
from __future__ import annotations

import http.client
import json
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from agent import server
from kb.fts import FtsIndex
from kb.parser import Doc


class FakeCfg:
    def __init__(self, kb_dir: Path, index_dir: Path):
        self.kb_dir = kb_dir
        self.index_dir = index_dir

    def get(self, section: str, key: str, default=None):
        return default


class FakeHit:
    def __init__(self, path: str, title: str = "RSA", category: str = "crypto"):
        self.doc_path = path
        self.title = title
        self.category = category
        self.score = 0.75


class FakeKB:
    def __init__(self, kb_dir: Path, index_dir: Path):
        self.cfg = FakeCfg(kb_dir, index_dir)
        self.calls: list[dict] = []

    def search(self, q, top_k=None, category=None, **_):
        self.calls.append({"q": q, "top_k": top_k, "category": category})
        return [FakeHit("crypto/rsa.md")]


class FakeResp:
    status_code = 200

    def __init__(self, lines=None, payload=None):
        self._lines = lines or []
        self._payload = payload
        self.closed = False

    def raise_for_status(self):
        pass

    def iter_lines(self):
        for item in self._lines:
            yield item

    def json(self):
        return self._payload

    def close(self):
        self.closed = True


@pytest.fixture()
def env(tmp_path: Path, monkeypatch):
    kb_dir = tmp_path / "kb"
    (kb_dir / "crypto").mkdir(parents=True)
    (kb_dir / "crypto" / "rsa.md").write_text(
        "---\ntitle: RSA\n---\n## 识别信号\n题目给了同一个 n，两组密文。\n",
        encoding="utf-8",
    )
    (tmp_path / "secret.txt").write_text("DO-NOT-LEAK", encoding="utf-8")
    (tmp_path / "config.toml").write_text("secret = 'DO-NOT-LEAK'", encoding="utf-8")

    index_dir = tmp_path / "index"
    index_dir.mkdir()
    fts = FtsIndex(index_dir / "fts.db")
    fts.rebuild([Doc(path="crypto/rsa.md", title="RSA", category="crypto",
                     tags=[], signals=[], body="正文")])

    fake_kb = FakeKB(kb_dir, index_dir)
    monkeypatch.setattr(server, "CFG", fake_kb.cfg)
    monkeypatch.setattr(server, "_KB", fake_kb)

    srv = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    try:
        yield {"port": srv.server_address[1], "kb": fake_kb, "tmp": tmp_path,
               "index_dir": index_dir}
    finally:
        srv.shutdown()
        srv.server_close()
        th.join(timeout=5)


def call(env, method: str, path: str, body=None):
    conn = http.client.HTTPConnection("127.0.0.1", env["port"], timeout=10)
    try:
        data = None
        headers = {}
        if body is not None:
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        conn.request(method, path, body=data, headers=headers)
        r = conn.getresponse()
        text = r.read().decode("utf-8", errors="replace")
        return r.status, text, r.getheader("Content-Type") or ""
    finally:
        conn.close()


def sse_events(text: str):
    events = []
    for line in text.splitlines():
        if line.startswith("data: "):
            events.append(json.loads(line[6:]))
    return events


def test_health_reports_model_and_index_independently(env, monkeypatch):
    def fail_get(*_a, **_k):
        raise ConnectionError("ollama down")

    monkeypatch.setattr("requests.get", fail_get)
    status, text, _ = call(env, "GET", "/api/health")
    body = json.loads(text)

    assert status == 200
    assert body["ok"] is False
    assert body["model_ok"] is False
    assert body["index_ok"] is True
    assert body["docs"] == 1
    assert body["index"]["docs"] == 1


def test_health_resolves_actual_model_name(env, monkeypatch):
    monkeypatch.setattr(
        "requests.get",
        lambda *a, **k: FakeResp(payload={"models": [
            {"name": "qwen2.5-coder-7b:local"},
            {"name": "other:latest"},
        ]}),
    )
    status, text, _ = call(env, "GET", "/api/health")
    body = json.loads(text)

    assert status == 200
    assert body["model_ok"] is True
    assert body["model"] == "qwen2.5-coder-7b:local"


def test_search_returns_hits_and_snippet(env):
    status, text, ctype = call(env, "POST", "/api/search",
                               {"q": "两组密文", "top_k": 5})
    body = json.loads(text)

    assert status == 200
    assert "application/json" in ctype
    assert body["hits"][0]["path"] == "crypto/rsa.md"
    assert "同一个 n" in body["hits"][0]["snippet"]
    assert env["kb"].calls[-1]["top_k"] == 5


@pytest.mark.parametrize("payload", [
    {"q": "x", "top_k": 999},
    {"q": "x", "top_k": "abc"},
    {"q": "x", "category": "not-a-cat"},
    {"q": ["not", "a", "string"]},
    {"q": "x" * (server.MAX_QUERY_CHARS + 1)},
])
def test_search_rejects_bad_input(env, payload):
    status, text, _ = call(env, "POST", "/api/search", payload)
    assert status == 400
    assert "error" in json.loads(text)


def test_doc_reads_inside_kb(env):
    status, text, _ = call(env, "GET", "/api/doc?path=crypto%2Frsa.md")
    body = json.loads(text)
    assert status == 200
    assert "同一个 n" in body["body"]


@pytest.mark.parametrize("path", [
    "../config.toml",
    "..%2Fconfig.toml",
    "%2Fetc%2Fpasswd",
    "C%3A%5CWindows%5Cwin.ini",
    "crypto%2F..%2F..%2Fsecret.txt",
    "crypto%2Frsa.txt",
])
def test_doc_rejects_outside_or_non_markdown(env, path):
    status, text, _ = call(env, "GET", "/api/doc?path=" + path)
    body = json.loads(text)
    assert status == 200
    assert body["error"]
    assert "DO-NOT-LEAK" not in text


@pytest.mark.parametrize("payload", [
    {"q": "x", "paths": "crypto/rsa.md"},
    {"q": "x", "paths": []},
    {"q": "x", "paths": ["crypto/rsa.md"] * (server.MAX_PATHS + 1)},
    {"q": "x" * (server.MAX_QUERY_CHARS + 1), "paths": ["crypto/rsa.md"]},
    {"q": "", "paths": ["crypto/rsa.md"]},
])
def test_ask_rejects_bad_input(env, payload):
    status, text, _ = call(env, "POST", "/api/ask", payload)
    assert status == 400
    assert "error" in json.loads(text)


def test_ask_rejects_path_traversal_without_leaking(env):
    status, text, ctype = call(env, "POST", "/api/ask", {
        "q": "读一下配置",
        "paths": ["../config.toml"],
    })
    assert status == 200
    assert "text/event-stream" in ctype
    events = sse_events(text)
    assert events and events[0]["t"] == "err"
    assert "路径越界" in events[0]["v"]
    assert "DO-NOT-LEAK" not in text


def test_ask_is_serial_and_rejects_when_busy(env):
    assert server._ASK_LOCK.acquire(blocking=False)
    try:
        status, text, _ = call(env, "POST", "/api/ask", {
            "q": "问题", "paths": ["crypto/rsa.md"],
        })
    finally:
        server._ASK_LOCK.release()

    assert status == 429
    assert "正在处理上一条问题" in json.loads(text)["error"]


def test_ask_stream_tok_done_contract(env, monkeypatch):
    monkeypatch.setattr(
        "requests.get",
        lambda *a, **k: FakeResp(payload={"models": [
            {"name": "qwen2.5-coder-7b:local"}]}),
    )
    fake = FakeResp(lines=[
        b'{"message":{"content":"\xe4\xbd\xa0"},"done":false}',
        b'{"message":{"content":"\xe5\xa5\xbd"},"done":false}',
        b'{"done":true,"eval_count":2}',
    ])
    seen: dict = {}

    def fake_post(_url, **kwargs):
        seen.update(kwargs.get("json") or {})
        return fake

    monkeypatch.setattr("requests.post", fake_post)

    status, text, ctype = call(env, "POST", "/api/ask", {
        "q": "问题", "paths": ["crypto/rsa.md"],
    })
    events = sse_events(text)

    assert status == 200
    assert "text/event-stream" in ctype
    assert seen["model"] == "qwen2.5-coder-7b:local"
    assert seen["options"]["num_ctx"] == server.NUM_CTX
    assert [e["t"] for e in events] == ["tok", "tok", "done"]
    assert "".join(e.get("v", "") for e in events) == "你好"
    assert events[-1]["info"].endswith("tok/s")
    assert fake.closed is True


def test_ask_stream_emits_err_on_model_exception(env, monkeypatch):
    monkeypatch.setattr("requests.get", lambda *a, **k: FakeResp(payload={"models": []}))

    def boom(*_a, **_k):
        raise RuntimeError("connection refused")

    monkeypatch.setattr("requests.post", boom)
    status, text, _ = call(env, "POST", "/api/ask", {
        "q": "问题", "paths": ["crypto/rsa.md"],
    })
    events = sse_events(text)

    assert status == 200
    assert events[-1]["t"] == "err"
    assert "RuntimeError" in events[-1]["v"]


def test_ask_stream_empty_model_output_is_err(env, monkeypatch):
    monkeypatch.setattr("requests.get", lambda *a, **k: FakeResp(payload={"models": []}))
    fake = FakeResp(lines=[b'{"done":true,"eval_count":0}'])
    monkeypatch.setattr("requests.post", lambda *a, **k: fake)

    status, text, _ = call(env, "POST", "/api/ask", {
        "q": "问题", "paths": ["crypto/rsa.md"],
    })
    events = sse_events(text)

    assert status == 200
    assert events[-1]["t"] == "err"
    assert "模型没有返回内容" in events[-1]["v"]
