"""按实际小节和查询词选解释材料，不重建索引。"""
from __future__ import annotations

import re

from .explain import match_terms
from .parser import split_front_matter


def select_excerpt(text: str, query: str = '', section: str = '', limit: int = 2600) -> str:
    _, body = split_front_matter(text)
    lines = body.splitlines(keepends=True)
    starts = [0]
    fence = None
    offset = 0
    for line in lines:
        marker = re.match(r'^\s*(`{3,}|~{3,})', line)
        if marker:
            char = marker[1][0]
            if fence is None:
                fence = char
            elif char == fence:
                fence = None
        elif fence is None and re.match(r'^#{1,6}\s+', line) and offset:
            starts.append(offset)
        offset += len(line)
    starts.append(len(body))
    blocks = [body[a:b].strip() for a, b in zip(starts, starts[1:]) if body[a:b].strip()]
    if not blocks:
        return ''
    terms = match_terms(query, body, limit=24)
    def score(block):
        title = re.sub(r'^#+\s*', '', block.splitlines()[0]).strip()
        low = block.casefold()
        return ((1000 if section and title == section else 0)
                + sum(len(term) * (5 if term.casefold() in title.casefold() else 1)
                      for term in terms if term.casefold() in low))
    selected = max(blocks, key=score)
    if len(selected) <= limit:
        return selected
    low = selected.casefold()
    pos = next((low.find(term.casefold()) for term in terms if term.casefold() in low), 0)
    start = max(0, pos - limit // 4)
    if start:
        start = selected.rfind('\n', 0, start) + 1
    prefix = '（小节片段）\n' if start else ''
    suffix = '\n（余文见原文）'
    room = limit - len(prefix) - len(suffix)
    if room <= 0:
        return selected[start:start + limit]
    return prefix + selected[start:start + room] + suffix
