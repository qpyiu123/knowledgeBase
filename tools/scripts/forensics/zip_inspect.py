#!/usr/bin/env python
"""ZIP / JAR 只读清单：列条目、统计顶层目录、按名称/内容检索。

用途：拿到 jar/apk/zip 附件时先看清楚结构，避免盲目解压。
**只读**：用 zipfile 读取目录与字节，不落盘、不解压、不执行任何内容。

输入：
  --zip PATH        要检查的压缩包
  --top N           只显示前 N 个顶层目录（默认 20）
  --grep PATTERN    正则；在条目名与可解码文本内容里搜索
  --max-bytes N     单条目读取上限（默认 2 MiB，防大文件拖慢）
  --json            输出 JSON

输出：entry_count、top_dirs、name_hits、content_hits、encrypted 等。
"""
from __future__ import annotations

import argparse
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared import add_json_flag, configure_stdio, emit  # noqa: E402


def inspect(path: Path, top: int, pattern: str | None, max_bytes: int) -> dict:
    if not path.is_file():
        raise SystemExit(f"文件不存在: {path}")
    if not zipfile.is_zipfile(path):
        raise SystemExit("不是有效的 ZIP/JAR 文件")
    rx = re.compile(pattern, re.IGNORECASE) if pattern else None
    name_hits: list[str] = []
    content_hits: list[dict] = []
    encrypted: list[str] = []
    tops: Counter[str] = Counter()
    with zipfile.ZipFile(path) as z:
        infos = z.infolist()
        for info in infos:
            name = info.filename
            if not name.endswith("/"):
                tops[name.split("/", 1)[0]] += 1
            if rx and rx.search(name):
                name_hits.append(name)
            if info.flag_bits & 0x1:
                encrypted.append(name)
            if rx and not name.endswith("/"):
                try:
                    if info.file_size > max_bytes:
                        continue
                    raw = z.read(name)
                except (RuntimeError, OSError, zipfile.BadZipFile):
                    continue
                text = raw.decode("utf-8", errors="replace")
                for m in rx.finditer(text):
                    content_hits.append({"entry": name,
                                         "match": m.group(0)[:200]})
                    if len(content_hits) >= 50:
                        break
    return {
        "read_only": True,
        "zip": str(path),
        "entry_count": len(infos),
        "file_count": sum(1 for i in infos if not i.filename.endswith("/")),
        "top_dirs": [{"name": k, "files": v}
                     for k, v in tops.most_common(max(1, top))],
        "encrypted": encrypted[:50],
        "name_hits": name_hits[:50],
        "content_hits": content_hits,
    }


def main(argv: list[str] | None = None) -> int:
    configure_stdio()
    ap = argparse.ArgumentParser(description="ZIP/JAR 只读清单")
    ap.add_argument("--zip", required=True, help="ZIP/JAR 路径")
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--grep", help="名称/内容正则")
    ap.add_argument("--max-bytes", type=int, default=2 * 1024 * 1024)
    add_json_flag(ap)
    args = ap.parse_args(argv)
    out = inspect(Path(args.zip), args.top, args.grep, args.max_bytes)
    emit(out, args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
