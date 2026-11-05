"""按实际小节和查询词选解释材料，不重建索引。"""

from __future__ import annotations

import re

from .explain import match_terms
from .parser import split_front_matter


def paired_code(root, rel: str, catalog):
    """只读取明确配对的脚本；多种方法合写时不随意选一个。"""
    if catalog is None:
        return None
    from .condition_guides import load_guides
    from .library import read_code

    guide = next((g for g in load_guides() if rel in g["paths"]), None)
    target = next(p for p in guide["paths"] if p.startswith("_methods/")) if guide else rel
    file = (root / target).resolve()
    if not file.is_relative_to(root.resolve()):
        return None
    links = catalog.info(target, file.read_text(encoding="utf-8"))["scripts"]
    return read_code(root, links[0]["path"]) if len(links) == 1 else None


def select_excerpt(text: str, query: str = "", section: str = "", limit: int = 2600) -> str:
    _, body = split_front_matter(text)
    lines = body.splitlines(keepends=True)
    starts = [0]
    fence = None
    offset = 0
    for line in lines:
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            char = marker[1][0]
            if fence is None:
                fence = char
            elif char == fence:
                fence = None
        elif fence is None and re.match(r"^#{1,6}\s+", line) and offset:
            starts.append(offset)
        offset += len(line)
    starts.append(len(body))
    blocks = [body[a:b].strip() for a, b in zip(starts, starts[1:]) if body[a:b].strip()]
    if not blocks:
        return ""
    terms = match_terms(query, body, limit=24)

    def score(block):
        title = re.sub(r"^#+\s*", "", block.splitlines()[0]).strip()
        low = block.casefold()
        return (1000 if section and title == section else 0) + sum(
            len(term) * (5 if term.casefold() in title.casefold() else 1)
            for term in terms
            if term.casefold() in low
        )

    selected = max(blocks, key=score)
    if len(selected) <= limit:
        return selected
    low = selected.casefold()
    pos = next((low.find(term.casefold()) for term in terms if term.casefold() in low), 0)
    start = max(0, pos - limit // 4)
    if start:
        start = selected.rfind("\n", 0, start) + 1
    prefix = "（小节片段）\n" if start else ""
    suffix = "\n（余文见原文）"
    room = limit - len(prefix) - len(suffix)
    if room <= 0:
        return selected[start : start + limit]
    return prefix + selected[start : start + room] + suffix
