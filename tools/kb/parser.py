"""Markdown front-matter 解析、分块、中英文关键词抽取。"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import yaml

FM_RE = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n?", re.S)

VALID_CATEGORIES = {
    "misc", "crypto", "reverse", "pwn", "web",
    "forensics", "mobile", "blockchain", "hardware", "osint", "ai",
}


@dataclass
class Doc:
    path: str                 # 相对 kb_dir 的 POSIX 路径
    title: str
    category: str
    tags: list[str] = field(default_factory=list)
    signals: list[str] = field(default_factory=list)
    difficulty: str = ""
    source: str = ""
    tools: list[str] = field(default_factory=list)
    body: str = ""
    mtime: float = 0.0
    warnings: list[str] = field(default_factory=list)

    # ---- 跨方向图谱字段（借鉴 temp_newData 的知识图谱设计）----
    # 关系分级是核心：不能把"提过"当成"用过"，更不能当成"需要"。
    #   relates_to   → 弱关联，只用于扩大阅读面，不提升排名
    #   analogous_to → 类比，相似但不同，不传递适用性
    #   differs_from → 易混淆项，用于区分
    #   requires     → 前置条件，可以 ALL/ANY 组合
    #   uses_tool    → 确实用到某工具
    #   illustrated_by / illustrated   → 案例证据
    relates_to: list[str] = field(default_factory=list)
    analogous_to: list[str] = field(default_factory=list)
    differs_from: list[str] = field(default_factory=list)
    requires: list[str] = field(default_factory=list)
    uses_tool: list[str] = field(default_factory=list)
    illustrated_by: list[str] = field(default_factory=list)
    # 多值分类：一个知识点可以同时属于多个方向
    also_category: list[str] = field(default_factory=list)
    kind: str = ""
    api_language: str = ""
    api_version: str = ""
    api_symbols: list[str] = field(default_factory=list)

    def meta_text(self) -> str:
        """用于索引的元数据拼接（权重靠前，FTS5 中用列权重体现）。"""
        return " ".join([self.title, *self.tags, *self.signals, *self.tools, self.source])

    def all_categories(self) -> list[str]:
        out = [self.category] if self.category else []
        for c in self.also_category:
            if c not in out:
                out.append(c)
        return out

    def relations(self) -> dict[str, list[str]]:
        """返回所有非空关系，供图谱索引使用。"""
        d = {}
        for name in ("relates_to", "analogous_to", "differs_from",
                     "requires", "uses_tool", "illustrated_by"):
            v = getattr(self, name)
            if v:
                d[name] = v
        return d


def split_front_matter(text: str, *, strict: bool = False) -> tuple[dict[str, Any], str]:
    m = FM_RE.match(text)
    if not m:
        return {}, text
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        if strict:
            raise
        return {}, text[m.end():]
    if not isinstance(meta, dict):
        if strict:
            raise ValueError("front-matter 必须是字段表")
        meta = {}
    return meta, text[m.end():]


def _as_list(v: Any) -> list[str]:
    if v is None:
        return []
    if isinstance(v, str):
        # 支持 "a, b, c" / "a、b"
        parts = re.split(r"[,，、;；]|\s{2,}", v)
        return [p.strip() for p in parts if p.strip()]
    if isinstance(v, (list, tuple, set)):
        return [str(x).strip() for x in v if str(x).strip()]
    return [str(v).strip()]


def load_doc(path: Path, kb_dir: Path) -> Doc:
    raw = path.read_text(encoding="utf-8", errors="replace")
    meta, body = split_front_matter(raw)
    rel = path.relative_to(kb_dir).as_posix()
    # 推断 category：优先 front-matter，其次目录名
    cat = str(meta.get("category", "")).strip().lower()
    if not cat:
        cat = path.parent.name.lower()
    doc = Doc(
        path=rel,
        title=str(meta.get("title") or path.stem).strip(),
        category=cat,
        tags=_as_list(meta.get("tags")),
        signals=_as_list(meta.get("signals")),
        difficulty=str(meta.get("difficulty") or "").strip().lower(),
        source=str(meta.get("source") or "").strip(),
        tools=_as_list(meta.get("tools")),
        body=body.strip(),
        mtime=path.stat().st_mtime,
        relates_to=_as_list(meta.get("relates_to")),
        analogous_to=_as_list(meta.get("analogous_to")),
        differs_from=_as_list(meta.get("differs_from")),
        requires=_as_list(meta.get("requires")),
        uses_tool=_as_list(meta.get("uses_tool")),
        illustrated_by=_as_list(meta.get("illustrated_by")),
        also_category=[c.strip().lower() for c in _as_list(meta.get("also_category"))],
        kind=str(meta.get("kind") or ""),
        api_language=str(meta.get("api_language") or ""),
        api_version=str(meta.get("version") or meta.get("api_version") or ""),
        api_symbols=_as_list(meta.get("api_symbols")),
    )
    if not FM_RE.match(raw):
        doc.warnings.append("缺少 front-matter")
    if doc.category not in VALID_CATEGORIES:
        doc.warnings.append(f"未知 category: {doc.category!r}")
    for c in doc.also_category:
        if c not in VALID_CATEGORIES:
            doc.warnings.append(f"未知 also_category: {c!r}")
    return doc


SKIP_DIRS = {"_templates", ".obsidian", ".git", "node_modules"}


def iter_md_paths(kb_dir: Path) -> Iterable[Path]:
    """按收录规则列出 Markdown 路径；manifest 与 iter_docs 共用这一处规则。"""
    if not kb_dir.exists():
        return
    for p in sorted(kb_dir.rglob("*.md")):
        if any(part in SKIP_DIRS for part in p.relative_to(kb_dir).parts[:-1]):
            continue
        if p.name.startswith("_"):
            continue
        yield p


def iter_docs(kb_dir: Path) -> Iterable[Doc]:
    for p in iter_md_paths(kb_dir):
        yield load_doc(p, kb_dir)


# --------------------------------------------------------------------------
# 分块
# --------------------------------------------------------------------------
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.M)
ARCHIVED_IMAGE_RE = re.compile(
    r"!\[([^\]\n]*)\]\((?:\.\./|\./|/)*_assets/images/"
    r"[0-9a-f]{64}\.(?:png|jpg|gif|webp)(?:\s+\"[^\"]*\")?\)"
)


def split_sections(body: str) -> list[tuple[str, str]]:
    """按 Markdown 标题切分，返回 [(heading_path, text)]。代码块内的 # 不切。"""
    lines = body.splitlines()
    sections: list[tuple[str, str]] = []
    cur_head = ""
    buf: list[str] = []
    in_fence = False

    def flush() -> None:
        text = "\n".join(buf).strip()
        if text:
            sections.append((cur_head, text))

    for line in lines:
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        if not in_fence:
            m = HEADING_RE.match(line)
            if m:
                flush()
                buf = []
                cur_head = m.group(2).strip()
                continue
        buf.append(line)
    flush()
    return sections


def section_of_chunk(text: str) -> str:
    """从 chunk 文本里取章节标题。

    chunk 的前几行形如：
        【web】SSTI（服务器端模板注入）
        ## 一、SSTI 检测与确认
        标签: ...｜识别信号: ...
    只在前 4 行里找，避免把正文里的标题误当成命中章节。
    """
    for line in text.splitlines()[:4]:
        if line.startswith("## "):
            return line[3:].strip()
    return ""


def chunk_doc(doc: Doc, chunk_chars: int = 900, overlap: int = 120) -> list[dict[str, Any]]:
    """把文档切成块。块文本 = 标题路径 + 元数据 + 正文块，便于向量检索命中。"""
    prefixes: list[str] = []
    head = f"【{doc.category}】{doc.title}"
    if doc.tags:
        prefixes.append("标签: " + " ".join(doc.tags))
    if doc.signals:
        prefixes.append("识别信号: " + "；".join(doc.signals))
    meta_block = "｜".join(prefixes)

    chunks: list[dict[str, Any]] = []
    index_body = ARCHIVED_IMAGE_RE.sub(r"\1", doc.body)
    sections = [
        (heading, text) for heading, text in split_sections(index_body)
        if heading != "原文配图"
    ] or [("", index_body)]
    for idx, (heading, text) in enumerate(sections):
        if len(text) <= chunk_chars:
            pieces = [text]
        else:
            pieces = _window(text, chunk_chars, overlap)
        for j, piece in enumerate(pieces):
            payload = "\n".join(
                x for x in (head, f"## {heading}" if heading else "", meta_block, piece) if x
            )
            chunks.append({
                "doc_path": doc.path,
                "chunk_index": len(chunks),
                "section": heading,
                "text": payload,
                "piece": piece,
            })
    return chunks


def _window(text: str, size: int, overlap: int) -> list[str]:
    out = []
    step = max(1, size - overlap)
    # 优先在换行处断开
    i = 0
    n = len(text)
    while i < n:
        end = min(n, i + size)
        if end < n:
            nl = text.rfind("\n", i + int(size * 0.6), end)
            if nl != -1:
                end = nl
        out.append(text[i:end])
        if end >= n:
            break
        i = max(i + 1, end - overlap)
    return out


# --------------------------------------------------------------------------
# 关键词抽取（用于 FTS 查询构造）
# --------------------------------------------------------------------------
CJK_RE = re.compile(r"[\u4e00-\u9fff]")
# 英文/技术词：任意长度的字母数字串（含 c、n、e 这类单字母），保留内部 . / : # - _
WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_./:#$@\-]*")
# 代码/路径里的符号分隔符，用于把 "phar://xxx.jpg" 拆成多个词
SPLIT_SYM = re.compile(r"[/:]+")

# 只去掉真正的虚词/疑问词；必须保留「不、没、无」等否定与实义词，
# 否则「e不同」会被砍成「同」，检索语义直接反转。
STOP_ZH = set("的了和是在我你他她它有而及与着就或吗呢吧啊呀么这那些个以对于把被给请帮想要")
STOP_EN = {
    "the", "and", "for", "with", "that", "this", "you", "are", "was", "how",
    "what", "why", "can", "could", "please", "help", "want", "need", "find",
    "a", "an", "is", "it", "to", "of", "in", "on", "at", "do", "does",
}


def tokenize_query(q: str) -> list[str]:
    """把自然语言查询拆成检索词：
    - 英文/技术词整词保留（rsa, ret2libc, CVE-2021-44228, 单独字母 n/e/c）
    - 技术词再拆出**连续字母数字子串**（bge-small-zh-v1.5 -> bge/小写形式），
      让「半截词」也能通过前缀匹配命中；含分隔符的也拆（phar://a.jpg -> phar, a.jpg）
    - 中文按 2-gram 切分，只去虚词停用词
    """
    q = unicodedata.normalize("NFKC", q).strip()
    tokens: list[str] = []

    for w in WORD_RE.findall(q):
        lw = w.lower().strip(".-/_")
        if not lw or lw in STOP_EN:
            continue
        # {{7*7}} / e=3 这类题面里的单个数字只是 payload 噪声，
        # 会命中全库大量代码块；单字母 n/e/c 仍保留（密码学常用）。
        if lw.isdigit() and len(lw) < 2:
            continue
        tokens.append(lw)
        # 拆出连续字母数字子串：ret2libc 保持整体，同时 CVE-2021-44228 拆成 cve/2021/44228，
        # bge-small-zh 拆成 bge/small/zh
        for sub in re.findall(r"[A-Za-z0-9]+", lw):
            if sub != lw and sub not in STOP_EN and len(sub) >= 2:
                tokens.append(sub)
        for part in SPLIT_SYM.split(lw):
            part = part.strip(".-_")
            if part and part != lw and part not in STOP_EN and len(part) >= 2:
                tokens.append(part)

    for run in re.findall(r"[\u4e00-\u9fff]+", q):
        run = "".join(ch for ch in run if ch not in STOP_ZH)
        if not run:
            continue
        if len(run) == 1:
            tokens.append(run)
        for i in range(len(run) - 1):
            tokens.append(run[i:i + 2])
        # 三字以上的整段也保留，提升长词命中率
        if len(run) >= 3:
            tokens.append(run)

    seen: set[str] = set()
    out: list[str] = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out
