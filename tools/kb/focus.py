"""从当前卡点另查资料，主查询保持不变；假设不作为技术事实。"""
from __future__ import annotations
import re


def latest_attempts(workspace: dict) -> list[dict]:
    latest = []
    seen = set()
    entries = workspace.get('entries') or []
    for index in range(len(entries) - 1, -1, -1):
        entry = entries[index]
        if entry.get('kind') != 'attempt':
            continue
        direction = (entry.get('direction') or '').strip()
        key = ('direction', direction) if direction else ('entry', index)
        if key not in seen:
            seen.add(key)
            latest.append(entry)
    return list(reversed(latest))


def recent_facts(workspace: dict, budget=4000) -> list[dict]:
    selected = []
    used = 0
    for entry in reversed(workspace.get('entries') or []):
        text = entry.get('text', '')
        if entry.get('kind') == 'fact' and text.strip() and used + len(text) <= budget:
            selected.append(entry)
            used += len(text)
    return list(reversed(selected))


def workspace_basis(workspace: dict) -> list[dict]:
    entries = workspace.get('entries') or []
    basis = []
    if workspace.get('pending_checks', '').strip():
        basis.append({'field': 'pending_checks', 'label': '待查项', 'text': workspace['pending_checks']})
    runtime = next((e for e in reversed(entries) if e.get('kind') == 'attempt'), None)
    if runtime and runtime.get('result') == 'failed' and runtime.get('failure_kind') == 'runtime':
        text = (runtime.get('conclusion') or runtime.get('text') or '').strip()
        if text:
            basis.append({'field': 'runtime_error', 'label': '最近运行错误', 'text': text, 'entry_id': runtime['id']})
    if workspace.get('goal', '').strip():
        basis.append({'field': 'goal', 'label': '当前目标', 'text': workspace['goal']})
    if workspace.get('hypotheses', '').strip():
        basis.append({'field': 'hypotheses', 'label': '待验证假设', 'text': workspace['hypotheses']})
    facts = recent_facts(workspace)
    if facts:
        basis.append({'field': 'facts', 'label': '近期已确认事实',
                      'text': '；'.join(e['text'] for e in facts),
                      'entry_ids': [e['id'] for e in facts]})
    return basis


def condition_query(workspace: dict, query: str) -> str:
    facts = [e['text'] for e in recent_facts(workspace)]
    return '；'.join([query, *facts])


def focus_hits(kb, workspace: dict, *, top_k: int = 5, category=None, doc_type=None):
    """按待查项、错误、目标和近期事实依次找资料，保留每条的记录依据。"""
    basis = workspace_basis(workspace)
    from .fts import FtsIndex
    names = {}
    for item in basis:
        literal = FtsIndex._exact_query(item['text'])
        names[item['field']] = ([literal] if literal else re.findall(
            r'(?<![A-Za-z0-9_.])[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+(?![A-Za-z0-9_.])', item['text']))
    if any(names.values()):
        for item in basis:
            names[item['field']] += re.findall(r'(?<![A-Za-z0-9_.])[A-Z][A-Za-z0-9_]*Error(?![A-Za-z0-9_.])', item['text'])
    precise = {}
    cache = {}
    for item in basis:
        matched = False
        for name in dict.fromkeys(names[item['field']]):
            if name not in cache:
                cache[name] = kb.search(name, top_k=top_k, category=category, doc_type=doc_type,
                                        retrieval='fts', expand=False)
            pattern = re.compile(r'(?<![\w.])' + re.escape(name) + r'(?![\w.])', re.I)
            for hit in cache[name]:
                text = str(getattr(hit, 'best_text', '') or '') + '\n' + str(getattr(hit, 'title', ''))
                if not pattern.search(text):
                    continue
                matched = True
                row = precise.setdefault(hit.doc_path, {'hit': hit, 'basis': [], 'names': set()})
                row['names'].add(name)
                if item not in row['basis']:
                    row['basis'].append(item)
        if names[item['field']] and not matched:
            item['missing'] = True
    if precise:
        coverage = max(len(row['names']) for row in precise.values())
        return [row for row in precise.values() if len(row['names']) == coverage], basis
    found = {}
    for item in basis:
        if names[item['field']]:
            continue
        hits = kb.search(item['text'], top_k=top_k, category=category, doc_type=doc_type,
                         retrieval='fts', expand=False)
        for hit in hits:
            if hit.doc_path not in found:
                found[hit.doc_path] = {'hit': hit, 'basis': []}
            found[hit.doc_path]['basis'].append(item)
    return list(found.values()), basis
