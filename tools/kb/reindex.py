"""增量重建：内容清单 + 向量分块缓存 + 临时库原子切换。

设计要点：
- FTS 仍然整库重建（块数固定、耗时短），但写入 ``fts.db.new``；
- 向量按 ``(rel_path, chunk_index)`` 的 chunk 文本 sha256 复用旧向量，
  只把新增/变化的块送去编码；
- 只有 FTS、向量、缓存、manifest 全部成功后才替换正式文件；
  任一步失败都删除临时文件、保留旧索引，并抛出带阶段名的 ReindexError。
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Any, Callable, Iterable

import numpy as np

from . import manifest
from .fts import FtsIndex
from .parser import Doc, chunk_doc, iter_docs
from .vectors import VectorIndex

CACHE_NAME = "vectors_cache.db"
CACHE_SCHEMA = """
CREATE TABLE IF NOT EXISTS chunk_cache(
    rel_path TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    sha256 TEXT NOT NULL,
    dim INTEGER NOT NULL,
    embedding BLOB NOT NULL,
    PRIMARY KEY(rel_path, chunk_index)
);
CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT);
"""


class ReindexError(RuntimeError):
    """重建失败；stage 取值 scan/fts/vectors/manifest/swap。"""

    def __init__(self, stage: str, message: str):
        super().__init__(message)
        self.stage = stage
        self.message = message


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _remove(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass
    except OSError:
        pass


def _replace(src: Path, dst: Path, retries: int = 25, delay: float = 0.2) -> None:
    """同盘 os.replace；Windows 上对短暂占用重试。"""
    last: Exception | None = None
    for _ in range(retries):
        try:
            os.replace(src, dst)
            return
        except PermissionError as e:  # 杀软/索引服务/旧连接短暂占用
            last = e
            time.sleep(delay)
    raise ReindexError("swap", f"替换 {dst.name} 失败: {last}")


def _load_cache(path: Path) -> tuple[dict[tuple[str, int], tuple[str, bytes]], dict[str, str]]:
    if not path.exists():
        return {}, {}
    entries: dict[tuple[str, int], tuple[str, bytes]] = {}
    meta: dict[str, str] = {}
    try:
        conn = sqlite3.connect(path)
        try:
            for k, v in conn.execute("SELECT k, v FROM meta"):
                meta[str(k)] = str(v)
            for rel, idx, sha, _dim, blob in conn.execute(
                "SELECT rel_path, chunk_index, sha256, dim, embedding FROM chunk_cache"
            ):
                entries[(str(rel), int(idx))] = (str(sha), bytes(blob))
        finally:
            conn.close()
    except sqlite3.Error:
        return {}, {}
    return entries, meta


def _write_cache(path: Path, items: list[dict[str, Any]], hashes: list[str],
                 mat: np.ndarray, backend: str) -> None:
    _remove(path)
    dim = int(mat.shape[1]) if len(items) else 0
    conn = sqlite3.connect(path)
    try:
        conn.executescript(CACHE_SCHEMA)
        with conn:
            conn.executemany(
                "INSERT OR REPLACE INTO chunk_cache"
                "(rel_path, chunk_index, sha256, dim, embedding) VALUES (?,?,?,?,?)",
                [
                    (it["doc_path"], int(it["chunk_index"]), sha, int(v.shape[0]),
                     v.astype(np.float32).tobytes())
                    for it, sha, v in zip(items, hashes, mat)
                ],
            )
            conn.execute("INSERT OR REPLACE INTO meta(k,v) VALUES ('dim',?)", (str(dim),))
            conn.execute("INSERT OR REPLACE INTO meta(k,v) VALUES ('backend',?)", (backend,))
            conn.execute("INSERT OR REPLACE INTO meta(k,v) VALUES ('built_at',?)",
                         (time.strftime("%Y-%m-%d %H:%M:%S"),))
            conn.execute("INSERT OR REPLACE INTO meta(k,v) VALUES ('count',?)",
                         (str(len(items)),))
    finally:
        conn.close()


def _build_items(docs: Iterable[Doc], chunk_chars: int, overlap: int
                 ) -> tuple[list[dict[str, Any]], list[str]]:
    items: list[dict[str, Any]] = []
    hashes: list[str] = []
    for doc in docs:
        for ch in chunk_doc(doc, chunk_chars, overlap):
            items.append({
                "doc_path": doc.path,
                "chunk_index": int(ch["chunk_index"]),
                "title": doc.title,
                "category": doc.category,
                "section": ch["section"],
                "text": ch["text"],
            })
            hashes.append(_sha256(ch["text"]))
    return items, hashes


def run_reindex(
    cfg,
    *,
    chunk_chars: int | None = None,
    overlap: int | None = None,
    batch_size: int | None = None,
    fts_only: bool = False,
    embedder=None,
    on_progress: Callable[[str, int, int], None] | None = None,
) -> dict[str, Any]:
    """执行一次重建。

    无 manifest/无缓存时自动退化为全量；返回统计或抛出 ReindexError。
    """
    kb_dir = Path(cfg.kb_dir)
    index_dir = Path(cfg.index_dir)
    index_dir.mkdir(parents=True, exist_ok=True)
    chunk_chars = int(chunk_chars if chunk_chars is not None
                      else cfg.get("search", "chunk_chars", 900))
    overlap = int(overlap if overlap is not None
                  else cfg.get("search", "chunk_overlap", 120))
    batch_size = int(batch_size if batch_size is not None
                     else cfg.get("embed", "batch_size", 32))

    docs = list(iter_docs(kb_dir))
    if not docs:
        raise ReindexError("scan", f"kb 目录为空: {kb_dir}")
    try:
        new_manifest = manifest.scan(kb_dir)
    except OSError as e:
        raise ReindexError("manifest", f"扫描 kb 失败: {e}") from e
    old_manifest = manifest.load(index_dir / manifest.MANIFEST_NAME)
    added, removed, changed = manifest.diff(old_manifest, new_manifest)

    t0 = time.time()
    fts_db = index_dir / "fts.db"
    vec_db = index_dir / "vectors.db"
    cache_db = index_dir / CACHE_NAME
    tmp_fts = index_dir / "fts.db.new"
    tmp_vec = index_dir / "vectors.db.new"
    tmp_cache = index_dir / (CACHE_NAME + ".new")
    tmp_manifest = index_dir / (manifest.MANIFEST_NAME + ".new")
    for p in (tmp_fts, tmp_vec, tmp_cache, tmp_manifest):
        _remove(p)

    try:
        # ---- 1. FTS：整库重建到临时文件 ----
        try:
            fst = FtsIndex(tmp_fts).rebuild(
                docs, chunk_chars, overlap,
                on_progress=(lambda i, n: on_progress("fts", i, n)) if on_progress else None,
            )
        except Exception as e:  # noqa: BLE001
            raise ReindexError("fts", f"FTS 重建失败: {type(e).__name__}: {e}") from e

        stats: dict[str, Any] = {
            "status": "fts_only" if fts_only else "ok",
            "docs": fst["docs"],
            "chunks": fst["chunks"],
            "added_docs": len(added),
            "changed_docs": len(changed),
            "removed_docs": len(removed),
            "reused": 0,
            "reencoded": 0,
            "removed_chunks": 0,
            "fts_seconds": fst["seconds"],
        }

        if fts_only:
            tmp_manifest.write_text(manifest.render(new_manifest), encoding="utf-8")
            _replace(tmp_fts, fts_db)
            _replace(tmp_manifest, index_dir / manifest.MANIFEST_NAME)
            stats["seconds"] = round(time.time() - t0, 2)
            stats["vectors_stale"] = True
            return stats

        # ---- 2. 向量：按 chunk 哈希复用 + 只编码新增/变化块 ----
        if embedder is None:
            try:
                from .rag import KB
                embedder = KB(cfg).embedder
            except Exception as e:  # noqa: BLE001
                raise ReindexError("vectors", f"初始化嵌入后端失败: {e}") from e
        if not getattr(embedder, "available", False):
            reason = getattr(embedder, "last_error", None) or "未知原因"
            raise ReindexError("vectors", f"嵌入模型不可用: {reason}")

        items, hashes = _build_items(docs, chunk_chars, overlap)
        old_entries, cache_meta = _load_cache(cache_db)
        cache_dim = int(cache_meta.get("dim") or 0)
        try:
            emb_dim = int(getattr(embedder, "dim", 0) or 0)
        except Exception:  # noqa: BLE001
            emb_dim = 0
        if cache_dim and emb_dim and cache_dim != emb_dim:
            old_entries = {}
            cache_dim = 0
        expected_dim = emb_dim or cache_dim

        by_index: dict[int, np.ndarray] = {}
        to_encode: list[str] = []
        to_idx: list[int] = []
        reused = 0
        for i, (it, sha) in enumerate(zip(items, hashes)):
            key = (it["doc_path"], it["chunk_index"])
            ent = old_entries.get(key)
            if ent and ent[0] == sha:
                vec = np.frombuffer(ent[1], dtype=np.float32)
                if not expected_dim or vec.shape[0] == expected_dim:
                    by_index[i] = vec
                    reused += 1
                    continue
            to_encode.append(it["text"])
            to_idx.append(i)

        if to_encode:
            try:
                encoded = np.asarray(
                    embedder.encode(to_encode, batch_size=batch_size), dtype=np.float32)
            except Exception as e:  # noqa: BLE001
                raise ReindexError("vectors", f"向量编码失败: {type(e).__name__}: {e}") from e
            if encoded.ndim != 2 or encoded.shape[0] != len(to_idx):
                raise ReindexError(
                    "vectors",
                    f"编码结果异常: shape={getattr(encoded, 'shape', None)}, "
                    f"期望 {len(to_idx)} 条")
            for i, v in zip(to_idx, encoded):
                by_index[i] = v
            final_dim = int(encoded.shape[1])
        elif items:
            final_dim = int(by_index[0].shape[0])
        else:
            final_dim = 0

        bad = [i for i in range(len(items))
               if i in by_index and int(by_index[i].shape[0]) != final_dim]
        if bad:
            raise ReindexError("vectors", "缓存向量维度与当前模型不一致，请删除 index/vectors_cache.db 后重建")
        if items:
            mat = np.vstack([by_index[i] for i in range(len(items))])
        else:
            mat = np.zeros((0, final_dim), dtype=np.float32)

        try:
            VectorIndex.write_store(tmp_vec, items, mat)
        except Exception as e:  # noqa: BLE001
            raise ReindexError("vectors", f"写入向量库失败: {type(e).__name__}: {e}") from e

        new_keys = {(it["doc_path"], it["chunk_index"]) for it in items}
        removed_chunks = sum(1 for k in old_entries if k not in new_keys)
        stats.update({
            "reused": reused,
            "reencoded": len(to_idx) if to_encode else 0,
            "removed_chunks": removed_chunks,
            "dim": final_dim,
            "backend": "sqlite-vec" if _sqlite_vec_available() else "numpy",
        })

        backend = str(stats["backend"])
        try:
            _write_cache(tmp_cache, items, hashes, mat, backend)
        except Exception as e:  # noqa: BLE001
            raise ReindexError("vectors", f"写入向量缓存失败: {type(e).__name__}: {e}") from e

        tmp_manifest.write_text(manifest.render(new_manifest), encoding="utf-8")

        # ---- 3. 全部成功后切换；临时文件先全部写好 ----
        _replace(tmp_vec, vec_db)
        _replace(tmp_cache, cache_db)
        _replace(tmp_fts, fts_db)
        _replace(tmp_manifest, index_dir / manifest.MANIFEST_NAME)

        stats["seconds"] = round(time.time() - t0, 2)
        stats["vectors_stale"] = False
        return stats
    finally:
        for p in (tmp_fts, tmp_vec, tmp_cache, tmp_manifest):
            _remove(p)


def _sqlite_vec_available() -> bool:
    from .vectors import HAS_SQLITE_VEC
    return bool(HAS_SQLITE_VEC)


def read_manifest(index_dir: Path) -> dict[str, str] | None:
    """便捷函数：读取 index/manifest.json。"""
    return manifest.load(Path(index_dir) / manifest.MANIFEST_NAME)


def manifest_info(index_dir: Path) -> dict[str, Any]:
    path = Path(index_dir) / manifest.MANIFEST_NAME
    if not path.exists():
        return {"exists": False}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"exists": True, "valid": False}
    return {
        "exists": True,
        "valid": data.get("version") == manifest.MANIFEST_VERSION,
        "version": data.get("version"),
        "built_at": data.get("built_at"),
        "count": len(data.get("files") or {}),
    }
