"""配置读取。优先 tomllib（3.11+），失败回退到极简 ini 解析。"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

try:  # Python 3.11+
    import tomllib as _toml

    def _load_toml(text: str) -> dict[str, Any]:
        return _toml.loads(text)

except ModuleNotFoundError:  # pragma: no cover
    _toml = None

    def _load_toml(text: str) -> dict[str, Any]:
        raise RuntimeError("需要 Python 3.11+ 的 tomllib，或安装 tomli")


DEFAULT_CONFIG = """\
[kb]
root = "."
kb_dir = "kb"
index_dir = "index"
models_dir = "models"

[search]
top_k = 8
rrf_k = 60
chunk_chars = 900
chunk_overlap = 120

[embed]
model_dir = "models/bge-small-zh-v1.5"
model_id = "BAAI/bge-small-zh-v1.5"
query_prefix = "为这个句子生成表示以用于检索相关文章："
batch_size = 32

[llm]
backend = "llama_cpp"        # llama_cpp | ollama | none
gguf_path = "models/gguf/qwen2.5-coder-7b-instruct-q4_k_m.gguf"
chat_format = "chatml"
n_ctx = 6144
n_gpu_layers = 20
kv_cache_type = "q8_0"
n_threads = 8
n_batch = 256
temperature = 0.2
max_tokens = 1200
timeout = 300

[ollama]
host = "http://127.0.0.1:11434"
model = "qwen2.5-coder:7b"
"""


def _deep_merge(base: dict, extra: dict) -> dict:
    out = dict(base)
    for k, v in extra.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def _defaults() -> dict[str, Any]:
    return _load_toml(DEFAULT_CONFIG)


@dataclass
class Config:
    data: dict[str, Any] = field(default_factory=_defaults)
    path: Path = ROOT / "config.toml"

    # ---- 便捷访问器 ----
    @property
    def kb_root(self) -> Path:
        return _abs(self.data["kb"]["root"])

    @property
    def kb_dir(self) -> Path:
        return self.kb_root / self.data["kb"]["kb_dir"]

    @property
    def index_dir(self) -> Path:
        return self.kb_root / self.data["kb"]["index_dir"]

    @property
    def models_dir(self) -> Path:
        return self.kb_root / self.data["kb"]["models_dir"]

    def get(self, section: str, key: str, default: Any = None) -> Any:
        return self.data.get(section, {}).get(key, default)

    def resolve(self, rel: str) -> Path:
        return _abs(rel)

    # ---- 加载 ----
    @classmethod
    def load(cls, path: str | Path | None = None) -> "Config":
        p = Path(path) if path else ROOT / "config.toml"
        data = _defaults()
        if p.exists():
            # 必须按 UTF-8 显式解码：Windows 上直接 open() 会走 GBK，
            # 导致 config.toml 里的中文（如 BGE 的 query 前缀）变乱码且静默失效。
            raw = p.read_bytes()
            if raw.startswith(b"\xef\xbb\xbf"):
                raw = raw[3:]
            loaded = _load_toml(raw.decode("utf-8", errors="replace"))
            data = _deep_merge(data, loaded)
        # 环境变量覆盖（方便临时切换后端）
        if os.environ.get("KB_LLM_BACKEND"):
            data["llm"]["backend"] = os.environ["KB_LLM_BACKEND"]
        if os.environ.get("KB_GGUF_PATH"):
            data["llm"]["gguf_path"] = os.environ["KB_GGUF_PATH"]
        if os.environ.get("KB_N_GPU_LAYERS"):
            data["llm"]["n_gpu_layers"] = int(os.environ["KB_N_GPU_LAYERS"])
        if os.environ.get("KB_OLLAMA_MODEL"):
            data["ollama"]["model"] = os.environ["KB_OLLAMA_MODEL"]
        return cls(data=data, path=p)

    def ensure_dirs(self) -> None:
        for d in (self.kb_dir, self.index_dir, self.models_dir):
            d.mkdir(parents=True, exist_ok=True)


def _abs(p: str | Path) -> Path:
    path = Path(p)
    return path if path.is_absolute() else (ROOT / path).resolve()
