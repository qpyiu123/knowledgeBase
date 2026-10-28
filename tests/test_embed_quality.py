"""嵌入后端质量基准：验证 ONNX 的语义区分度显著优于手写 NumPy 前向。

这个测试记录了一个真实踩过的坑：
手写 NumPy BERT 前向"能跑出 512 维归一化向量"，但同义文本与无关文本的
余弦间隔只有 0.03（ONNX 是 0.11~0.13），等于语义检索完全失效。
所以默认只走 ONNX，NumPy 版必须显式允许。

如果本机没有 ONNX 模型，测试自动跳过。
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from kb.config import Config  # noqa: E402
from kb.embedder import Embedder  # noqa: E402

SAME = [
    ("栈溢出 ret2libc", "泄露 libc 基址后调用 system 拿 shell"),
    ("PHAR 反序列化", "php 文件包含 phar:// 触发元数据反序列化"),
    ("PNG 图片隐写", "数据藏在图片像素中，binwalk 能分离出文件"),
]
DIFF = [
    ("栈溢出 ret2libc", "EXIF 元数据里的 GPS 坐标"),
    ("PHAR 反序列化", "nginx 反向代理缓存配置"),
]


def _real_embedder() -> Embedder | None:
    cfg = Config.load()
    onnx_dir = cfg.resolve(str(cfg.get("embed", "onnx_dir", "models/bge-small-zh-v1.5-onnx")))
    if not onnx_dir.exists() or not list(onnx_dir.glob("*.onnx")):
        return None
    e = Embedder(
        cfg.resolve(str(cfg.get("embed", "model_dir"))),
        str(cfg.get("embed", "query_prefix", "")),   # 一定要把前缀传进去
        onnx_dir=onnx_dir,
    )
    return e if e.available else None


@pytest.fixture(scope="module")
def real_embedder():
    e = _real_embedder()
    if e is None:
        pytest.skip("no ONNX embedding model on this machine")
    return e


def _margin(enc) -> tuple[float, float]:
    pos, neg = [], []
    for a, b in SAME:
        v = enc.encode([a, b])
        pos.append(float(v[0] @ v[1]))
    for a, b in DIFF:
        v = enc.encode([a, b])
        neg.append(float(v[0] @ v[1]))
    return float(np.mean(pos)), float(np.mean(neg))


def test_onnx_margin_is_healthy(real_embedder):
    pos, neg = _margin(real_embedder)
    margin = pos - neg
    assert margin > 0.05, f"区分度过低: same={pos:.3f} diff={neg:.3f} margin={margin:.3f}"


def test_onnx_deterministic(real_embedder):
    a = real_embedder.encode(["栈溢出 ret2libc"])
    b = real_embedder.encode(["栈溢出 ret2libc"])
    assert np.allclose(a, b, atol=1e-5)


def test_onnx_batch_equals_single(real_embedder):
    """批量编码与单条编码必须基本一致。

    容差取 5e-2 而不是 1e-5：默认用的是 int8 量化 ONNX，
    不同 batch 形状下 padding 量不同会带来约 0.02 的量化噪声
    （实测 max diff 0.019）。这个量级远小于语义间隔（0.11+），不影响检索。
    """
    texts = ["栈溢出 ret2libc", "PHAR 反序列化", "短"]
    batch = real_embedder.encode(texts, batch_size=8)
    single = np.vstack([real_embedder.encode([t])[0] for t in texts])
    assert np.allclose(batch, single, atol=5e-2), \
        f"max diff {float(abs(batch - single).max()):.4f}"


def test_onnx_dim_is_512(real_embedder):
    assert real_embedder.dim == 512


def test_onnx_query_prefix_used(real_embedder):
    """BGE 的检索需要给 query 加前缀；加了前缀后结果应当不同。"""
    q = "RSA 共模攻击"
    plain = real_embedder.encode([q], is_query=False)[0]
    prefixed = real_embedder.encode([q], is_query=True)[0]
    assert not np.allclose(plain, prefixed, atol=1e-3)
