#!/usr/bin/env python
"""黑名单过滤只读探针：报告候选输入会命中哪些词，**不执行候选输入**。

用途：遇到 Python 沙箱/关键字过滤题时，先静态比对过滤表，判断哪些词被挡。
**只读且不执行**：不调用 eval/exec/compile，不导入用户代码，不写文件。

输入：
  --blacklist "os,eval,__class__"   逗号/分号分隔的黑名单词
  --blacklist-file PATH             或从 UTF-8 文件读取（一行一个/逗号分隔）
  --payload "..."                   要检查的候选字符串
  --payload-file PATH               或从 UTF-8 文件读取候选
  --json                            输出 JSON

输出：match、hit_count、hits、payload_length、ascii、braces 等。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared import add_json_flag, configure_stdio, emit  # noqa: E402


def split_terms(text: str) -> list[str]:
    terms = [t.strip() for t in re.split(r"[,，;；\n\r]+", text or "")]
    return [t for t in terms if t]


def read_text(value: str | None, path: str | None) -> str:
    if value is not None:
        return value
    if path:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    return ""


def probe(blacklist: list[str], payload: str) -> dict:
    hits = [t for t in blacklist if t and t in payload]
    return {
        "read_only": True,
        "executed": False,
        "payload_length": len(payload),
        "is_ascii": payload.isascii(),
        "has_braces": "{" in payload and "}" in payload,
        "blacklist_size": len(blacklist),
        "hit_count": len(hits),
        "hits": hits,
        "match": not hits,
    }


def main(argv: list[str] | None = None) -> int:
    configure_stdio()
    ap = argparse.ArgumentParser(description="黑名单过滤只读探针（不执行输入）")
    ap.add_argument("--blacklist", help="逗号/分号分隔的黑名单词")
    ap.add_argument("--blacklist-file")
    ap.add_argument("--payload", default="")
    ap.add_argument("--payload-file")
    add_json_flag(ap)
    args = ap.parse_args(argv)
    bl_text = read_text(args.blacklist, args.blacklist_file)
    if not bl_text and args.blacklist_file is None and args.blacklist is None:
        ap.error("需要 --blacklist 或 --blacklist-file")
    payload = read_text(args.payload, args.payload_file)
    out = probe(split_terms(bl_text), payload)
    emit(out, args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
