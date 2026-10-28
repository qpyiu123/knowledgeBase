"""知识库内容清单（index/manifest.json）。

清单记录每篇被收录 Markdown 的 sha256，用于判断哪些文档新增/修改/删除。
收录规则与 parser.iter_docs 同源，避免脚本、Python 各算一套导致篇数漂移。
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any

from .parser import iter_md_paths

MANIFEST_VERSION = 1
MANIFEST_NAME = "manifest.json"


class ScanResult(dict[str, str]):
    """清单扫描结果：仍可直接当 dict 用，另带不可读文件列表。

    ``skipped`` 为 ``[(kb 相对路径, 错误描述)]``；单文件被占用/拒绝读取
    不应让整库重建失败。
    """

    def __init__(self) -> None:
        super().__init__()
        self.skipped: list[tuple[str, str]] = []


def describe_error(err: OSError) -> str:
    """把 OSError/PermissionError 转成可展示文本（含 errno）。"""
    errno = getattr(err, "errno", None)
    text = getattr(err, "strerror", None) or str(err)
    return f"{errno}: {text}" if errno is not None else text


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def scan(kb_dir: Path, old: dict[str, str] | None = None) -> ScanResult:
    """返回 {kb 相对 POSIX 路径: sha256}，不可读文件记入 ``result.skipped``。

    传入上一次清单 ``old`` 时，不可读文件保留旧 sha，避免下次重建被误判为
    changed 而重复编码；没有旧值的文件只记入 skipped，不进入清单。
    """
    kb_dir = Path(kb_dir)
    old = old or {}
    out = ScanResult()
    for p in iter_md_paths(kb_dir):
        rel = p.relative_to(kb_dir).as_posix()
        try:
            out[rel] = sha256_file(p)
        except OSError as e:  # PermissionError 是 OSError 子类
            out.skipped.append((rel, describe_error(e)))
            if rel in old:
                out[rel] = old[rel]
    return out


def diff(old: dict[str, str] | None, new: dict[str, str] | None
         ) -> tuple[list[str], list[str], list[str]]:
    """返回 (added, removed, changed)，均为排序后的路径列表。"""
    old = old or {}
    new = new or {}
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    changed = sorted(k for k in (set(old) & set(new)) if old[k] != new[k])
    return added, removed, changed


def load(path: Path) -> dict[str, str] | None:
    """读取清单；不存在、损坏或版本不认识时返回 None（调用方退化为全量）。"""
    path = Path(path)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict) or data.get("version") != MANIFEST_VERSION:
        return None
    files = data.get("files")
    if not isinstance(files, dict):
        return None
    out: dict[str, str] = {}
    for k, v in files.items():
        if isinstance(k, str) and isinstance(v, str):
            out[k] = v
    return out


def render(files: dict[str, str], built_at: str | None = None) -> str:
    payload = {
        "version": MANIFEST_VERSION,
        "built_at": built_at or time.strftime("%Y-%m-%d %H:%M:%S"),
        "count": len(files),
        "files": dict(sorted(files.items())),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def save(path: Path, files: dict[str, str], built_at: str | None = None) -> dict[str, Any]:
    """原子写入清单（同目录临时文件 + os.replace）。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".new")
    tmp.write_text(render(files, built_at), encoding="utf-8")
    os.replace(tmp, path)
    return json.loads(render(files, built_at))
