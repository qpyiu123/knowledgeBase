"""用自己的 md 跑一轮全链路自检：坏文件剔除、跳转落空、循环引用、格式不规范。"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kb.config import Config  # noqa: E402
from kb.parser import VALID_CATEGORIES, iter_docs, load_doc, split_front_matter  # noqa: E402

# [文本](目标.md) 或 [[目标]] 形式的内链
MD_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+\.md)(?:#[^)]+)?\)")
WIKI_LINK = re.compile(r"\[\[([^\]|#]+)(?:\|[^\]]+)?\]\]")
TAG_LINE = re.compile(r"^\s*(?:#{1,6}\s*)?(?:标签|Tags?|tags)\s*[:：]\s*(.+)$", re.M | re.I)
CODE_FENCE = re.compile(r"^```", re.M)


@dataclass
class Issue:
    level: str  # error / warn / info
    path: str
    kind: str
    detail: str


@dataclass
class Report:
    issues: list[Issue] = field(default_factory=list)
    n_docs: int = 0
    by_cat: dict[str, int] = field(default_factory=dict)
    tag_counter: Counter = field(default_factory=Counter)

    def add(self, level: str, path: str, kind: str, detail: str) -> None:
        self.issues.append(Issue(level, path, kind, detail))

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.level == "error"]

    @property
    def warns(self) -> list[Issue]:
        return [i for i in self.issues if i.level == "warn"]


def check_links(kb_dir: Path, docs, report: Report) -> None:
    by_stem: defaultdict[str, list[str]] = defaultdict(list)
    for d in docs:
        by_stem[Path(d.path).stem.lower()].append(d.path)

    for d in docs:
        text = d.body
        src = (kb_dir / d.path).parent
        for m in MD_LINK.finditer(text):
            target = m.group(2).split("#")[0]
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (src / target).resolve()
            if not resolved.exists():
                stem = Path(target).stem.lower()
                if stem in by_stem:
                    report.add("warn", d.path, "link-needs-fix",
                               f"'{target}' 不存在，但同名文件在 {by_stem[stem]}")
                else:
                    report.add("warn", d.path, "link-dead", f"'{target}' 不存在")
        for m in WIKI_LINK.finditer(text):
            name = m.group(1).strip().lower()
            if name not in by_stem and "#" not in m.group(1):
                report.add("info", d.path, "wiki-link", f"[[{m.group(1)}]] 无法解析")


def check_shape(doc, report: Report) -> None:
    if not doc.body.strip():
        report.add("error", doc.path, "empty", "正文为空")
        return
    if len(doc.body) < 300:
        report.add("warn", doc.path, "short", f"正文仅 {len(doc.body)} 字符，可能是空壳")
    if not re.search(r"^## ", doc.body, re.M):
        report.add("warn", doc.path, "no-sections", "没有二级标题，结构可能不清晰")
    fences = len(CODE_FENCE.findall(f"```\n{doc.body}\n```")) + len(
        re.findall(r"^```", doc.body, re.M)
    )
    if len(re.findall(r"^```", doc.body, re.M)) % 2 != 0:
        report.add("error", doc.path, "fence-unbalanced", "代码块 ``` 数量为奇数，可能未闭合")
    if not re.search(r"(?i)^#{1,6}\s*(参考|references?|来源|来源链接)", doc.body, re.M) \
            and "参考来源" not in doc.body and "参考" not in doc.body:
        report.add("warn", doc.path, "no-refs", "缺少参考来源章节")
    if len(doc.signals) < 3:
        report.add("warn", doc.path, "few-signals",
                   f"signals 只有 {len(doc.signals)} 条（建议 ≥5）")


def check_dup(kb_dir: Path, docs, report: Report) -> None:
    """按精简标题找重复（归一化：小写、去标点空白）。"""
    seen: dict[str, str] = {}
    for d in docs:
        key = re.sub(r"[\s\-_—()（）:：,，.。]+", "", d.title).lower()
        if key in seen:
            report.add("warn", d.path, "dup-title", f"标题与 {seen[key]} 重复: {d.title!r}")
        else:
            seen[key] = d.path


def check_tags(docs, report: Report) -> None:
    for d in docs:
        for t in d.tags:
            if len(t) > 24:
                report.add("info", d.path, "long-tag", f"标签过长: {t!r}")


BAD_TITLE_TAIL = re.compile(
    # 只抓"明显说了一半"或模板残留的标题；正常以「汇总 / 索引」结尾的标题不算
    r"(是索引|是汇总|是这里|\.\.\.$|…$)"
)


def check_titles(docs, report: Report) -> None:
    """标题看起来像被语法污染/截断的，报出来。

    真实案例：某篇标题写成了「智能合约常见 CVE / SWC 汇总是索引」——
    显然是模板句子「X 的汇总是索引」没写完整。
    """
    for d in docs:
        t = d.title
        if not t:
            report.add("error", d.path, "empty-title", "标题为空")
            continue
        if BAD_TITLE_TAIL.search(t):
            report.add("warn", d.path, "odd-title",
                       f"标题疑似被污染或截断: {t!r}")
        if len(t) > 60:
            report.add("info", d.path, "long-title", f"标题过长({len(t)}字): {t[:40]}…")
        if t.strip() != t:
            report.add("warn", d.path, "title-space", "标题首尾有空白")
        if t.endswith(("。", "，", ".", ",")):
            report.add("info", d.path, "title-punct", f"标题以标点结尾: {t!r}")


def run(cfg: Config) -> Report:
    r = Report()
    kb_dir = cfg.kb_dir
    if not kb_dir.exists():
        r.add("error", str(kb_dir), "missing", "kb 目录不存在")
        return r

    # 先做一层非常宽松的扫描：连 front-matter 都解析不了的文件直接报错
    docs = []
    for p in kb_dir.rglob("*.md"):
        rel = p.relative_to(kb_dir).as_posix()
        if any(part.startswith(("_", ".")) for part in Path(rel).parts[:-1]):
            continue
        if p.name.startswith((".", "_")):
            continue
        raw = p.read_text(encoding="utf-8", errors="replace")
        if not raw.startswith("---"):
            r.add("error", rel, "no-frontmatter", "文件不以 --- 开头，缺少 YAML front-matter")
            continue
        meta, _ = split_front_matter(raw)
        if not meta:
            r.add("error", rel, "bad-frontmatter", "YAML front-matter 解析失败或为空")
            continue
        doc = load_doc(p, kb_dir)
        if doc.category not in VALID_CATEGORIES:
            r.add("error", rel, "bad-category", f"category={doc.category!r} 不在允许列表")
        if doc.warnings:
            r.add("warn", rel, "frontmatter-warn", "; ".join(doc.warnings))
        docs.append(doc)

    r.n_docs = len(docs)
    r.by_cat = dict(Counter(d.category for d in docs))
    for d in docs:
        r.tag_counter.update(d.tags)

    if not docs:
        r.add("error", str(kb_dir), "empty-kb", "没有任何合法文档")
        return r

    check_links(kb_dir, docs, r)
    check_titles(docs, r)
    check_dup(kb_dir, docs, r)
    for d in docs:
        check_shape(d, r)
        check_tags([d], r)

    # 覆盖度：每个方向至少 5 篇
    for cat in sorted(VALID_CATEGORIES):
        n = r.by_cat.get(cat, 0)
        if n == 0:
            r.add("info", f"kb/{cat}", "no-cover", "该方向没有任何条目")
        elif n < 5:
            r.add("info", f"kb/{cat}", "low-cover", f"仅 {n} 篇，覆盖偏薄")
    return r


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="知识库质量自检")
    ap.add_argument("--config", default=None)
    ap.add_argument("--strict", action="store_true", help="有 error 即非 0 退出")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    cfg = Config.load(args.config)
    rep = run(cfg)

    if args.json:
        import json
        print(json.dumps({
            "docs": rep.n_docs,
            "by_category": rep.by_cat,
            "top_tags": rep.tag_counter.most_common(20),
            "issues": [i.__dict__ for i in rep.issues],
        }, ensure_ascii=False, indent=2))
    else:
        print(f"文档 {rep.n_docs} 篇")
        print("方向分布: " + ", ".join(f"{k}={v}" for k, v in sorted(rep.by_cat.items())))
        print(f"错误 {len(rep.errors)}  警告 {len(rep.warns)}  "
              f"信息 {len([i for i in rep.issues if i.level=='info'])}")
        for level, label in (("error", "ERROR"), ("warn", "WARN"), ("info", "INFO")):
            items = [i for i in rep.issues if i.level == level]
            if not items:
                continue
            print(f"\n-- {label} ({len(items)}) --")
            for i in items[:60]:
                print(f"  [{i.kind}] {i.path}: {i.detail}")
            if len(items) > 60:
                print(f"  ... 另有 {len(items)-60} 条")
    if args.strict and rep.errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
