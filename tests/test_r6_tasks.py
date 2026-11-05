from test_server_api import call, env, server, sse_events


def test_direct_sends_only_original_input(env, monkeypatch):
    seen = []
    def collect(messages, state):
        seen.extend(messages)
        yield server._sse({"t": "tok", "v": "结果"})
        yield server._sse({"t": "done", "info": "完成"})
    monkeypatch.setattr(server, "_stream_messages", collect)
    text = "  原文\n保留空格  "
    code, body, _ = call(env, "POST", "/api/ask", {
        "q": text, "task": "raw", "paths": ["不应读取"], "workspace_id": "不应读取",
    })
    assert code == 200 and sse_events(body)[-1]["t"] == "done"
    assert seen == [{"role": "user", "content": text}]


def test_translation_does_not_read_workspace_or_search(env, monkeypatch):
    seen = []
    def collect(messages, state):
        seen.extend(messages)
        yield server._sse({"t": "done", "info": "完成"})
    monkeypatch.setattr(server, "_stream_messages", collect)
    monkeypatch.setattr(server, "get_kb", lambda: (_ for _ in ()).throw(AssertionError("翻译不得查库")))
    code, _, _ = call(env, "POST", "/api/ask", {"q": "Keep `bytes.decode`", "task": "translate", "target": "zh"})
    assert code == 200 and len(seen) == 2
    assert seen[0]["role"] == "system" and "中文" in seen[0]["content"]
    assert seen[1] == {"role": "user", "content": "Keep `bytes.decode`"}
