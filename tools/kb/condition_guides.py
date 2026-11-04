"""少量方法的条件核对；只使用查询里明确给出的事实，不改变查询或排序。"""
from __future__ import annotations

import json
import math
import re
from functools import lru_cache
from pathlib import Path

GUIDES_FILE = Path(__file__).with_suffix('.json')
_UNCERTAIN = re.compile(r'是否|是不是|可能|假设|如果|不确定|未确认|不知道|不保证|无法确认|待确认|待检查|不清楚|例如|示例|例子|需要|要求|前提|条件|如何|怎么|为什么|请解释|能否|能用|什么是')
_BOUNDARY = re.compile(r'[。；;\n!?！？]')


@lru_cache(maxsize=2)
def _load(path: str, mtime: int) -> tuple[dict, ...]:
    return tuple(json.loads(Path(path).read_text(encoding='utf-8'))['guides'])


def load_guides() -> tuple[dict, ...]:
    return _load(str(GUIDES_FILE), GUIDES_FILE.stat().st_mtime_ns)


def _compact(query: str) -> tuple[str, list[int]]:
    chars, offsets = [], []
    for i, char in enumerate(query):
        if not char.isspace():
            for c in char.casefold():
                chars.append(c)
                offsets.append(i)
    return ''.join(chars), offsets


def _uncertain(q: str, start: int, end: int) -> bool:
    left = max((m.end() for m in _BOUNDARY.finditer(q, 0, start)), default=0)
    stop = _BOUNDARY.search(q, end)
    right = stop.start() if stop else len(q)
    suffix = re.split(r'[,，、]', q[end:right + 1], 1)[0]
    return bool(_UNCERTAIN.search(q[left:start]) or re.search(r'吗|么|[?？]', suffix))


def _observations(rule: dict, query: str, q: str, offsets: list[int]) -> list[tuple[bool, str]]:
    def matches(key):
        return [m for p in rule.get(key, []) for m in re.finditer(p, q)
                if not _uncertain(q, m.start(), m.end())]
    negatives = matches('negative')
    out = []
    for positive, matches_ in ((False, negatives), (True, matches('positive'))):
        for m in matches_:
            if positive and any(n.start() <= m.start() and n.end() >= m.end() for n in negatives):
                continue
            prefix = q[max(0, m.start() - 4):m.start()]
            if not positive and re.search(r'并非$|不是$', prefix):
                continue
            # “不是同一明文”要保留整个否定句作为证据。
            neg = re.search(r'并非$|不是$|没有$', prefix) if positive else None
            start = m.start() - len(neg.group()) if neg else m.start()
            out.append((positive and not neg, query[offsets[start]:offsets[m.end() - 1] + 1]))
    return out


def _assignments(q: str) -> dict[str, list[int]]:
    values: dict[str, list[int]] = {}
    for m in re.finditer(r'(?<![a-z0-9_])([en](?:[1-9][0-9]*)?)\s*=\s*(0x[0-9a-f]+|[0-9]+)(?![a-z0-9_.])', q):
        if _uncertain(q, m.start(), m.end()):
            continue
        try:
            value = int(m[2], 16 if m[2].startswith('0x') else 10)
        except ValueError:
            continue
        values.setdefault(m[1], []).append(value)
    return values


def _numeric(kind: str, values: dict[str, list[int]], q: str) -> list[tuple[bool, str]]:
    if kind == 'coprime-e':
        explicit = [(int(m[1]) == 1, m[0]) for m in re.finditer(r'gcd\(e1[,，]e2\)=([0-9]+)(?![0-9])', q)
                    if not _uncertain(q, m.start(), m.end())]
    else:
        explicit = []
    names = {'same-n': ('n1', 'n2'), 'different-n': ('n1', 'n2'),
             'coprime-e': ('e1', 'e2'), 'same-e': ('e1', 'e2'),
             'exponent': ('e',), 'count': ('e',)}.get(kind, ())
    if not names or not all(n in values for n in names):
        return explicit
    if any(len(set(values[n])) != 1 for n in names):
        return [(True, '参数重复赋值且数值冲突'), (False, '参数重复赋值且数值冲突')]
    nums = [values[n][0] for n in names]
    text = ', '.join(f'{n}={v}' for n, v in zip(names, nums))
    if kind in ('same-n', 'different-n'):
        return [(nums[0] == nums[1] if kind == 'same-n' else nums[0] != nums[1], text)]
    if kind == 'coprime-e':
        g = math.gcd(*nums)
        return explicit + [(g == 1, f'{text}，gcd={g}')]
    if kind == 'same-e':
        return [(nums[0] == nums[1], text)]
    if kind == 'exponent':
        return [(nums[0] >= 2, text)]
    # 不由“两组密文”等方法名称猜组数；只读取明确给出的数量。
    counts = []
    chinese = {'一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
    for m in re.finditer(r'(?:共有|有|给出)?([0-9]+|[一二两三四五六七八九十])组密文', q):
        if not _uncertain(q, m.start(), m.end()):
            count = chinese.get(m[1]) if m[1] in chinese else int(m[1])
            counts.append((count >= nums[0], f'{text}，{m[0]}'))
    return counts


def evaluate_guide(guide: dict, query: str) -> list[dict]:
    q, offsets = _compact(query)
    values = _assignments(query.casefold())
    conditions = []
    for rule in guide['conditions']:
        observations = _observations(rule, query, q, offsets)
        observations += _numeric(rule.get('kind', ''), values, q)
        statuses = {bool(yes) for yes, _ in observations}
        if len(statuses) == 2:
            status, evidence = 'unknown', '同时出现线索冲突：' + '；'.join(dict.fromkeys(t for _, t in observations))
        elif statuses:
            status = 'known' if True in statuses else 'unsatisfied'
            evidence = '查询证据：' + '；'.join(dict.fromkeys(t for _, t in observations))
        else:
            status, evidence = 'unknown', '查询未提供明确事实，请核对原题参数。'
        conditions.append({'id': rule['id'], 'label': rule['label'], 'status': status,
                           'status_label': {'known': '已知', 'unknown': '未知', 'unsatisfied': '不满足'}[status],
                           'evidence': evidence, 'need': [rule['check']], 'check': rule['check'],
                           'source': 'kb/' + guide['source']['path'], 'trace': 'rule'})
    return conditions
