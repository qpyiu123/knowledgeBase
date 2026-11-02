"""方法脚本自检冒烟测试：对 kb/_methods/scripts 下每个脚本跑 --selftest。

规则：
- 每个脚本必须支持 `--selftest`，退出码 0 才算通过；超时 30s 视为失败。
- 用仓库 .venv 的解释器（sys.executable 若已是 .venv 就用它，否则回退到 .venv 路径），
  这样 pytest 从任意目录启动都能找到同一套依赖。
- 新增方法脚本只要放到 kb/_methods/scripts/*.py 并实现 --selftest，就会自动纳入本测试。
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "kb" / "_methods" / "scripts"

TIMEOUT_S = 30


def _python_exe() -> str:
    """优先使用仓库内的 .venv 解释器。"""
    venv_py = REPO_ROOT / ".venv" / "Scripts" / "python.exe"
    if venv_py.is_file():
        return str(venv_py)
    return sys.executable


def _script_list() -> list[Path]:
    if not SCRIPTS_DIR.is_dir():
        return []
    return sorted(p for p in SCRIPTS_DIR.glob("*.py") if not p.name.startswith("_"))


SCRIPTS = _script_list()


def test_scripts_dir_exists() -> None:
    assert SCRIPTS_DIR.is_dir(), f"缺少方法脚本目录：{SCRIPTS_DIR}"
    assert SCRIPTS, f"{SCRIPTS_DIR} 下没有任何 .py 脚本"


def test_scripts_have_selftest_flag() -> None:
    """每个脚本都必须实现 --selftest（避免漏掉 CLI 入口）。"""
    missing = []
    for path in SCRIPTS:
        text = path.read_text(encoding="utf-8", errors="replace")
        if "--selftest" not in text:
            missing.append(path.name)
    assert not missing, f"这些脚本没有 --selftest：{missing}"


@pytest.mark.parametrize("script", SCRIPTS, ids=[p.stem for p in SCRIPTS])
def test_script_selftest_passes(script: Path) -> None:
    proc = subprocess.run(
        [_python_exe(), str(script), "--selftest"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=TIMEOUT_S,
    )
    detail = f"\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    assert proc.returncode == 0, f"{script.name} --selftest 退出码 {proc.returncode}{detail}"
    assert "selftest ok" in proc.stdout.lower(), f"{script.name} 没有输出 selftest ok{detail}"
