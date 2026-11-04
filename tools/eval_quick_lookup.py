"""比较直接命中与通过明确来源关系找到方法的结果，不修改原预期表。"""
from __future__ import annotations

import json
import time
from pathlib import Path

from kb.config import Config
from kb.evaluation import load_queries
from kb.rag import KB

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    kb = KB(Config.load())
    results = []
    for case in load_queries(ROOT / 'eval/r1_quick_lookup.json'):
        start = time.perf_counter()
        hits = kb.search(case.query, top_k=5, retrieval='fts', expand=False)
        direct, linked = None, None
        for rank, hit in enumerate(hits[:5], 1):
            if hit.doc_path in case.expected:
                direct = rank
                break
        if direct is None:
            for rank, hit in enumerate(hits[:5], 1):
                file = kb.cfg.kb_dir / hit.doc_path
                info = kb.library.info(hit.doc_path, file.read_text(encoding='utf-8'))
                methods = {method['path'] for method in info['methods']}
                if methods.intersection(case.expected):
                    linked = {'rank': rank, 'source': hit.doc_path}
                    break
        results.append({'id': case.id, 'query': case.query, 'expected': case.expected,
                        'direct_rank': direct, 'method_link': linked,
                        'ms': round((time.perf_counter() - start) * 1000, 1)})
    report = {'queries': len(results), 'direct_at_5': sum(r['direct_rank'] is not None for r in results),
              'direct_or_linked_at_5': sum(r['direct_rank'] is not None or r['method_link'] is not None for r in results),
              'results': results}
    out = ROOT / 'work/r1/eval-30-linked.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({key: value for key, value in report.items() if key != 'results'}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
