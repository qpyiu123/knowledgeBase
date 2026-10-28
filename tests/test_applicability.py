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


def test_requires_stays_unknown_when_context_only_mentions_it(kb: Path):
    # next_2：检索命中前提资料 ≠ 前提已满足，只能给 unknown。
    out = evaluate_conditions(kb, "a.md", "这题怎么打", ["b.md"])
    assert out["status"] == STATUS_UNKNOWN
    cond = out["conditions"][0]
    assert cond["status"] == STATUS_UNKNOWN
    assert "在本批命中中出现过" in cond["evidence"]
    assert "由你确认" in cond["evidence"]
    assert "kb/b.md" in cond["evidence"]


def test_requires_becomes_known_when_query_names_target(kb: Path):
    out = evaluate_conditions(kb, "a.md", "先看基础 B 再打", [])
    assert out["status"] == STATUS_KNOWN
    assert out["conditions"][0]["status"] == STATUS_KNOWN
    assert "点名" in out["conditions"][0]["evidence"]


def test_document_without_rules_is_unknown(kb: Path):
    # next_1：有 front matter 的条目没有登记规则时不能再假装 known。
    out = evaluate_conditions(kb, "crypto/c.md", "任意查询", [])
    assert out["status"] == STATUS_UNKNOWN
    assert out["conditions"] == []
    assert out["label"] == "尚未评估，无已知前提线索"
    assert "没有登记适用条件" in out["hint"]
    assert "人工补规则" in out["hint"]
    assert out["trace"] == {"rules": 0, "requires": 0}


def test_non_document_without_front_matter_stays_known(kb: Path):
    (kb / "note.md").write_text("随手记，不是资料条目\n", encoding="utf-8")
    out = evaluate_conditions(kb, "note.md", "任意查询", [])
    assert out["status"] == STATUS_KNOWN
    assert out["label"] == "无额外适用前提"
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


def test_keyword_rule_conflicting_evidence_is_unknown(kb: Path):
    # next_4：肯定词与否定词同时出现时不强行判满足。
    rel = "crypto/rsa-common-modulus-attack.md"
    out = evaluate_conditions(kb, rel, "同一个 n，但是不同 n", [])
    cond = next(c for c in out["conditions"] if c["id"] == "rsa-same-modulus")
    assert out["status"] == STATUS_UNKNOWN
    assert cond["status"] == STATUS_UNKNOWN
    assert "线索冲突" in cond["evidence"]
    assert "同时出现" in cond["evidence"]
    assert "缺少前提" in out["hint"]


def _use_version_rule(monkeypatch, **overrides):
    rule = {
        "id": "version-test",
        "paths": ["crypto/c.md"],
        "label": "版本测试",
        "kind": "version",
        "source": "crypto/c.md",
    }
    rule.update(overrides)
    monkeypatch.setattr("kb.applicability.load_rules", lambda: (rule,))


def test_version_rule_accepts_segmented_versions_in_range(kb: Path, monkeypatch):
    # next_3：2.31 / 2.32 按整数段比较，2.31 与 2.31.0 视为相等。
    _use_version_rule(monkeypatch, min="2.31", max="2.32")
    for query in ("glibc 2.31", "glibc 2.32", "glibc 2.31.0"):
        out = evaluate_conditions(kb, "crypto/c.md", query, [])
        assert out["status"] == STATUS_KNOWN, query
        assert out["conditions"][0]["status"] == STATUS_KNOWN


def test_version_rule_lower_bound_is_inclusive(kb: Path, monkeypatch):
    # 2.27 在 2.27–2.35 的闭区间内，仍然算 known。
    _use_version_rule(monkeypatch, min="2.27", max="2.35")
    out = evaluate_conditions(kb, "crypto/c.md", "glibc 2.27", [])
    assert out["status"] == STATUS_KNOWN
    assert "2.27–2.35" in out["conditions"][0]["evidence"]


def test_version_rule_rejects_out_of_range_and_overflow(kb: Path, monkeypatch):
    _use_version_rule(monkeypatch, min="2.31", max="2.35")
    over = evaluate_conditions(kb, "crypto/c.md", "glibc 3.2", [])
    assert over["status"] == STATUS_UNSATISFIED
    assert "超出" in over["conditions"][0]["evidence"]

    work = evaluate_conditions(kb, "crypto/c.md", "glibc 2.35.1", [])
    assert work["status"] == STATUS_UNSATISFIED
    assert "2.35.1" in work["conditions"][0]["evidence"]

    missing = evaluate_conditions(kb, "crypto/c.md", "版本没给", [])
    assert missing["status"] == STATUS_UNKNOWN
    assert "未给出 glibc 版本" in missing["conditions"][0]["evidence"]


def test_version_rule_invalid_bounds_is_unknown(kb: Path, monkeypatch):
    _use_version_rule(monkeypatch, min="abc", max="2.35")
    out = evaluate_conditions(kb, "crypto/c.md", "glibc 2.32", [])
    assert out["status"] == STATUS_UNKNOWN
    assert out["conditions"][0]["evidence"] == "规则版本区间无效"


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
    (kb / "note.md").write_text("随手记\n", encoding="utf-8")
    out = evaluate_paths(kb, ["a.md", "note.md"], "这题怎么打")
    assert out["status"] == STATUS_UNKNOWN
    assert out["unknown"] == 1
    assert out["unsatisfied"] == 0
    assert any("缺少前提" in line for line in out["hint"].splitlines())

    # next_1：有 front matter 但没有规则，也要在汇总里显式标 unknown。
    no_rule = evaluate_paths(kb, ["crypto/c.md", "note.md"], "这题怎么打")
    assert no_rule["status"] == STATUS_UNKNOWN
    assert no_rule["unknown"] == 1
    assert any("尚未评估" in line for line in no_rule["hint"].splitlines())

    known = evaluate_paths(kb, ["note.md"], "这题怎么打")
    assert known["status"] == STATUS_KNOWN
    assert known["unknown"] == 0
    assert known["hint"] == "所有可判定前提均已知，或该资料没有额外前提。"


def test_resolve_target_rejects_ambiguous_and_missing(kb: Path):
    assert resolve_target(kb, "b.md") == "b.md"
    assert resolve_target(kb, "missing.md") is None
    (kb / "x").mkdir()
    (kb / "y").mkdir()
    (kb / "x" / "dup.md").write_text("---\ntitle: D\n---\n", encoding="utf-8")
    (kb / "y" / "dup.md").write_text("---\ntitle: D\n---\n", encoding="utf-8")
    assert resolve_target(kb, "dup.md") is None
