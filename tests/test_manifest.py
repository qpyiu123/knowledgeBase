"""内容清单 manifest：收录规则、哈希、diff 与持久化。"""
from __future__ import annotations

import json
from pathlib import Path

from kb import manifest
from kb.parser import iter_docs


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _make_kb(root: Path) -> Path:
    kb = root / "kb"
    _write(kb / "crypto" / "rsa.md", "---\ntitle: RSA\n---\n正文 rsa\n")
    _write(kb / "web" / "ssti.md", "---\ntitle: SSTI\n---\n正文 ssti\n")
    _write(kb / "_des" / "cards" / "card.md", "---\ntitle: 卡片\n---\ncard\n")
    _write(kb / "_templates" / "tpl.md", "ignore\n")
    _write(kb / ".obsidian" / "x.md", "ignore\n")
    _write(kb / "node_modules" / "n.md", "ignore\n")
    _write(kb / "crypto" / "node_modules" / "deep.md", "ignore\n")
    _write(kb / "_draft.md", "ignore\n")
    return kb


def test_scan_follows_parser_collection_rules(tmp_path: Path):
    kb = _make_kb(tmp_path)
    files = manifest.scan(kb)
    assert set(files) == {
        "crypto/rsa.md", "web/ssti.md", "_des/cards/card.md",
    }
    assert len(files) == len(list(iter_docs(kb)))


def test_scan_hashes_file_bytes(tmp_path: Path):
    kb = _make_kb(tmp_path)
    import hashlib
    files = manifest.scan(kb)
    raw = (kb / "crypto" / "rsa.md").read_bytes()
    assert files["crypto/rsa.md"] == hashlib.sha256(raw).hexdigest()
    assert manifest.scan(kb) == files


def test_diff_added_removed_changed(tmp_path: Path):
    kb = _make_kb(tmp_path)
    old = manifest.scan(kb)
    _write(kb / "crypto" / "rsa.md", "---\ntitle: RSA\n---\n改过 rsa\n")
    _write(kb / "misc" / "new.md", "---\ntitle: NEW\n---\nnew\n")
    (kb / "web" / "ssti.md").unlink()

    new = manifest.scan(kb)
    added, removed, changed = manifest.diff(old, new)
    assert added == ["misc/new.md"]
    assert removed == ["web/ssti.md"]
    assert changed == ["crypto/rsa.md"]


def test_diff_handles_missing_sides():
    assert manifest.diff(None, {"a.md": "1"}) == (["a.md"], [], [])
    assert manifest.diff({"a.md": "1"}, None) == ([], ["a.md"], [])
    assert manifest.diff(None, None) == ([], [], [])


def test_save_and_load_roundtrip(tmp_path: Path):
    files = {"crypto/rsa.md": "aa", "web/ssti.md": "bb"}
    path = tmp_path / "index" / "manifest.json"
    manifest.save(path, files, built_at="2026-10-28 12:00:00")
    assert manifest.load(path) == files

    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["version"] == manifest.MANIFEST_VERSION
    assert data["count"] == 2
    assert data["built_at"] == "2026-10-28 12:00:00"
    assert not (tmp_path / "index" / "manifest.json.new").exists()


def test_load_rejects_missing_and_unknown_version(tmp_path: Path):
    path = tmp_path / "manifest.json"
    assert manifest.load(path) is None

    path.write_text(json.dumps({"version": 99, "files": {"a": "b"}}), encoding="utf-8")
    assert manifest.load(path) is None

    path.write_text(json.dumps({"version": 1, "files": "bad"}), encoding="utf-8")
    assert manifest.load(path) is None
