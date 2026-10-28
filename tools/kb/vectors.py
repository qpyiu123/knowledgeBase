"""向量检索层。

优先 sqlite-vec（快、零依赖库），缺失时自动降级到 numpy 暴力余弦相似度
（几千分块量级下 numpy 也只要几毫秒，完全够用）。
嵌入模型不可用（未下载）时整个向量层静默禁用，检索退化为纯 FTS。
"""
from __future__ import annotations

import sqlite3
import time
from pathlib import Path
from typing import Any, Iterable

from . import _blas  # noqa: F401
from .parser import Doc, chunk_doc

import numpy as np

try:
    import sqlite_vec  # type: ignore
    HAS_SQLITE_VEC = True
except Exception:  # pragma: no cover
    HAS_SQLITE_VEC = False

from .embedder import Embedder  # noqa: E402  （重新导出，供外部 import）


class VectorIndex:
    def __init__(self, db_path: Path, embedder: Embedder | None):
        self.db_path = Path(db_path)
        self.embedder = embedder

    @property
    def enabled(self) -> bool:
        return self.embedder is not None and self.embedder.available and self.db_path.exists()

    # ---------------- 建索引 ----------------
    def rebuild(self, docs: Iterable[Doc], chunk_chars: int = 900, overlap: int = 120,
                batch_size: int = 32, on_progress=None) -> dict[str, Any]:
        if self.embedder is None or not self.embedder.available:
            return {"enabled": False, "reason": self.embedder.last_error if self.embedder else "no embedder"}
        docs = list(docs)
        t0 = time.time()
        items: list[dict[str, Any]] = []
        for doc in docs:
            for ch in chunk_doc(doc, chunk_chars, overlap):
                items.append({
                    "doc_path": doc.path,
                    "title": doc.title,
                    "category": doc.category,
                    "section": ch["section"],
                    "text": ch["text"],
                })
        if not items:
            return {"enabled": True, "chunks": 0}

        texts = [it["text"] for it in items]
        vecs = self.embedder.encode(texts, batch_size=batch_size, show_progress=bool(on_progress))
        dim = vecs.shape[1]

        if self.db_path.exists():
            self.db_path.unlink()
        conn = sqlite3.connect(self.db_path)
        try:
            if HAS_SQLITE_VEC:
                conn.enable_load_extension(True)
                sqlite_vec.load(conn)
                conn.enable_load_extension(False)
                conn.execute(
                    f"CREATE VIRTUAL TABLE vec_chunks USING vec0(embedding float[{dim}])"
                )
            else:
                conn.execute(
                    "CREATE TABLE vec_chunks(rowid INTEGER PRIMARY KEY, embedding BLOB NOT NULL)"
                )
            conn.execute("""
                CREATE TABLE chunk_meta(
                    rowid INTEGER PRIMARY KEY, doc_path TEXT, title TEXT,
                    category TEXT, section TEXT, text TEXT
                )
            """)
            conn.execute("CREATE TABLE meta(k TEXT PRIMARY KEY, v TEXT)")

            with conn:
                for i, (it, v) in enumerate(zip(items, vecs)):
                    rid = i + 1
                    blob = v.astype(np.float32).tobytes()
                    if HAS_SQLITE_VEC:
                        conn.execute(
                            "INSERT INTO vec_chunks(rowid, embedding) VALUES (?,?)", (rid, blob)
                        )
                    else:
                        conn.execute(
                            "INSERT INTO vec_chunks(rowid, embedding) VALUES (?,?)", (rid, blob)
                        )
                    conn.execute(
                        "INSERT INTO chunk_meta(rowid,doc_path,title,category,section,text)"
                        " VALUES (?,?,?,?,?,?)",
                        (rid, it["doc_path"], it["title"], it["category"], it["section"], it["text"]),
                    )
                conn.execute("INSERT INTO meta(k,v) VALUES ('dim',?)", (str(dim),))
                conn.execute("INSERT INTO meta(k,v) VALUES ('backend',?)",
                             ("sqlite-vec" if HAS_SQLITE_VEC else "numpy",))
                conn.execute("INSERT INTO meta(k,v) VALUES ('built_at',?)",
                             (time.strftime("%Y-%m-%d %H:%M:%S"),))
                conn.execute("INSERT INTO meta(k,v) VALUES ('count',?)", (str(len(items)),))
        finally:
            conn.close()

        return {
            "enabled": True,
            "chunks": len(items),
            "dim": dim,
            "backend": "sqlite-vec" if HAS_SQLITE_VEC else "numpy",
            "seconds": round(time.time() - t0, 2),
        }

    # ---------------- 查询 ----------------
    def search(self, query: str, top_k: int = 8, category: str | None = None) -> list[dict[str, Any]]:
        if not self.enabled:
            return []
        assert self.embedder is not None
        t0 = time.time()
        qv = self.embedder.encode([query], is_query=True)[0]
        conn = self._connect()
        try:
            backend = self._meta(conn, "backend")
            fetch_n = top_k * 6 if category else top_k
            if backend == "sqlite-vec":
                rows = conn.execute(
                    "SELECT rowid, distance FROM vec_chunks WHERE embedding MATCH ?"
                    " ORDER BY distance LIMIT ?",
                    (qv.tobytes(), fetch_n),
                ).fetchall()
                scored = [(rid, 1.0 - float(dist)) for rid, dist in rows]
            else:
                scored = self._numpy_scan(conn, qv, fetch_n)
            out = []
            for rid, score in scored:
                m = conn.execute(
                    "SELECT doc_path,title,category,section,text FROM chunk_meta WHERE rowid=?",
                    (rid,),
                ).fetchone()
                if not m:
                    continue
                if category and m[2] != category:
                    continue
                out.append({
                    "doc_path": m[0], "title": m[1], "category": m[2],
                    "section": m[3], "text": m[4],
                    "score": float(score), "source": "vec",
                    "ms": round((time.time() - t0) * 1000, 1),
                })
                if len(out) >= top_k:
                    break
            return out
        finally:
            conn.close()

    def _numpy_scan(self, conn: sqlite3.Connection, qv: np.ndarray, n: int):
        rows = conn.execute("SELECT rowid, embedding FROM vec_chunks").fetchall()
        if not rows:
            return []
        ids = np.array([r[0] for r in rows], dtype=np.int64)
        mat = np.vstack([np.frombuffer(r[1], dtype=np.float32) for r in rows])
        sims = mat @ qv  # 已归一化 => 余弦相似度
        idx = np.argsort(-sims)[:n]
        return [(int(ids[i]), float(sims[i])) for i in idx]

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        if HAS_SQLITE_VEC:
            try:
                conn.enable_load_extension(True)
                sqlite_vec.load(conn)
                conn.enable_load_extension(False)
            except Exception:
                pass
        return conn

    @staticmethod
    def _meta(conn, k) -> str | None:
        try:
            r = conn.execute("SELECT v FROM meta WHERE k=?", (k,)).fetchone()
            return r[0] if r else None
        except sqlite3.OperationalError:
            return None

    def stats(self) -> dict[str, Any]:
        if not self.db_path.exists():
            return {"enabled": False}
        conn = self._connect()
        try:
            return {
                "enabled": True,
                "backend": self._meta(conn, "backend"),
                "dim": self._meta(conn, "dim"),
                "count": self._meta(conn, "count"),
                "built_at": self._meta(conn, "built_at"),
                "sqlite_vec": HAS_SQLITE_VEC,
            }
        finally:
            conn.close()
