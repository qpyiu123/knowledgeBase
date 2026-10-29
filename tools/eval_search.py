#!/usr/bin/env python
"""可复现检索评测入口。

用法：
    python tools/eval_search.py                     # 旧集 + 扩容集
    python tools/eval_search.py --set legacy        # 只跑旧 22 条基线
    python tools/eval_search.py --set expanded      # 只跑 P10 扩容集
    python tools/eval_search.py --mode fts
    python tools/eval_search.py --top-k 10 --json
    python tools/eval_search.py --queries eval/search_queries.json -v

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
from kb.evaluation import evaluate_at_ks, load_queries  # noqa: E402
from kb.fusion import fuse_single_source  # noqa: E402
from kb.rag import KB  # noqa: E402

LEGACY_FILE = ROOT / "eval" / "search_queries.json"
EXPANDED_FILE = ROOT / "eval" / "search_queries_expanded.json"

# P1/P8 旧 22 条固定集基线（见 docs/PROJECT_MEMORY.md 第 7 节）。
LEGACY_BASELINE = {
    "top1": 1.0,
    "hit@5": 1.0,
    "mrr": 1.0,
    "recall@5": 1.0,
}
# 允许的绝对下降：recall@5 超过 1 个绝对点即视为回退。
MAX_RECALL_DROP = 0.01


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


def _set_path(name: str) -> Path:
    return {"legacy": LEGACY_FILE, "expanded": EXPANDED_FILE}[name]


def _print_summary(name: str, path: str, result: dict, verbose: bool) -> None:
    agg = result["aggregate"]
    print(f"查询集: {name} ({agg['queries']} 条)  {path}")
    print(f"模式: {result['mode']}  primary_k={agg['primary_k']}  "
          f"candidate_top_k={agg['top_k']}")
    print("汇总: "
          f"top1={agg['top1']:.4f}  MRR={agg['mrr']:.4f}  "
          f"hit@5={agg.get('hit@5', 0):.4f}  recall@5={agg.get('recall@5', 0):.4f}  "
          f"hit@10={agg.get('hit@10', 0):.4f}  recall@10={agg.get('recall@10', 0):.4f}  "
          f"avg_latency={agg.get('avg_latency_ms', 0):.1f} ms")
    print()

    if verbose:
        for s in result["scores"]:
            mark = "OK " if s.get(f"hit@{agg['primary_k']}") else "MISS"
            first = s["first_hit_rank"] or "-"
            print(f"  [{mark}] first={first:<3} top1={int(s['top1'])}  "
                  f"{s['id']:<28} {s['query']}")
        print()

    if result["misses"]:
        print("未命中：")
        for m in result["misses"]:
            print(f"  - {m['id']}: {m['query']}")
            print(f"    expected={m['expected']}")
            print(f"    got={m['ranked'][:5]}")
        print()


def _compare_legacy(agg: dict) -> list[str]:
    print("旧 22 条基线对照（P1/P8 基线 → 本次）：")
    regressions: list[str] = []
    for metric, base in LEGACY_BASELINE.items():
        now = float(agg.get(metric, 0.0))
        delta = now - base
        flag = ""
        if metric == "recall@5" and base - now > MAX_RECALL_DROP:
            flag = "  <-- 回退"
            regressions.append(metric)
        elif metric != "recall@5" and now < base:
            flag = "  (下降)"
        print(f"  {metric:<9} {base:.4f} -> {now:.4f}  (Δ{delta:+.4f}){flag}")
    if not regressions:
        print("  结论: recall@5 未出现超过 1 个绝对点的回退。")
    print()
    return regressions


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="固定查询集检索评测")
    ap.add_argument("--config", default=None, help="config.toml 路径")
    ap.add_argument("--queries", default=None,
                    help="自定义单个查询集（指定后忽略 --set）")
    ap.add_argument("--set", choices=["all", "legacy", "expanded"], default="all",
                    help="all=旧集与扩容集都跑（默认）")
    ap.add_argument("--top-k", type=int, default=5,
                    help="primary_k（top1/hit/recall 的主截断点，默认 5）")
    ap.add_argument("--mode", choices=["hybrid", "fts"], default="hybrid")
    ap.add_argument("--no-expand", action="store_true", help="关闭图谱扩展")
    ap.add_argument("--no-latency", action="store_true", help="不统计查询延迟")
    ap.add_argument("--no-warmup", action="store_true",
                    help="跳过预热（默认先跑一次以排除向量模型加载时间）")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--json-out", help="把 JSON 结果写到文件（UTF-8）")
    ap.add_argument("-v", "--verbose", action="store_true", help="逐条输出排名")
    args = ap.parse_args(argv)

    if args.top_k <= 0:
        ap.error("--top-k 必须是正整数")

    if args.queries:
        sets = {"custom": (Path(args.queries), load_queries(args.queries))}
    elif args.set == "legacy":
        sets = {"legacy": (LEGACY_FILE, load_queries(LEGACY_FILE))}
    elif args.set == "expanded":
        sets = {"expanded": (EXPANDED_FILE, load_queries(EXPANDED_FILE))}
    else:
        sets = {
            "legacy": (LEGACY_FILE, load_queries(LEGACY_FILE)),
            "expanded": (EXPANDED_FILE, load_queries(EXPANDED_FILE)),
        }

    kb = KB(Config.load(args.config))
    search = build_search(kb, args.mode, not args.no_expand)

    if not args.no_warmup:
        # 预热一次，避免首次加载 ONNX 嵌入模型把平均延迟拉高。
        first = next(iter(sets.values()))[1][0]
        try:
            search(first.query, top_k=1)
        except Exception:  # noqa: BLE001  # 预热失败不应改变正式评测结果
            pass

    ks = tuple(sorted({args.top_k, 10}))
    results: dict[str, dict] = {}
    missing_all: list[str] = []
    for name, (path, cases) in sets.items():
        missing = _check_expected(cases, kb)
        missing_all.extend(missing)
        if missing and not args.json:
            print(f"警告：{name} 中以下 expected 路径不存在：")
            for m in missing:
                print("  " + m)
            print()

        result = evaluate_at_ks(
            cases, search, ks=ks, primary_k=args.top_k,
            measure_latency=not args.no_latency,
        )
        result["mode"] = args.mode
        result["queries_file"] = str(path)
        result["set"] = name
        if missing:
            result["missing_expected"] = missing
        results[name] = result

    regressions: list[str] = []
    payload: dict = {
        "mode": args.mode,
        "sets": results,
        "baseline_legacy": LEGACY_BASELINE,
    }
    if "legacy" in results:
        regressions = [
            metric for metric, base in LEGACY_BASELINE.items()
            if metric == "recall@5"
            and base - float(results["legacy"]["aggregate"].get(metric, 0)) > MAX_RECALL_DROP
        ]
        payload["regressions"] = regressions
    if missing_all:
        payload["missing_expected"] = missing_all
    primary_name = "legacy" if "legacy" in results else next(iter(results))
    payload["aggregate"] = results[primary_name]["aggregate"]
    payload["queries_file"] = results[primary_name]["queries_file"]
    payload["set"] = primary_name

    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 2 if regressions else 0

    for name, result in results.items():
        _print_summary(name, result["queries_file"], result, args.verbose)
        if name == "legacy":
            _compare_legacy(result["aggregate"])

    return 2 if regressions else 0


if __name__ == "__main__":
    raise SystemExit(main())
