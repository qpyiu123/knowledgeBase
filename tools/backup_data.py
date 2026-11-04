"""备份知识库、索引和个人记录；恢复时只写入新的空目录。"""
from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import stat
import sys
import tempfile
from datetime import datetime
from pathlib import Path, PurePosixPath
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
DIRECTORIES = ("kb", "index", "licenses", "work/workspaces", "work/feedback", "work/attachments")


def allowed(name: str) -> bool:
    return name == "config.toml" or any(name.startswith(d + "/") for d in DIRECTORIES)


def backup(root: Path = ROOT, output: Path | None = None) -> Path:
    root = root.resolve()
    backup_dir = root / "backup"
    backup_dir.mkdir(exist_ok=True)
    output = output or backup_dir / f"ctf_kb_{datetime.now():%Y%m%d_%H%M%S_%f}.zip"
    paths = []
    for name in DIRECTORIES:
        base = root / name
        if base.exists():
            paths.extend(p for p in base.rglob("*") if p.is_file()
                         and p.resolve().is_relative_to(base.resolve())
                         and "__pycache__" not in p.parts and p.suffix not in (".pyc", ".new")
                         and not p.name.endswith(("-wal", "-shm", "-journal")))
    if (root / "config.toml").is_file():
        paths.append(root / "config.toml")
    if not paths:
        raise ValueError("没有可备份的资料或记录")
    # SQLite 备份接口可读取服务正在使用的库，包含已提交的 WAL 内容。
    with tempfile.TemporaryDirectory(prefix=".snapshot_", dir=backup_dir) as tmp:
        with ZipFile(output, "x", compression=ZIP_DEFLATED) as archive:
            names = []
            for i, path in enumerate(sorted(paths)):
                name = path.relative_to(root).as_posix()
                if path.suffix == ".db":
                    snapshot = Path(tmp) / f"{i}.db"
                    source = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
                    target = sqlite3.connect(snapshot)
                    try:
                        source.backup(target)
                    finally:
                        source.close()
                        target.close()
                    archive.write(snapshot, name)
                else:
                    archive.write(path, name)
                names.append(name)
            archive.writestr("backup-manifest.json", json.dumps(
                {"schema": 1, "created_at": datetime.now().isoformat(), "files": names},
                ensure_ascii=False, indent=2))
    return output


def restore(archive_path: Path, destination: Path) -> int:
    destination = destination.resolve()
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise ValueError("恢复目录必须为空，请指定一个新目录，原资料会保留")
    with ZipFile(archive_path) as archive:
        files = []
        names = set()
        for item in archive.infolist():
            name = item.filename
            if name == "backup-manifest.json" or item.is_dir():
                continue
            path = PurePosixPath(name)
            if ("\\" in name or ":" in name or path.is_absolute() or ".." in path.parts
                    or not allowed(name) or name in names
                    or stat.S_ISLNK(item.external_attr >> 16)):
                raise ValueError(f"备份中有不支持的路径：{name}")
            names.add(name)
            files.append(item)
        bad = archive.testzip()
        if bad:
            raise ValueError(f"备份文件损坏：{bad}")
        destination.mkdir(parents=True, exist_ok=True)
        for item in files:
            target = destination / item.filename
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(item) as source, target.open("xb") as output:
                shutil.copyfileobj(source, output)
    return len(files)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--restore", type=Path)
    parser.add_argument("--destination", type=Path)
    args = parser.parse_args()
    try:
        if args.restore:
            if not args.destination:
                parser.error("恢复时请用 --destination 指定新目录")
            print(f"已恢复 {restore(args.restore, args.destination)} 个文件到 {args.destination}")
        else:
            print(f"备份已生成：{backup(args.root, args.output)}")
    except (OSError, ValueError, sqlite3.Error) as exc:
        print(f"备份或恢复失败：{exc}")
        return 1
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    raise SystemExit(main())
