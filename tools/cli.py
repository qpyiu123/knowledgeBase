#!/usr/bin/env python
"""CTF 知识库命令行入口。

用法速查：
    kb index                    重建索引（FTS + 向量）
    kb search "n相同 e不同"      模糊检索
    kb ask "附件是 pyc 有花指令"  检索 + 本地模型作答
    kb show crypto/xxx.md       查看一条
    kb cat crypto               列出一个方向全部条目
    kb doctor                   环境自检
    kb bench                    测一次推理速度
    kb lint                     校验所有 md 的 front-matter
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

# 让 stdout/stderr 一律走 UTF-8（否则重定向到文件时中文变乱码、进度条刷不出来）
os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

# 让 `python tools/cli.py` 与 `python -m tools.cli` 都能直接跑
sys.path.insert(0, str(Path(__file__).resolve().parent))

from kb.config import Config  # noqa: E402
from kb.fts import FtsIndex  # noqa: E402
from kb.fusion import FusedHit  # noqa: E402
from kb.llm import LLMError  # noqa: E402
from kb.parser import VALID_CATEGORIES, iter_docs, load_doc, split_front_matter  # noqa: E402
from kb.rag import KB  # noqa: E402

# Windows 控制台中文 + ANSI
if os.name == "nt":
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    except Exception:
        pass
    os.system("")


class C:
    G = "\033[32m"; Y = "\033[33m"; B = "\033[36m"; M = "\033[35m"
    R = "\033[31m"; DIM = "\033[2m"; BOLD = "\033[1m"; END = "\033[0m"

    @classmethod
    def strip(cls) -> None:
        for k in ("G", "Y", "B", "M", "R", "DIM", "BOLD", "END"):
            setattr(cls, k, "")


def _fmt_hits(hits: list[FusedHit], cfg: Config, verbose: bool = False) -> str:
    if not hits:
        return f"{C.Y}没有命中。试试更短的关键词，或先运行 kb index。{C.END}"
    out = []
    for i, h in enumerate(hits, 1):
        src = "+".join(h.sources)
        head = (
            f"{C.BOLD}{i:>2}. {h.title}{C.END}  "
            f"{C.M}[{h.category}]{C.END} "
            f"{C.DIM}score={h.score:.4f} via={src}{C.END}"
        )
        out.append(head)
        out.append(f"    {C.DIM}{h.doc_path}{C.END}")
        if verbose and h.best_text:
            snippet = " ".join(h.best_text.split())[:220]
            out.append(f"    {snippet}")
    return "\n".join(out)


# ---------------------------------------------------------------- commands
def cmd_index(cfg: Config, args) -> int:
    from kb.reindex import ReindexError, run_reindex

    cfg.ensure_dirs()
    stage_labels = {"scan": "扫描", "fts": "FTS", "vectors": "向量",
                    "manifest": "manifest", "swap": "切换"}
    chunk_chars = int(cfg.get("search", "chunk_chars", 900))
    overlap = int(cfg.get("search", "chunk_overlap", 120))

    print(f"{C.B}== 重建索引（FTS + 向量增量）=={C.END}")
    last = {"stage": ""}

    def progress(stage: str, i: int, n: int) -> None:
        if stage == "fts":
            if last["stage"] != "fts":
                print(f"{C.B}== 建 FTS 索引 =={C.END}")
                last["stage"] = "fts"
            if i == n or i % 200 == 0:
                print(f"\r  {i}/{n} 篇...", end="", flush=True)

    try:
        res = run_reindex(
            cfg, chunk_chars=chunk_chars, overlap=overlap,
            fts_only=bool(getattr(args, "fts_only", False)),
            on_progress=progress,
        )
    except ReindexError as e:
        label = stage_labels.get(e.stage, e.stage)
        print(f"\n{C.R}索引失败（阶段: {label}）{C.END}: {e.message}")
        print(f"{C.Y}已删除临时文件并回滚，旧索引保持不变。{C.END}")
        print(f"\n{C.R}失败回滚{C.END}  阶段={label}  reused=0, reencoded=0")
        return 1

    skipped = res.get("skipped") or []

    def skipped_tail() -> str:
        if not skipped:
            return ""
        names = ", ".join(str(it["path"]) for it in skipped[:5])
        if len(skipped) > 5:
            names += "…"
        print(f"{C.Y}警告：跳过 {len(skipped)} 个不可读文件（保持旧哈希）{C.END}",
              file=sys.stderr)
        for it in skipped[:20]:
            print(f"  {it['path']}: {it['error']}", file=sys.stderr)
        return f"（跳过 {len(skipped)} 个不可读文件: {names}）"

    if res["status"] == "fts_only":
        tail = skipped_tail()
        print(f"\n{C.Y}警告：仅 FTS 更新，向量索引停留在旧时间。{C.END}")
        print(f"{C.DIM}可稍后在嵌入模型可用时重新运行 kb index 补齐向量。{C.END}")
        print(f"\n{C.Y}仅 FTS{C.END}  docs={res['docs']}, chunks={res['chunks']}, "
              f"reused=0, reencoded=0, {res['seconds']}s{tail}")
        return 0

    tail = skipped_tail()
    print(f"\n{C.G}完整增量更新{C.END}  docs={res['docs']}, chunks={res['chunks']}, "
          f"reused={res['reused']}, reencoded={res['reencoded']}, "
          f"removed_chunks={res['removed_chunks']}, {res['seconds']}s{tail}")
    print(f"{C.DIM}新增 {res['added_docs']} 篇 / 修改 {res['changed_docs']} 篇 / "
          f"删除 {res['removed_docs']} 篇；manifest: {cfg.index_dir / 'manifest.json'}{C.END}")
    return 0


def cmd_hint(cfg: Config, args) -> int:
    """没思路时：侦察附件 + 给方向建议。"""
    from agent.hint import hint_for

    kb = KB(cfg) if not args.no_kb else None
    targets = args.paths
    if not targets:
        # 不给路径就自动找 work/attachments 下的所有文件
        d = cfg.kb_dir.parent / "work" / "attachments"
        if d.is_dir():
            targets = [str(p) for p in sorted(d.iterdir()) if p.is_file()][:5]
        if not targets:
            print("没有指定附件，也没找到 work/attachments/")
            return 2

    rc = 0
    for t in targets:
        r = hint_for(t, question=args.question or "", kb=kb)
        if args.json:
            print(json.dumps(r.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(f"{C.B}== {t} =={C.END}")
            if r.model:
                print(f"{C.DIM}模型 {r.model}  {r.tok_s:.1f} tok/s{C.END}\n")
            print(r.render())
            print()
        if not r.hints:
            rc = 1
    return rc

def cmd_graph(cfg: Config, args) -> int:
    from kb.graph import BOOSTING, RELATION_KINDS, Graph
    from kb.parser import iter_docs

    if args.build or not (cfg.index_dir / "graph.db").exists():
        docs = list(iter_docs(cfg.kb_dir))
        g = Graph(cfg.index_dir / "graph.db")
        res = g.rebuild(docs)
        print(f"图谱已建立: {res['nodes']} 节点, {res['edges']} 边")
        if res["unresolved_count"]:
            print(f"未能解析 {res['unresolved_count']} 处:")
            for u in res["unresolved"][:10]:
                print("  ", u)
        g.close()

    if args.expand:
        kb = KB(cfg)
        d = kb.expand(args.expand, hops=args.hops)
        print(f"\n扩展: {args.expand} (hops={args.hops})")
        print(f"  节点 {len(d.get('nodes', []))}, 截断={d.get('truncated')}, "
              f"{d.get('elapsed_ms')}ms")
        for n in d.get("nodes", []):
            tag = "关联" if n["via"] in BOOSTING else "对照"
            print(f"  [{tag}:{n['via']}] hop={n['hop']}  {n['key']}")
        return 0

    g = Graph(cfg.index_dir / "graph.db")
    st = g.stats()
    print(f"节点: {st['nodes']}   边: {st['edges']}   跨方向: {st['cross_category']}")
    for k, v in st["by_kind"].items():
        mark = "提升" if k in BOOSTING else "仅对照"
        print(f"  {k:<16} {v:>4}  [{mark}]")
    g.close()
    return 0

def cmd_search(cfg: Config, args) -> int:
    kb = KB(cfg)
    t0 = time.time()
    if args.vec_only:
        hits = kb.vec.search(args.query, top_k=args.top_k, category=args.category)
        from kb.fusion import FusedHit
        fused = [FusedHit(doc_path=h["doc_path"], title=h["title"], category=h["category"],
                          score=h["score"], sources=["vec"], best_text=h.get("text", ""))
                 for h in hits]
    elif args.fts_only:
        raw = kb.fts.search(args.query, top_k=args.top_k, category=args.category, mode=args.mode)
        from kb.fusion import fuse_single_source
        fused = fuse_single_source(raw, args.top_k)
    else:
        fused = kb.search(args.query, top_k=args.top_k, category=args.category, mode=args.mode)
    dt = (time.time() - t0) * 1000

    if args.json:
        out = {
            "query": args.query, "ms": round(dt, 1),
            "hits": [h.as_dict() for h in fused],
        }
        # 附带图谱信息，方便排查"这条是怎么被找出来的"
        gv = [(h.doc_path, getattr(h, "graph_via", None))
              for h in fused if getattr(h, "graph_via", None)]
        if gv:
            out["graph_edges"] = [{"path": p, "via": v} for p, v in gv]
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(f"{C.DIM}查询: {args.query}  ({dt:.0f} ms){C.END}\n")
        print(_fmt_hits(fused, cfg, verbose=args.verbose))
        gh = [(h, getattr(h, "graph_via", None)) for h in fused
              if getattr(h, "graph_via", None)]
        if gh:
            print(f"\n{C.DIM}── 图谱关联 ──{C.END}")
            for h, via in gh:
                mode = "关联" if getattr(h, "graph_boost", False) else "对照"
                print(f"  [{mode}:{via}] {h.doc_path}")
    return 0 if fused else 2


def cmd_ask(cfg: Config, args) -> int:
    kb = KB(cfg)
    try:
        if args.stream:
            hits, gen = kb.ask_stream(args.question, top_k=args.top_k,
                                      category=args.category,
                                      force_backend=args.backend)
            print(_fmt_hits(hits, cfg))
            print(f"\n{C.B}== 作答 =={C.END}\n")
            buf = []
            for piece in gen:
                buf.append(piece)
                sys.stdout.write(piece)
                sys.stdout.flush()
            print()
            return 0 if "".join(buf).strip() else 1
        ans = kb.ask(args.question, top_k=args.top_k, category=args.category,
                     force_backend=args.backend)
    except LLMError as e:
        print(f"{C.R}模型不可用{C.END}: {e}", file=sys.stderr)
        print(f"{C.DIM}已保留检索结果，见下方（用 kb search 单独查）{C.END}\n", file=sys.stderr)
        hits = kb.search(args.question, top_k=args.top_k, category=args.category)
        print(_fmt_hits(hits, cfg))
        return 3

    if args.json:
        print(json.dumps({
            "question": args.question,
            "answer": ans.answer,
            "backend": ans.backend,
            "model": ans.model,
            "stats": ans.stats,
            "hits": [h.as_dict() for h in ans.hits],
        }, ensure_ascii=False, indent=2))
        return 0

    print(_fmt_hits(ans.hits, cfg))
    print(f"\n{C.B}== 作答 ({ans.backend}/{Path(ans.model).name}) =={C.END}\n")
    print(ans.answer)
    s = ans.stats
    if s:
        print(f"\n{C.DIM}-- prompt={s.get('prompt_tokens')} tok, "
              f"gen={s.get('completion_tokens')} tok, {s.get('seconds')}s "
              f"({s.get('tokens_per_sec')} tok/s){C.END}")
    return 0


def cmd_show(cfg: Config, args) -> int:
    p = args.path
    cand = cfg.kb_dir / p
    if not cand.exists():
        # 允许只给文件名片段
        matches = [d for d in iter_docs(cfg.kb_dir) if p.lower() in d.path.lower()]
        if not matches:
            print(f"{C.R}找不到: {p}{C.END}")
            return 1
        if len(matches) > 1:
            print(f"{C.Y}匹配到多条，请更精确：{C.END}")
            for m in matches[:20]:
                print("  " + m.path)
            return 2
        cand = cfg.kb_dir / matches[0].path
    print(cand.read_text(encoding="utf-8", errors="replace"))
    return 0


def cmd_cat(cfg: Config, args) -> int:
    """列出一个方向的全部条目（title + path）。"""
    docs = [d for d in iter_docs(cfg.kb_dir) if not args.category or d.category == args.category]
    if not docs:
        print(f"{C.Y}没有条目{C.END}")
        return 1
    by_cat: dict[str, list] = {}
    for d in docs:
        by_cat.setdefault(d.category, []).append(d)
    for cat in sorted(by_cat):
        items = by_cat[cat]
        print(f"\n{C.BOLD}{C.M}== {cat} ({len(items)}) =={C.END}")
        for d in sorted(items, key=lambda x: x.title):
            diff = d.difficulty[:1].upper() if d.difficulty else "-"
            print(f"  {C.Y}{diff}{C.END} {d.title:<38} {C.DIM}{d.path}{C.END}")
    print(f"\n{C.DIM}共 {len(docs)} 条{C.END}")
    return 0


def cmd_doctor(cfg: Config, args) -> int:
    ok, warn = f"{C.G}OK{C.END}", f"{C.Y}WARN{C.END}"
    bad = f"{C.R}FAIL{C.END}"
    print(f"{C.BOLD}CTF 知识库自检{C.END}  根目录: {cfg.kb_root}\n")

    # Python
    print(f"[{ok}] Python {sys.version.split()[0]}  ({sys.executable})")

    # KB
    docs = list(iter_docs(cfg.kb_dir))
    cats: dict[str, int] = {}
    for d in docs:
        cats[d.category] = cats.get(d.category, 0) + 1
    if docs:
        print(f"[{ok}] 知识库 {len(docs)} 篇  " + ", ".join(f"{k}={v}" for k, v in sorted(cats.items())))
    else:
        print(f"[{bad}] 知识库为空: {cfg.kb_dir}")

    # FTS
    st = FtsIndex(cfg.index_dir / "fts.db").stats()
    if st["docs"]:
        print(f"[{ok}] FTS 索引 {st['docs']} 篇/{st['chunks']} 块  建于 {st['built_at']}")
    else:
        print(f"[{warn}] FTS 索引未建立（运行 kb index）")

    # 向量
    kb = KB(cfg)
    if not kb.embedder.available:
        print(f"[{warn}] 嵌入模型缺失: {kb.embedder.last_error}")
    else:
        vs = kb.vec.stats()
        if vs.get("enabled"):
            print(f"[{ok}] 向量索引 {vs.get('count')} 块 dim={vs.get('dim')} "
                  f"backend={vs.get('backend')} 嵌入={kb.embedder.backend}")
        else:
            print(f"[{warn}] 嵌入模型就绪但向量索引未建（运行 kb index）")

    # LLM
    backend = str(cfg.get("llm", "backend"))
    print(f"[{C.DIM}..{C.END}] LLM backend = {backend}")
    try:
        from kb.llm import get_backend
        be = get_backend(cfg)
        if be is None:
            print(f"[{C.DIM}..{C.END}] 未启用模型（仅检索）")
        else:
            ok2, msg = be.health()
            print(f"[{ok if ok2 else bad}] {be.name}: {msg}")
    except Exception as e:  # noqa: BLE001
        print(f"[{bad}] {e}")

    # GPU
    try:
        import subprocess
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,memory.used", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=10,
        )
        print(f"[{ok}] GPU: {r.stdout.strip()}")
    except Exception as e:
        print(f"[{C.DIM}..{C.END}] nvidia-smi 不可用: {e}")
    return 0


def cmd_bench(cfg: Config, args) -> int:
    kb = KB(cfg)
    be = kb.backend(args.backend)
    if be is None:
        print(f"{C.R}未启用后端{C.END}")
        return 1
    prompt = [{"role": "user", "content": "用一句话解释 RSA 共模攻击的原理。"}]
    print(f"{C.B}加载模型并生成 64 tokens...{C.END}")
    t0 = time.time()
    res = be.chat(prompt, max_tokens=args.max_tokens, temperature=0.1)
    print(f"首次(含加载) {time.time()-t0:.1f}s")
    print(f"{C.G}{res.tokens_per_sec} tok/s{C.END}  "
          f"(prompt={res.prompt_tokens}, gen={res.completion_tokens}, {res.seconds}s)")
    print(f"\n{res.text[:400]}")
    return 0


def cmd_lint(cfg: Config, args) -> int:
    problems = 0
    docs = list(iter_docs(cfg.kb_dir))
    seen: dict[str, str] = {}
    for d in docs:
        if d.path in seen:
            print(f"{C.R}[重复]{C.END} {d.path}")
            problems += 1
        if d.warnings:
            print(f"{C.Y}[{d.path}]{C.END} " + "; ".join(d.warnings))
            problems += 1
        if not d.signals:
            print(f"{C.Y}[缺 signals]{C.END} {d.path}")
            problems += 1
        if not d.title or d.title == Path(d.path).stem:
            print(f"{C.DIM}[无 title]{C.END} {d.path}")
    print(f"\n检查 {len(docs)} 篇，问题 {problems} 个")
    return 0 if problems == 0 else 1


def cmd_stats(cfg: Config, args) -> int:
    st = FtsIndex(cfg.index_dir / "fts.db").stats()
    print(json.dumps(st, ensure_ascii=False, indent=2))
    return 0


# ---------------------------------------------------------------- main
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="kb", description="CTF 知识库：模糊检索 + 本地模型作答")
    p.add_argument("--config", help="config.toml 路径", default=None)
    p.add_argument("--no-color", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("index", help="重建索引（增量向量编码）")
    s.add_argument("--fts-only", action="store_true",
                   help="只刷新 FTS；向量索引保持旧状态，会打印警告")
    s.set_defaults(func=cmd_index)

    s = sub.add_parser("search", help="模糊检索")
    s.add_argument("query")
    s.add_argument("-k", "--top-k", type=int, default=None)
    s.add_argument("-c", "--category", choices=sorted(VALID_CATEGORIES))
    s.add_argument("--mode", choices=["or", "and"], default="or", help="or=宽松(默认) and=严格")
    s.add_argument("--fts-only", action="store_true")
    s.add_argument("--vec-only", action="store_true")
    s.add_argument("-v", "--verbose", action="store_true", help="显示摘要片段")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_search)

    s = sub.add_parser("ask", help="检索 + 模型作答")
    s.add_argument("question")
    s.add_argument("-k", "--top-k", type=int, default=None)
    s.add_argument("-c", "--category", choices=sorted(VALID_CATEGORIES))
    s.add_argument("--backend", choices=["llama_cpp", "ollama", "none"])
    s.add_argument("--stream", action="store_true")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_ask)

    s = sub.add_parser("show", help="查看条目")
    s.add_argument("path")
    s.set_defaults(func=cmd_show)

    s = sub.add_parser("cat", help="列出条目")
    s.add_argument("category", nargs="?", choices=sorted(VALID_CATEGORIES))
    s.set_defaults(func=cmd_cat)

    s = sub.add_parser("doctor", help="环境自检")
    s.set_defaults(func=cmd_doctor)

    s = sub.add_parser("bench", help="推理速度测试")
    s.add_argument("--backend", choices=["llama_cpp", "ollama"])
    s.add_argument("--max-tokens", type=int, default=64)
    s.set_defaults(func=cmd_bench)

    s = sub.add_parser("lint", help="校验所有 md")
    s.set_defaults(func=cmd_lint)

    s = sub.add_parser("hint", help="没思路时：侦察附件并给出探索方向")
    s.add_argument("paths", nargs="*", help="附件路径（留空则自动扫 work/attachments）")
    s.add_argument("-q", "--question", help="题面描述（可选）")
    s.add_argument("--no-kb", action="store_true", help="不查知识库，只用模型")
    s.add_argument("--json", action="store_true", help="输出 JSON")
    s.set_defaults(func=cmd_hint)

    s = sub.add_parser("graph", help="知识图谱：建图/统计/扩展")
    s.add_argument("--build", action="store_true", help="重建图谱")
    s.add_argument("--expand", nargs="+", metavar="PATH", help="从若干文档出发扩展")
    s.add_argument("--hops", type=int, default=1, help="扩展跳数")
    s.set_defaults(func=cmd_graph)

    s = sub.add_parser("stats", help="索引统计")
    s.set_defaults(func=cmd_stats)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.no_color or not sys.stdout.isatty():
        C.strip()
    cfg = Config.load(args.config)
    try:
        return int(args.func(cfg, args) or 0)
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
