#!/usr/bin/env python
"""可复现检索评测入口。

用法：
    python tools/eval_search.py
    python tools/eval_search.py --mode fts
    python tools/eval_search.py --top-k 10 --json
    python tools/eval_search.py --queries eval/search_queries.json

评测只读本地索引；不使用真实 LLM、不访问网络。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
os.environ.setdefault("PYTHONUTF8", "1")
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

from kb.config import Config  # noqa: E402
from kb.evaluation import evaluate, load_queries  # noqa: E402
from kb.fusion import fuse_single_source  # noqa: E402
from kb.rag import KB  # noqa: E402


def _doc_type(path: str) -> str:
    return "card" if path.startswith("_des/cards/") else "topic"


def _dedupe_docs(hits):
    seen: set[str] = set()
    out = []
    for h in hits:
        if h.doc_path in seen:
            continue
        seen.add(h.doc_path)
        out.append(h)
    return out


def build_search(kb: KB, mode: str, expand: bool):
    if mode == "fts":
        def search(query: str, top_k: int = 5, category=None, doc_type=None):
            raw = kb.fts.search(query, top_k=max(top_k * 4, top_k), category=category)
            hits = fuse_single_source(_dedupe_docs(raw), top_k)
            if doc_type:
                hits = [h for h in hits if _doc_type(h.doc_path) == doc_type]
            return hits[:top_k]
        return search

    def search(query: str, top_k: int = 5, category=None, doc_type=None):
        kwargs = {"top_k": top_k, "category": category, "expand": expand}
        try:
            return kb.search(query, doc_type=doc_type, **kwargs)
        except TypeError:
            hits = kb.search(query, **kwargs)
            if doc_type:
                hits = [h for h in hits if _doc_type(h.doc_path) == doc_type]
            return hits[:top_k]
    return search


def _check_expected(cases, kb: KB) -> list[str]:
    missing = []
    for c in cases:
        for p in c.expected:
            if not (kb.cfg.kb_dir / p).is_file():
                missing.append(f"{c.id}: {p}")
    return missing


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="固定查询集检索评测")
    ap.add_argument("--config", default=None, help="config.toml 路径")
    ap.add_argument("--queries", default=str(ROOT / "eval" / "search_queries.json"))
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--mode", choices=["hybrid", "fts"], default="hybrid")
    ap.add_argument("--no-expand", action="store_true", help="关闭图谱扩展")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--json-out", help="把 JSON 结果写到文件（UTF-8）")
    args = ap.parse_args(argv)

    cases = load_queries(args.queries)
    kb = KB(Config.load(args.config))
    missing = _check_expected(cases, kb)
    if missing and not args.json:
        print("警告：以下 expected 路径不存在：")
        for m in missing:
            print("  " + m)

    result = evaluate(cases, build_search(kb, args.mode, not args.no_expand),
                      top_k=args.top_k)
    result["mode"] = args.mode
    result["queries_file"] = str(Path(args.queries))
    if missing:
        result["missing_expected"] = missing

    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    agg = result["aggregate"]
    print(f"查询集: {args.queries}  ({agg['queries']} 条)")
    print(f"模式: {args.mode}  top_k={agg['top_k']}")
    print("汇总: "
          f"top1={agg['top1']:.4f}  hit@{agg['top_k']}={agg['hit']:.4f}  "
          f"MRR={agg['mrr']:.4f}  recall@{agg['top_k']}={agg['recall']:.4f}")
    print()
    for s in result["scores"]:
        mark = "OK " if s["hit"] else "MISS"
        first = s["first_hit_rank"] or "-"
        print(f"  [{mark}] first={first:<3} top1={int(s['top1'])}  "
              f"{s['id']:<18} {s['query']}")
    if result["misses"]:
        print("\n未命中：")
        for m in result["misses"]:
            print(f"  - {m['id']}: {m['query']}")
            print(f"    expected={m['expected']}")
            print(f"    got={m['ranked'][:5]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
