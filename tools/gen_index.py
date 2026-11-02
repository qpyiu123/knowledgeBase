"""为知识库生成 `_index.md` 导航页：按方向分类，附识别信号速查。"""
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kb.config import Config  # noqa: E402
from kb.parser import iter_md_paths, load_doc  # noqa: E402

CAT_TITLES = {
    "misc": "杂项 Misc",
    "crypto": "密码学 Crypto",
    "reverse": "逆向 Reverse",
    "pwn": "二进制利用 Pwn",
    "web": "Web",
    "forensics": "取证 Forensics",
    "mobile": "移动端 Mobile",
    "blockchain": "区块链 Blockchain",
    "hardware": "硬件 Hardware",
    "osint": "情报 OSINT",
    "ai": "AI 安全",
}
DIFF_ORDER = {"easy": 0, "medium": 1, "hard": 2, "": 3}


def build(cfg: Config) -> str:
    docs = []
    for path in iter_md_paths(cfg.kb_dir):
        try:
            docs.append(load_doc(path, cfg.kb_dir))
        except OSError as e:
            print(f"跳过不可读文件: {path} ({e})", file=sys.stderr)
    by_cat: dict[str, list] = defaultdict(list)
    signals: defaultdict[str, list[str]] = defaultdict(list)
    for d in docs:
        by_cat[d.category].append(d)
        for s in d.signals:
            signals[s].append(d.title)

    lines = [
        "# CTF 知识库索引",
        "",
        f"共 **{len(docs)}** 条，覆盖 **{len(by_cat)}** 个方向。",
        "本文件由 `python tools/gen_index.py` 自动生成，请勿手改。",
        "",
        "> 用法：`kb search \"题面关键词\"` 模糊查；`kb ask \"题目描述\"` 让本地模型给思路。",
        "",
        "## 方向总览",
        "",
        "| 方向 | 条目数 | 说明 |",
        "|---|---|---|",
    ]
    for cat in CAT_TITLES:
        if cat in by_cat:
            lines.append(f"| [{CAT_TITLES[cat]}](#{cat}) | {len(by_cat[cat])} | |")
    lines.append("")

    for cat, title in CAT_TITLES.items():
        items = by_cat.get(cat)
        if not items:
            continue
        lines += [f'<a id="{cat}"></a>', f"## {title} ({len(items)})", ""]
        items.sort(key=lambda d: (DIFF_ORDER.get(d.difficulty, 3), d.title))
        for d in items:
            diff = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}.get(d.difficulty, "⚪")
            link = d.path[:-3] + ".md"
            sig = "、".join(d.signals[:4])
            extra = f" — _{sig}_" if sig else ""
            lines.append(f"- {diff} [{d.title}]({link}){extra}")
        lines.append("")

    # 识别信号速查表（做题时最常用的入口）
    lines += ["## 识别信号速查", "", "看到题面里出现这些词，直接去对应条目：", ""]
    hot = sorted(signals.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    for sig, titles in hot[:200]:
        if len(sig) < 2:
            continue
        lines.append(f"- **{sig}** → " + "、".join(sorted(set(titles))[:4]))
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    cfg = Config.load()
    cfg.ensure_dirs()
    out = cfg.kb_dir / "_index.md"
    text = build(cfg)
    out.write_text(text, encoding="utf-8")
    print(f"已生成 {out}  ({len(text.splitlines())} 行)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
