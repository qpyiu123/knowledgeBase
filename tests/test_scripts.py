"""tools/scripts 只读工具库的离线冒烟测试。

只运行本仓库脚本，输入全部在 tmp_path 内生成；不联网、不执行用户内容。
"""
from __future__ import annotations

import io
import json
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_json(script: str, *args: str) -> dict:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "scripts" / script), *args, "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def test_rsa_factor_probe_runs_read_only():
    out = run_json("crypto/rsa_factor_probe.py", "--n", "143")
    assert out["read_only"] is True
    assert out["n_bits"] == 8
    assert out["small_factors"] == {"11": 1}
    assert out["cofactor"] == "13"
    assert out["cofactor_probable_prime"] is True
    assert out["fully_factored"] is False


def test_zip_inspect_lists_and_greps_without_extracting(tmp_path: Path):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("game/Main.class", b"\xca\xfe\xba\xbe")
        z.writestr("game/flag.txt", "flag{script_lib}")
        z.writestr("META-INF/MANIFEST.MF", "Manifest-Version: 1.0\n")
    jar = tmp_path / "sample.jar"
    jar.write_bytes(buf.getvalue())

    out = run_json("forensics/zip_inspect.py", "--zip", str(jar), "--grep", "flag")
    assert out["read_only"] is True
    assert out["entry_count"] == 3
    assert out["file_count"] == 3
    assert out["name_hits"] == ["game/flag.txt"]
    assert any("flag" == hit["match"] for hit in out["content_hits"])
    assert not (tmp_path / "game").exists()


def test_filter_probe_never_executes_payload():
    out = run_json(
        "misc/filter_probe.py",
        "--blacklist", "eval,exec,__class__",
        "--payload", "{print(open('flag').read())}",
    )
    assert out["read_only"] is True
    assert out["executed"] is False
    assert out["hit_count"] == 0
    assert out["match"] is True
    assert out["has_braces"] is True
