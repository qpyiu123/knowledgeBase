"""P1 可复现评测的指标测试（不加载真实索引）。"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from kb.evaluation import QueryCase, evaluate, load_queries, rank_metrics


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
