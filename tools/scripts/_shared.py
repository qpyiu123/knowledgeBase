"""只读脚本库的最小公共工具：解析输入、输出 JSON、失败即退出。

本目录下的脚本只做本地只读分析：不写文件、不执行输入内容、不联网、
不自动调用外部程序。需要写盘或执行样本时，请另立明确授权的任务。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001
            pass


def add_json_flag(ap: argparse.ArgumentParser) -> None:
    ap.add_argument("--json", action="store_true", help="输出 JSON（便于测试）")


def emit(obj: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True))
        return
    for key, value in obj.items():
        if isinstance(value, (dict, list)):
            print(f"{key}: {json.dumps(value, ensure_ascii=False)}")
        else:
            print(f"{key}: {value}")


def read_int_arg(value: str | None, path: str | None) -> int:
    """从参数或文件读取一个十进制/0x 整数；文件只读第一段数字。"""
    if value:
        return parse_int(value)
    if not path:
        raise SystemExit("需要 --n/--p 或 --n-file/--p-file")
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    return parse_int(text)


def parse_int(text: str) -> int:
    m = re.search(r"(?:0x[0-9a-fA-F]+|[0-9]+)", str(text or ""))
    if not m:
        raise SystemExit("没有找到整数")
    token = m.group(0)
    if token.lower().startswith("0x"):
        return int(token, 16)
    return int(token, 10)
