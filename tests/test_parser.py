"""解析器与关键词抽取的单元测试。"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from kb.parser import (  # noqa: E402
    chunk_doc, load_doc, split_front_matter, split_sections, tokenize_query,
)

SAMPLE = """---
title: 弱 RSA 共模攻击
category: crypto
tags: [rsa, 共模攻击]
signals: [n 相同, e 不同, 两组密文]
difficulty: easy
tools: [python, gmpy2]
---

## 一、识别信号
同一明文用两组相同 n 不同 e 加密。

## 二、原理
gcd(e1,e2)=1 时存在 a·e1+b·e2=1。

```python
# 代码块里的 ## 不应被当成标题
print("hello")
```

## 三、脚本
用 gmpy2.gcdext。
"""


def test_split_front_matter():
    meta, body = split_front_matter(SAMPLE)
    assert meta["category"] == "crypto"
    assert meta["title"] == "弱 RSA 共模攻击"
    assert body.lstrip().startswith("## 一、识别信号")
    assert "---" not in body[:20]


def test_split_front_matter_missing():
    meta, body = split_front_matter("# no meta\nhello")
    assert meta == {}
    assert body.startswith("# no meta")


def test_split_sections_ignores_fence():
    _, body = split_front_matter(SAMPLE)
    secs = split_sections(body)
    heads = [h for h, _ in secs]
    assert heads == ["一、识别信号", "二、原理", "三、脚本"], heads
    # 代码块内容留在「二、原理」里
    assert "print" in dict(secs)["二、原理"]


def test_load_doc(tmp_path: Path):
    kb = tmp_path / "kb"
    (kb / "crypto").mkdir(parents=True)
    f = kb / "crypto" / "rsa-cm.md"
    f.write_text(SAMPLE, encoding="utf-8")
    doc = load_doc(f, kb)
    assert doc.path == "crypto/rsa-cm.md"
    assert doc.category == "crypto"
    assert doc.tags == ["rsa", "共模攻击"]
    assert doc.signals == ["n 相同", "e 不同", "两组密文"]
    assert doc.warnings == []


def test_load_doc_infers_category(tmp_path: Path):
    kb = tmp_path / "kb"
    (kb / "pwn").mkdir(parents=True)
    f = kb / "pwn" / "a.md"
    f.write_text("---\ntitle: abc\n---\nbody\n", encoding="utf-8")
    doc = load_doc(f, kb)
    assert doc.category == "pwn"


def test_chunk_doc(tmp_path: Path):
    kb = tmp_path / "kb"
    (kb / "crypto").mkdir(parents=True)
    f = kb / "crypto" / "rsa-cm.md"
    f.write_text(SAMPLE, encoding="utf-8")
    doc = load_doc(f, kb)
    chunks = chunk_doc(doc, chunk_chars=900, overlap=100)
    assert len(chunks) >= 3
    assert all(c["doc_path"] == "crypto/rsa-cm.md" for c in chunks)
    # 每个块都带上下文，便于向量命中
    assert "弱 RSA 共模攻击" in chunks[0]["text"]
    assert "识别信号" in chunks[0]["text"]


def test_chunk_long_section():
    from kb.parser import Doc
    body = "## s\n" + ("长文本" * 600)
    doc = Doc(path="x.md", title="t", category="misc", body=body)
    chunks = chunk_doc(doc, chunk_chars=300, overlap=50)
    assert len(chunks) > 3
    for c in chunks:
        assert len(c["piece"]) <= 310


def test_tokenize_chinese_bigram():
    toks = tokenize_query("n相同 e不同 两组密文")
    assert "rsa" not in toks
    assert "相同" in toks
    assert "不同" in toks
    assert "密文" in toks
    assert "n" in toks and "e" in toks


def test_tokenize_english_and_cve():
    toks = tokenize_query("CVE-2021-44228 Log4Shell 怎么 利用")
    assert "cve-2021-44228" in toks
    assert "log4shell" in toks


def test_tokenize_dedup():
    toks = tokenize_query("前端前端")
    assert len(toks) == len(set(toks))


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
