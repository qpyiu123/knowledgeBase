"""P2 附件侦察：结构化分析、隔离落盘与安全边界。"""
from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import subprocess
import zipfile
from pathlib import Path

import pytest

from agent import attachment
from eval_attachments import (
    BUILDERS,
    build_png_appended_zip,
    evaluate_cases,
    load_cases,
)


def _zip(files: dict[str, str]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, text in files.items():
            z.writestr(name, text)
    return buf.getvalue()


def test_png_report_detects_type_carve_and_decode():
    data, name = build_png_appended_zip()
    report = attachment.analyze_bytes(data, name)

    assert report["type"]["kind"] == "PNG 图片"
    assert report["type"]["extension_mismatch"] is False
    assert any(c["type"] == "ZIP" for c in report["carve"])
    decoded = [d["decoded"] for d in report["decoded"]]
    assert "flag{p2_c4rv3_d3c0d3}" in decoded
    assert any("IEND" in a for a in report["anomalies"])
    assert report["structures"]["png"]["width"] == 1
    assert report["executed"] is False
    assert "未执行" in report["execution_note"]


def test_report_is_structured_and_has_hash():
    data = b"hello CTF\n"
    report = attachment.analyze_bytes(data, "note.txt")

    assert report["schema_version"] == 1
    assert report["file"]["size"] == len(data)
    assert report["file"]["sha256"] == hashlib.sha256(data).hexdigest()
    assert report["type"]["is_text"] is True
    assert "hello CTF" in report["type"]["preview"]
    assert report["carve"] == []


def test_fake_extension_and_zip_entries():
    data = _zip({"readme.txt": "just a zip"})
    report = attachment.analyze_bytes(data, "fake.png")

    assert report["type"]["kind"].startswith("ZIP")
    assert report["type"]["extension_mismatch"] is True
    assert any("扩展名 .png" in a for a in report["anomalies"])
    assert report["structures"]["zip"]["entries"][0]["name"] == "readme.txt"


def test_base64_decode_is_strict_and_structured():
    flag = "flag{p2_text_d3cod3}"
    data = ("hint: " + base64.b64encode(flag.encode()).decode() + "\n").encode()
    report = attachment.analyze_bytes(data, "hint.txt")

    assert report["decoded"] == [{
        "method": "base64",
        "encoded": base64.b64encode(flag.encode()).decode(),
        "decoded": flag,
        "truncated": False,
    }]


def test_script_extension_only_warns_never_executes(monkeypatch):
    def boom(*_a, **_k):
        raise AssertionError("附件分析不允许执行外部命令")

    monkeypatch.setattr(subprocess, "run", boom)
    monkeypatch.setattr(subprocess, "Popen", boom)
    monkeypatch.setattr(attachment._recon, "run_tool", boom)

    data = b"print('hello')\n# flag{p2_n0_exec}\n"
    report = attachment.analyze_bytes(data, "run.py")

    assert report["executed"] is False
    assert any("不会运行" in w for w in report["warnings"])
    assert report["type"]["is_text"] is True


def test_safe_filename_strips_paths_and_dangerous_chars():
    assert attachment.safe_filename("../../etc/passwd") == "passwd"
    assert attachment.safe_filename("..\\..\\win.ini") == "win.ini"
    assert attachment.safe_filename('a<b>:c?.txt') == "a_b__c_.txt"
    assert attachment.safe_filename("   ") == "attachment.bin"
    assert attachment.safe_filename("x" * 300).endswith("x")


def test_save_attachment_uses_isolated_directory(tmp_path: Path):
    root = tmp_path / "attachments"
    saved = attachment.save_attachment(b"abc", "../../evil.txt", root)

    target = Path(saved["saved"])
    assert target.is_file()
    assert target.read_bytes() == b"abc"
    assert target.parent.parent == root
    assert target.parent != root
    assert target.name == "upload_evil.txt"
    assert saved["sha256"] == hashlib.sha256(b"abc").hexdigest()
    assert saved["original_name"] == "../../evil.txt"


def test_analyze_upload_copies_then_analyzes(tmp_path: Path):
    root = tmp_path / "attachments"
    report = attachment.analyze_upload(b"hello", "note.txt", root)

    assert report["storage"]["isolated"] is True
    saved = Path(report["storage"]["saved"])
    assert saved.is_file()
    assert saved.read_bytes() == b"hello"
    assert saved.parent.parent == root


def test_analyze_probe_text_compatibility():
    data, name = build_png_appended_zip()
    ok, text = attachment.analyze_probe(name, data=data)
    assert ok is True
    assert "类型判定: PNG 图片" in text
    assert "内嵌文件（雕刻结果）" in text
    assert "flag{p2_c4rv3_d3c0d3}" in text


# ---------------------------------------------------------------- 可复现评测
def test_attachment_eval_all_cases_pass():
    result = evaluate_cases(load_cases())
    assert result["total"] >= 5
    assert result["failed"] == 0, result["results"]
    assert result["pass_rate"] == 1.0


def test_attachment_eval_samples_are_deterministic():
    for builder in BUILDERS.values():
        first = builder()
        second = builder()
        assert first == second


def test_attachment_eval_rejects_unknown_builder(tmp_path: Path):
    p = tmp_path / "cases.json"
    p.write_text(json.dumps({"cases": [
        {"id": "x", "builder": "missing", "expect": {}}
    ]}), encoding="utf-8")
    with pytest.raises(ValueError):
        load_cases(p)


def test_attachment_analysis_needs_no_network_or_model(monkeypatch):
    def no_network(*_a, **_k):
        raise AssertionError("附件侦察不应联网/调用模型")

    monkeypatch.setattr(os, "system", no_network)
    monkeypatch.setattr("requests.post", no_network)
    monkeypatch.setattr("requests.get", no_network)

    report = attachment.analyze_bytes(b"plain text", "a.txt")
    assert report["type"]["is_text"] is True
