"""P1 命中解释的离线测试。"""
from __future__ import annotations

from kb.explain import (
    doc_type,
    doc_type_label,
    make_snippet,
    match_terms,
    source_labels,
    strip_chunk_prefix,
)
from kb.parser import section_of_chunk, tokenize_query

CHUNK = (
    "【web】SSTI（服务器端模板注入）\n"
    "## 一、检测与确认\n"
    "标签: SSTI web｜识别信号: 输入被渲染；7*7 回显 49\n"
    "提交 {{7*7}} 如果回显 49，确认模板注入。\n"
)


def test_strip_chunk_prefix_removes_index_metadata():
    body = strip_chunk_prefix(CHUNK)
    assert "【web】" not in body
    assert "## 一、检测" not in body
    assert "标签:" not in body
    assert "识别信号:" not in body
    assert "{{7*7}}" in body


def test_make_snippet_is_hit_paragraph_not_document_head():
    snip = make_snippet(CHUNK, "7*7 回显")
    assert "提交" in snip
    assert "标签:" not in snip
    assert len(snip) <= 322


def test_match_terms_skips_single_digit_payload_noise():
    terms = match_terms("SSTI {{7*7}} 回显", CHUNK)
    assert "ssti" in terms
    assert "回显" in terms
    assert "7" not in terms
    assert tokenize_query("{{7*7}}") == []


def test_section_and_doc_type():
    assert section_of_chunk(CHUNK) == "一、检测与确认"
    assert doc_type("_des/cards/crypto/x.full.md") == "card"
    assert doc_type("crypto/rsa.md") == "topic"
    assert doc_type_label("_des/cards/crypto/x.full.md") == "比赛卡片"
    assert doc_type_label("crypto/rsa.md") == "专题文档"


def test_source_labels():
    assert source_labels(["fts", "vec", "graph:relates_to"]) == [
        "词面命中", "语义相近", "图谱关联",
    ]
