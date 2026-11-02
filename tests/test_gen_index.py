"""索引页与图谱构建在单文件不可读时应跳过并继续。"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import gen_index
import kb.parser as parser
from cli import cmd_graph


def _write(path: Path, title: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        f'title: "{title}"\n'
        "category: crypto\n"
        f"signals: [\"{title}\"]\n"
        "---\n"
        "## 正文\n\n"
        f"{title} 正文\n",
        encoding="utf-8",
    )


def _kb(tmp_path: Path) -> Path:
    kb = tmp_path / "kb"
    _write(kb / "crypto" / "ok.md", "可读条目")
    _write(kb / "crypto" / "bad.md", "不可读条目")
    return kb


def _patch_unreadable(monkeypatch, bad_name: str) -> None:
    real = parser.load_doc

    def fake(path, kb_dir):
        if Path(path).name == bad_name:
            raise PermissionError(13, "Permission denied", str(path))
        return real(path, kb_dir)

    monkeypatch.setattr(parser, "load_doc", fake)
    monkeypatch.setattr(gen_index, "load_doc", fake)


def test_gen_index_skips_unreadable_file(tmp_path, monkeypatch, capsys) -> None:
    kb = _kb(tmp_path)
    _patch_unreadable(monkeypatch, "bad.md")
    text = gen_index.build(SimpleNamespace(kb_dir=kb))
    assert "可读条目" in text
    assert "不可读条目" not in text
    assert "跳过不可读文件" in capsys.readouterr().err


def test_graph_build_skips_unreadable_file(tmp_path, monkeypatch, capsys) -> None:
    kb = _kb(tmp_path)
    _patch_unreadable(monkeypatch, "bad.md")
    cfg = SimpleNamespace(kb_dir=kb, index_dir=tmp_path / "index")
    args = SimpleNamespace(build=True, expand=None, hops=1)
    assert cmd_graph(cfg, args) == 0
    out = capsys.readouterr()
    assert "图谱已建立: 1 节点" in out.out
    assert "跳过不可读文件" in out.err
