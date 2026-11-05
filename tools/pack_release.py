"""用现有资源制作可搬运目录；不下载、不覆盖、不复制个人数据。"""

from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import sys
import tomllib
from contextlib import closing
from pathlib import Path

from kb import manifest

ROOT = Path(__file__).resolve().parents[1]
PROFILES = {
    "both": ("qwen35-9b", "qwen35-4b"),
    "9b": ("qwen35-9b",),
    "4b": ("qwen35-4b",),
    "none": (),
}
WEB = "tools/agent/webapp"
PYTHON = "runtime/python-portable"
NATIVE = "runtime/llama-b11669-vulkan"
ONNX = "models/bge-small-zh-v1.5-onnx"
INDEX_FILES = ("fts.db", "vectors.db", "vectors_cache.db", "manifest.json")
CORE = (
    "start.ps1",
    "backup.ps1",
    "tools/python-runtime.ps1",
    "tools/python_runtime.py",
    "tools/llama_runtime.py",
    "tools/cli.py",
    "tools/backup_data.py",
    "requirements-runtime.txt",
    "tools/agent/web/index.html",
    f"{WEB}/dist/index.html",
    f"{PYTHON}/python.exe",
    f"{PYTHON}/python313._pth",
    f"{PYTHON}/LICENSE.txt",
    "licenses/python-3.9-license.html",
    "licenses/离线包第三方来源.md",
    "docs/data/r4-curation.json",
    "docs/data/r1-reference-import.json",
    "licenses/BAAI-bge-small-zh-v1.5-README.md",
)
KB_TYPES = {
    ".md",
    ".py",
    ".txt",
    ".json",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".svg",
    ".c",
    ".cpp",
    ".js",
    ".sh",
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def scoped_files(base: Path, suffixes=None):
    """跳过缓存与隐藏目录，不把指向其他目录的链接装包。"""
    for path in sorted(base.rglob("*")):
        parts = path.relative_to(base).parts
        if any(p.startswith(".") or p in ("__pycache__", "node_modules") for p in parts):
            continue
        if path.is_file() and path.suffix not in (".pyc", ".pyo", ".log", ".part"):
            if suffixes is not None and path.suffix.lower() not in suffixes:
                continue
            if not path.resolve().is_relative_to(base.resolve()):
                raise ValueError(f"目录外链接不能装包：{path}")
            yield path


def frontend_notices(root: Path) -> dict[str, Path]:
    web = root / WEB
    entries = read_json(web / "package-lock.json")["packages"]
    files = {}
    for rel, meta in entries.items():
        if not rel or meta.get("dev"):
            continue
        base = web / rel
        if not base.is_dir():
            if meta.get("optional"):
                continue
            raise FileNotFoundError(f"缺少前端依赖 {rel}，请在开发环境准备构建和许可文件")
        version = read_json(base / "package.json")["version"]
        if version != meta["version"]:
            raise ValueError(f"{rel} 已安装版本与锁定版本不同，请重新准备前端构建")
        name = rel.removeprefix("node_modules/")
        for file in sorted(base.iterdir()):
            if file.is_file() and file.name.upper().startswith(
                ("LICENSE", "COPYING", "NOTICE", "LICENCE")
            ):
                files[f"licenses/frontend/{name}/{file.name}"] = file
    return files


def make_config(source: Path, selected: str | None) -> str:
    config = tomllib.loads(source.read_text(encoding="utf-8-sig"))
    search, embed = config["search"], config["embed"]
    sections = {
        "kb": {"root": ".", "kb_dir": "kb", "index_dir": "index", "models_dir": "models"},
        "runtime": {"python": "auto"},
        "search": {k: search[k] for k in ("top_k", "rrf_k", "chunk_chars", "chunk_overlap")},
        "embed": {
            "model_dir": ONNX,
            "onnx_dir": ONNX,
            "model_id": embed["model_id"],
            "query_prefix": embed["query_prefix"],
            "batch_size": embed["batch_size"],
        },
        "llm": {
            "backend": "llama_server" if selected else "none",
            "n_ctx": 8192,
            "n_threads": 6,
            "n_gpu_layers": 99,
            "temperature": 0.2,
            "max_tokens": 1200,
            "timeout": 300,
        },
        "llama_server": {
            "model": selected or "qwen35-9b",
            "runtime": NATIVE,
            "port": 8766,
            "device": "auto",
        },
        "feedback": {"file": "work/feedback/feedback.jsonl"},
        "attachment": {"dir": "work/attachments", "max_bytes": 8388608},
        "workspace": {"dir": "work/workspaces"},
    }
    return (
        "\n\n".join(
            "["
            + section
            + "]\n"
            + "\n".join(
                f"{key} = {json.dumps(value, ensure_ascii=False)}" for key, value in values.items()
            )
            for section, values in sections.items()
        )
        + "\n"
    )


def check_index(root: Path) -> dict:
    known = manifest.load(root / "index/manifest.json")
    current = manifest.scan(root / "kb")
    if not known or current.skipped or current != known:
        raise ValueError("索引清单与当前资料不同；请先完成 .\\start.ps1 -Reindex")
    with closing(sqlite3.connect((root / "index/fts.db").as_uri() + "?mode=ro", uri=True)) as db:
        indexed = {row[0] for row in db.execute("SELECT path FROM docs")}
        chunks = db.execute("SELECT count(*) FROM chunks").fetchone()[0]
    with closing(
        sqlite3.connect((root / "index/vectors.db").as_uri() + "?mode=ro", uri=True)
    ) as db:
        vector_chunks = db.execute("SELECT count(*) FROM chunk_meta").fetchone()[0]
    if indexed != set(known) or not chunks or vector_chunks != chunks:
        raise ValueError("关键词、语义索引与资料数不一致；请重新构建完整索引")
    return {"docs": len(known), "chunks": chunks, "vector_chunks": vector_chunks}


def plan(root: Path, profile: str):
    root = root.resolve()
    selected = PROFILES[profile]
    files = {name: root / name for name in CORE}
    files["开箱说明.md"] = root / "docs/离线包使用说明.md"
    for directory, suffixes in (
        ("kb", KB_TYPES),
        ("tools/kb", {".py", ".json"}),
        ("tools/agent", {".py"}),
        (f"{WEB}/dist", None),
        (PYTHON, None),
    ):
        # agent 的前端源码与依赖不随包走。
        paths = (
            sorted((root / directory).glob("*.py"))
            if directory == "tools/agent"
            else scoped_files(root / directory, suffixes)
        )
        files.update((p.relative_to(root).as_posix(), p) for p in paths)
    for name in INDEX_FILES:
        files[f"index/{name}"] = root / "index" / name
    if (root / "index/graph.db").is_file():
        files["index/graph.db"] = root / "index/graph.db"
    for name in ("model_quantized.onnx", "tokenizer.json", "vocab.txt", "config.json"):
        files[f"{ONNX}/{name}"] = root / ONNX / name
    files.update(frontend_notices(root))
    resources = read_json(root / "docs/data/llama-resources.json")
    model_records = {row["id"]: row for row in resources["artifacts"] if row["role"] == "chat"}
    if selected:
        for model in selected:
            row = model_records[model]
            weight = root / row["path"]
            if not weight.is_file() or weight.stat().st_size != row["bytes"]:
                raise ValueError(f"{model} 权重缺失或不完整，请用现有完整文件准备后重试")
            files[row["path"]] = weight
        for path in scoped_files(root / NATIVE):
            if path.suffix.lower() == ".dll" or path.name in (
                "llama-server.exe",
                "LICENSE-LLVM-OpenMP",
            ):
                files[path.relative_to(root).as_posix()] = path
        for name in (
            f"{NATIVE}/llama-server.exe",
            f"{NATIVE}/llama-server-impl.dll",
            f"{NATIVE}/ggml-vulkan.dll",
            f"{NATIVE}/LICENSE-LLVM-OpenMP",
            "licenses/llama.cpp-b11669-LICENSE",
            "licenses/Apache-2.0.txt",
        ):
            files[name] = root / name
    for name, path in files.items():
        if (
            Path(name).is_absolute()
            or ".." in Path(name).parts
            or not path.is_file()
            or not path.resolve().is_relative_to(root)
        ):
            raise FileNotFoundError(f"包所需文件缺失或在项目外：{name}")
    return files, [model_records[model] for model in selected]


def pack(root: Path, destination: Path, profile: str) -> dict:
    root, destination = root.resolve(), destination.resolve()
    if destination.exists():
        raise FileExistsError(f"输出目录已存在，请指定新目录：{destination}")
    for name in ("kb", "index", "runtime", "models", "tools", "licenses"):
        if destination.is_relative_to(root / name):
            raise ValueError("输出目录不能放在输入资料或运行资源目录内")
    files, models = plan(root, profile)
    index = check_index(root)
    settings = make_config(root / "config.toml", models[0]["id"] if models else None)
    sizes = {name: path.stat().st_size for name, path in files.items()}
    parent = next(path for path in destination.parents if path.exists())
    if sum(sizes.values()) > shutil.disk_usage(parent).free:
        raise OSError("磁盘空间不足；可选只带 4B 或仅查询的包")
    destination.mkdir(parents=True)
    for name, source in sorted(files.items()):
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if target.stat().st_size != sizes[name]:
            raise OSError(f"复制大小不一致：{name}；请指定新目录重新打包")
    (destination / "config.toml").write_text(settings, encoding="utf-8")
    sizes["config.toml"] = (destination / "config.toml").stat().st_size
    report = {
        "schema": 1,
        "application_version": read_json(root / WEB / "package.json")["version"],
        "profile": profile,
        "default_model": models[0]["id"] if models else None,
        "models": models,
        "index": index,
        "bytes": sum(sizes.values()),
        "files": sizes,
    }
    (destination / "release-manifest.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", choices=PROFILES, default="both")
    parser.add_argument("--destination", type=Path)
    args = parser.parse_args()
    destination = args.destination or ROOT / "release" / f"CTF知识库-R5-{args.models}"
    try:
        report = pack(ROOT, destination, args.models)
    except (ValueError, OSError, sqlite3.Error) as error:
        print(f"打包失败：{error}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {k: v for k, v in report.items() if k != "files"}
            | {"directory": str(destination.resolve()), "file_count": len(report["files"])},
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
