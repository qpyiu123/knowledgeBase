"""设置页的保存、当前值与生效说明。"""
from __future__ import annotations

import os
import threading

from kb.config import Config
from kb.user_settings import FIELDS, OVERRIDES, normalize, read, save

LOCK = threading.Lock()


def fields(saved_cfg, active_cfg):
    result = []
    for name, (group, label, default, limits, apply) in FIELDS.items():
        section, key = name.split(".", 1)
        override = OVERRIDES.get(name)
        env = os.environ.get(override) if override else None
        value = saved_cfg.get(section, key, default)
        effective = active_cfg.get(section, key, default)
        if env:
            effective = ("cpu" if env == "1" else effective) if name == "llama_server.compute" else env
        result.append({"key": name, "group": group, "label": label, "value": value,
                       "effective": effective, "override": override if env else None,
                       "kind": type(default).__name__, "options": limits if isinstance(default, str) else [],
                       "limits": limits if isinstance(default, (int, float)) else [], "apply": apply})
    return result


def update(config, changes):
    changes = normalize(changes)
    with LOCK:
        proposed = {**read(config.path), **changes}
        saved = Config.load(config.path, environment=False)
        for name, value in proposed.items():
            section, key = name.split(".", 1)
            saved.data.setdefault(section, {})[key] = value
        if saved.get("llm", "max_tokens") >= saved.get("llm", "n_ctx"):
            raise ValueError("最大输出长度应小于上下文长度")
        if saved.get("search", "chunk_overlap") >= saved.get("search", "chunk_chars"):
            raise ValueError("片段重叠长度应小于片段长度")
        if saved.get("runtime", "port", 8765) == saved.get("llama_server", "port", 8766):
            raise ValueError("网页端口和推理端口不能相同")
        save(config.path, proposed)
        live = {section: dict(values) for section, values in config.data.items()}
        for name, value in changes.items():
            if FIELDS[name][4] in ("立即", "下次启动模型") and not os.environ.get(OVERRIDES.get(name, "")):
                section, key = name.split(".", 1)
                live.setdefault(section, {})[key] = value
        return Config(data=live, path=config.path)
