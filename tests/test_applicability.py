"""适用条件三态（known / unknown / unsatisfied）的离线测试。

判定完全由 `requires` front matter 与 `applicability_rules.json` 完成，
不调用模型、不访问网络。
"""
from __future__ import annotations

from pathlib import Path

import pytest

from kb.applicability import (
    STATUS_KNOWN,
    STATUS_UNKNOWN,
    STATUS_UNSATISFIED,
    evaluate_conditions,
    evaluate_paths,
    load_rules,
    resolve_target,
)


@pytest.fixture()
def kb(tmp_path: Path) -> Path:
    root = tmp_path / "kb"
    (root / "crypto").mkdir(parents=True)
    (root / "a.md").write_text(
        "---\ntitle: 进阶利用\nrequires: [b.md]\n---\n正文\n",
        encoding="utf-8",
    )
    (root / "b.md").write_text(
        "---\ntitle: 基础 B\n---\n前置知识\n",
        encoding="utf-8",
    )
    (root / "crypto" / "c.md").write_text(
        "---\ntitle: 无前提\n---\n正文\n",
        encoding="utf-8",
    )
    return root


def test_rules_file_loads():
    rules = load_rules()
    assert len(rules) == 8
    assert all(r.get("id") and r.get("paths") for r in rules)


def test_requires_is_unknown_without_context_or_named_query(kb: Path):
    out = evaluate_conditions(kb, "a.md", "这题怎么打", [])
    assert out["status"] == STATUS_UNKNOWN
    assert out["trace"] == {"rules": 0, "requires": 1}
    cond = out["conditions"][0]
    assert cond["id"] == "requires:b.md"
    assert cond["status"] == STATUS_UNKNOWN
    assert "基础 B" in cond["label"]
    assert "缺少前提" in out["hint"]
    assert "unknown" in out["hint"]
    assert "kb/b.md" in out["hint"]


def test_requires_becomes_known_when_context_includes_it(kb: Path):
    out = evaluate_conditions(kb, "a.md", "这题怎么打", ["b.md"])
    assert out["status"] == STATUS_KNOWN
    assert out["conditions"][0]["status"] == STATUS_KNOWN
    assert "已在本次检索上下文中" in out["conditions"][0]["evidence"]


def test_requires_becomes_known_when_query_names_target(kb: Path):
    out = evaluate_conditions(kb, "a.md", "先看基础 B 再打", [])
    assert out["status"] == STATUS_KNOWN
    assert out["conditions"][0]["status"] == STATUS_KNOWN
    assert "点名" in out["conditions"][0]["evidence"]


def test_no_conditions_is_known(kb: Path):
    out = evaluate_conditions(kb, "crypto/c.md", "任意查询", [])
    assert out["status"] == STATUS_KNOWN
    assert out["conditions"] == []
    assert out["hint"] == ""
    assert out["trace"] == {"rules": 0, "requires": 0}


def test_keyword_rule_known_unknown_and_negative(kb: Path):
    rel = "crypto/rsa-common-modulus-attack.md"
    known = evaluate_conditions(kb, rel, "同一个 n，两组密文", [])
    assert known["status"] == STATUS_KNOWN
    assert any(c["id"] == "rsa-same-modulus" for c in known["conditions"])

    unknown = evaluate_conditions(kb, rel, "RSA 怎么解", [])
    assert unknown["status"] == STATUS_UNKNOWN
    assert "缺少前提" in unknown["hint"]

    bad = evaluate_conditions(kb, rel, "这题是不同 n", [])
    assert bad["status"] == STATUS_UNSATISFIED
    assert "不满足" in bad["hint"]
    assert "不同n" in bad["hint"]


def test_version_rule_known_and_out_of_range(kb: Path):
    rel = "pwn/largebin-attack-chain.md"
    inside = evaluate_conditions(kb, rel, "glibc 2.35 的 largebin UAF 堆溢出", [])
    assert inside["status"] == STATUS_KNOWN
    assert any(c["id"] == "largebin-libc-version" for c in inside["conditions"])

    outside = evaluate_conditions(kb, rel, "glibc 2.29 UAF 堆溢出", [])
    assert outside["status"] == STATUS_UNSATISFIED
    assert "超出" in outside["hint"]

    missing = evaluate_conditions(kb, rel, "largebin 怎么打", [])
    assert missing["status"] == STATUS_UNKNOWN
    assert "glibc 2.31–2.35" in missing["hint"]


def test_evaluate_paths_summarizes_unknown(kb: Path):
    out = evaluate_paths(kb, ["a.md", "crypto/c.md"], "这题怎么打")
    assert out["status"] == STATUS_UNKNOWN
    assert out["unknown"] == 1
    assert out["unsatisfied"] == 0
    assert any("缺少前提" in line for line in out["hint"].splitlines())

    known = evaluate_paths(kb, ["b.md", "crypto/c.md"], "这题怎么打")
    assert known["status"] == STATUS_KNOWN
    assert known["unknown"] == 0


def test_resolve_target_rejects_ambiguous_and_missing(kb: Path):
    assert resolve_target(kb, "b.md") == "b.md"
    assert resolve_target(kb, "missing.md") is None
    (kb / "x").mkdir()
    (kb / "y").mkdir()
    (kb / "x" / "dup.md").write_text("---\ntitle: D\n---\n", encoding="utf-8")
    (kb / "y" / "dup.md").write_text("---\ntitle: D\n---\n", encoding="utf-8")
    assert resolve_target(kb, "dup.md") is None
