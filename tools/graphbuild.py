"""知识图谱构建工具：从 kb 的 front-matter 建图，或做关系质量检查。

用法：
  python tools/graphbuild.py            # 建图并打印统计
  python tools/graphbuild.py --check    # 只检查关系，不写库
  python tools/graphbuild.py --suggest  # 基于标签重叠，建议可能的关联
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout.reconfigure(encoding="utf-8")

from kb.config import Config
from kb.graph import BOOSTING, RELATION_KINDS, Graph
from kb.parser import iter_docs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只检查，不写库")
    ap.add_argument("--suggest", action="store_true", help="给出关联建议")
    args = ap.parse_args()

    cfg = Config.load()
    docs = list(iter_docs(cfg.kb_dir))
    print(f"文档: {len(docs)} 篇")

    # ---- 统计现有关系 ----
    kind_count: Counter = Counter()
    with_rel = 0
    for d in docs:
        r = d.relations()
        if r:
            with_rel += 1
        for k, v in r.items():
            kind_count[k] += len(v)
    print(f"已有关系字段的文档: {with_rel}/{len(docs)} "
          f"({with_rel/len(docs):.0%})")
    if kind_count:
        print("关系统计:")
        for k, c in kind_count.most_common():
            doc = RELATION_KINDS.get(k, {}).get("doc", "")
            boost = "提升" if k in BOOSTING else "仅对照"
            print(f"  {k:<16} {c:>4} 条  [{boost}]  {doc}")
    else:
        print("  （暂无任何关系字段）")

    if args.check:
        # 检查指向不存在的目标
        known = {d.path for d in docs}
        titles = {d.title for d in docs}
        bad = []
        for d in docs:
            for k, targets in d.relations().items():
                for t in targets:
                    if t in known or t in titles:
                        continue
                    if any(p.rsplit("/", 1)[-1].replace(".md", "") == t for p in known):
                        continue
                    bad.append((d.path, k, t))
        if bad:
            print(f"\n无法解析的关系目标 {len(bad)} 处:")
            for p, k, t in bad[:20]:
                print(f"  {p}  -{k}->  {t}")
        else:
            print("\n所有关系目标都能解析。")
        return 0

    if args.suggest:
        suggest(docs)
        return 0

    # ---- 建图 ----
    g = Graph(cfg.index_dir / "graph.db")
    res = g.rebuild(docs)
    print(f"\n图谱已建立: {res['nodes']} 个节点, {res['edges']} 条边")
    if res["unresolved_count"]:
        print(f"未能解析的目标 {res['unresolved_count']} 处:")
        for u in res["unresolved"][:10]:
            print(f"  {u}")
    st = g.stats()
    print(f"跨方向边: {st['cross_category']} 条")
    g.close()
    return 0


def suggest(docs) -> None:
    """基于标签共现给出关联建议（仅供人工确认，不自动写回）。"""
    by_tag: dict[str, list[str]] = defaultdict(list)
    for d in docs:
        for t in d.tags:
            by_tag[t.lower()].append(d.path)

    pairs: Counter = Counter()
    for tag, paths in by_tag.items():
        if len(paths) < 2 or len(paths) > 12:
            continue
        for i in range(len(paths)):
            for j in range(i + 1, len(paths)):
                a, b = sorted((paths[i], paths[j]))
                if a.split("/")[0] == b.split("/")[0]:
                    continue        # 同方向的不算跨方向
                pairs[(a, b, tag)] += 1

    print(f"\n跨方向标签共现 Top 20（候选 relates_to，需人工确认）:")
    for (a, b, tag), _ in pairs.most_common(20):
        print(f"  [{tag}]  {a}\n           {b}")


if __name__ == "__main__":
    raise SystemExit(main())
