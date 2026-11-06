"""DB-Q2 signals 修复工具与清单的回归测试。

覆盖：
  * 清单里 21 篇的真实文件现已能解析，``source`` 非空，``signals`` 语义正确；
  * DB-Q3 删除 15 篇冗余旧篇后，清单保留 6 条活跃条目与 15 条退役证据；
  * 修复只改 ``signals`` 一行，其它字段与正文逐字不变（可用原哈希反向证明）；
  * 工具支持 dry-run、写入前校验原文件哈希、重复运行幂等；
  * 原文件确实曾因未加引号而 YAML 解析失败（历史事实，不回写成“缺 source”）。
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest
import yaml

import repair_signals as rs
from kb.parser import load_doc, split_front_matter

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tools" / "kb" / "signals_repair_manifest.json"


def manifest() -> dict:
    return rs.load_manifest(MANIFEST)


def pre_gallery_bytes(path: Path) -> bytes:
    """历史清单的校验值使用 CRLF；后加的配图库不属于当时的正文。"""
    body = path.read_text(encoding="utf-8")
    base, sep, gallery = body.partition("\n\n## 原文配图\n\n")
    if sep:
        assert all("_assets/images/" in line for line in gallery.splitlines() if line)
        body = base + "\n"
    return body.replace("\n", "\r\n").encode("utf-8")


def test_manifest_active_and_retired_cover_21_imported_docs() -> None:
    data = manifest()
    active = data["entries"]
    retired = data.get("retired_entries", [])
    assert len(active) == 6
    assert len(retired) == 15
    assert len(active) + len(retired) == 21
    assert all(e["path"].startswith("_imported/") for e in active + retired)
    kb = ROOT / "kb"
    assert all((kb / e["path"]).is_file() for e in active)
    assert all(not (kb / e["path"]).exists() for e in retired)


def test_current_files_parse_and_keep_body() -> None:
    kb = ROOT / "kb"
    for e in manifest()["entries"]:
        p = kb / e["path"]
        doc = load_doc(p, kb)
        assert doc.source, e["path"]
        assert doc.signals == e["signals_expected"], e["path"]
        assert doc.category, e["path"]
        assert doc.title, e["path"]
        raw = pre_gallery_bytes(p)
        assert rs.sha256_bytes(raw) == e["fixed_sha256"], e["path"]
        body = rs.body_text_of(raw.decode("utf-8"))
        assert rs.sha256_bytes(body.encode("utf-8")) == e["body_sha256"], e["path"]
        assert "缺少 front-matter" not in doc.warnings


def test_only_signals_line_changed_and_original_was_invalid() -> None:
    kb = ROOT / "kb"
    for e in manifest()["entries"]:
        p = kb / e["path"]
        fixed = pre_gallery_bytes(p).decode("utf-8")
        old = rs.replace_once(
            fixed,
            e["signals_fixed"] + _eol_of(fixed, e["signals_fixed"]),
            e["signals_original"] + _eol_of(fixed, e["signals_fixed"]),
        )
        assert rs.sha256_bytes(old.encode("utf-8")) == e["original_sha256"], e["path"]
        assert rs.body_text_of(old) == rs.body_text_of(fixed), e["path"]
        # 原文的 YAML 确实解析失败；parser 当时会整块丢弃元数据。
        fm, _ = rs.split_front_matter_lines(old)
        with pytest.raises(yaml.YAMLError):
            yaml.safe_load("".join(fm[1:-1]))
        meta, body = split_front_matter(old)
        assert meta == {} and body


def _eol_of(text: str, line: str) -> str:
    idx = text.index(line)
    tail = text[idx + len(line):]
    if tail.startswith("\r\n"):
        return "\r\n"
    if tail.startswith("\n"):
        return "\n"
    raise AssertionError("找不到 signals 行换行符")


def _synthetic(tmp_path: Path) -> tuple[Path, Path]:
    kb = tmp_path / "kb"
    p = kb / "_imported" / "misc" / "demo.md"
    p.parent.mkdir(parents=True)
    original = (
        "---\r\n"
        'title: "[Misc] demo"\r\n'
        "category: misc\r\n"
        "tags: [demo]\r\n"
        "signals: [[Misc] demo, Git]\r\n"
        'source: "https://example.com/demo"\r\n'
        "---\r\n"
        "正文第一行\r\n正文第二行\r\n"
    )
    p.write_bytes(original.encode("utf-8"))
    fixed = rs.replace_signals_line(
        original, "signals: [[Misc] demo, Git]", 'signals: ["[Misc] demo", "Git"]')
    entry = {
        "path": "_imported/misc/demo.md",
        "original_sha256": rs.sha256_bytes(original.encode("utf-8")),
        "fixed_sha256": rs.sha256_bytes(fixed.encode("utf-8")),
        "body_sha256": rs.sha256_bytes(
            rs.body_text_of(original).encode("utf-8")),
        "signals_original": "signals: [[Misc] demo, Git]",
        "signals_fixed": 'signals: ["[Misc] demo", "Git"]',
        "signals_expected": ["[Misc] demo", "Git"],
    }
    mpath = tmp_path / "manifest.json"
    mpath.write_text(json.dumps(
        {"version": 1, "entries": [entry]}, ensure_ascii=False), encoding="utf-8")
    return p, mpath


def test_dry_run_then_repair_then_idempotent(tmp_path: Path) -> None:
    p, mpath = _synthetic(tmp_path)
    args = ["--project-root", str(tmp_path), "--manifest", str(mpath)]
    before = p.read_bytes()
    assert rs.main(args + ["--dry-run"]) == 0
    assert p.read_bytes() == before, "dry-run 不得写盘"
    assert rs.main(args) == 0
    after = p.read_bytes()
    assert rs.sha256_bytes(after) == rs.load_manifest(mpath)["entries"][0]["fixed_sha256"]
    assert rs.main(args) == 0
    assert p.read_bytes() == after, "重复运行必须无变化"
    assert not list(p.parent.glob("*.repair-tmp"))


def test_hash_guard_refuses_changed_file(tmp_path: Path) -> None:
    p, mpath = _synthetic(tmp_path)
    p.write_bytes(p.read_bytes().replace(b"\xe6\xad\xa3\xe6\x96\x87", b"\xe6\x94\xb9\xe6\x96\x87"))
    before = p.read_bytes()
    assert rs.main(["--project-root", str(tmp_path), "--manifest", str(mpath)]) == 1
    assert p.read_bytes() == before
    assert not list(p.parent.glob("*.repair-tmp"))
