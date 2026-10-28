"""纯 NumPy 的 BERT 前向推理（用于 BGE small 嵌入）。

为什么自己写：本机 Python 3.14 装 PyTorch 会失败，
sentence-transformers 因此不可用；而 ONNX 导出需要 transformers+torch。
bge-small-zh 只有 4 层、hidden=512、词表 21128，
纯 numpy 前向在 CPU 上单条约 10~30ms，完全够建索引和在线检索。

权重直接读 safetensors（不依赖 torch 或 safetensors 包，自己按格式解析）。
"""
from __future__ import annotations

import json
import struct
from dataclasses import dataclass
from pathlib import Path

from . import _blas  # noqa: F401  （必须最先导入：锁定 BLAS 线程数）

import numpy as np


# --------------------------------------------------------------- safetensors
DTYPES = {
    "F32": np.float32,
    "F16": np.float16,
    "BF16": None,  # 需要特殊处理
}


def load_safetensors(path: Path) -> dict[str, np.ndarray]:
    """自己解析 safetensors：8 字节头长度 + JSON 头 + 数据区。"""
    with open(path, "rb") as f:
        raw_len = f.read(8)
        if len(raw_len) != 8:
            raise ValueError(f"safetensors 头部损坏: {path}")
        (header_len,) = struct.unpack("<Q", raw_len)
        header = json.loads(f.read(header_len).decode("utf-8"))
        blob = f.read()

    out: dict[str, np.ndarray] = {}
    for name, info in header.items():
        if name == "__metadata__":
            continue
        dtype = info["dtype"]
        shape = tuple(info["shape"])
        begin, end = info["data_offsets"]
        buf = blob[begin:end]
        if dtype == "BF16":
            u16 = np.frombuffer(buf, dtype=np.uint16)
            u32 = u16.astype(np.uint32) << 16
            arr = u32.view(np.float32)
        else:
            np_dtype = DTYPES.get(dtype)
            if np_dtype is None:
                continue
            arr = np.frombuffer(buf, dtype=np_dtype)
        out[name] = arr.reshape(shape).astype(np.float32, copy=False)
    return out


def _bf16_to_f32(buf: bytes) -> np.ndarray:
    u16 = np.frombuffer(buf, dtype=np.uint16)
    return (u16.astype(np.uint32) << 16).view(np.float32)


# --------------------------------------------------------------- tokenizer
import re  # noqa: E402

SPLIT_RE = re.compile(r"[\u4e00-\u9fff]|[a-z]+|[0-9]|[^\sa-z0-9\u4e00-\u9fff]")


class BertTokenizer:
    def __init__(self, vocab_path: Path, do_lower: bool = True, max_len: int = 512):
        self.vocab: dict[str, int] = {}
        # 必须用 newline='' 或彻底 strip 掉 \r\n：BGE 的 vocab.txt 是 CRLF 换行，
        # 只 rstrip("\n") 会让每个 token 尾部残留 \r，导致查词表全部 miss 退化成 [UNK]
        # （这个 bug 会让整条嵌入完全没有语义，且极难察觉）。
        with open(vocab_path, encoding="utf-8") as f:
            raw = f.read()
        for i, line in enumerate(raw.splitlines()):
            self.vocab[line.rstrip("\r\n")] = i
        self.do_lower = do_lower
        self.max_len = max_len
        self.cls = self.vocab.get("[CLS]", 101)
        self.sep = self.vocab.get("[SEP]", 102)
        self.pad = self.vocab.get("[PAD]", 0)
        self.unk = self.vocab.get("[UNK]", 100)
        self._wc: dict[str, list[int]] = {}

    def _wordpiece(self, w: str) -> list[int]:
        cached = self._wc.get(w)
        if cached is not None:
            return cached
        if w in self.vocab:
            res = [self.vocab[w]]
            self._wc[w] = res
            return res
        out: list[int] = []
        start, n = 0, len(w)
        while start < n:
            end = n
            cur = None
            while start < end:
                sub = ("##" + w[start:end]) if start > 0 else w[start:end]
                if sub in self.vocab:
                    cur = self.vocab[sub]
                    break
                end -= 1
            if cur is None:
                out = [self.unk]
                break
            out.append(cur)
            start = end
        self._wc[w] = out
        return out

    def encode(self, text: str, truncate: int | None = None) -> list[int]:
        t = text.lower() if self.do_lower else text
        limit = truncate or (self.max_len - 2)
        ids = [self.cls]
        for tok in SPLIT_RE.findall(t):
            ids.extend(self._wordpiece(tok))
            if len(ids) >= limit:
                break
        return ids[:limit] + [self.sep]


# --------------------------------------------------------------- model
def _gelu(x: np.ndarray) -> np.ndarray:
    # BERT 用的是精确 GELU (erf)
    from math import sqrt
    return 0.5 * x * (1.0 + _erf(x / sqrt(2.0)))


def _erf(x: np.ndarray) -> np.ndarray:
    """tanh 近似，误差 < 1e-7，足够 embedding 使用。"""
    s = np.sign(x)
    ax = np.abs(x)
    t = 1.0 / (1.0 + 0.3275911 * ax)
    y = 1.0 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t
                - 0.284496736) * t + 0.254829592) * t * np.exp(-ax * ax)
    return s * y


def _gelu_inplace(x: np.ndarray) -> np.ndarray:
    """就地计算 GELU，省一次大数组分配。"""
    from math import sqrt
    ax = np.abs(x)
    t = 1.0 / (1.0 + 0.3275911 * ax)
    y = 1.0 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t
                - 0.284496736) * t + 0.254829592) * t
    y *= np.exp(-ax * ax)
    y = 0.5 * (1.0 + np.sign(x) * y)
    x *= y
    return x


def _layer_norm(x: np.ndarray, w: np.ndarray, b: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """批量 LayerNorm；先展平成 2D 再做，避免 einsum 维度问题且 BLAS 更友好。"""
    shape = x.shape
    flat = x.reshape(-1, shape[-1])
    mu = flat.mean(-1, keepdims=True)
    flat = flat - mu
    var = np.einsum("ij,ij->i", flat, flat)[:, None] / flat.shape[-1]
    var += eps
    np.sqrt(var, out=var)
    flat /= var
    flat *= w
    flat += b
    return flat.reshape(shape)


def _softmax(x: np.ndarray) -> np.ndarray:
    m = x.max(-1, keepdims=True)
    e = np.exp(x - m)
    return e / e.sum(-1, keepdims=True)


@dataclass
class BertConfig:
    hidden: int
    layers: int
    heads: int
    intermediate: int
    vocab: int
    max_position: int


class NumpyBertEncoder:
    """BERT 前向 + BGE 的 CLS pooling + L2 归一化。"""

    def __init__(self, model_dir: Path, max_len: int = 512):
        model_dir = Path(model_dir)
        cfg = json.loads((model_dir / "config.json").read_text(encoding="utf-8"))
        self.cfg = BertConfig(
            hidden=int(cfg["hidden_size"]),
            layers=int(cfg["num_hidden_layers"]),
            heads=int(cfg["num_attention_heads"]),
            intermediate=int(cfg["intermediate_size"]),
            vocab=int(cfg["vocab_size"]),
            max_position=int(cfg.get("max_position_embeddings", 512)),
        )
        self.head_dim = self.cfg.hidden // self.cfg.heads

        st = model_dir / "model.safetensors"
        pt = model_dir / "pytorch_model.bin"
        if st.exists():
            self.w = load_safetensors(st)
        elif pt.exists():
            raise RuntimeError(
                "只有 pytorch_model.bin，没有 safetensors；本机未装 torch，无法加载。\n"
                "请重新运行 python tools/fetch_models.py --embed 拉取 model.safetensors"
            )
        else:
            raise FileNotFoundError(f"{model_dir} 下没有模型权重")

        self.tok = BertTokenizer(
            model_dir / "vocab.txt",
            do_lower=bool(cfg.get("do_lower_case", True)),
            max_len=self.cfg.max_position,
        )
        prefix = "bert." if any(k.startswith("bert.") for k in self.w) else ""
        self.p = prefix
        self.max_len = max_len

    # 权重访问
    def g(self, name: str) -> np.ndarray:
        key = self.p + name
        if key in self.w:
            return self.w[key]
        return self.w[name]

    def _embeddings(self, ids: np.ndarray) -> np.ndarray:
        word = self.g("embeddings.word_embeddings.weight")[ids]
        pos = self.g("embeddings.position_embeddings.weight")[: ids.shape[1]]
        tok_type = self.g("embeddings.token_type_embeddings.weight")[0]
        x = word + pos[None, :, :] + tok_type[None, None, :]
        return _layer_norm(
            x,
            self.g("embeddings.LayerNorm.weight"),
            self.g("embeddings.LayerNorm.bias"),
        )

    def _layer(self, x: np.ndarray, mask: np.ndarray, i: int) -> np.ndarray:
        H, hd = self.cfg.hidden, self.head_dim
        pre = f"encoder.layer.{i}."
        # self-attention
        q = x @ self.g(pre + "attention.self.query.weight").T + self.g(pre + "attention.self.query.bias")
        k = x @ self.g(pre + "attention.self.key.weight").T + self.g(pre + "attention.self.key.bias")
        v = x @ self.g(pre + "attention.self.value.weight").T + self.g(pre + "attention.self.value.bias")
        L = x.shape[0]
        q = q.reshape(L, self.cfg.heads, hd).transpose(1, 0, 2)
        k = k.reshape(L, self.cfg.heads, hd).transpose(1, 0, 2)
        v = v.reshape(L, self.cfg.heads, hd).transpose(1, 0, 2)

        scores = (q @ k.transpose(0, 2, 1)) / np.sqrt(hd)
        scores = scores + (1.0 - mask)[None, :, None] * -1e9
        attn = _softmax(scores)
        ctx = (attn @ v).transpose(1, 0, 2).reshape(L, H)

        a = ctx @ self.g(pre + "attention.output.dense.weight").T + self.g(pre + "attention.output.dense.bias")
        a = _layer_norm(a, self.g(pre + "attention.output.LayerNorm.weight"),
                        self.g(pre + "attention.output.LayerNorm.bias"))
        x = x + a
        # FFN
        f = x @ self.g(pre + "intermediate.dense.weight").T + self.g(pre + "intermediate.dense.bias")
        f = _gelu(f)
        f = f @ self.g(pre + "output.dense.weight").T + self.g(pre + "output.dense.bias")
        f = _layer_norm(f, self.g(pre + "output.LayerNorm.weight"),
                        self.g(pre + "output.LayerNorm.bias"))
        return x + f

    def encode_text(self, text: str, truncate: int | None = None) -> np.ndarray:
        ids = self.tok.encode(text, truncate=truncate or (self.max_len - 2))
        return self._forward(np.array([ids], dtype=np.int64))[0]

    def _matmul_packed(self, x: np.ndarray, w_t: np.ndarray) -> np.ndarray:
        """x @ w_t。w_t 必须是预转置的 C 连续矩阵（见 wT()）。

        行数很少时把行数补到 32 再乘，避免 BLAS 在极小矩阵上的固定开销。
        """
        rows = x.shape[0]
        if rows >= 32:
            return x @ w_t
        pad = np.zeros((32 - rows, x.shape[1]), dtype=x.dtype)
        return (np.concatenate([x, pad], axis=0) @ w_t)[:rows]

    def _forward(self, ids: np.ndarray) -> np.ndarray:
        """ids: (B, L) -> (B, hidden) 归一化后的 CLS 向量。

        整批 token 展平成 (B*L, H) 再算，让每个 matmul 都吃到 BLAS 的大矩阵吞吐。
        必须支持 padding：长度分桶后同一批里长短不一，短序列尾巴上是 [PAD](id=0)。
        """
        pad_id = int(getattr(self.tok, "pad", 0))
        mask = (ids != pad_id).astype(np.float32)
        mask[:, 0] = 1.0                 # 至少保留一位，避免整行全屏蔽

        x = self._embeddings(ids)                      # (B,L,H)
        B, L, H = x.shape
        hd = self.head_dim
        nh = self.cfg.heads
        flat = x.reshape(B * L, H)

        # (B,1,1,L) 广播到 attention 分数；(B,1,L,1) 广播到 value
        key_bias = ((1.0 - mask) * np.float32(-1e30))[:, None, None, :]
        val_mask = mask[:, None, :, None]

        for i in range(self.cfg.layers):
            pre = f"encoder.layer.{i}."
            wq = self.wT(self.g(pre + "attention.self.query.weight"))
            wk = self.wT(self.g(pre + "attention.self.key.weight"))
            wv = self.wT(self.g(pre + "attention.self.value.weight"))
            w_qkv = self._cached(
                f"{i}:qkv_wT",
                lambda a=wq, b=wk, c=wv: np.hstack([a, b, c]),
            )
            b_qkv = self._cached(
                f"{i}:qkv_b",
                lambda: np.concatenate([
                    self.g(pre + "attention.self.query.bias"),
                    self.g(pre + "attention.self.key.bias"),
                    self.g(pre + "attention.self.value.bias"),
                ]),
            )
            qkv = self._matmul_packed(flat, w_qkv) + b_qkv      # (B*L, 3H)
            qkv = qkv.reshape(B, L, 3, nh, hd).transpose(2, 0, 3, 1, 4)
            q, k, v = qkv[0], qkv[1], qkv[2]                     # (B,nh,L,hd)

            # 注意力：必须屏蔽 padding，否则混合长度 batch 的短句会被长句尾巴干扰
            # （实测 "w1 w2" 与 "w3 w4 w5" 同批时与单条编码差到 0.066，足以让检索错乱）
            scores = (q @ k.transpose(0, 1, 3, 2)) * np.float32(1.0 / np.sqrt(hd))
            if L > 1:
                scores = scores + key_bias
            scores = scores.astype(np.float32, copy=False)
            scores -= scores.max(-1, keepdims=True)
            probs = np.exp(scores)
            probs /= probs.sum(-1, keepdims=True)
            # value 侧把 padding 位置清零，避免其 embedding 漏进上下文
            ctx = (probs @ (v * val_mask)).transpose(0, 2, 1, 3).reshape(B * L, H)

            a = self._matmul_packed(
                ctx, self.wT(self.g(pre + "attention.output.dense.weight"))
            ) + self.g(pre + "attention.output.dense.bias")
            a = _layer_norm(a, self.g(pre + "attention.output.LayerNorm.weight"),
                            self.g(pre + "attention.output.LayerNorm.bias"))
            flat = flat + a

            f = self._matmul_packed(
                flat, self.wT(self.g(pre + "intermediate.dense.weight"))
            ) + self.g(pre + "intermediate.dense.bias")
            _gelu_inplace(f)
            f = self._matmul_packed(
                f, self.wT(self.g(pre + "output.dense.weight"))
            ) + self.g(pre + "output.dense.bias")
            f = _layer_norm(f, self.g(pre + "output.LayerNorm.weight"),
                            self.g(pre + "output.LayerNorm.bias"))
            flat = flat + f

        cls = flat.reshape(B, L, H)[:, 0, :]
        norms = np.linalg.norm(cls, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return (cls / norms).astype(np.float32)

    def _cached(self, key: str, make):
        c = getattr(self, "_cache", None)
        if c is None:
            c = self._cache = {}
        v = c.get(key)
        if v is None:
            v = np.ascontiguousarray(make(), dtype=np.float32)
            c[key] = v
        return v

    def wT(self, weight: np.ndarray) -> np.ndarray:
        """返回**预转置且 C 连续**的权重副本，并缓存。

        关键性能点：直接写 `x @ W.T` 时，W.T 是 F-contiguous 的视图，
        OpenBLAS 每次都不得不重新打包权重（实测 x(300,512)@W.T(512,2048) 要 3.17ms，
        而预先转置成 C 连续后只要 ~0.35ms，快近 10 倍）。
        每层有 QKV/out/ffn1/ffn2 共 4 个权重，4 层 => 16 次，差距被放大到数百毫秒。
        """
        key = f"wT:{id(weight)}"
        v = self._cache.get(key) if hasattr(self, "_cache") else None
        if v is None:
            v = np.ascontiguousarray(weight.T, dtype=np.float32)
            if not hasattr(self, "_cache"):
                self._cache = {}
            self._cache[key] = v
        return v

    def encode_batch(self, texts: list[str], batch_size: int = 16,
                     show_progress: bool = False) -> np.ndarray:
        """按**长度分桶**后分批跑。同一批内长度接近，能显著减少 padding 浪费。

        实测：模型单次前向有约 40~60ms 的固定开销，所以 batch_size 不能太小；
        但 900 字的 chunk 和 20 字的标题放一起又会浪费大量算力。
        这里先按 token 长度排序，再在长度相近的窗口内切批。
        """
        n = len(texts)
        if n == 0:
            return np.zeros((0, self.cfg.hidden), dtype=np.float32)

        enc = [self.tok.encode(t, truncate=self.max_len - 2) for t in texts]
        lens = [len(e) for e in enc]
        order = sorted(range(n), key=lambda i: lens[i])
        out = np.zeros((n, self.cfg.hidden), dtype=np.float32)

        bs = max(1, int(batch_size))
        for bi in range(0, n, bs):
            idxs = order[bi:bi + bs]
            width = max(lens[i] for i in idxs)
            ids = np.zeros((len(idxs), width), dtype=np.int64)
            for r, i in enumerate(idxs):
                ids[r, :lens[i]] = enc[i]
            out[idxs] = self._forward(ids)
            if show_progress:
                print(f"\r  编码 {min(bi + bs, n)}/{n}", end="", flush=True)
        if show_progress:
            print()
        return out

    def _layer_batch(self, x: np.ndarray, mask: np.ndarray, i: int) -> np.ndarray:
        B, L, H = x.shape
        hd = self.head_dim
        pre = f"encoder.layer.{i}."
        q = x @ self.g(pre + "attention.self.query.weight").T + self.g(pre + "attention.self.query.bias")
        k = x @ self.g(pre + "attention.self.key.weight").T + self.g(pre + "attention.self.key.bias")
        v = x @ self.g(pre + "attention.self.value.weight").T + self.g(pre + "attention.self.value.bias")
        q = q.reshape(B, L, self.cfg.heads, hd).transpose(0, 2, 1, 3)
        k = k.reshape(B, L, self.cfg.heads, hd).transpose(0, 2, 1, 3)
        v = v.reshape(B, L, self.cfg.heads, hd).transpose(0, 2, 1, 3)

        scores = (q @ k.transpose(0, 1, 3, 2)) / np.sqrt(hd)
        scores = scores + (1.0 - mask)[:, None, None, :] * -1e9
        attn = _softmax(scores)
        ctx = (attn @ v).transpose(0, 2, 1, 3).reshape(B, L, H)

        a = ctx @ self.g(pre + "attention.output.dense.weight").T + self.g(pre + "attention.output.dense.bias")
        a = _layer_norm(a, self.g(pre + "attention.output.LayerNorm.weight"),
                        self.g(pre + "attention.output.LayerNorm.bias"))
        x = x + a
        f = x @ self.g(pre + "intermediate.dense.weight").T + self.g(pre + "intermediate.dense.bias")
        f = _gelu(f)
        f = f @ self.g(pre + "output.dense.weight").T + self.g(pre + "output.dense.bias")
        f = _layer_norm(f, self.g(pre + "output.LayerNorm.weight"),
                        self.g(pre + "output.LayerNorm.bias"))
        return x + f
