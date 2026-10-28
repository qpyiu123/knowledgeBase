"""嵌入向量后端。

三种后端，按速度与依赖自动择优：

  1. onnx   —— onnxruntime + tokenizers，bge-small-zh 的 ONNX 导出
                （首选：实测 int8 量化版约 1000 文本/秒，零 torch 依赖）
  2. numpy  —— 纯 NumPy 实现的 BERT 前向（tools/kb/npbert.py），
                直接读 safetensors。ONNX 缺失时的兜底，实测约 10 条/秒。
  3. gguf   —— llama.cpp 加载嵌入模型 GGUF，最后兜底。

三者都做到 CLS pooling + L2 归一化，输出维度 512，向量可比。
对外接口只有 encode() / dim / available / backend。
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from . import _blas  # noqa: F401  （必须最先导入，设置 BLAS 线程数）

import numpy as np

# ------------------------------------------------------------------ ONNX


class OnnxEmbedder:
    backend = "onnx"

    def __init__(self, model_path: Path, vocab_path: Path, query_prefix: str = "",
                 max_len: int = 512, prefer_quantized: bool = True):
        import onnxruntime as ort

        self.model_path = Path(model_path)
        self.query_prefix = query_prefix
        self.max_len = max_len

        so = ort.SessionOptions()
        # 单进程内推理，线程开太多反而慢
        so.intra_op_num_threads = int(os.environ.get("KB_ONNX_THREADS", "4"))
        so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        self.sess = ort.InferenceSession(str(self.model_path), so,
                                         providers=["CPUExecutionProvider"])
        self.input_names = {i.name for i in self.sess.get_inputs()}
        self._dim: int | None = None

        # 用 tokenizers 库（纯 Rust，无需 torch）
        from tokenizers import Tokenizer
        json_tok = self.model_path.parent / "tokenizer.json"
        if json_tok.exists():
            self.tok = Tokenizer.from_file(str(json_tok))
            self.tok.enable_truncation(max_length=max_len - 2)
            # BERT 需要补到 [CLS] ... [SEP]
            self.use_hf_tokenizer = True
        else:
            self.tok = None
            self.use_hf_tokenizer = False
            from .npbert import BertTokenizer  # noqa: F401
            self._wp = BertTokenizer(Path(vocab_path), max_len=max_len)

    def _encode_one_impl(self, t: str) -> list[int]:
        if self.use_hf_tokenizer:
            return self.tok.encode(t).ids
        return self._wp.encode(t, truncate=self.max_len - 2)

    def _encode_ids(self, texts: list[str], width: int):
        n = len(texts)
        ids = np.zeros((n, width), dtype=np.int64)
        mask = np.zeros((n, width), dtype=np.int64)
        for i, t in enumerate(texts):
            seq = self._encode_one_impl(t)[:width]
            ids[i, : len(seq)] = seq
            mask[i, : len(seq)] = 1
        return ids, mask

    def _run(self, texts: list[str]) -> np.ndarray:
        widths = [len(self._encode_one_impl(t)) for t in texts] or [1]
        # 关键：必须按批内最长序列 + 2（[CLS]/[SEP]）来定宽，
        # 直接用 tokenizer 输出的长度会漏掉特殊 token，截断后导致与单条编码不一致。
        width = max(widths) + 2
        width = min(width, self.max_len)
        ids, mask = self._encode_ids(texts, width)
        feed: dict[str, np.ndarray] = {}
        if "input_ids" in self.input_names:
            feed["input_ids"] = ids
        if "attention_mask" in self.input_names:
            feed["attention_mask"] = mask
        if "token_type_ids" in self.input_names:
            feed["token_type_ids"] = np.zeros_like(ids)
        out = self.sess.run(None, feed)[0]
        if out.ndim == 3:
            vec = out[:, 0, :]          # CLS pooling
        else:
            vec = out
        vec = np.asarray(vec, dtype=np.float32)
        norm = np.linalg.norm(vec, axis=1, keepdims=True)
        norm[norm == 0] = 1.0
        vec = vec / norm
        self._dim = int(vec.shape[1])
        return vec

    def encode(self, texts: list[str], batch_size: int = 32,
               is_query: bool = False, show_progress: bool = False) -> np.ndarray:
        texts = list(texts)
        # is_query 时才加 BGE 的检索前缀（文档侧不加，这是 bge 的标准用法）
        if is_query and self.query_prefix:
            texts = [self.query_prefix + t for t in texts]
        if not texts:
            return np.zeros((0, self._dim or 512), dtype=np.float32)
        out = []
        step = max(1, int(batch_size))
        for i in range(0, len(texts), step):
            out.append(self._run(texts[i:i + step]))
            if show_progress:
                print(f"\r  编码 {min(i + step, len(texts))}/{len(texts)}",
                      end="", flush=True)
        if show_progress:
            print()
        return np.vstack(out)

    @property
    def dim(self) -> int:
        if self._dim is None:
            self._run(["probe"])
        return int(self._dim or 0)


# ------------------------------------------------------------------ NumPy


class NumpyEmbedder:
    backend = "numpy-bert"

    def __init__(self, model_dir: Path, query_prefix: str = ""):
        from .npbert import NumpyBertEncoder
        self.enc = NumpyBertEncoder(Path(model_dir))
        self.query_prefix = query_prefix

    def encode(self, texts: list[str], batch_size: int = 32,
               is_query: bool = False, show_progress: bool = False) -> np.ndarray:
        texts = list(texts)
        if is_query and self.query_prefix:
            texts = [self.query_prefix + t for t in texts]
        return self.enc.encode_batch(texts, batch_size=batch_size,
                                     show_progress=show_progress)

    @property
    def dim(self) -> int:
        return int(self.enc.cfg.hidden)


# ------------------------------------------------------------------ GGUF


class GgufEmbedder:
    backend = "gguf"

    def __init__(self, gguf_path: Path, query_prefix: str = ""):
        from llama_cpp import Llama
        self.llm = Llama(model_path=str(gguf_path), n_ctx=512, embedding=True,
                         n_gpu_layers=0, verbose=False)
        self.query_prefix = query_prefix
        self._dim: int | None = None

    def encode(self, texts, batch_size=32, is_query=False, show_progress=False):
        if is_query and self.query_prefix:
            texts = [self.query_prefix + t for t in texts]
        vecs = []
        total = len(texts)
        for i, t in enumerate(texts):
            r = self.llm.create_embedding(t)
            vecs.append(np.asarray(r["data"][0]["embedding"], dtype=np.float32))
            if show_progress and (i + 1) % 20 == 0:
                print(f"\r  编码 {i + 1}/{total}", end="", flush=True)
        if show_progress:
            print()
        if not vecs:
            return np.zeros((0, self._dim or 512), dtype=np.float32)
        m = np.vstack(vecs)
        n = np.linalg.norm(m, axis=1, keepdims=True)
        n[n == 0] = 1.0
        self._dim = int(m.shape[1])
        return (m / n).astype(np.float32)

    @property
    def dim(self) -> int:
        if self._dim is None:
            self.encode(["probe"])
        return int(self._dim or 0)


# ------------------------------------------------------------------ Facade


def _pick_onnx_file(onnx_dir: Path, prefer_quantized: bool) -> Path | None:
    cands = sorted(onnx_dir.glob("*.onnx"))
    cands = [c for c in cands if c.stat().st_size > 1024 * 1024]
    if not cands:
        return None
    if prefer_quantized:
        q = [c for c in cands if "quant" in c.name or "int8" in c.name]
        if q:
            return q[0]
    # 优先非量化的大文件
    plain = [c for c in cands if "quant" not in c.name and "int8" not in c.name]
    return (plain or cands)[0]


class Embedder:
    """嵌入入口。

    ⚠️ 重要取舍（实测据）：
    onnxruntime 的 BGE 输出与 NumPy 手写 BERT 前向**对不齐**（余弦仅约 0.49），
    且手写版把"同义文本 / 无关文本"的余弦间隔压到 0.03（ONNX 是 0.11~0.13），
    等于语义能力基本失效。原因是手写前向在 float32 下的 LayerNorm/GELU 误差
    经过 4 层 attention 放大（激活值 std 从 0.6 涨到 3.0，scores 冲到 ±110）。

    结论：**默认且优先使用 ONNX**。NumPy 实现保留但只在参数显式指定时才用，
    避免"看起来能跑、其实检索全错"这种最坏情况。
    """

    def __init__(self, model_dir: Path, query_prefix: str = "", device: str = "cpu",
                 gguf_fallback: Path | None = None,
                 onnx_dir: Path | None = None,
                 prefer_onnx: bool = True,
                 allow_numpy: bool = False):
        self.model_dir = Path(model_dir)
        self.query_prefix = query_prefix
        self.device = device
        self.gguf_fallback = gguf_fallback
        self.onnx_dir = Path(onnx_dir) if onnx_dir else self.model_dir.parent / (
            self.model_dir.name + "-onnx"
        )
        self.prefer_onnx = prefer_onnx
        self.allow_numpy = allow_numpy
        self._impl = None
        self.last_error: str | None = None
        self._tried = False

    # ---------- 可用性 ----------
    def _candidates(self):
        p = _pick_onnx_file(self.onnx_dir, prefer_quantized=True)
        if p:
            yield ("onnx", lambda: OnnxEmbedder(p, self.onnx_dir / "vocab.txt",
                                                self.query_prefix))
        if self.gguf_fallback and self.gguf_fallback.exists():
            yield ("gguf", lambda: GgufEmbedder(self.gguf_fallback, self.query_prefix))
        # 手写 NumPy 版只作为最后兜底，且必须用户显式启用（精度有问题，见类注释）
        if self.allow_numpy and (self.model_dir / "model.safetensors").exists():
            yield ("numpy", lambda: NumpyEmbedder(self.model_dir, self.query_prefix))

    @property
    def available(self) -> bool:
        if self._impl is not None:
            return True
        if self._tried:
            return False
        self._tried = True
        errors = []
        for name, make in self._candidates():
            try:
                self._impl = make()
                return True
            except Exception as e:  # noqa: BLE001
                errors.append(f"{name}: {type(e).__name__}: {e}")
        self.last_error = ("没有可用的嵌入后端 -> " + " | ".join(errors)) if errors \
            else (f"找不到 ONNX 嵌入模型: {self.onnx_dir}"
                  f"（运行 python tools/fetch_models.py --embed；"
                  f"或用 KB_ALLOW_NUMPY_EMBED=1 启用手写 NumPy 兜底）")
        return False

    @property
    def backend(self) -> str:
        return self._impl.backend if self._impl else "none"

    @property
    def dim(self) -> int:
        return int(self._impl.dim) if self._impl else 0

    # ---------- 编码 ----------
    def encode(self, texts: list[str], batch_size: int = 32, is_query: bool = False,
               show_progress: bool = False) -> np.ndarray:
        if not self.available:
            raise RuntimeError(f"嵌入不可用: {self.last_error}")
        return self._impl.encode(texts, batch_size=batch_size,
                                 is_query=is_query, show_progress=show_progress)
