#!/usr/bin/env python
"""把 F:\\ctf 的 evidence.sqlite3 中已核许可的散文正文导入 kb/_imported_cats/（阶段 1）。

来源库只读打开（``file:<path>?mode=ro``）。同一 ``source_id`` 的段落合并为一篇 Markdown，
段落间重叠的部分（后段以前段结尾若干字开头）先剪掉再拼接，避免重复，同时不丢任何内容。

许可字段（license / attribution / source_url / event / year / content_sha256 及 metadata 里
其余键）原样写进 front-matter 的 ``origin_meta`` 与 body 顶部元信息块，一个字都不丢。

用法（在项目根执行）::

    python tools/import_cat_prose.py --dry-run --limit 20    # 抽样，只写 work 下的报告
    python tools/import_cat_prose.py --full                  # 全量写入 kb/_imported_cats/
    python tools/import_cat_prose.py --full --resume         # 被杀后续跑（已有文件跳过）

去重：与 ``index/manifest.json`` 记录的既有文件比对源 content_sha256 / source_url、
标题撞车；manifest 落盘 ``work/import_cats/manifest.json``。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from kb.parser import FM_RE, VALID_CATEGORIES, iter_md_paths, split_front_matter  # noqa: E402

DEFAULT_SRC = Path(r"F:\ctf\CTF知识库\80_知识工作台\data\evidence.sqlite3")
OUT_DIR = ROOT / "kb" / "_imported_cats"
WORK_DIR = ROOT / "work" / "import_cats"
MANIFEST_PATH = WORK_DIR / "manifest.json"
PROGRESS_PATH = WORK_DIR / "progress.json"
INDEX_MANIFEST = ROOT / "index" / "manifest.json"

KINDS = ("source_prose",)
ORIGIN_TAG = "origin_tag:imported_cats"

# 来源库 domain（含技法表）到 kb 11 类的映射；映射不上的落 misc，并在 body 顶部保留原 domain。
DOMAIN_MAP = {
    "web": "web", "crypto": "crypto", "pwn": "pwn", "reverse": "reverse",
    "misc": "misc", "forensics": "forensics", "mobile": "mobile",
    "hardware": "hardware", "osint": "osint", "ai": "ai", "blockchain": "blockchain",
    "cases": "misc", "languages": "misc", "programming": "misc", "reference": "misc",
}

BAD_NAME_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
WARN_CHARS = 6000   # 单篇超长给告警（检索前缀噪声）


def read_only_connect(path: Path) -> sqlite3.Connection:
    """只读打开源库；路径里可能有中文与反斜杠，统一用 POSIX 形式拼 URI。"""
    p = str(Path(path)).replace("\\", "/")
    return sqlite3.connect(f"file:{p}?mode=ro", uri=True)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()


def yaml_scalar(v) -> str:
    """把任意 JSON 值转成安全的 YAML 标量；嵌套对象用 JSON（保证可逆、零丢失）。"""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False, sort_keys=True)
    s = "" if v is None else str(v)
    return json.dumps(s, ensure_ascii=False)


def sanitize_filename(title: str, fallback: str) -> str:
    name = BAD_NAME_RE.sub("_", title).strip().strip(".")
    name = re.sub(r"\s+", " ", name)
    if len(name) > 80:
        name = name[:80].rstrip()
    return name or fallback


def url_hash(url: str) -> str:
    return hashlib.sha256(url.strip().encode("utf-8", "replace")).hexdigest()


def strip_overlap(prev: str, nxt: str, min_len: int = 24) -> tuple[str, int]:
    """后段若以前段结尾开头（抽取重叠），剪掉重叠部分。返回 (新文本, 剪掉字数)。"""
    lo = min(len(prev), len(nxt))
    for k in range(lo, min_len - 1, -1):
        if prev.endswith(nxt[:k]):
            return nxt[k:].lstrip("\r\n"), k
    return nxt, 0


@dataclass
class SourceDoc:
    source_id: str
    title: str
    domain: str
    passages: list[tuple[str, str, str, dict]] = field(default_factory=list)  # (pid, section, body, meta)


def load_sources(conn: sqlite3.Connection, limit: int = 0) -> list[SourceDoc]:
    sql = ("select id, source_id, title, domain, section, body, metadata from passages "
           f"where kind in ({','.join('?' * len(KINDS))}) order by source_id, rowid")
    cur = conn.execute(sql, KINDS)
    docs: dict[str, SourceDoc] = {}
    for pid, sid, title, dom, sec, body, md in cur:
        try:
            meta = json.loads(md or "{}")
        except ValueError:
            meta = {"_raw_metadata": md}
        if not isinstance(meta, dict):
            meta = {"_raw_metadata": md}
        d = docs.get(sid)
        if d is None:
            d = SourceDoc(source_id=sid, title=(title or "").strip() or sid,
                          domain=(dom or "").strip().lower())
            docs[sid] = d
        d.passages.append((pid, (sec or "").strip(), body or "", meta))
    out = sorted(docs.values(), key=lambda d: d.source_id)
    return out[:limit] if limit else out


def compose_body(doc: SourceDoc) -> tuple[str, list[str], dict]:
    """按 section 分组拼接（稳定顺序），章节内剪掉段落重叠。"""
    order: list[str] = []
    groups: dict[str, list[str]] = {}
    order_keys: dict[str, tuple[int, str]] = {}
    for pid, sec, body, _meta in doc.passages:
        key = sec or "正文"
        if key not in groups:
            groups[key] = []
            order_keys[key] = (len(order), key)
            order.append(key)
    flat: list[tuple[str, str]] = []  # (section, body)
    trimmed = 0
    for pid, sec, body, _meta in doc.passages:
        text = body.strip()
        if not text:
            continue
        if flat:
            prev_text = flat[-1][1]
            text, cut = strip_overlap(prev_text, text)
            trimmed += cut
        if not text:
            continue
        if flat and flat[-1][0] == (sec or "正文"):
            flat[-1] = (flat[-1][0], flat[-1][1] + "\n\n" + text)
        else:
            flat.append(((sec or "正文"), text))
    groups = {}
    for sec, text in flat:
        groups.setdefault(sec, []).append(text)

    warnings: list[str] = []
    chunks: list[str] = []
    for sec in sorted(groups, key=lambda s: order_keys.get(s, (10**6, s))):
        heading = "正文" if sec == "正文" else sec
        parts = groups[sec]
        if len(parts) > 1:
            body_text = f"## {heading}\n\n" + "\n\n".join(parts)
        else:
            body_text = f"## {heading}\n\n{parts[0]}"
        chunks.append(body_text)
    stats = {"passages": len(doc.passages), "sections": len(groups),
             "trimmed_chars": trimmed}
    return "\n\n".join(chunks), warnings, stats


def first_meta(doc: SourceDoc) -> dict:
    """取 source 级元数据（各段 metadata 里 source 级字段应当一致，取首段并记录分歧）。"""
    merged: dict = {}
    for _pid, _sec, _body, meta in doc.passages:
        for k, v in meta.items():
            if k not in merged:
                merged[k] = v
    return merged


def build_front_matter(doc: SourceDoc, meta: dict, title: str, category: str,
                       subtitle: str, body: str) -> str:
    tags: list[str] = []
    for t in meta.get("tags") or []:
        t = str(t).strip()
        if t and t not in tags:
            tags.append(t)
    if len(tags) > 12:
        tags = tags[:12]
    tags.append(ORIGIN_TAG)

    lines = ["---",
             f"title: {yaml_scalar(title)}",
             f"category: {category}",
             "tags: [" + ", ".join(yaml_scalar(t) for t in tags) + "]",
             "signals: [" + ", ".join(yaml_scalar(t) for t in tags[:3]) + "]",
             "difficulty: medium",
             f"source: {yaml_scalar(meta.get('source_url') or '')}",
             "tools: []",
             "origin: imported_cats",
             f"origin_id: {yaml_scalar(doc.source_id)}",
             f"origin_domain: {yaml_scalar(doc.domain or '')}",
             f"origin_family: {yaml_scalar(meta.get('source_family') or '')}",
             f"origin_event: {yaml_scalar(meta.get('event') or '')}",
             f"origin_year: {yaml_scalar(meta.get('year') if meta.get('year') is not None else '')}",
             f"origin_license: {yaml_scalar(meta.get('license') or '')}",
             f"origin_attribution: {yaml_scalar(meta.get('attribution') or meta.get('source_author') or '')}",
             f"origin_verification: {yaml_scalar(meta.get('verification_status') or '')}",
             f"origin_content_sha256: {yaml_scalar(meta.get('content_sha256') or '')}",
             f"origin_body_sha256: {sha256_text(body)}",
             f"origin_title: {yaml_scalar(doc.title)}",
             ]
    if subtitle:
        lines.append(f"origin_section_of: {yaml_scalar(subtitle)}")
    lines.append("origin_meta:")
    for k in sorted(meta):
        lines.append(f"  {k}: {yaml_scalar(meta[k])}")
    lines.append(f"updated: {time.strftime('%Y-%m-%d')}")
    lines.append("---")
    return "\n".join(lines)


def license_block(meta: dict, doc: SourceDoc, title: str) -> str:
    """body 顶部元信息块：许可与出处原文照录，保证即使 front-matter 解析失败也不丢。"""
    def g(*keys) -> str:
        for k in keys:
            v = meta.get(k)
            if v not in (None, "", []):
                return v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
        return ""

    def one_line(s: str) -> str:
        # 元信息块每条一行，换行折成空格只影响展示；原文仍在 origin_meta 完整保留
        return " ".join(str(s).split())

    rows = [
        ("来源", g("source_url") or "（无）"),
        ("许可", g("license") or "（未声明）"),
        ("署名", g("attribution", "source_author") or "（未提供）"),
        ("文档族", g("source_family") or "（无）"),
        ("赛事", g("event") or "（无）"),
        ("年份", str(meta.get("year")) if meta.get("year") is not None else "（无）"),
        ("核验状态", g("verification_status") or "（无）"),
        ("正文 sha256", g("content_sha256") or "（无）"),
        ("导入 ID", doc.source_id),
        ("原 domain", doc.domain or "（无）"),
    ]
    if g("license_local_path"):
        rows.append(("许可文件", g("license_local_path")))
    if g("license_evidence_urls"):
        rows.append(("许可依据", g("license_evidence_urls")))
    if g("local_path", "original_path"):
        rows.append(("本地快照", g("local_path", "original_path")))
    if g("source_revision", "revision"):
        rows.append(("源修订", g("source_revision", "revision")))
    if g("fetched_at_utc"):
        rows.append(("抓取时间", g("fetched_at_utc")))
    if g("scope_note"):
        rows.append(("收录说明", g("scope_note")))
    if g("basis"):
        rows.append(("判定依据", g("basis")))
    if meta.get("asset_refs"):
        rows.append(("附件引用", json.dumps(meta["asset_refs"], ensure_ascii=False)))
    body = ["> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。"]
    body.append(">")
    for k, v in rows:
        body.append(f"> - {k}：{one_line(v)}")
    if meta.get("source_url"):
        body.append("")
        body.append(f"> 原文：{meta['source_url']}")
    return "\n".join(body)


def existing_index_state() -> dict:
    """读 index/manifest.json 的既有文件路径集合，用于标题/路径撞车检查。"""
    paths: set[str] = set()
    if INDEX_MANIFEST.exists():
        try:
            data = json.loads(INDEX_MANIFEST.read_text(encoding="utf-8"))
            paths = set((data.get("files") or {}).keys())
        except (OSError, ValueError):
            paths = set()
    return {"paths": paths}


def scan_existing_corpus(kb_dir: Path, limit_note: int = 0) -> dict:
    """扫描 kb/（含 _imported/）既有文档的 source_url/sha256/标题，用于去重。

    只读 front-matter 与正文里以 ``原文：`` 标注的链接，不做全文比对（简报要求）。
    """
    urls: dict[str, str] = {}
    hashes: dict[str, str] = {}
    titles: dict[str, str] = {}
    files = 0
    for p in iter_md_paths(kb_dir):
        rel = p.relative_to(kb_dir).as_posix()
        if rel.startswith("_imported_cats/"):
            continue
        try:
            raw = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        files += 1
        meta, body = split_front_matter(raw)
        src = str(meta.get("source") or "").strip()
        if src.startswith("http"):
            urls.setdefault(url_hash(src), rel)
        for key in ("origin_url", "origin_source_url"):
            v = str(meta.get(key) or "").strip()
            if v.startswith("http"):
                urls.setdefault(url_hash(v), rel)
        for key in ("origin_sha256", "origin_body_sha256", "origin_content_sha256"):
            v = str(meta.get(key) or "").strip()
            if v:
                hashes.setdefault(v, rel)
        m = re.search(r"^> 原文：\s*(\S+)\s*$", body, re.M)
        if m and m.group(1).startswith("http"):
            urls.setdefault(url_hash(m.group(1)), rel)
        t = str(meta.get("title") or p.stem).strip()
        if t:
            titles.setdefault(t, rel)
    return {"files": files, "urls": urls, "hashes": hashes, "titles": titles}


def plan(docs: list[SourceDoc], index_state: dict, corp: dict | None) -> tuple[list[dict], Counter]:
    """生成每篇的输出计划并做去重判定。返回 (items, stats)。"""
    stats: Counter = Counter()
    items: list[dict] = []
    seen_sha: dict[str, str] = {}      # 正文 sha256 -> 已保留篇目（按简报细则的"同 sha 跳过"）
    seen_url: dict[str, str] = {}
    seen_title: dict[str, str] = {}
    seen_name: set[str] = set()
    by_rel: dict[str, dict] = {}
    for doc in docs:
        meta = first_meta(doc)
        stats["sources"] += 1
        csha = str(meta.get("content_sha256") or "")
        # 源库的 content_sha256 实际是**每段**的哈希：NewStar/Hello-CTF 的首页段都只有
        # "---\ncomments: true\n---" 之类样板，于是几百篇 source 共享同一个前缀哈希。
        # 用它做文档级去重会误杀，故只有在「哈希不同 + 正文相同」时才按细则判重复。
        url = str(meta.get("source_url") or "").strip()
        title = doc.title
        if doc.domain in ("cases", "languages"):
            # 同一 WP 按方向拆成多段：标题后加方向后缀，避免同名文件互相覆盖
            suffix = {"cases": "misc", "languages": "reference"}.get(doc.domain, doc.domain)
            title = f"{doc.title}（{suffix}）"
        cat = DOMAIN_MAP.get(doc.domain, "")
        category = cat or "misc"
        if category not in VALID_CATEGORIES:
            category = "misc"
        body, warnings, bstats = compose_body(doc)
        stats["passages"] += bstats["passages"]
        stats["trimmed_chars"] += bstats["trimmed_chars"]

        dup_reason = ""
        item_body_sha = sha256_text(body)
        # 1) 正文级重复（本批已保留篇目正文完全相同）
        if item_body_sha in seen_sha:
            dup_reason = f"同 content_sha256（本批正文相同 {seen_sha[item_body_sha]}）"
        # 2) 同一 source_url 会被抽取器按方向/题目拆成多条 source_id；按简报"同 source_id 合并、
        #    既有同源跳过"的意图，来源 URL 已在保留集合里的后续条目**合并进首篇**而不丢弃。
        elif url and url_hash(url) in seen_url:
            dup_reason = f"合并同 source_url（本批 {seen_url[url_hash(url)]}）"
        elif url and corp and url_hash(url) in corp["urls"]:
            dup_reason = f"同 source_url（既有 {corp['urls'][url_hash(url)]}）"
        elif title in seen_title:
            dup_reason = f"同标题（本批 {seen_title[title]}）"
        elif corp and title in corp["titles"]:
            dup_reason = f"同标题（既有 {corp['titles'][title]}）"

        slug = re.sub(r"[^0-9A-Za-z_.-]+", "_", doc.source_id).strip("_") or "src"
        fname = sanitize_filename(title, slug) + f"__{slug}.md"
        rel = f"_imported_cats/{category}/{fname}"
        if rel.lower() in seen_name:
            rel = f"_imported_cats/{category}/{sanitize_filename(title, slug)}__{slug}_{stats['sources']}.md"
        seen_name.add(rel.lower())

        item = {
            "source_id": doc.source_id,
            "title": title,
            "category": category,
            "origin_domain": doc.domain,
            "path": rel,
            "body": body,
            "meta": meta,
            "content_sha256": csha,
            "source_url": url,
            "body_sha256": sha256_text(body),
            "passages": bstats["passages"],
            "chars": len(body),
            "warnings": warnings,
            "dup_reason": dup_reason,
            "merged_sources": [],
            "merged_passages": 0,
        }
        if dup_reason.startswith("合并同 source_url"):
            # 同一来源的另一方向/另一题：正文并入首篇的对应章节，源不丢、段不丢
            head_rel = seen_url[url_hash(url)]
            head = by_rel.get(head_rel)
            if head is not None and body.strip():
                sec = sanitize_filename(title, doc.source_id)
                block = f"## 【来源分段】{sec}\n\n{body.strip()}"
                head["body"] = f"{head['body'].strip()}\n\n{block}"
                head["chars"] = len(head["body"])
                head["merged_sources"].append(doc.source_id)
                head["merged_passages"] += bstats["passages"]
                head["body_sha256"] = sha256_text(head["body"])
                # 合并后正文变了：哈希索引换成新正文哈希，旧哈希不再占用
                seen_sha.pop(item["body_sha256"], None)
                seen_sha[head["body_sha256"]] = head_rel
                stats["merged_sources"] += 1
                stats["merged_passages"] += bstats["passages"]
                continue
        if dup_reason:
            stats["dup_sources"] += 1
            stats["dup_passages"] += bstats["passages"]
            stats["dup_" + dup_reason.split("（")[0]] += 1
            items.append(item)
            continue
        if bstats["passages"] == 0 or len(body.strip()) < 40:
            stats["empty_sources"] += 1
            item["dup_reason"] = "正文过短（<40 字），不导入"
            items.append(item)
            continue
        # 只有真的会落盘才占位，避免被跳过项把后来的真身也判成重复
        seen_sha[item["body_sha256"]] = rel
        if url:
            seen_url[url_hash(url)] = rel
        seen_title[title] = rel
        if len(body) > WARN_CHARS:
            stats["long_docs"] += 1
        by_rel[rel] = item
        items.append(item)
    stats["kept_sources"] = stats["sources"] - stats["dup_sources"] - stats["empty_sources"]
    stats["written_files"] = len(by_rel)
    return items, stats


def render_doc(item: dict) -> str:
    doc = SourceDoc(source_id=item["source_id"], title=item["title"],
                    domain=item["origin_domain"])
    fm = build_front_matter(doc, item["meta"], item["title"], item["category"],
                            item.get("subtitle", ""), item["body"])
    block = license_block(item["meta"], doc, item["title"])
    head = f"# {item['title']}"
    if item["origin_domain"] and DOMAIN_MAP.get(item["origin_domain"]) != item["category"]:
        head += f"\n\n<!-- 原 domain: {item['origin_domain']} -->"
    return f"{fm}\n{head}\n\n{block}\n\n{item['body'].strip()}\n"


def write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, path)


def load_progress() -> dict:
    if PROGRESS_PATH.exists():
        try:
            return json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))
        except ValueError:
            return {}
    return {}


def update_progress(**kw) -> None:
    prog = load_progress()
    prog.update(kw)
    prog["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save_json(PROGRESS_PATH, prog)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="导入 evidence.sqlite3 里已核许可的散文正文")
    ap.add_argument("--src", default=str(DEFAULT_SRC), help="evidence.sqlite3 路径（只读打开）")
    ap.add_argument("--out", default=str(OUT_DIR), help="输出目录（默认 kb/_imported_cats）")
    ap.add_argument("--full", action="store_true", help="全量写入输出目录")
    ap.add_argument("--dry-run", action="store_true", help="只生成计划与报告，不写 kb")
    ap.add_argument("--limit", type=int, default=0, help="只处理前 N 个 source（抽样验证用）")
    ap.add_argument("--resume", action="store_true", help="目标文件已存在且 sha 匹配则跳过")
    ap.add_argument("--kinds", default=None,
                    help="要导入的 kind（逗号分隔；默认只导 source_prose）")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    global KINDS
    if args.kinds:
        KINDS = tuple(k.strip() for k in args.kinds.split(",") if k.strip())
    for k in KINDS:
        if k not in ("source_prose", "user_prose", "technique_guide"):
            print(f"未知 kind: {k}", file=sys.stderr)
            return 2

    src = Path(args.src)
    if not src.exists():
        print(f"源库不存在: {src}", file=sys.stderr)
        return 2
    out_dir = Path(args.out)
    conn = read_only_connect(src)
    t0 = time.time()
    docs = load_sources(conn, args.limit)
    corp = None
    if not args.limit:
        corp = scan_existing_corpus(ROOT / "kb")
    items, stats = plan(docs, existing_index_state(), corp)
    elapsed = round(time.time() - t0, 1)
    print(f"源库: {src}（只读）  kind={','.join(KINDS)}  source={stats['sources']}  段={stats['passages']}")
    if corp:
        print(f"既有语料扫描: {corp['files']} 篇（kb/ 除 _imported_cats）；"
              f"已知 URL {len(corp['urls'])} / sha {len(corp['hashes'])} / 标题 {len(corp['titles'])}")
    print(f"计划: 保留 {stats['kept_sources']} 个 source / 去重跳过 {stats['dup_sources']} 个"
          f"（{stats['dup_passages']} 段）/ 过短 {stats['empty_sources']} 个；"
          f"其中 {stats['merged_sources']} 个同源分段并入首篇（{stats['merged_passages']} 段）；"
          f"段落重叠剪掉 {stats['trimmed_chars']} 字；落盘 {stats.get('written_files', 0)} 篇；耗时 {elapsed}s")

    if args.verbose or args.dry_run:
        for it in items[: (20 if args.limit or args.dry_run else 200)]:
            flag = it["dup_reason"] or "keep"
            print(f"  [{flag}] {it['path']}  ({it['passages']} 段, {it['chars']} 字)")

    report = {
        "src": str(src),
        "kinds": list(KINDS),
        "stats": dict(stats),
        "sources": [
            {k: it[k] for k in ("source_id", "title", "category", "path", "passages",
                                "chars", "content_sha256", "source_url", "dup_reason")}
            for it in items
        ],
    }
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    report_name = "dryrun_report.json" if (args.dry_run or args.limit) else "import_report.json"
    save_json(WORK_DIR / report_name, report)

    if args.dry_run:
        print(f"[dry-run] 报告写入 work/import_cats/{report_name}，未写 kb/")
        return 0

    written = skipped_existing = 0
    manifest = {}
    if MANIFEST_PATH.exists():
        try:
            manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        except ValueError:
            manifest = {}
    files = manifest.setdefault("files", {})
    for n, it in enumerate(items, 1):
        if it["dup_reason"]:
            continue
        target = out_dir / Path(it["path"]).relative_to("_imported_cats")
        text = render_doc(it)
        if args.resume and target.exists():
            try:
                old = target.read_text(encoding="utf-8", errors="replace")
            except OSError:
                old = ""
            if f"origin_body_sha256: {it['body_sha256']}" in old:
                skipped_existing += 1
                written += 0
                files[it["path"]] = {
                    "source_id": it["source_id"], "title": it["title"],
                    "category": it["category"], "content_sha256": it["content_sha256"],
                    "source_url": it["source_url"], "body_sha256": it["body_sha256"],
                    "passages": it["passages"], "chars": it["chars"],
                }
                continue
        write_atomic(target, text)
        written += 1
        files[it["path"]] = {
            "source_id": it["source_id"], "title": it["title"],
            "category": it["category"], "content_sha256": it["content_sha256"],
            "source_url": it["source_url"], "body_sha256": it["body_sha256"],
            "passages": it["passages"], "chars": it["chars"],
        }
        if n % 100 == 0:
            update_progress(step="import", written=written, seen=n,
                            total=len(items), updated_at=time.strftime("%Y-%m-%dT%H:%M:%S"))
            if MANIFEST_PATH.exists():
                save_json(MANIFEST_PATH, manifest)
            print(f"  …已写 {written} 篇（扫描 {n}/{len(items)}）", flush=True)
    manifest.update({
        "version": 1,
        "built_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "src": str(src),
        "kinds": list(KINDS),
        "dedupe": {
            "dup_sources": stats["dup_sources"],
            "dup_passages": stats["dup_passages"],
            "empty_sources": stats["empty_sources"],
            "chars": {k[len("dup_"):]: v for k, v in stats.items() if k.startswith("dup_")},
        },
        "kept_sources": stats["kept_sources"],
        "written_this_run": written,
        "resumed_skipped": skipped_existing,
    })
    save_json(MANIFEST_PATH, manifest)
    update_progress(step="import_done", written=written, resumed_skipped=skipped_existing,
                    kept_sources=stats["kept_sources"], dup_sources=stats["dup_sources"],
                    out=str(out_dir))
    print(f"写入 {written} 篇（续跑跳过 {skipped_existing}）；manifest -> work/import_cats/manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
