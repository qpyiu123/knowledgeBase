"""按显式清单修复旧导入批里未加引号的 ``signals`` flow 序列。

DB-Q1 实测：``_imported/`` 下有 21 篇 front-matter 的 ``signals`` 形如
``signals: [[Misc] 清北问答, Git]`` / ``signals: [RSA? cmd5!]``，YAML 解析失败，
索引侧因此把整块元数据丢弃。本工具只做**最小修复**：

* 只改 front-matter 里的 ``signals`` 一行，把每个元素加上双引号；
* 文件其余字节（包括 CRLF 换行、其它字段、正文）逐字不变；
* 清单显式列出路径、修复前后 SHA256 与正文 SHA256，写入前先校验原文件哈希；
* ``--dry-run`` 只报告不写盘；已修复的文件再次运行报告 ``already_repaired``，
  不产生任何写入（幂等）。

清单：``tools/kb/signals_repair_manifest.json``。

用法::

    .\\.venv\\Scripts\\python.exe tools\\repair_signals.py --dry-run
    .\\.venv\\Scripts\\python.exe tools\\repair_signals.py
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Sequence

import yaml

TOOLS_DIR = Path(__file__).resolve().parent
DEFAULT_MANIFEST = TOOLS_DIR / "kb" / "signals_repair_manifest.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def split_front_matter_lines(text: str) -> tuple[list[str], list[str]]:
    """按原始行（保留换行符）切出 front-matter 与正文，不正规化换行。"""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise ValueError("文件不以 --- 开头，缺少 front-matter")
    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "..."):
            return lines[: i + 1], lines[i + 1:]
    raise ValueError("front-matter 未闭合")


def body_text_of(text: str) -> str:
    _, body = split_front_matter_lines(text)
    return "".join(body)


def _strip_eol(line: str) -> str:
    return line.rstrip("\r\n")


def replace_signals_line(text: str, old_line: str, new_line: str) -> str:
    """只在 front-matter 内替换唯一一行 signals，保留该行原来的换行符。"""
    fm, body = split_front_matter_lines(text)
    hits = [i for i, line in enumerate(fm[1:-1], start=1)
            if _strip_eol(line) == old_line]
    if len(hits) != 1:
        raise ValueError(f"front-matter 内 signals 原行命中 {len(hits)} 次（应为 1）")
    i = hits[0]
    eol = fm[i][len(_strip_eol(fm[i])):]
    fm[i] = new_line + eol
    new_text = "".join(fm + body)
    # 反向替换必须还原原文，证明其余字节完全没动。
    if replace_once(new_text, new_line + eol, old_line + eol) != text:
        raise ValueError("替换后无法逐字还原原文，拒绝写入")
    return new_text


def replace_once(text: str, old: str, new: str) -> str:
    idx = text.find(old)
    if idx < 0:
        return text
    return text[:idx] + new + text[idx + len(old):]


def load_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("清单缺少非空 entries")
    seen: set[str] = set()
    for e in entries:
        for key in ("path", "original_sha256", "fixed_sha256", "body_sha256",
                    "signals_original", "signals_fixed", "signals_expected"):
            if key not in e:
                raise ValueError(f"清单条目缺少 {key}: {e}")
        if e["path"] in seen:
            raise ValueError(f"清单重复路径: {e['path']}")
        seen.add(e["path"])
    return data


def validate_fixed(text: str, entry: dict[str, Any]) -> None:
    """修复后必须能解析、字段齐全、signals 语义正确、正文逐字未变。"""
    meta, body = split_front_matter_text(text)
    if not isinstance(meta, dict) or not meta:
        raise ValueError("修复后 front-matter 仍无法解析为映射")
    for key in ("title", "category", "source"):
        if not str(meta.get(key) or "").strip():
            raise ValueError(f"修复后 {key} 为空")
    signals = meta.get("signals")
    if not isinstance(signals, list) or signals != entry["signals_expected"]:
        raise ValueError(f"修复后 signals={signals!r} != {entry['signals_expected']!r}")
    body_sha = sha256_bytes(body.encode("utf-8"))
    if body_sha != entry["body_sha256"]:
        raise ValueError(
            f"正文哈希变化: {body_sha} != {entry['body_sha256']}")


def split_front_matter_text(text: str) -> tuple[dict[str, Any], str]:
    fm, body = split_front_matter_lines(text)
    block = "".join(fm[1:-1])
    meta = yaml.safe_load(block) or {}
    return (meta if isinstance(meta, dict) else {}), "".join(body)


def repair_entry(kb_dir: Path, entry: dict[str, Any], *,
                 dry_run: bool) -> dict[str, Any]:
    rel = entry["path"]
    path = kb_dir / rel
    result: dict[str, Any] = {"path": rel, "status": "", "written": False}
    try:
        raw = path.read_bytes()
    except OSError as e:
        result.update(status="error", error=f"读取失败: {e}")
        return result
    current = sha256_bytes(raw)

    if current == entry["fixed_sha256"]:
        result["status"] = "already_repaired"
        return result
    if current != entry["original_sha256"]:
        result.update(status="error",
                      error=f"原文件哈希不匹配: {current} != {entry['original_sha256']}")
        return result

    text = raw.decode("utf-8")
    try:
        new_text = replace_signals_line(
            text, entry["signals_original"], entry["signals_fixed"])
        validate_fixed(new_text, entry)
    except (ValueError, yaml.YAMLError) as e:
        result.update(status="error", error=str(e))
        return result

    new_raw = new_text.encode("utf-8")
    if sha256_bytes(new_raw) != entry["fixed_sha256"]:
        result.update(status="error", error="修复后哈希与清单不符，拒绝写入")
        return result

    if dry_run:
        result["status"] = "would_repair"
        return result

    tmp = path.with_name(path.name + ".repair-tmp")
    try:
        tmp.write_bytes(new_raw)
        os.replace(tmp, path)
    except OSError as e:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
        result.update(status="error", error=f"写入失败: {e}")
        return result
    after = sha256_bytes(path.read_bytes())
    if after != entry["fixed_sha256"]:
        result.update(status="error", error="写入后哈希校验失败")
        return result
    result.update(status="repaired", written=True)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="repair_signals.py",
        description="按显式清单修复 signals YAML 引号（最小改动、可 dry-run、幂等）")
    ap.add_argument("--project-root", default=str(TOOLS_DIR.parent))
    ap.add_argument("--kb-dir", default=None,
                    help="知识库目录（默认 <project-root>/kb）")
    ap.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    ap.add_argument("--dry-run", action="store_true", help="只检查并报告，不写盘")
    ap.add_argument("--json", action="store_true", help="机器可读输出")
    args = ap.parse_args(argv)

    root = Path(args.project_root).resolve()
    kb_dir = Path(args.kb_dir).resolve() if args.kb_dir else root / "kb"
    manifest = load_manifest(Path(args.manifest))
    results = [repair_entry(kb_dir, e, dry_run=args.dry_run)
               for e in manifest["entries"]]
    counts: dict[str, int] = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    summary = {
        "batch": manifest.get("batch", "DB-Q2"),
        "dry_run": args.dry_run,
        "manifest": str(Path(args.manifest).resolve()),
        "counts": counts,
        "results": results,
    }
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        for r in results:
            extra = f" — {r['error']}" if r.get("error") else ""
            print(f"{r['status']:16} {r['path']}{extra}")
        print(json.dumps(counts, ensure_ascii=False, sort_keys=True))
    return 1 if counts.get("error") else 0


if __name__ == "__main__":
    sys.exit(main())
