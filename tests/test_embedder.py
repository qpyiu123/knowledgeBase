"""嵌入与向量层测试。

不依赖任何预训练模型文件：用随机小权重构造一个配置一致的 safetensors，
验证 NumpyBertEncoder 的前向形状、归一化、批处理一致性。
"""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from kb import npbert  # noqa: E402
from kb.embedder import Embedder  # noqa: E402


def write_safetensors(path: Path, tensors: dict[str, np.ndarray]) -> None:
    """按 safetensors 格式写出：8字节头长 + JSON头 + 数据。"""
    header = {}
    offset = 0
    blobs = []
    for name, arr in tensors.items():
        a = np.ascontiguousarray(arr, dtype=np.float32)
        start = offset
        offset += a.tobytes().__len__()
        header[name] = {"dtype": "F32", "shape": list(a.shape),
                        "data_offsets": [start, offset]}
        blobs.append(a.tobytes())
    raw = json.dumps(header).encode("utf-8")
    with open(path, "wb") as f:
        f.write(struct.pack("<Q", len(raw)))
        f.write(raw)
        for b in blobs:
            f.write(b)


@pytest.fixture()
def tiny_bert(tmp_path: Path) -> Path:
    """构造一个 1 层、hidden=8、vocab=64 的极小 BERT 目录。"""
    rng = np.random.default_rng(0)
    H, I, V = 8, 16, 64
    (tmp_path / "config.json").write_text(json.dumps({
        "hidden_size": H, "num_hidden_layers": 1, "num_attention_heads": 2,
        "intermediate_size": I, "vocab_size": V, "max_position_embeddings": 32,
        "do_lower_case": True,
    }), encoding="utf-8")

    # 词表：前 5 个是特殊 token，其余用单字符
    vocab = ["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"]
    for i in range(V - 5):
        vocab.append(f"w{i}")
    (tmp_path / "vocab.txt").write_text("\n".join(vocab) + "\n", encoding="utf-8")

    def w(*shape):
        return (rng.standard_normal(shape) * 0.1).astype(np.float32)

    p = "bert."
    t = {
        p + "embeddings.word_embeddings.weight": w(V, H),
        p + "embeddings.position_embeddings.weight": w(32, H),
        p + "embeddings.token_type_embeddings.weight": w(2, H),
        p + "embeddings.LayerNorm.weight": np.ones(H, np.float32),
        p + "embeddings.LayerNorm.bias": np.zeros(H, np.float32),
    }
    pre = p + "encoder.layer.0."
    for name, shape in [
        ("attention.self.query", (H, H)), ("attention.self.key", (H, H)),
        ("attention.self.value", (H, H)),
    ]:
        t[pre + name + ".weight"] = w(*shape)
        t[pre + name + ".bias"] = np.zeros(H, np.float32)
    t[pre + "attention.output.dense.weight"] = w(H, H)
    t[pre + "attention.output.dense.bias"] = np.zeros(H, np.float32)
    t[pre + "attention.output.LayerNorm.weight"] = np.ones(H, np.float32)
    t[pre + "attention.output.LayerNorm.bias"] = np.zeros(H, np.float32)
    t[pre + "intermediate.dense.weight"] = w(I, H)
    t[pre + "intermediate.dense.bias"] = np.zeros(I, np.float32)
    t[pre + "output.dense.weight"] = w(H, I)
    t[pre + "output.dense.bias"] = np.zeros(H, np.float32)
    t[pre + "output.LayerNorm.weight"] = np.ones(H, np.float32)
    t[pre + "output.LayerNorm.bias"] = np.zeros(H, np.float32)

    write_safetensors(tmp_path / "model.safetensors", t)
    return tmp_path


def test_safetensors_roundtrip(tiny_bert):
    from kb.npbert import load_safetensors
    w = load_safetensors(tiny_bert / "model.safetensors")
    assert "bert.embeddings.word_embeddings.weight" in w
    assert w["bert.embeddings.word_embeddings.weight"].shape == (64, 8)


def test_encoder_shape_and_norm(tiny_bert):
    enc = npbert.NumpyBertEncoder(tiny_bert)
    v = enc.encode_text("w1 w2 w3")
    assert v.shape == (8,)
    assert np.isclose(np.linalg.norm(v), 1.0, atol=1e-5)


def test_encoder_batch_consistent(tiny_bert):
    """单条编码与批量编码的结果必须一致（长度分桶不能改变结果）。"""
    enc = npbert.NumpyBertEncoder(tiny_bert)
    texts = ["w1 w2", "w1 w2", "w3 w4 w5", "w1 w2"]
    batch = enc.encode_batch(texts, batch_size=2)
    single = np.vstack([enc.encode_text(t) for t in texts])
    assert np.allclose(batch, single, atol=1e-5)


def test_encoder_batch_order_preserved(tiny_bert):
    """长度分桶会改变处理顺序，但输出必须回到原顺序。"""
    enc = npbert.NumpyBertEncoder(tiny_bert)
    texts = ["w1", "w1 w2 w3 w4 w5 w6", "w1 w2"]
    batch = enc.encode_batch(texts, batch_size=1)
    for i, t in enumerate(texts):
        assert np.allclose(batch[i], enc.encode_text(t), atol=1e-5)


def test_encoder_deterministic(tiny_bert):
    enc = npbert.NumpyBertEncoder(tiny_bert)
    a = enc.encode_text("w1 w2 w3")
    b = enc.encode_text("w1 w2 w3")
    assert np.allclose(a, b)


def test_tokenizer_specials(tiny_bert):
    enc = npbert.NumpyBertEncoder(tiny_bert)
    ids = enc.tok.encode("w1 w2")
    assert ids[0] == 2      # [CLS]
    assert ids[-1] == 3     # [SEP]


def test_embedder_unavailable_when_missing(tmp_path: Path):
    e = Embedder(tmp_path / "nope")
    assert not e.available
    assert e.last_error
    with pytest.raises(RuntimeError):
        e.encode(["x"])


def test_embedder_available(tiny_bert):
    # NumPy 兜底需要在构造时显式允许（默认只走 ONNX，见 embedder 类注释）
    e = Embedder(tiny_bert, query_prefix="", allow_numpy=True)
    assert e.available, e.last_error
    assert e.backend == "numpy-bert"
    v = e.encode(["w1 w2"])
    assert v.shape == (1, 8)


def test_embedder_numpy_not_default(tiny_bert):
    """只有 NumPy 模型时，默认不应该启用（避免精度问题悄悄污染检索）。"""
    e = Embedder(tiny_bert, query_prefix="")
    assert not e.available


def test_embedder_query_prefix_changes_result(tiny_bert):
    a = Embedder(tiny_bert, query_prefix="", allow_numpy=True)
    b = Embedder(tiny_bert, query_prefix="前缀：", allow_numpy=True)
    assert not np.allclose(a.encode(["w1 w2"], is_query=True),
                           b.encode(["w1 w2"], is_query=True))
