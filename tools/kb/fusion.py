"""RRF（Reciprocal Rank Fusion）融合 + 文档级去重。

score(d) = Σ_i  w_i / (k + rank_i(d))
关键词与向量两路互补：FTS 抓术语精确命中，向量抓"意思相近但词面不同"。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .fts import Hit


@dataclass
class FusedHit:
    doc_path: str
    title: str
    category: str
    score: float
    sources: list[str] = field(default_factory=list)
    best_text: str = ""
    section: str = ""
    per_source: dict[str, float] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "path": self.doc_path,
            "title": self.title,
            "category": self.category,
            "score": round(self.score, 5),
            "sources": self.sources,
            "section": self.section,
        }


def rrf_fuse(
    fts_hits: list[Hit],
    vec_hits: list[dict[str, Any]],
    k: int = 60,
    w_fts: float = 1.0,
    w_vec: float = 1.0,
    top_k: int = 8,
    doc_level: bool = True,
) -> list[FusedHit]:
    """RRF 融合，默认按**文档**去重排名。

    为什么必须做文档级去重：
      两路召回都是 chunk 级的，同一篇文档常常贡献多个 chunk。
      直接按 chunk 名次算 RRF 会让"自己的 chunk 占满前几名"的副作用反噬：
        A 文档: 命中 rank 1,2,3,4
        B 文档: 命中 rank 5
      看起来 A 更强，但实际会影响"该文档与其它文档的相对权重"，
      导致真正排第一的那篇在某些情况下被别的文档挤掉。
      实测：一篇 RSA 题目 FTS 命中 1/2/3/4 名，融合后却输给另一篇。

    做法：先按 doc_path 合并，用该文档**最好的名次**代表它在单路中的排名，
    再算 1/(k+rank)。这样 RRF 融合的是"文档排序"，而非"块排序"。
    """
    def dedup(items: list[tuple[str, Any]]) -> list[tuple[str, Any]]:
        if not doc_level:
            return items
        seen: set[str] = set()
        out: list[tuple[str, Any]] = []
        for key, obj in items:
            if key in seen:
                continue
            seen.add(key)
            out.append((key, obj))
        return out

    fts_list = dedup([(h.doc_path, h) for h in fts_hits])
    vec_list = dedup([(v["doc_path"], v) for v in vec_hits])

    acc: dict[str, FusedHit] = {}
    ranks: dict[str, dict[str, float]] = {}

    def push(key: str, title: str, cat: str, source: str, rank: int, weight: float,
             text: str = "", section: str = ""):
        contrib = weight / (k + rank + 1)
        h = acc.get(key)
        if h is None:
            h = FusedHit(doc_path=key, title=title, category=cat, score=0.0)
            acc[key] = h
        h.score += contrib
        if source not in h.sources:
            h.sources.append(source)
        ranks.setdefault(key, {})[source] = contrib
        if text and len(text) > len(h.best_text):
            h.best_text = text
            h.section = section or h.section

    for rank, (doc_path, hit) in enumerate(fts_list):
        push(doc_path, hit.title, hit.category, "fts", rank, w_fts,
             hit.origin, getattr(hit, "section", ""))
    for rank, (doc_path, hit) in enumerate(vec_list):
        push(doc_path, hit["title"], hit["category"], "vec", rank, w_vec,
             hit.get("text", ""), hit.get("section", ""))

    for key, h in acc.items():
        h.per_source = ranks.get(key, {})

    ranked = sorted(acc.values(), key=lambda x: -x.score)
    return ranked[:top_k]


def fuse_single_source(hits: list[Hit], top_k: int = 8) -> list[FusedHit]:
    """没有向量索引时的降级路径：按 FTS 顺序直接用。"""
    out = []
    for h in hits[:top_k]:
        out.append(FusedHit(
            doc_path=h.doc_path, title=h.title, category=h.category,
            score=1.0 / (60 + len(out)), sources=["fts"],
            best_text=h.origin, section=getattr(h, "section", ""),
        ))
    return out
