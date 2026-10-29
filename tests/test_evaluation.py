"""P1 可复现评测的指标测试（不加载真实索引）。"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from kb.evaluation import (
    QueryCase,
    evaluate,
    evaluate_at_ks,
    load_queries,
    rank_metrics,
)


def test_rank_metrics_hit_and_mrr():
    m = rank_metrics(["b", "a", "c"], ["a"], top_k=5)
    assert m["top1"] == 0.0
    assert m["hit"] == 1.0
    assert m["rr"] == 0.5
    assert m["recall"] == 1.0


def test_rank_metrics_miss():
    m = rank_metrics(["x", "y"], ["a"], top_k=5)
    assert m["top1"] == 0.0
    assert m["hit"] == 0.0
    assert m["rr"] == 0.0
    assert m["recall"] == 0.0


def test_rank_metrics_multi_relevant_recall():
    m = rank_metrics(["a", "x", "b"], ["a", "b"], top_k=5)
    assert m["recall"] == 1.0
    assert m["rr"] == 1.0


def test_evaluate_aggregates_and_sanitizes_duplicates():
    cases = [
        QueryCase("q1", "one", ["a"]),
        QueryCase("q2", "two", ["b"]),
    ]

    def search(query, top_k=5, category=None, doc_type=None):
        if query == "one":
            return ["a", "a", "x"]
        return ["x", "b"]

    result = evaluate(cases, search, top_k=5)
    agg = result["aggregate"]
    assert agg["top1"] == 0.5
    assert agg["hit"] == 1.0
    assert agg["mrr"] == 0.75
    assert result["misses"] == []
    assert result["scores"][0]["ranked"] == ["a", "x"]


def test_load_queries_rejects_missing_expected(tmp_path: Path):
    p = tmp_path / "q.json"
    p.write_text(json.dumps({"queries": [{"query": "x"}]}), encoding="utf-8")
    with pytest.raises(ValueError):
        load_queries(p)


def test_repo_eval_set_is_loadable():
    qfile = Path(__file__).resolve().parents[1] / "eval" / "search_queries.json"
    cases = load_queries(qfile)
    assert len(cases) >= 20
    assert len({c.id for c in cases}) == len(cases)


def test_expanded_eval_set_is_loadable_and_derived_from_kb():
    root = Path(__file__).resolve().parents[1]
    qfile = root / "eval" / "search_queries_expanded.json"
    cases = load_queries(qfile)
    assert len(cases) >= 60
    assert len({c.id for c in cases}) == len(cases)
    expected = {p for c in cases for p in c.expected}
    assert len(expected) >= 40
    missing = [p for p in expected if not (root / "kb" / p).is_file()]
    assert missing == []


def test_evaluate_at_ks_reports_recall_and_latency():
    cases = [QueryCase("q1", "one", ["a"]), QueryCase("q2", "two", ["b"])]

    def search(query, top_k=10, category=None, doc_type=None):
        if query == "one":
            return ["x", "y", "z", "a"][:top_k]
        return ["x", "b"][:top_k]

    result = evaluate_at_ks(cases, search, ks=(5, 10), primary_k=5)
    agg = result["aggregate"]
    assert agg["queries"] == 2
    assert agg["top_k"] == 10
    assert agg["top1"] == 0.0
    assert agg["hit@5"] == 1.0
    assert agg["recall@5"] == 1.0
    assert agg["recall@10"] == 1.0
    assert agg["avg_latency_ms"] >= 0.0
    assert result["scores"][0]["latency_ms"] is not None


def test_evaluate_at_ks_separates_recall_at_5_and_10():
    cases = [QueryCase("q1", "one", ["a"])]

    def search(query, top_k=10, category=None, doc_type=None):
        return ["x", "y", "z", "w", "v", "u", "a"][:top_k]

    result = evaluate_at_ks(cases, search, ks=(5, 10), primary_k=5)
    agg = result["aggregate"]
    assert agg["hit@5"] == 0.0
    assert agg["recall@5"] == 0.0
    assert agg["hit@10"] == 1.0
    assert agg["recall@10"] == 1.0
    assert agg["mrr"] == pytest.approx(1.0 / 7, abs=1e-4)
