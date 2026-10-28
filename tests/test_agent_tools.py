"""工具层测试：路径越界、权限、参数校验、知识库检索。"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent import tools as T  # noqa: E402


# ------------------------------------------------------------------ 路径安全
def test_read_file_rejects_traversal():
    r = T.read_file("../../Windows/System32/drivers/etc/hosts")
    assert not r.ok
    assert "越界" in r.content


def test_read_file_rejects_absolute_outside():
    r = T.read_file("C:/Windows/win.ini")
    assert not r.ok
    assert "越界" in r.content


def test_write_file_cannot_escape_workspace():
    """试图写到 tools/ 时必须被重定向进 work/，绝不能真的落到 tools/。"""
    from agent import tools as T2
    target = "tools/hacked_probe.py"
    real_tools_file = T2.ROOT / "tools" / "hacked_probe.py"
    r = T.write_file(target, "print(1)")
    try:
        # 无论成功与否，都不应该在真实的 tools/ 下产生文件
        assert not real_tools_file.exists(), "安全漏洞：写穿了 work/ 目录"
        if r.ok:
            # 允许被安全地重定向进 work/
            assert "work" in r.content.lower()
    finally:
        if real_tools_file.exists():
            real_tools_file.unlink()
        for p in (T2.WORKSPACE / "tools").glob("hacked_probe.py"):
            p.unlink()


def test_write_file_rejects_venv():
    r = T.write_file("../.venv/x.py", "print(1)")
    assert not r.ok
    assert "越界" in r.content


def test_read_rejects_binary_ext():
    r = T.read_file("models/gguf/qwen2.5-coder-7b-instruct-q4_k_m.gguf")
    assert not r.ok


def test_empty_path_rejected():
    assert not T.read_file("").ok
    assert not T.write_file("", "x").ok


# ------------------------------------------------------------------ 读写
def test_write_and_read_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(T, "WORKSPACE", tmp_path)
    monkeypatch.setattr(T, "WRITE_ROOTS", [tmp_path])
    monkeypatch.setattr(T, "READ_ROOTS", [tmp_path])

    w = T.write_file("sub/exp.py", "print('hello')\n")
    assert w.ok, w.content
    assert (tmp_path / "sub" / "exp.py").exists()

    r = T.read_file("sub/exp.py")
    assert r.ok
    assert "print('hello')" in r.content


def test_write_adds_py_ext(tmp_path, monkeypatch):
    monkeypatch.setattr(T, "WORKSPACE", tmp_path)
    monkeypatch.setattr(T, "WRITE_ROOTS", [tmp_path])
    w = T.write_file("notes", "hi")
    assert w.ok
    assert (tmp_path / "notes.py").exists()


def test_write_overwrites_reports(tmp_path, monkeypatch):
    monkeypatch.setattr(T, "WORKSPACE", tmp_path)
    monkeypatch.setattr(T, "WRITE_ROOTS", [tmp_path])
    T.write_file("a.py", "v1")
    w2 = T.write_file("a.py", "v2")
    assert "覆盖" in w2.content
    assert (tmp_path / "a.py").read_text(encoding="utf-8") == "v2"


def test_read_truncates_long_file(tmp_path, monkeypatch):
    monkeypatch.setattr(T, "WORKSPACE", tmp_path)
    monkeypatch.setattr(T, "READ_ROOTS", [tmp_path])
    f = tmp_path / "long.txt"
    f.write_text("\n".join(f"line{i}" for i in range(500)), encoding="utf-8")
    r = T.read_file("long.txt", max_lines=10)
    assert r.ok
    assert "显示前 10 行" in r.content
    assert "line9" in r.content
    assert "line10" not in r.content


def test_read_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr(T, "WORKSPACE", tmp_path)
    monkeypatch.setattr(T, "READ_ROOTS", [tmp_path])
    r = T.read_file("nope.txt")
    assert not r.ok
    assert "不存在" in r.content


# ------------------------------------------------------------------ search_kb
def test_search_kb_empty_query():
    r = T.search_kb("")
    assert not r.ok


def test_search_kb_real_hit():
    """真实索引存在时，中文题面应能命中。"""
    from kb.config import Config
    cfg = Config.load()
    if not (cfg.index_dir / "fts.db").exists():
        pytest.skip("no index built")
    r = T.search_kb("n 相同 e 不同 两组密文")
    assert r.ok
    assert "共模" in r.content or "RSA" in r.content


def test_search_kb_bad_category_falls_back():
    """非法 category 应被忽略而不是报错。"""
    from kb.config import Config
    cfg = Config.load()
    if not (cfg.index_dir / "fts.db").exists():
        pytest.skip("no index built")
    r = T.search_kb("栈溢出", category="不存在的方向")
    assert r.ok


# ------------------------------------------------------------------ dispatch
def test_dispatch_unknown_tool():
    r = T.dispatch("rm_rf", {})
    assert not r.ok
    assert "未知工具" in r.content


def test_dispatch_bad_args():
    r = T.dispatch("read_file", {"paths": "x"})
    assert not r.ok
    assert "参数不匹配" in r.content


def test_dispatch_non_dict():
    r = T.dispatch("read_file", "x")
    assert not r.ok


def test_tool_specs_are_valid_openai_shape():
    assert len(T.TOOL_SPECS) == 3
    names = {s["function"]["name"] for s in T.TOOL_SPECS}
    assert names == {"search_kb", "read_file", "write_file"}
    for s in T.TOOL_SPECS:
        assert s["type"] == "function"
        assert s["function"]["parameters"]["type"] == "object"
        assert "required" in s["function"]["parameters"]


# ---- 回归：双重转义的 content 必须还原成真实换行 ----
def test_write_file_unescapes_double_backslash_n(tmp_path, monkeypatch):
    """曾经的 bug：模型传来的 content 是双重转义（\\\\n），
    直接把整段脚本写成了单行，文件语法错误。"""
    import ast
    monkeypatch.setattr(T, "WORKSPACE", tmp_path)
    monkeypatch.setattr(T, "WRITE_ROOTS", [tmp_path])
    monkeypatch.setattr(T, "READ_ROOTS", [tmp_path])

    escaped = "import sys\\n\\ndef main():\\n    print('hi')\\n"
    r = T.write_file("exp.py", escaped)
    assert r.ok
    text = (tmp_path / "exp.py").read_text(encoding="utf-8")
    assert "\n" in text, "换行没有被还原，脚本会写成一行"
    assert "\\n" not in text
    ast.parse(text)          # 必须是合法 Python


def test_write_file_keeps_real_newlines(tmp_path, monkeypatch):
    """已经是真实换行的内容不能被再处理坏。"""
    monkeypatch.setattr(T, "WORKSPACE", tmp_path)
    monkeypatch.setattr(T, "WRITE_ROOTS", [tmp_path])
    src = "a = 1\nb = 2\n"
    T.write_file("x.py", src)
    assert (tmp_path / "x.py").read_text(encoding="utf-8") == src


def test_unescape_body_handles_quotes():
    out = T._unescape_body('print(\\"hello\\")')
    assert out == 'print("hello")'
