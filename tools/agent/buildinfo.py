"""代码构建指纹：用于判断正在运行的后端是否与当前代码一致。

指纹覆盖 `tools/agent/`、`tools/kb/` 下的 Python 源码与 `start.ps1`；
git 可用时附带短 HEAD。只读文件，不启动服务、不联网。
"""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _source_files(root: Path = ROOT) -> list[Path]:
    files: list[Path] = []
    for name in ("agent", "kb"):
        base = root / "tools" / name
        if base.is_dir():
            files.extend(p for p in base.rglob("*.py")
                         if "__pycache__" not in p.parts)
    extra = root / "start.ps1"
    if extra.is_file():
        files.append(extra)
    return sorted(set(files))


def fingerprint(root: Path = ROOT) -> str:
    h = hashlib.sha256()
    for path in _source_files(root):
        try:
            rel = path.relative_to(root).as_posix()
            data = path.read_bytes()
        except OSError:
            continue
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(data)
        h.update(b"\0")
    return h.hexdigest()


def git_head(root: Path = ROOT) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    if out.returncode != 0:
        return ""
    return out.stdout.strip()


def build_id(root: Path = ROOT) -> str:
    fp = fingerprint(root)[:8]
    head = git_head(root)
    return f"{head}-{fp}" if head else fp


BUILD_ID = build_id()


if __name__ == "__main__":
    print(BUILD_ID)
