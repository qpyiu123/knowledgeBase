"""本地大模型后端。

本机实测结论（RTX 3050 Ti Laptop 4GB / i5-12500H / 31GB RAM）：

| 方案                       | 速度       | 备注 |
|---------------------------|-----------|------|
| Ollama + 7B Q4_K_M 默认   | 16.2 tok/s | 显存峰值 3662/4096 MB |
| Ollama + num_gpu=16       | 18.2 tok/s | 最佳点 |
| Ollama + num_gpu=20       |  3.9 tok/s | 超显存，掉回 CPU，别用 |
| Ollama + num_gpu=0        |  9.7 tok/s | 纯 CPU 对照 |
| llama-cpp-python 直载 3B  |  9.6 tok/s | pip wheel 无 CUDA 后端 |

以上为历史开发机数据。当前默认使用独立 llama-server / Vulkan，
Qwen3.5-9B 默认、4B 可选；Ollama 和 Python 直载保留显式兼容入口。
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

from .config import Config


@dataclass
class GenResult:
    text: str
    model: str
    backend: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    seconds: float = 0.0
    tokens_per_sec: float = 0.0
    extra: dict[str, Any] = field(default_factory=dict)


class LLMError(RuntimeError):
    pass


class BaseBackend:
    name = "base"

    def chat(self, messages: list[dict[str, str]], max_tokens: int | None = None,
             temperature: float | None = None) -> GenResult:
        raise NotImplementedError

    def stream(self, messages: list[dict[str, str]], max_tokens: int | None = None,
               temperature: float | None = None) -> Iterator[str]:
        yield self.chat(messages, max_tokens, temperature).text

    def health(self) -> tuple[bool, str]:
        return True, "ok"


# ---------------------------------------------------------------- Ollama
class OllamaBackend(BaseBackend):
    name = "ollama"

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.host = str(cfg.get("ollama", "host", "http://127.0.0.1:11434")).rstrip("/")
        self._want = str(cfg.get("ollama", "model", "qwen2.5-coder-7b"))
        self._resolved: str | None = None

    # ---- 模型名解析 ----
    def list_models(self) -> list[dict]:
        """返回 /api/tags 的完整条目，包含 name / model / digest。

        坑：用 `ollama create xxx:local -f Modelfile` 从本地 GGUF 导入时，
        /api/tags 里的 `name` 是 `xxx:local`，但**实际能被 /api/chat 接受的是
        digest 前缀**（如 b9b2b23ea43d）。只按 name 调用会 404。
        所以这里把 name / model / digest 前 12 位都当作候选标识。
        """
        import requests
        try:
            r = requests.get(f"{self.host}/api/tags", timeout=5)
            r.raise_for_status()
            return list(r.json().get("models", []))
        except Exception as e:  # noqa: BLE001
            raise LLMError(f"连不上 Ollama ({self.host})：{e}") from e

    @staticmethod
    def _candidates(entry: dict) -> list[str]:
        cands = []
        for key in ("name", "model"):
            v = entry.get(key)
            if v and v not in cands:
                cands.append(v)
        d = entry.get("digest") or ""
        if d:
            short = d.split(":")[-1][:12]
            if short and short not in cands:
                cands.append(short)
        return cands

    def resolve_model(self) -> str:
        """把配置里的期望名解析成**实际能被 /api/chat 接受**的标识。

        策略：
          1) 把 /api/tags 里的 name / model / digest12 全部作为候选
          2) 按与配置名的相似度排序（完全一致 > 基础名一致 > 互相包含）
          3) 用 /api/show 逐个探测，返回第一个真能用的
        这样即使 Ollama 因为导入方式不同而只用 digest 索引模型，也能自动对上。
        """
        if self._resolved:
            return self._resolved
        entries = self.list_models()
        if not entries:
            raise LLMError("Ollama 里没有任何模型（运行 tools\\setup_ollama.ps1 导入）")

        want = self._want.lower()
        base = want.split(":")[0]

        def norm(s: str) -> str:
            # 去掉 :tag / :latest，并把 . _ - 视作等价，方便 qwen2.5-coder-7b 与 qwen25-coder-7b 互认
            s = s.lower().split(":")[0]
            for ch in (".", "_", "-"):
                s = s.replace(ch, "")
            return s

        wnorm = norm(want)

        def score(name: str) -> int:
            n = name.lower()
            nn = norm(n)
            if n == want:
                return 100
            if nn == wnorm:
                return 80
            if nn.startswith(wnorm) or wnorm.startswith(nn):
                return 60
            if wnorm in nn:
                return 40
            if len(nn) == 12 and all(c in "0123456789abcdef" for c in nn):
                return 10          # digest 前缀，兜底
            return 0

        # 收集 (score, candidate)，按分数降序去重
        scored: list[tuple[int, str]] = []
        seen: set[str] = set()
        for e in entries:
            for c in self._candidates(e):
                if c in seen:
                    continue
                seen.add(c)
                s = score(c)
                if s > 0:
                    scored.append((s, c))
        scored.sort(key=lambda x: -x[0])

        if not scored:
            names = [e.get("name", "?") for e in entries]
            raise LLMError(f"Ollama 里找不到匹配 {self._want!r} 的模型，现有：{names}")

        # 同分优先按 name 而非 digest 探测
        for sc, cand in scored:
            if self._probe(cand):
                self._resolved = cand
                return cand

        self._resolved = scored[0][1]
        return self._resolved

    def _probe(self, name: str) -> bool:
        """用 /api/show 验证这个名字 Ollama 认不认。"""
        import requests
        try:
            r = requests.post(f"{self.host}/api/show", json={"model": name}, timeout=5)
            return r.status_code == 200
        except Exception:  # noqa: BLE001
            return False

    def health(self) -> tuple[bool, str]:
        try:
            name = self.resolve_model()
            return True, f"{self.host} / {name}"
        except LLMError as e:
            return False, str(e)

    # ---- 调用 ----
    def _post(self, payload: dict, stream: bool = False):
        import requests
        try:
            r = requests.post(f"{self.host}/api/chat", json=payload, stream=stream,
                              timeout=int(self.cfg.get("llm", "timeout", 300)))
            if r.status_code != 200:
                raise LLMError(f"Ollama 返回 {r.status_code}: {r.text[:300]}")
            return r
        except LLMError:
            raise
        except Exception as e:  # noqa: BLE001
            raise LLMError(f"Ollama 调用失败：{e}") from e

    def _options(self, max_tokens, temperature) -> dict:
        opts = {
            "temperature": float(temperature if temperature is not None
                                 else self.cfg.get("llm", "temperature", 0.2)),
            "num_predict": int(max_tokens or self.cfg.get("llm", "max_tokens", 1200)),
            "num_ctx": int(self.cfg.get("llm", "n_ctx", 6144)),
        }
        ng = self.cfg.get("llm", "ollama_num_gpu")
        if ng is not None:
            opts["num_gpu"] = int(ng)
        return opts

    def chat(self, messages, max_tokens=None, temperature=None) -> GenResult:
        model = self.resolve_model()
        t0 = time.time()
        r = self._post({
            "model": model,
            "messages": messages,
            "stream": False,
            "keep_alive": str(self.cfg.get("llm", "keep_alive", "30m")),
            "options": self._options(max_tokens, temperature),
        })
        dt = time.time() - t0
        j = r.json()
        ec = int(j.get("eval_count", 0) or 0)
        ed = (j.get("eval_duration", 0) or 0) / 1e9
        return GenResult(
            text=(j.get("message") or {}).get("content", ""),
            model=model, backend=self.name,
            prompt_tokens=int(j.get("prompt_eval_count", 0) or 0),
            completion_tokens=ec,
            seconds=round(dt, 2),
            tokens_per_sec=round(ec / ed, 2) if ed > 0 and ec else 0.0,
            extra={"load_seconds": round((j.get("load_duration", 0) or 0) / 1e9, 2)},
        )

    def stream(self, messages, max_tokens=None, temperature=None) -> Iterator[str]:
        model = self.resolve_model()
        r = self._post({
            "model": model,
            "messages": messages,
            "stream": True,
            "keep_alive": str(self.cfg.get("llm", "keep_alive", "30m")),
            "options": self._options(max_tokens, temperature),
        }, stream=True)
        for line in r.iter_lines():
            if not line:
                continue
            try:
                j = json.loads(line)
            except json.JSONDecodeError:
                continue
            if j.get("error"):
                raise LLMError(j["error"])
            piece = (j.get("message") or {}).get("content")
            if piece:
                yield piece
            if j.get("done"):
                break


# ---------------------------------------------------------------- llama.cpp
class LlamaCppBackend(BaseBackend):
    name = "llama_cpp"

    def __init__(self, cfg: Config):
        self.cfg = cfg
        gguf = cfg.resolve(str(cfg.get("llm", "gguf_path")))
        if not gguf.exists():
            raise LLMError(
                f"GGUF 模型不存在: {gguf}\n"
                f"请先运行: python tools/fetch_models.py --gguf"
            )
        self.gguf = gguf
        self._llm = None

    def health(self) -> tuple[bool, str]:
        try:
            import llama_cpp
            gpu = llama_cpp.llama_supports_gpu_offload()
        except Exception as e:  # noqa: BLE001
            return False, f"llama-cpp-python 不可用: {e}"
        note = "支持 GPU 卸载" if gpu else "此 wheel 为 CPU-only，n_gpu_layers 会被忽略"
        return True, f"{self.gguf.name} ({note})"

    def _load(self):
        if self._llm is not None:
            return self._llm
        from llama_cpp import Llama

        kwargs: dict[str, Any] = dict(
            model_path=str(self.gguf),
            n_ctx=int(self.cfg.get("llm", "n_ctx", 6144)),
            n_batch=int(self.cfg.get("llm", "n_batch", 256)),
            n_gpu_layers=int(self.cfg.get("llm", "n_gpu_layers", 0)),
            n_threads=int(self.cfg.get("llm", "n_threads", 8)),
            flash_attn=True,
            verbose=False,
        )
        try:
            from llama_cpp import GGML_TYPE_Q8_0, GGML_TYPE_Q4_0  # type: ignore
            kv = str(self.cfg.get("llm", "kv_cache_type", "q8_0")).lower()
            kwargs["type_k"] = GGML_TYPE_Q8_0 if kv == "q8_0" else GGML_TYPE_Q4_0
            kwargs["type_v"] = kwargs["type_k"]
        except Exception:
            pass
        cf = self.cfg.get("llm", "chat_format", "chatml")
        if cf:
            kwargs["chat_format"] = cf
        self._llm = Llama(**kwargs)
        return self._llm

    def chat(self, messages, max_tokens=None, temperature=None) -> GenResult:
        llm = self._load()
        t0 = time.time()
        out = llm.create_chat_completion(
            messages=messages,
            max_tokens=int(max_tokens or self.cfg.get("llm", "max_tokens", 1200)),
            temperature=float(temperature if temperature is not None
                              else self.cfg.get("llm", "temperature", 0.2)),
            top_p=0.95,
            repeat_penalty=1.05,
        )
        dt = time.time() - t0
        text = out["choices"][0]["message"]["content"] or ""
        u = out.get("usage", {}) or {}
        ct = int(u.get("completion_tokens", 0))
        return GenResult(
            text=text, model=self.gguf.name, backend=self.name,
            prompt_tokens=int(u.get("prompt_tokens", 0)),
            completion_tokens=ct, seconds=round(dt, 2),
            tokens_per_sec=round(ct / dt, 2) if dt > 0 else 0.0,
        )

    def stream(self, messages, max_tokens=None, temperature=None) -> Iterator[str]:
        llm = self._load()
        for chunk in llm.create_chat_completion(
            messages=messages,
            max_tokens=int(max_tokens or self.cfg.get("llm", "max_tokens", 1200)),
            temperature=float(temperature if temperature is not None
                              else self.cfg.get("llm", "temperature", 0.2)),
            stream=True,
        ):
            piece = (chunk["choices"][0].get("delta") or {}).get("content")
            if piece:
                yield piece


def get_backend(cfg: Config, force: str | None = None) -> BaseBackend | None:
    backend = (force or str(cfg.get("llm", "backend", "none"))).lower().strip()
    if backend in ("none", "off", ""):
        return None
    if backend == "ollama":
        return OllamaBackend(cfg)
    if backend == 'llama_server':
        from .llama_server import LlamaServerBackend
        return LlamaServerBackend(cfg)
    if backend in ("llama_cpp", "llamacpp", "gguf"):
        return LlamaCppBackend(cfg)
    raise LLMError(f"未知 backend: {backend}")
