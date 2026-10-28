"""FTS5 关键词检索层。

设计要点：
1. 原生 FTS5 的 unicode61 分词器不会切中文，中文查询几乎必然命中 0 条。
   解法：入库前用 write_cjk() 把中文串切成「空格分隔的二元组」再写入索引，
   查询时对中文做同样的切分，从而让中文也享受 BM25 排序。
2. 原文另存 origin 列（不参与匹配），命中后展示原文。
3. 支持前缀模糊（token*），并带 LIKE 兜底，保证「输入半截词也能出结果」。
"""
from __future__ import annotations

import re
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .parser import Doc, chunk_doc, tokenize_query

CJK = r"\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff"
CJK_RUN = re.compile(f"[{CJK}]+")

# 列顺序 -> 权重（title 最高，其次是信号词，再次是标签）
COLUMNS = ("title", "signals", "tags", "path", "body", "origin")
WEIGHTS = (12.0, 9.0, 6.0, 3.0, 1.0, 0.2)
_WARNED = False


def write_cjk(text: str) -> str:
    """把中文连续串切成二元组，让 FTS5 能索引中文。"""
    def repl(m: re.Match[str]) -> str:
        s = m.group(0)
        if len(s) == 1:
            return f" {s} {s} "
        grams = [s[i:i + 2] for i in range(len(s) - 1)]
        return " " + " ".join(grams) + f" {s} "
    return CJK_RUN.sub(repl, text)


@dataclass
class Hit:
    doc_path: str
    title: str
    category: str
    score: float
    origin: str
    section: str = ""
    source: str = "fts"


SCHEMA = f"""
CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5(
    title, signals, tags, path, body, origin,
    tokenize = 'unicode61 remove_diacritics 2',
    prefix = '2 3 4'
);
CREATE TABLE IF NOT EXISTS docs(
    path TEXT PRIMARY KEY,
    title TEXT, category TEXT, difficulty TEXT,
    source TEXT, tags TEXT, signals TEXT, mtime REAL, nchunks INTEGER
);
CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT);
"""


def _warn(msg: str) -> None:
    global _WARNED
    if not _WARNED:
        import sys
        print(f"[fts] {msg}", file=sys.stderr)
        _WARNED = True


class FtsIndex:
    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    # ---------------- 建索引 ----------------
    def rebuild(
        self,
        docs: Iterable[Doc],
        chunk_chars: int = 900,
        overlap: int = 120,
        on_progress=None,
    ) -> dict[str, Any]:
        docs = list(docs)
        t0 = time.time()
        conn = sqlite3.connect(self.db_path)
        try:
            conn.executescript(SCHEMA)
            conn.execute("DELETE FROM chunks")
            conn.execute("DELETE FROM docs")

            n_chunks = 0
            for i, doc in enumerate(docs):
                chunks = chunk_doc(doc, chunk_chars, overlap)
                rows = []
                for ch in chunks:
                    rows.append((
                        write_cjk(doc.title),
                        write_cjk(" ".join(doc.signals)) + " " + write_cjk(doc.title),
                        write_cjk(" ".join(doc.tags) + " " + " ".join(doc.tools)),
                        # 注意：path 列是**原文列**，不能做 CJK 切分，否则 / 变空格、
                        # 无法与 docs.path 做 JOIN。想搜路径的话由 tokenizer 生成"子串词"。
                        doc.path,
                        write_cjk(ch["text"]),
                        ch["text"],
                    ))
                conn.executemany(
                    "INSERT INTO chunks(title,signals,tags,path,body,origin) VALUES (?,?,?,?,?,?)",
                    rows,
                )
                conn.execute(
                    "INSERT INTO docs(path,title,category,difficulty,source,tags,signals,mtime,nchunks)"
                    " VALUES (?,?,?,?,?,?,?,?,?)",
                    (
                        doc.path, doc.title, doc.category, doc.difficulty, doc.source,
                        ",".join(doc.tags), ";".join(doc.signals), doc.mtime, len(rows),
                    ),
                )
                n_chunks += len(rows)
                if on_progress and (i + 1) % 20 == 0:
                    on_progress(i + 1, len(docs))

            conn.execute(
                "INSERT OR REPLACE INTO meta(k,v) VALUES ('built_at', ?)",
                (time.strftime("%Y-%m-%d %H:%M:%S"),),
            )
            conn.commit()
        finally:
            conn.close()
        return {
            "docs": len(docs),
            "chunks": n_chunks,
            "seconds": round(time.time() - t0, 2),
        }

    # ---------------- 查询 ----------------
    @staticmethod
    def build_match(tokens: list[str], mode: str = "or") -> str:
        """构造 FTS5 MATCH 表达式。

        注意：混合字面量与 * 前缀会触发 FTS5 语法错误，所以
        - 纯 ASCII 词 -> 双引号字面量（内部符号变空格）+ `*` 前缀模糊
        - 中文/其它 -> 双引号字面量，不加 `*`（否则中缀查询全表扫，很慢）
        """
        parts = []
        for t in tokens:
            t = t.replace('"', "").strip()
            if not t or not t.replace("*", "").strip("*"):
                continue
            safe = re.sub(r"[^\w\u3400-\u9fff]+", " ", t, flags=re.UNICODE).strip()
            if not safe:
                continue
            words = safe.split()
            if not words:
                continue
            if all(re.fullmatch(r"[A-Za-z0-9_]+", w) for w in words):
                parts.append('"' + " ".join(words) + '"_*'.replace("_*", "*"))
                # 多词时同时给出纯字面量，避免长串命中不到
                if len(words) > 1:
                    parts.append('"' + " ".join(words) + '"')
            else:
                parts.append('"' + safe + '"')
        if not parts:
            return ""
        # 去重保序
        seen: set[str] = set()
        uniq = []
        for p in parts:
            if p not in seen:
                seen.add(p)
                uniq.append(p)
        joiner = " OR " if mode == "or" else " AND "
        return joiner.join(uniq)

    def search(
        self,
        query: str,
        top_k: int = 8,
        category: str | None = None,
        mode: str = "or",
    ) -> list[Hit]:
        tokens = tokenize_query(query)
        match = self.build_match(tokens, mode)
        conn = sqlite3.connect(self.db_path)
        try:
            rows = self._fts_rows(conn, match, top_k * 4)
            if not rows and tokens:
                # 兜底 1：严格 AND
                match_and = self.build_match(tokens, "and")
                if match_and and match_and != match:
                    rows = self._fts_rows(conn, match_and, top_k * 4)
            if not rows and tokens:
                # 兜底 2：退化到 LIKE 子串匹配
                rows = self._like_rows(conn, tokens, top_k * 4)
            hits: list[Hit] = []
            for row in rows:
                path, title, cat, score, origin = row
                if category and cat != category:
                    continue
                hits.append(Hit(
                    doc_path=path, title=title, category=cat,
                    score=float(score), origin=origin or "", source="fts",
                ))
                if len(hits) >= top_k:
                    break
            return hits
        finally:
            conn.close()

    def _fts_rows(self, conn: sqlite3.Connection, match: str, limit: int):
        if not match:
            return []
        # 注意：bm25() 的参数是**不带 rowid 的列数**，本表 6 列 => 传 6 个权重。
        # 传错个数会抛 OperationalError，被下面的 except 吞成"0 命中"。
        #
        # 另一个必须规避的坑：JOIN 之后 WHERE 条件会落到**右表**上，
        # FTS5 会把 `chunks MATCH ?` 当成普通比较，从而永远返回 0 行。
        # 所以必须先只用 chunks 过滤出 rowid，再回连 docs。
        w = ", ".join(str(float(x)) for x in WEIGHTS)
        # 再一个坑：FTS5 的 rowid 列是**未声明**的，在子查询里 `AS rid` 会变成 NULL，
        # 必须写成 `rowid AS rid` 或直接 `chunks.rowid`。这里显式取 chunks.rowid。
        sql = f"""
            SELECT d.path, d.title, d.category, s.score, c.origin
            FROM (
                SELECT chunks.rowid AS rid,
                       bm25(chunks, {w}) AS score
                FROM chunks
                WHERE chunks MATCH ?
                ORDER BY score
                LIMIT ?
            ) AS s
            JOIN chunks c ON c.rowid = s.rid
            JOIN docs d  ON d.path = c.path
            ORDER BY s.score
        """
        try:
            return conn.execute(sql, (match, limit)).fetchall()
        except sqlite3.OperationalError as e:
            _warn(f"MATCH 失败({e}) match={match!r}")
            return []

    def _like_rows(self, conn: sqlite3.Connection, tokens: list[str], limit: int):
        if not tokens:
            return []
        tok = tokens[:4]
        conds = " OR ".join(["chunks.origin LIKE ?"] * len(tok))
        params = [f"%{t}%" for t in tok]
        sql = f"""
            SELECT d.path, d.title, d.category, -1.0 AS score, chunks.origin
            FROM chunks JOIN docs d ON d.path = chunks.path
            WHERE {conds}
            LIMIT ?
        """
        try:
            return conn.execute(sql, (*params, limit)).fetchall()
        except sqlite3.OperationalError:
            return []

    # ---------------- 元信息 ----------------
    def stats(self) -> dict[str, Any]:
        conn = sqlite3.connect(self.db_path)
        try:
            n_docs = conn.execute("SELECT COUNT(*) FROM docs").fetchone()[0]
            n_chunks = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
            row = conn.execute("SELECT v FROM meta WHERE k='built_at'").fetchone()
            cats = conn.execute(
                "SELECT category, COUNT(*) FROM docs GROUP BY category ORDER BY 2 DESC"
            ).fetchall()
            return {
                "docs": n_docs,
                "chunks": n_chunks,
                "built_at": row[0] if row else None,
                "categories": dict(cats),
            }
        except sqlite3.OperationalError:
            return {"docs": 0, "chunks": 0, "built_at": None, "categories": {}}
        finally:
            conn.close()

    def get_doc(self, rel_path: str) -> dict[str, Any] | None:
        conn = sqlite3.connect(self.db_path)
        try:
            r = conn.execute(
                "SELECT path,title,category,difficulty,source,tags,signals FROM docs WHERE path=?",
                (rel_path,),
            ).fetchone()
        finally:
            conn.close()
        if not r:
            return None
        return {
            "path": r[0], "title": r[1], "category": r[2], "difficulty": r[3],
            "source": r[4], "tags": r[5], "signals": r[6],
        }
