"""增量重建：向量缓存复用、FTS 同步、原子切换与失败回滚。"""
from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

import numpy as np
import pytest

from kb import manifest as manifest_mod
from kb.config import Config
from kb.fts import FtsIndex
from kb.reindex import CACHE_NAME, ReindexError, run_reindex
from kb.vectors import VectorIndex


class FakeEmbedder:
    available = True
    backend = "fake"

    def __init__(self, dim: int = 4, fail: bool = False):
        self.dim = dim
        self.fail = fail
        self.calls: list[int] = []
        self.texts: list[str] = []

    def encode(self, texts, batch_size=32, is_query=False, show_progress=False):
        texts = list(texts)
        if self.fail:
            raise RuntimeError("boom")
        self.calls.append(len(texts))
        self.texts.extend(texts)
        rows = []
        for t in texts:
            h = hashlib.sha256(t.encode("utf-8")).digest()
            v = np.frombuffer(h[: self.dim], dtype=np.uint8).astype(np.float32) + 1.0
            v = v / float(np.linalg.norm(v))
            rows.append(v)
        if not rows:
            return np.zeros((0, self.dim), dtype=np.float32)
        return np.vstack(rows)


class UnavailableEmbedder:
    available = False
    backend = "none"
    dim = 0
    last_error = "test: no model"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


A_DOC = """---
title: RSA 共模
category: crypto
tags: [rsa]
signals: [n 相同]
---

## 原理
alpha_原理 同余关系。

## 脚本
bravo_脚本 扩展欧几里得。
"""

B_DOC = """---
title: SSTI
category: web
tags: [ssti]
signals: [模板注入]
---

## 识别
charlie_web 模板回显。
"""

C_DOC = """---
title: ret2libc
category: pwn
tags: [rop]
signals: [栈溢出]
---

## 利用
delta_pwn 泄露 libc。
"""


@pytest.fixture()
def env(tmp_path: Path):
    cfg = Config.load(tmp_path / "missing.toml")
    cfg.data["kb"]["root"] = str(tmp_path)
    kb = tmp_path / "kb"
    _write(kb / "crypto" / "a.md", A_DOC)
    _write(kb / "web" / "b.md", B_DOC)
    _write(kb / "pwn" / "c.md", C_DOC)
    return cfg, kb


def _manifest(cfg) -> dict[str, str]:
    return manifest_mod.load(Path(cfg.index_dir) / manifest_mod.MANIFEST_NAME) or {}


def _cache_rows(cfg) -> int:
    conn = sqlite3.connect(Path(cfg.index_dir) / CACHE_NAME)
    try:
        return conn.execute("SELECT COUNT(*) FROM chunk_cache").fetchone()[0]
    finally:
        conn.close()


def _cache_keys(cfg) -> set[tuple[str, int]]:
    conn = sqlite3.connect(Path(cfg.index_dir) / CACHE_NAME)
    try:
        return {(r[0], int(r[1])) for r in
                conn.execute("SELECT rel_path, chunk_index FROM chunk_cache")}
    finally:
        conn.close()


def _embedding(cfg, doc_path: str) -> bytes:
    # 用 VectorIndex 的连接逻辑，sqlite-vec 可用时先加载 vec0 扩展。
    conn = VectorIndex(Path(cfg.index_dir) / "vectors.db", None)._connect()
    try:
        return conn.execute(
            "SELECT v.embedding FROM vec_chunks v JOIN chunk_meta m ON m.rowid=v.rowid"
            " WHERE m.doc_path=? ORDER BY v.rowid LIMIT 1", (doc_path,)
        ).fetchone()[0]
    finally:
        conn.close()


def test_full_then_incremental(env):
    cfg, kb = env
    emb = FakeEmbedder()

    first = run_reindex(cfg, embedder=emb)
    assert first["status"] == "ok"
    assert first["docs"] == 3
    assert first["reused"] == 0
    assert first["reencoded"] == first["chunks"]
    assert first["chunks"] == 4  # a 两个章节 + b + c
    assert emb.calls == [4]

    assert (Path(cfg.index_dir) / "manifest.json").exists()
    assert set(_manifest(cfg)) == {"crypto/a.md", "web/b.md", "pwn/c.md"}
    assert FtsIndex(Path(cfg.index_dir) / "fts.db").search("alpha_原理", top_k=3)
    assert VectorIndex(Path(cfg.index_dir) / "vectors.db", emb).stats()["count"] == "4"
    assert _cache_rows(cfg) == 4
    b_vec_before = _embedding(cfg, "web/b.md")

    # 改一篇（a 的脚本章节）、加一篇、删一篇
    _write(kb / "crypto" / "a.md",
           A_DOC.replace("bravo_脚本 扩展欧几里得。", "bravo_脚本 marker_new 扩展欧几里得。"))
    _write(kb / "misc" / "d.md",
           "---\ntitle: 新条目\ncategory: misc\n---\n\n## 内容\nfoxtrot_new 新文档。\n")
    (kb / "pwn" / "c.md").unlink()

    emb2 = FakeEmbedder()
    second = run_reindex(cfg, embedder=emb2)
    assert second["status"] == "ok"
    assert second["added_docs"] == 1
    assert second["changed_docs"] == 1
    assert second["removed_docs"] == 1
    assert second["chunks"] == 4
    # 只重编码 a 的「脚本」块 + 新增 d；a 的「原理」块与 b 复用缓存。
    assert second["reused"] == 2
    assert second["reencoded"] == 2
    assert second["removed_chunks"] == 1
    assert emb2.calls == [2]
    assert sum("marker_new" in t for t in emb2.texts) == 1
    assert all("alpha_原理" not in t for t in emb2.texts)
    assert all("charlie_web" not in t for t in emb2.texts)

    fts = FtsIndex(Path(cfg.index_dir) / "fts.db")
    assert fts.search("marker_new", top_k=3)[0].doc_path == "crypto/a.md"
    assert fts.search("foxtrot_new", top_k=3)[0].doc_path == "misc/d.md"
    assert fts.get_doc("pwn/c.md") is None
    assert _embedding(cfg, "web/b.md") == b_vec_before

    assert set(_manifest(cfg)) == {"crypto/a.md", "web/b.md", "misc/d.md"}
    assert _cache_keys(cfg) == {
        ("crypto/a.md", 0), ("crypto/a.md", 1), ("web/b.md", 0), ("misc/d.md", 0),
    }


def test_fts_only_keeps_vectors(env):
    cfg, kb = env
    run_reindex(cfg, embedder=FakeEmbedder())
    vec_bytes = (Path(cfg.index_dir) / "vectors.db").read_bytes()
    cache_bytes = (Path(cfg.index_dir) / CACHE_NAME).read_bytes()

    _write(kb / "web" / "b.md", B_DOC.replace("charlie_web", "hotel_fts_only"))
    res = run_reindex(cfg, fts_only=True, embedder=UnavailableEmbedder())
    assert res["status"] == "fts_only"
    assert res["vectors_stale"] is True
    assert res["reused"] == 0 and res["reencoded"] == 0

    assert FtsIndex(Path(cfg.index_dir) / "fts.db").search("hotel_fts_only", top_k=3)
    assert (Path(cfg.index_dir) / "vectors.db").read_bytes() == vec_bytes
    assert (Path(cfg.index_dir) / CACHE_NAME).read_bytes() == cache_bytes
    assert set(_manifest(cfg)) == {"crypto/a.md", "web/b.md", "pwn/c.md"}


def test_vector_failure_rolls_back_old_index(env):
    cfg, kb = env
    run_reindex(cfg, embedder=FakeEmbedder())
    fts_before = (Path(cfg.index_dir) / "fts.db").read_bytes()
    vec_before = (Path(cfg.index_dir) / "vectors.db").read_bytes()
    manifest_before = (Path(cfg.index_dir) / "manifest.json").read_bytes()

    _write(kb / "web" / "b.md", B_DOC.replace("charlie_web", "india_broken"))
    with pytest.raises(ReindexError) as exc:
        run_reindex(cfg, embedder=FakeEmbedder(fail=True))
    assert exc.value.stage == "vectors"

    assert (Path(cfg.index_dir) / "fts.db").read_bytes() == fts_before
    assert (Path(cfg.index_dir) / "vectors.db").read_bytes() == vec_before
    assert (Path(cfg.index_dir) / "manifest.json").read_bytes() == manifest_before
    for name in ("fts.db.new", "vectors.db.new", CACHE_NAME + ".new", "manifest.json.new"):
        assert not (Path(cfg.index_dir) / name).exists()
    assert not FtsIndex(Path(cfg.index_dir) / "fts.db").search("india_broken", top_k=3)


def test_unavailable_embedder_reports_failure_not_ready(env):
    cfg, _ = env
    run_reindex(cfg, embedder=FakeEmbedder())
    fts_before = (Path(cfg.index_dir) / "fts.db").read_bytes()
    with pytest.raises(ReindexError) as exc:
        run_reindex(cfg, embedder=UnavailableEmbedder())
    assert exc.value.stage == "vectors"
    assert "嵌入模型不可用" in exc.value.message
    assert (Path(cfg.index_dir) / "fts.db").read_bytes() == fts_before
