"""固定卡点样例比较主查询与附加资料；只使用离线索引和样例工作区。"""
from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from agent import server
from eval_conditions import peak_memory_mib


def main():
    cases = json.loads((ROOT / 'eval/r3_focus.json').read_text(encoding='utf-8'))
    workspaces = {}
    for case in cases:
        entries = [{'id': f"{case['id']}-f{i}", 'kind': 'fact', 'text': text}
                   for i, text in enumerate(case.get('facts', []))]
        entries += [{'id': f"{case['id']}-a{i}", 'kind': 'attempt', **entry}
                    for i, entry in enumerate(case.get('attempts', []))]
        workspaces[case['id']] = {**case, 'title': case['id'], 'entries': entries}
    results = []
    timings = {'A': [], 'AB': []}
    with patch.object(server, '_workspace_store', return_value=SimpleNamespace(load=workspaces.__getitem__)), \
            patch('kb.rag.get_backend', side_effect=AssertionError('卡点评测禁止生成')) as generation:
        kb = server.get_kb()
        for case in cases:
            expected = set(case['expected'])
            assert all((kb.cfg.kb_dir / path).is_file() for path in expected)
            outputs = {}
            for mode in ('A', 'AB'):
                t0 = time.perf_counter()
                outputs[mode] = server.api_search({'q': case['query'], 'top_k': 5, 'retrieval': 'fts',
                    'with_conditions': False, **({'workspace_id': case['id']} if mode == 'AB' else {})})
                timings[mode].append(round((time.perf_counter() - t0) * 1000, 2))
            paths = {mode: [hit['path'] for hit in data['hits']] for mode, data in outputs.items()}
            assert paths['A'] == paths['AB']
            assert outputs['A']['query'] == outputs['AB']['query'] == case['query']
            focus = outputs['AB']['focus']
            related = {h['path'] for h in focus['hits']}
            target_hits = [h for h in focus['hits'] if h['path'] in expected]
            wrong_status = [h['path'] for h in target_hits if 'status' in case
                            and h['applicability']['status'] != case['status']]
            results.append({'id': case['id'], 'query': case['query'], 'expected': case['expected'],
                'primary': paths['A'], 'focus': [h['path'] for h in focus['hits']],
                'A_found': bool(expected.intersection(paths['A'])),
                'AB_found': bool(expected.intersection(set(paths['AB']) | related)),
                'wrong_status': wrong_status,
                'empty_focus_correct': not focus['hits'] if case.get('empty_focus') else None,
                'excluded_scopes': [h['applicability']['guide']['title'] for h in focus['excluded']]})
        report = {'date': '2026-11-05', 'queries': len(cases),
            'covered_cases': sum(bool(c['expected']) for c in cases),
            'A_found': sum(r['A_found'] for r in results), 'AB_found': sum(r['AB_found'] for r in results),
            'same_primary_order': len(cases), 'wrong_condition_status': sum(len(r['wrong_status']) for r in results),
            'missing_or_empty_correct': sum(r['empty_focus_correct'] is True for r in results),
            'median_ms': {m: round(statistics.median(v), 2) for m, v in timings.items()},
            'peak_working_set_mib': peak_memory_mib(), 'generation_calls': generation.call_count,
            'results': results}
    out = ROOT / 'work/r33/focus-eval.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'results'}, ensure_ascii=False))
    return int(bool(report['wrong_condition_status'] or report['AB_found'] != report['covered_cases']
                    or report['missing_or_empty_correct'] != sum(c.get('empty_focus', False) for c in cases)))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
