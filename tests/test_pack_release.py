"""用小文件验证打包选择、索引核对和隐私文件排除。"""

import json
from pathlib import Path
import sqlite3
import tomllib

import pytest

import pack_release as release
from kb import manifest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "项目 源"

    def put(path, text="test"):
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    for path in (
        *release.CORE,
        "docs/离线包使用说明.md",
        "kb/misc/example.md",
        "kb/_methods/scripts/example.py",
        "work/workspaces/private.json",
        "logs/web.log",
        ".git/config",
        ".venv/Scripts/python.exe",
        f"{release.WEB}/dist/assets/site.js",
        f"{release.PYTHON}/Lib/__pycache__/junk.pyc",
        f"{release.NATIVE}/llama-server.exe",
        f"{release.NATIVE}/llama-server-impl.dll",
        f"{release.NATIVE}/ggml-vulkan.dll",
        f"{release.NATIVE}/LICENSE-LLVM-OpenMP",
        "licenses/llama.cpp-b11669-LICENSE",
        "licenses/Apache-2.0.txt",
        "index/vectors_cache.db",
    ):
        put(path)
    for name in ("model_quantized.onnx", "tokenizer.json", "vocab.txt", "config.json"):
        put(f"{release.ONNX}/{name}")
    put(f"{release.WEB}/package.json", '{"version":"2.0.0"}')
    put(
        f"{release.WEB}/package-lock.json",
        json.dumps(
            {
                "packages": {
                    "node_modules/example": {"version": "1.0.0"},
                    "node_modules/dev-tool": {"version": "1.0.0", "dev": True},
                }
            }
        ),
    )
    put(f"{release.WEB}/node_modules/example/package.json", '{"version":"1.0.0"}')
    put(f"{release.WEB}/node_modules/example/LICENSE")
    models = []
    for model in ("qwen35-9b", "qwen35-4b", "old-qwen3"):
        path = f"models/gguf/{model}.gguf"
        put(path)
        models.append({"id": model, "role": "chat", "path": path, "bytes": 4})
    put("docs/data/llama-resources.json", json.dumps({"artifacts": models}))
    put("config.toml", (ROOT / "config.toml").read_text(encoding="utf-8"))
    manifest.save(root / "index/manifest.json", manifest.scan(root / "kb"))
    for name, sql in (
        (
            "fts.db",
            "create table docs(path); insert into docs values('misc/example.md'); create table chunks(id); insert into chunks values(1);",
        ),
        ("vectors.db", "create table chunk_meta(id); insert into chunk_meta values(1);"),
    ):
        db = sqlite3.connect(root / "index" / name)
        try:
            db.executescript(sql)
        finally:
            db.close()
    return root


@pytest.mark.parametrize(
    "profile,models",
    [
        ("both", ["qwen35-9b", "qwen35-4b"]),
        ("9b", ["qwen35-9b"]),
        ("4b", ["qwen35-4b"]),
        ("none", []),
    ],
)
def test_pack_profiles(project, tmp_path, profile, models):
    target = tmp_path / "新目录 带空格"
    result = release.pack(project, target, profile)
    config = tomllib.loads((target / "config.toml").read_text(encoding="utf-8"))
    assert result["default_model"] == (models[0] if models else None)
    assert {p.stem for p in target.rglob("*.gguf")} == set(models)
    assert config["llm"]["backend"] == ("llama_server" if models else "none")
    assert config["runtime"]["python"] == "auto" and config["kb"]["root"] == "."
    assert (target / release.NATIVE).is_dir() == bool(models)
    assert result["index"] == {"docs": 1, "chunks": 1, "vector_chunks": 1}
    assert (target / "licenses/frontend/example/LICENSE").is_file()
    for name in (".git", ".venv", "logs", "work", f"{release.WEB}/node_modules"):
        assert not (target / name).exists()
    assert not list(target.rglob("*.pyc"))
    assert (project / "models/gguf/old-qwen3.gguf").exists()
    assert sum(result["files"].values()) == result["bytes"]


def test_existing_destination_is_not_overwritten(project, tmp_path):
    target = tmp_path / "existing"
    target.mkdir()
    marker = target / "do-not-overwrite.txt"
    marker.write_text("keep", encoding="utf-8")
    with pytest.raises(FileExistsError):
        release.pack(project, target, "none")
    assert marker.read_text(encoding="utf-8") == "keep"


def test_stale_index_rejected_before_copy(project, tmp_path):
    (project / "kb/misc/example.md").write_text("edited", encoding="utf-8")
    target = tmp_path / "result"
    with pytest.raises(ValueError, match="索引清单"):
        release.pack(project, target, "none")
    assert not target.exists()


def test_partial_model_rejected_before_copy(project, tmp_path):
    (project / "models/gguf/qwen35-4b.gguf").write_text("incomplete", encoding="utf-8")
    target = tmp_path / "result"
    with pytest.raises(ValueError, match="权重缺失或不完整"):
        release.pack(project, target, "both")
    assert not target.exists()
