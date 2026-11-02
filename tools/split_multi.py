"""把 ``_imported*`` 里一个文件合并多道题的分段拆成每题一篇。

DB-Q1/Q2 实测：``_imported_cats`` 有 13 个文件在正文里带 ≥2 个
``## 【来源分段】`` 标题，是导入器把同一来源页的多篇 writeup 合进了一个文件。
本工具按 DB-Q3 规则拆分：

* 第 1 段（含文件原有 H1/来源元信息与首个 ``## 正文``）留在**原文件名**里；
* 第 2..N 段各写一个新文件 ``<分段标题>__<原导入ID>-seg<序号>.md``；
* 新文件复制原 front-matter，只改 ``title``（赛事 / 题名）并新增
  ``split_from``；正文从分段标题之后逐字照搬，包括 ``## 正文`` 小标题；
* 默认 dry-run 只打印计划；``--apply`` 才写盘，写入前校验原文件 SHA256；
* 每个文件的计划与每段归一化哈希写入 ``work/q3/split_log.json``；
* 重跑 ``--apply`` 不会产生变化（拆完后原文件只剩 1 段，不再命中）。

用法::

    .\\.venv\\Scripts\\python.exe tools\\split_multi.py
    .\\.venv\\Scripts\\python.exe tools\\split_multi.py --apply
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Sequence

TOOLS_DIR = Path(__file__).resolve().parent
SCOPE_DIRS = ("_imported", "_imported_cats")
HEADING_RE = re.compile(r"^##[ \t]*【来源分段】[ \t]*(.+?)[ \t]*$")
ILLEGAL = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def normalized_hash(text: str) -> str:
    return sha256_text(text.strip())


def split_front_matter(text: str) -> tuple[str, str]:
    """返回 (front-matter 文本含首尾 --- 与换行, 正文文本)；正文逐字保留。"""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise ValueError("文件不以 --- 开头，缺少 front-matter")
    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "..."):
            return "".join(lines[: i + 1]), "".join(lines[i + 1:])
    raise ValueError("front-matter 未闭合")


def find_segment_headings(body: str) -> list[dict[str, Any]]:
    headings: list[dict[str, Any]] = []
    offset = 0
    for line in body.splitlines(keepends=True):
        m = HEADING_RE.match(line.rstrip("\r\n"))
        if m:
            headings.append({
                "title": m.group(1).strip(),
                "start": offset,
                "end": offset + len(line),
            })
        offset += len(line)
    return headings


def segment_title(heading: str) -> str:
    """``赛事 _ 题名`` -> ``赛事 / 题名``；没有分隔符时原样返回。"""
    if " _ " in heading:
        event, name = heading.split(" _ ", 1)
        return f"{event.strip()} / {name.strip()}"
    return heading.strip()


def safe_filename(title: str) -> str:
    name = ILLEGAL.sub("_", title).strip().rstrip(". ")
    return name or "segment"


def origin_id_of(stem: str) -> str:
    if "__" not in stem:
        raise ValueError(f"文件名缺少 __<导入ID>: {stem}")
    return stem.rsplit("__", 1)[1]


def replace_title_and_add_split_from(fm: str, title: str, split_from: str) -> str:
    lines = fm.splitlines(keepends=True)
    out: list[str] = []
    done = False
    for line in lines:
        if not done and line.startswith("title:"):
            eol = line[len(line.rstrip("\r\n")):]
            out.append(f"title: {json.dumps(title, ensure_ascii=False)}{eol}")
            out.append(f"split_from: {json.dumps(split_from, ensure_ascii=False)}{eol}")
            done = True
        else:
            out.append(line)
    if not done:
        raise ValueError("front-matter 缺少 title 行")
    return "".join(out)


def build_plan(kb_dir: Path, rel: str) -> dict[str, Any]:
    path = kb_dir / rel
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    fm, body = split_front_matter(text)
    headings = find_segment_headings(body)
    if len(headings) < 2:
        raise ValueError("命中文件的来源分段不足 2 个")
    origin_id = origin_id_of(path.stem)
    first_title = path.stem.rsplit("__", 1)[0].replace(" _ ", " / ", 1)
    segments: list[dict[str, Any]] = []
    preamble = body[: headings[0]["start"]]
    segments.append({
        "seg": 1,
        "heading": first_title,
        "title": first_title,
        "body": preamble,
        "body_sha256": normalized_hash(preamble),
        "target": rel,
        "new_body": preamble,
        "new_front_matter": None,
    })
    for idx, heading in enumerate(headings):
        start = heading["end"]
        end = headings[idx + 1]["start"] if idx + 1 < len(headings) else len(body)
        seg_body = body[start:end]
        ordinal = idx + 2
        title = segment_title(heading["title"])
        target = f"{path.parent.relative_to(kb_dir).as_posix()}/" \
                 f"{safe_filename(heading['title'])}__{origin_id}-seg{ordinal}.md"
        segments.append({
            "seg": ordinal,
            "heading": heading["title"],
            "title": title,
            "body": seg_body,
            "body_sha256": normalized_hash(seg_body),
            "target": target,
            "new_body": seg_body,
            "new_front_matter": replace_title_and_add_split_from(
                fm, title, rel),
        })
    return {
        "path": rel,
        "sha256": sha256_bytes(raw),
        "origin_id": origin_id,
        "category": _front_matter_value(fm, "category"),
        "segments": segments,
        "targets": [s["target"] for s in segments[1:]],
    }


def _front_matter_value(fm: str, key: str) -> str:
    m = re.search(rf"^{key}:\s*(.+)$", fm, flags=re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""


def find_multi_segment_files(kb_dir: Path) -> list[str]:
    found: list[str] = []
    for name in SCOPE_DIRS:
        root = kb_dir / name
        if not root.is_dir():
            continue
        for p in sorted(root.rglob("*.md")):
            try:
                text = p.read_text(encoding="utf-8")
                _, body = split_front_matter(text)
            except (OSError, UnicodeDecodeError, ValueError):
                continue
            if len(find_segment_headings(body)) >= 2:
                found.append(p.relative_to(kb_dir).as_posix())
    return found


def _write_atomic(path: Path, data: bytes) -> None:
    tmp = path.with_name(path.name + ".split-tmp")
    try:
        tmp.write_bytes(data)
        os.replace(tmp, path)
    except OSError:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def finalize_text(text: str) -> str:
    """逐字保留正文，只把文件末尾的空白行收敛为一个换行。"""
    eol = "\r\n" if "\r\n" in text else "\n"
    return text.rstrip("\r\n") + eol


def apply_plan(kb_dir: Path, plan: dict[str, Any]) -> dict[str, Any]:
    path = kb_dir / plan["path"]
    before = path.read_bytes()
    if sha256_bytes(before) != plan["sha256"]:
        raise ValueError("原文件哈希在计划后发生变化，拒绝写入")
    created: list[str] = []
    for seg in plan["segments"][1:]:
        target = kb_dir / seg["target"]
        data = finalize_text(seg["new_front_matter"] + seg["new_body"]).encode("utf-8")
        if target.exists():
            if target.read_bytes() == data:
                created.append(seg["target"])
                continue
            raise ValueError(f"目标文件已存在且内容不同: {seg['target']}")
        target.parent.mkdir(parents=True, exist_ok=True)
        _write_atomic(target, data)
        created.append(seg["target"])
    if sha256_bytes(path.read_bytes()) != plan["sha256"]:
        raise ValueError("写入新文件后原文件被改动，拒绝覆盖")
    fm, _ = split_front_matter(before.decode("utf-8"))
    reduced = finalize_text(fm + plan["segments"][0]["new_body"]).encode("utf-8")
    _write_atomic(path, reduced)
    return {
        "path": plan["path"],
        "original_sha256_before": plan["sha256"],
        "original_sha256_after": sha256_bytes(path.read_bytes()),
        "created": created,
        "segments": [
            {"seg": s["seg"], "heading": s["heading"], "target": s["target"],
             "body_sha256": s["body_sha256"]}
            for s in plan["segments"]
        ],
    }


def load_log(path: Path) -> dict[str, Any]:
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and isinstance(data.get("files"), list):
                return data
        except (OSError, ValueError):
            pass
    return {"batch": "DB-Q3", "files": []}


def save_log(path: Path, entry: dict[str, Any]) -> None:
    data = load_log(path)
    data["files"] = [f for f in data["files"] if f.get("path") != entry["path"]]
    data["files"].append(entry)
    data["files"].sort(key=lambda f: f["path"])
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    os.replace(tmp, path)


def run(kb_dir: Path, *, apply: bool = False, log_path: Path | None = None,
        only: Sequence[str] | None = None) -> dict[str, Any]:
    rels = find_multi_segment_files(kb_dir)
    plans = []
    errors = []
    for rel in rels:
        if only and rel not in only:
            continue
        try:
            plans.append(build_plan(kb_dir, rel))
        except (OSError, UnicodeDecodeError, ValueError) as e:
            errors.append({"path": rel, "error": str(e)})
    applied = []
    if apply:
        for plan in plans:
            try:
                entry = apply_plan(kb_dir, plan)
            except (OSError, UnicodeDecodeError, ValueError) as e:
                errors.append({"path": plan["path"], "error": str(e)})
                continue
            applied.append(entry)
            if log_path is not None:
                save_log(log_path, entry)
    return {
        "dry_run": not apply,
        "detected": len(rels),
        "planned": len(plans),
        "applied": len(applied),
        "new_files": sum(len(p["targets"]) for p in plans),
        "plans": plans,
        "applied_files": applied,
        "errors": errors,
    }


def _print_plan(plan: dict[str, Any]) -> None:
    print(f"SPLIT {plan['path']}  sha256={plan['sha256'][:12]}  "
          f"segments={len(plan['segments'])}")
    for seg in plan["segments"]:
        marker = "keep " if seg["seg"] == 1 else "new  "
        print(f"  {marker}seg{seg['seg']} -> {seg['target']}  "
              f"body_sha256={seg['body_sha256'][:12]}  title={seg['title']}")


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="split_multi.py",
        description="拆分 _imported/_imported_cats 里合并多题的 Markdown（默认 dry-run）")
    ap.add_argument("--project-root", default=str(TOOLS_DIR.parent))
    ap.add_argument("--kb-dir", default=None,
                    help="知识库目录（默认 <project-root>/kb）")
    ap.add_argument("--apply", action="store_true", help="真正写盘（默认只打印计划）")
    ap.add_argument("--log", default=None,
                    help="拆分证据 JSON（默认 <project-root>/work/q3/split_log.json）")
    ap.add_argument("--json", action="store_true", help="机器可读输出")
    args = ap.parse_args(argv)

    root = Path(args.project_root).resolve()
    kb_dir = Path(args.kb_dir).resolve() if args.kb_dir else root / "kb"
    log_path = Path(args.log) if args.log else root / "work" / "q3" / "split_log.json"
    result = run(kb_dir, apply=args.apply, log_path=log_path)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for plan in result["plans"]:
            _print_plan(plan)
        for err in result["errors"]:
            print(f"ERROR {err['path']} — {err['error']}")
        print(json.dumps({
            "dry_run": result["dry_run"],
            "detected": result["detected"],
            "planned": result["planned"],
            "applied": result["applied"],
            "new_files": result["new_files"],
        }, ensure_ascii=False, sort_keys=True))
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
