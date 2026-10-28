"""可复现检索评测：固定查询集 + top1/top5/MRR。

指标定义（越低越差，范围 0..1）：
- top1：第 1 名命中任一 expected 文档
- hit@k：前 k 名命中任一 expected 文档（本文件默认 k=5）
- MRR：第一个命中名次的倒数（未命中记 0）
- recall@k：前 k 名覆盖了多少 expected 文档

同一篇文档的多个 chunk 不应重复占位；调用方应先做文档级去重。
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence


@dataclass
class QueryCase:
    id: str
    query: str
    expected: list[str]
    category: str | None = None
    doc_type: str | None = None


@dataclass
class QueryScore:
    case: QueryCase
    ranked: list[str]
    first_hit_rank: int | None
    top1: float
    hit_at_k: float
    rr: float
    recall_at_k: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.case.id,
            "query": self.case.query,
            "expected": self.case.expected,
            "ranked": self.ranked,
            "first_hit_rank": self.first_hit_rank,
            "top1": self.top1,
            "hit": self.hit_at_k,
            "rr": round(self.rr, 4),
            "recall": round(self.recall_at_k, 4),
        }


def load_queries(path: str | Path) -> list[QueryCase]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    items = raw.get("queries", raw) if isinstance(raw, dict) else raw
    if not isinstance(items, list) or not items:
        raise ValueError("评测文件里没有 queries")
    cases: list[QueryCase] = []
    seen: set[str] = set()
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"第 {i + 1} 条不是对象")
        q = str(item.get("query") or "").strip()
        expected = item.get("expected") or []
        if not q:
            raise ValueError(f"第 {i + 1} 条缺少 query")
        if isinstance(expected, str):
            expected = [expected]
        expected = [str(p).replace("\\", "/").strip() for p in expected if str(p).strip()]
        if not expected:
            raise ValueError(f"{q!r} 缺少 expected")
        cid = str(item.get("id") or f"q{i + 1}")
        if cid in seen:
            raise ValueError(f"id 重复: {cid}")
        seen.add(cid)
        cases.append(QueryCase(
            id=cid,
            query=q,
            expected=expected,
            category=item.get("category"),
            doc_type=item.get("doc_type"),
        ))
    return cases


def rank_metrics(ranked: Sequence[str], expected: Iterable[str], top_k: int = 5) -> dict[str, Any]:
    exp = {str(x) for x in expected}
    ranked = list(ranked)
    first: int | None = None
    for i, path in enumerate(ranked, 1):
        if path in exp:
            first = i
            break
    hit = 1.0 if first is not None and first <= top_k else 0.0
    recall = 0.0
    if exp:
        recall = len(set(ranked[:top_k]) & exp) / len(exp)
    return {
        "top1": 1.0 if ranked and ranked[0] in exp else 0.0,
        "hit": hit,
        "rr": 1.0 / first if first else 0.0,
        "recall": recall,
        "first": first,
    }


def evaluate(
    cases: Sequence[QueryCase],
    search: Callable[..., Sequence[Any]],
    top_k: int = 5,
) -> dict[str, Any]:
    """search(case.query, top_k=..., category=..., doc_type=...) -> 有序结果对象。

    结果对象需带 doc_path 属性，或本身是文档路径字符串。
    """
    scores: list[QueryScore] = []
    for case in cases:
        hits = search(case.query, top_k=top_k, category=case.category,
                      doc_type=case.doc_type)
        ranked: list[str] = []
        for h in hits:
            p = h if isinstance(h, str) else getattr(h, "doc_path", None)
            if p and p not in ranked:
                ranked.append(str(p))
        m = rank_metrics(ranked, case.expected, top_k)
        scores.append(QueryScore(
            case=case, ranked=ranked, first_hit_rank=m["first"],
            top1=m["top1"], hit_at_k=m["hit"], rr=m["rr"],
            recall_at_k=m["recall"],
        ))

    n = len(scores)
    if n == 0:
        raise ValueError("没有评测查询")
    agg = {
        "queries": n,
        "top_k": top_k,
        "top1": round(sum(s.top1 for s in scores) / n, 4),
        "hit": round(sum(s.hit_at_k for s in scores) / n, 4),
        "mrr": round(sum(s.rr for s in scores) / n, 4),
        "recall": round(sum(s.recall_at_k for s in scores) / n, 4),
    }
    return {
        "aggregate": agg,
        "scores": [
            {
                "id": s.case.id,
                "query": s.case.query,
                "expected": s.case.expected,
                "ranked": s.ranked,
                "first_hit_rank": s.first_hit_rank,
                "top1": s.top1,
                "hit": s.hit_at_k,
                "rr": round(s.rr, 4),
                "recall": round(s.recall_at_k, 4),
            }
            for s in scores
        ],
        "misses": [
            {"id": s.case.id, "query": s.case.query,
             "expected": s.case.expected, "ranked": s.ranked}
            for s in scores if s.hit_at_k == 0.0
        ],
    }
