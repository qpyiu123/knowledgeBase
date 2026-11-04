"""同一索引比较快查与附加条件核对；不调用模型、不写索引。"""
from __future__ import annotations

import ctypes
import json
import os
import platform
import statistics
import sys
import time
from unittest.mock import patch
from pathlib import Path

from agent import server
from kb.applicability import evaluate_conditions
from kb.condition_guides import load_guides

ROOT = Path(__file__).resolve().parents[1]


def peak_memory_mib():
    if os.name != 'nt':
        return None
    from ctypes import wintypes
    class Counters(ctypes.Structure):
        _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)] + [
            (name, ctypes.c_size_t) for name in ('PeakWorkingSetSize', 'WorkingSetSize',
                'QuotaPeakPagedPoolUsage', 'QuotaPagedPoolUsage', 'QuotaPeakNonPagedPoolUsage',
                'QuotaNonPagedPoolUsage', 'PagefileUsage', 'PeakPagefileUsage')]
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    psapi = ctypes.WinDLL('psapi', use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
        raise ctypes.WinError(ctypes.get_last_error())
    return round(counters.PeakWorkingSetSize / 1024**2, 1)


@patch('requests.post', side_effect=AssertionError('本评测禁止调用生成服务'))
def main(generation_request):
    cases = json.loads((ROOT / 'eval/r2_conditions.json').read_text(encoding='utf-8'))
    server.GENERATION_DISABLED = True
    start = time.perf_counter()
    kb = server.get_kb()
    init_ms = round((time.perf_counter() - start) * 1000, 1)
    # 文件时间和大小用于确认本次评测没有重建索引。
    before = {p.name: (p.stat().st_size, p.stat().st_mtime_ns) for p in kb.cfg.index_dir.iterdir() if p.is_file()}
    timings = {'A': [], 'AB': []}
    results = []
    for index, case in enumerate(cases):
        outputs = {}
        for mode in (('A', 'AB') if index % 2 == 0 else ('AB', 'A')):
            t0 = time.perf_counter()
            outputs[mode] = server.api_search({'q': case['query'], 'top_k': 5, 'retrieval': 'fts',
                                              'with_conditions': mode == 'AB'})
            timings[mode].append(round((time.perf_counter() - t0) * 1000, 2))
        paths = {mode: [h['path'] for h in data['hits']] for mode, data in outputs.items()}
        assert paths['A'] == paths['AB']
        assert outputs['A']['query'] == outputs['AB']['query'] == case['query']
        guide = next((g for g in load_guides() if case['path'] in g['paths']), None)
        expected = set(guide['paths'] if guide else [case['path']])
        app = evaluate_conditions(kb.cfg.kb_dir, case['path'], case['query'])
        errors = [key for key, value in case.get('conditions', {}).items()
                  if next(c['status'] for c in app['conditions'] if c['id'] == key) != value]
        linked = any(expected.intersection(link['path'] for link in h.get('methods', []))
                     for h in outputs['AB']['hits'])
        contrasts = any(expected.intersection(c['path'] for c in (h.get('applicability') or {}).get('guide', {}).get('contrasts', []))
                        for h in outputs['AB']['hits'])
        results.append({'id': case['id'], 'query': case['query'], 'target': case['path'],
                        'paths': paths['A'], 'same_order': True,
                        'direct_at_5': bool(expected.intersection(paths['A'])), 'method_link': linked,
                        'condition_link': contrasts, 'expected_status': case['status'],
                        'status': app['status'], 'condition_errors': errors,
                        'registered_conditions': len(app['conditions']),
                        'unknown_conditions': sum(c['status'] == 'unknown' for c in app['conditions'])})
    warm = {'A': [], 'AB': []}
    for case in cases:
        for mode in ('AB', 'A'):
            t0 = time.perf_counter()
            server.api_search({'q': case['query'], 'top_k': 5, 'retrieval': 'fts', 'with_conditions': mode == 'AB'})
            warm[mode].append(round((time.perf_counter() - t0) * 1000, 2))
    after = {p.name: (p.stat().st_size, p.stat().st_mtime_ns) for p in kb.cfg.index_dir.iterdir() if p.is_file()}
    assert before == after
    report = {'date': '2026-11-05', 'python': sys.version.split()[0], 'platform': platform.platform(),
              'queries': len(cases), 'kb_init_ms': init_ms, 'first_query_A_ms': timings['A'][0],
              'cold_definition': '新进程首查；操作系统文件缓存未清空',
              'first_pass_median_ms': {m: round(statistics.median(t), 2) for m, t in timings.items()},
              'repeat_median_ms': {m: round(statistics.median(t), 2) for m, t in warm.items()},
              'repeat_max_ms': {m: max(t) for m, t in warm.items()}, 'peak_working_set_mib': peak_memory_mib(),
              'same_order': sum(r['same_order'] for r in results),
              'direct_at_5': sum(r['direct_at_5'] for r in results),
              'reachable_A_at_5': sum(r['direct_at_5'] or r['method_link'] for r in results),
              'reachable_AB_at_5': sum(r['direct_at_5'] or r['method_link'] or r['condition_link'] for r in results),
              'wrong_status': sum(r['status'] != r['expected_status'] for r in results),
              'condition_errors': sum(len(r['condition_errors']) for r in results),
              'no_registered_guide': sum(not r['registered_conditions'] for r in results),
              'unknown_conditions': sum(r['unknown_conditions'] for r in results),
              'index_unchanged': True, 'generation_calls': generation_request.call_count, 'results': results}
    out = ROOT / 'work/r2/condition-eval.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'results'}, ensure_ascii=False))
    return int(bool(report['wrong_status'] or report['condition_errors']))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
