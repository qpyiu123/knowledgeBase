"""FTS 检索与融合测试。"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from kb.fts import FtsIndex, write_cjk  # noqa: E402
from kb.fusion import fuse_single_source, rrf_fuse  # noqa: E402
from kb.fts import Hit  # noqa: E402
from kb.parser import Doc  # noqa: E402

DOCS = [
    Doc(path="crypto/rsa-cm.md", title="弱 RSA 共模攻击", category="crypto",
        tags=["rsa", "共模攻击"], signals=["n 相同", "e 不同", "两组密文", "一个明文两次加密"],
        body="## 原理\n同余关系，扩展欧几里得算法。\n## 脚本\n用 gmpy2.gcdext 求逆元。"),
    Doc(path="web/phar.md", title="PHAR 反序列化", category="web",
        tags=["php", "反序列化"], signals=["上传 phar", "文件包含", "phar://"],
        body="## 原理\nphar 元数据在解析时反序列化。\n## 脚本\n生成恶意 phar 文件。"),
    Doc(path="pwn/ret2libc.md", title="ret2libc 栈溢出", category="pwn",
        tags=["栈溢出", "rop"], signals=["checksec 无 canary", "给了 libc.so.6"],
        body="## 原理\n泄露 libc 基址后调用 system。\n## 脚本\npwntools 模板。"),
]


@pytest.fixture()
def idx(tmp_path: Path) -> FtsIndex:
    f = FtsIndex(tmp_path / "fts.db")
    f.rebuild(DOCS)
    return f


def test_write_cjk():
    out = write_cjk("共模攻击")
    assert "共模" in out and "模攻" in out and "攻击" in out


def test_search_chinese(idx):
    hits = idx.search("两组密文 e 不同", top_k=5)
    assert hits, "中文查询必须能命中"
    assert hits[0].doc_path == "crypto/rsa-cm.md"


def test_search_english(idx):
    hits = idx.search("ret2libc", top_k=5)
    assert hits and hits[0].doc_path == "pwn/ret2libc.md"


def test_search_prefix_fuzzy(idx):
    # 半截词也要能出
    hits = idx.search("ret2li", top_k=5)
    assert hits and hits[0].doc_path == "pwn/ret2libc.md"


def test_search_category_filter(idx):
    hits = idx.search("反序列化", top_k=5, category="pwn")
    assert all(h.category == "pwn" for h in hits)


def test_search_like_fallback(idx):
    # 生僻中文串，bigram 都命不中时走 LIKE 兜底
    hits = idx.search("扩展欧几里得", top_k=5)
    assert hits


def test_search_empty_query(idx):
    assert idx.search("", top_k=5) == []


def test_stats(idx):
    st = idx.stats()
    assert st["docs"] == 3
    assert st["chunks"] >= 3
    assert st["categories"] == {"crypto": 1, "web": 1, "pwn": 1}


def test_rrf_prefers_agreement():
    fts = [Hit("a.md", "A", "misc", 1.0, "t"), Hit("b.md", "B", "misc", 2.0, "t")]
    vec = [
        {"doc_path": "b.md", "title": "B", "category": "misc", "text": "x", "score": 0.9},
        {"doc_path": "a.md", "title": "A", "category": "misc", "text": "y", "score": 0.8},
    ]
    fused = rrf_fuse(fts, vec, top_k=2)
    # 两路都出现的文档得分相同且高于只在一路出现的
    assert {f.doc_path for f in fused} == {"a.md", "b.md"}
    assert all(f.score > 0 for f in fused)
    assert len(fused[0].sources) == 2


def test_rrf_single_source():
    fts = [Hit("a.md", "A", "misc", 1.0, "t")]
    fused = rrf_fuse(fts, [], top_k=5)
    assert len(fused) == 1 and fused[0].sources == ["fts"]


def test_fuse_single_source():
    fts = [Hit("a.md", "A", "misc", 1.0, "t")]
    assert fuse_single_source(fts)[0].doc_path == "a.md"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
