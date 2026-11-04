"""检索结果解释：命中段落、命中词、命中来源与文档类型。

只做展示层整理，不改变排序。排序由 RRF / 评测决定。
"""
from __future__ import annotations

import re
from typing import Any, Iterable

from .parser import tokenize_query

_CJK = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")
_META_PREFIXES = ("标签:", "识别信号:")


def doc_type(path: str) -> str:
    """方法卡、比赛卡片与专题文档。"""
    if path.startswith("_methods/"):
        return "method"
    return "card" if path.startswith("_des/cards/") else "topic"


def doc_type_label(path: str) -> str:
    return {"method": "方法卡", "card": "比赛卡片", "topic": "专题文档"}[doc_type(path)]


def strip_chunk_prefix(text: str) -> str:
    """去掉 chunk 顶部的【方向】标题、章节名与 标签/识别信号 元数据。

    chunk_doc 为了保证向量召回，会把元数据拼进每个 chunk；展示摘要时
    这些前缀只是噪音，真正的命中段落从元数据之后开始。
    """
    lines = text.splitlines()
    out: list[str] = []
    started = False
    skipped_heading = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not started:
            if i == 0 and stripped.startswith("【"):
                continue
            if not skipped_heading and stripped.startswith("## "):
                skipped_heading = True
                continue
            if stripped.startswith(_META_PREFIXES):
                continue
        started = True
        out.append(line)
    body = "\n".join(out).strip()
    return body or text.strip()


def _first_pos(body: str, terms: Iterable[str]) -> int:
    low = body.casefold()
    best = -1
    for t in terms:
        if len(t) < 2 and not _CJK.search(t):
            continue
        p = low.find(t.casefold())
        if p != -1 and (best == -1 or p < best):
            best = p
    return best


def make_snippet(text: str, query: str = "", width: int = 320) -> str:
    """从命中 chunk 里取一段可读正文，优先截取命中词附近。"""
    body = strip_chunk_prefix(text or "")
    body = re.sub(r"[ \t]+", " ", body)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    if not body:
        return ""
    if len(body) <= width:
        return body
    pos = _first_pos(body, match_terms(query, body, limit=12))
    start = 0 if pos < 0 else max(0, pos - 60)
    end = min(len(body), start + width)
    if end - start < width and start > 0:
        start = max(0, end - width)
    out = body[start:end].strip()
    if start > 0:
        out = "…" + out
    if end < len(body):
        out = out.rstrip() + "…"
    return out


def match_terms(query: str, text: str, limit: int = 8) -> list[str]:
    """返回 query 分词里确实出现在命中段落中的词（去重保序）。"""
    if not query or not text:
        return []
    low = text.casefold()
    seen: set[str] = set()
    out: list[str] = []
    # 先放长词/中文词，单字母 n/e/c 放后面，避免解释里只剩噪音。
    tokens = [t for t in tokenize_query(query) if t not in seen]
    tokens.sort(key=lambda t: (len(t) < 2 and not _CJK.search(t), -len(t)))
    for t in tokens:
        if t in seen:
            continue
        if t.casefold() in low:
            seen.add(t)
            out.append(t)
            if len(out) >= limit:
                break
    return out


def source_labels(sources: Iterable[str]) -> list[str]:
    labels = []
    for s in sources:
        if s == "fts":
            labels.append("词面命中")
        elif s == "vec":
            labels.append("语义相近")
        elif s.startswith("graph:"):
            labels.append("图谱关联")
        elif s:
            labels.append(s)
    return labels


def match_info(hit: Any, query: str) -> dict[str, Any]:
    """给 API / UI 用的命中原因。hit 需带 sources / best_text / per_source。"""
    text = getattr(hit, "best_text", "") or ""
    sources = [s for s in (getattr(hit, "sources", None) or []) if s]
    per_source = getattr(hit, "per_source", None) or {}
    info: dict[str, Any] = {
        "sources": sources,
        "labels": source_labels(sources),
        "terms": match_terms(query, text),
        "rrf": {k: round(float(v), 6) for k, v in per_source.items()},
    }
    via = getattr(hit, "graph_via", None)
    if via:
        info["graph"] = {
            "via": via,
            "hop": getattr(hit, "graph_hop", None),
            "boost": bool(getattr(hit, "graph_boost", False)),
        }
    return info
