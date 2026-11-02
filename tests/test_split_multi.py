"""DB-Q3 多题合并文件拆分工具的回归测试。"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
import yaml

import split_multi as sm


def _doc(title: str, category: str, segments: list[tuple[str, str]]) -> str:
    lines = [
        "---",
        f'title: "{title}"',
        f"category: {category}",
        "tags: [demo]",
        'source: "https://example.com/source"',
        'origin: imported_cats',
        'origin_id: "demo-1"',
        "---",
        f"# {title}",
        "",
        "> 来源：example",
        "",
        "## 正文",
        "",
        f"第一段：{title}",
        "",
    ]
    for name, body in segments:
        lines.extend([f"## 【来源分段】{name}", "", "## 正文", "", body, ""])
    return "\n".join(lines)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def _kb(tmp_path: Path) -> Path:
    kb = tmp_path / "kb"
    _write(kb / "_imported_cats" / "misc" / "multi__src-1.md",
           _doc("赛事 A / 题目一", "misc",
                [("赛事 A _ 题目二", "第二段正文"), ("赛事 A _ 题目三", "第三段正文")]))
    _write(kb / "_imported" / "pwn" / "multi2__src-2.md",
           _doc("赛事 B / 题目甲", "pwn",
                [("赛事 B _ 题目乙", "乙正文"), ("赛事 B _ 题目丙", "丙正文"),
                 ("赛事 B _ 题目丁", "丁正文")]))
    _write(kb / "_imported_cats" / "misc" / "single__src-3.md",
           _doc("赛事 C / 唯一题", "misc", []))
    _write(kb / "_des" / "misc" / "ignored__src-4.md",
           _doc("赛事 D / 忽略", "misc",
                [("赛事 D _ 不拆", "不应拆"), ("赛事 D _ 也不拆", "不应拆")]))
    return kb


def test_detects_only_scope_multi_segment(tmp_path: Path) -> None:
    kb = _kb(tmp_path)
    found = sm.find_multi_segment_files(kb)
    assert found == [
        "_imported/pwn/multi2__src-2.md",
        "_imported_cats/misc/multi__src-1.md",
    ]


def test_dry_run_does_not_write(tmp_path: Path) -> None:
    kb = _kb(tmp_path)
    before = {p: p.read_bytes() for p in kb.rglob("*.md")}
    log = tmp_path / "work" / "q3" / "split_log.json"
    result = sm.run(kb, apply=False, log_path=log)
    assert result["planned"] == 2
    assert result["applied"] == 0
    assert result["new_files"] == 5
    after = {p: p.read_bytes() for p in kb.rglob("*.md")}
    assert before == after
    assert not log.exists()


def test_apply_writes_front_matter_and_reduces_original(tmp_path: Path) -> None:
    kb = _kb(tmp_path)
    log = tmp_path / "work" / "q3" / "split_log.json"
    result = sm.run(kb, apply=True, log_path=log)
    assert result["applied"] == 2
    assert not result["errors"]

    new = kb / "_imported_cats/misc/赛事 A _ 题目二__src-1-seg2.md"
    assert new.is_file()
    fm, body = sm.split_front_matter(new.read_text(encoding="utf-8"))
    meta = yaml.safe_load(fm.strip().strip("-").strip())
    assert meta["title"] == "赛事 A / 题目二"
    assert meta["category"] == "misc"
    assert meta["source"] == "https://example.com/source"
    assert meta["split_from"] == "_imported_cats/misc/multi__src-1.md"
    assert "第二段正文" in body
    assert "第三段正文" not in body

    original = kb / "_imported_cats/misc/multi__src-1.md"
    text = original.read_text(encoding="utf-8")
    assert "## 【来源分段】" not in sm.split_front_matter(text)[1]
    assert "第一段：赛事 A / 题目一" in text
    assert "赛事 A / 题目一" in text

    saved = json.loads(log.read_text(encoding="utf-8"))
    assert len(saved["files"]) == 2
    assert len(saved["files"][0]["segments"]) >= 2


def test_segment_bodies_are_verbatim(tmp_path: Path) -> None:
    kb = _kb(tmp_path)
    rel = "_imported_cats/misc/multi__src-1.md"
    original = (kb / rel).read_text(encoding="utf-8")
    _, body = sm.split_front_matter(original)
    headings = sm.find_segment_headings(body)
    expected = [body[: headings[0]["start"]]]
    for i, h in enumerate(headings):
        end = headings[i + 1]["start"] if i + 1 < len(headings) else len(body)
        expected.append(body[h["end"]:end])

    sm.run(kb, apply=True, log_path=tmp_path / "log.json")
    _, new_first = sm.split_front_matter((kb / rel).read_text(encoding="utf-8"))
    assert new_first == sm.finalize_text(expected[0])
    targets = [
        "_imported_cats/misc/赛事 A _ 题目二__src-1-seg2.md",
        "_imported_cats/misc/赛事 A _ 题目三__src-1-seg3.md",
    ]
    for target, seg_body in zip(targets, expected[1:]):
        _, got = sm.split_front_matter((kb / target).read_text(encoding="utf-8"))
        assert got == sm.finalize_text(seg_body)
        assert sm.normalized_hash(got) == sm.normalized_hash(seg_body)


def test_apply_is_idempotent(tmp_path: Path) -> None:
    kb = _kb(tmp_path)
    log = tmp_path / "work" / "q3" / "split_log.json"
    sm.run(kb, apply=True, log_path=log)
    snapshot = {p: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in kb.rglob("*.md")}
    second = sm.run(kb, apply=True, log_path=log)
    assert second["detected"] == 0
    assert second["applied"] == 0
    assert second["new_files"] == 0
    assert snapshot == {p: hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in kb.rglob("*.md")}


def test_hash_guard_refuses_changed_file(tmp_path: Path) -> None:
    kb = _kb(tmp_path)
    rel = "_imported_cats/misc/multi__src-1.md"
    plan = sm.build_plan(kb, rel)
    path = kb / rel
    path.write_bytes(path.read_bytes() + b"\nchanged\n")
    with pytest.raises(ValueError, match="哈希"):
        sm.apply_plan(kb, plan)
    assert not (kb / "_imported_cats/misc/赛事 A _ 题目二__src-1-seg2.md").exists()


def test_cli_dry_run_default(tmp_path: Path) -> None:
    kb = _kb(tmp_path)
    rc = sm.main(["--project-root", str(tmp_path), "--kb-dir", str(kb)])
    assert rc == 0
    assert not (kb / "_imported_cats/misc/赛事 A _ 题目二__src-1-seg2.md").exists()
