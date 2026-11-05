import socket

import pytest

from agent import settings
from agent.model_control import ModelControl
from kb.config import Config


def test_settings_saved_and_restart_values_are_separate(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text("[runtime]\nport=8765\n", encoding="utf-8")
    active = Config.load(path)
    changed = settings.update(active, {
        "ui.generation": "manual", "search.top_k": 12, "runtime.port": 9210,
    })
    assert changed.get("ui", "generation") == "manual"
    assert changed.get("search", "top_k") == 12
    assert changed.get("runtime", "port") == 8765
    assert Config.load(path).get("runtime", "port") == 9210
    assert path.read_text(encoding="utf-8") == "[runtime]\nport=8765\n"
    with pytest.raises(ValueError):
        settings.update(changed, {"llm.n_ctx": 512})
    assert Config.load(path).get("llm", "n_ctx") == 8192


def test_model_status_and_manual_policy_do_not_spawn(tmp_path, monkeypatch):
    import llama_runtime
    monkeypatch.setattr(llama_runtime, "spawn", lambda *args: pytest.fail("不应启动模型"))
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    cfg = Config()
    cfg.data["llama_server"]["port"] = port
    control = ModelControl(tmp_path)
    assert control.status()["state"] == "stopped"
    with pytest.raises(RuntimeError, match="设置"):
        control.prepare(cfg, allow_start=False)


def test_demand_load_is_reused_and_stop_only_owned_process(tmp_path, monkeypatch):
    import llama_runtime
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    cfg = Config()
    cfg.data["llama_server"]["port"] = port
    calls = []
    class Process:
        pid = 321
        code = None
        def poll(self): return self.code
        def terminate(self): self.code = 0
        def wait(self, timeout): return self.code
    p = Process()
    monkeypatch.setattr(llama_runtime, "spawn", lambda *args: calls.append(args) or p)
    monkeypatch.setattr(llama_runtime, "wait_ready", lambda *args, **kwargs: {})
    control = ModelControl(tmp_path)
    assert control.prepare(cfg) is cfg
    assert control.prepare(cfg, allow_start=False) is cfg
    assert control.status()["state"] == "ready" and len(calls) == 1
    control.stop()
    assert p.code == 0 and control.status()["state"] == "stopped"
