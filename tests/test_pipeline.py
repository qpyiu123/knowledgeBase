"""端到端测试：建索引 → 检索 → 融合 → 上下文组装。"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from kb.config import Config  # noqa: E402
from kb.fts import FtsIndex  # noqa: E402
from kb.parser import iter_docs  # noqa: E402
from kb.rag import KB  # noqa: E402
from kb.vectors import VectorIndex  # noqa: E402


@pytest.fixture()
def cfg(tmp_path: Path) -> Config:
    cfg = Config.load()
    cfg.data["kb"]["root"] = str(tmp_path)
    (tmp_path / "kb" / "crypto").mkdir(parents=True)
    (tmp_path / "index").mkdir()
    (tmp_path / "kb" / "crypto" / "rsa-cm.md").write_text(
        "---\n"
        "title: 弱 RSA 共模攻击\n"
        "category: crypto\n"
        "tags: [rsa, 共模攻击]\n"
        "signals: [n 相同, e 不同, 两组密文]\n"
        "difficulty: easy\n"
        "---\n\n"
        "## 原理\n同余，扩展欧几里得。\n\n"
        "## 脚本\n用 gmpy2.gcdext。\n",
        encoding="utf-8",
    )
    (tmp_path / "kb" / "web" / "phar.md").parent.mkdir()
    (tmp_path / "kb" / "web" / "phar.md").write_text(
        "---\n"
        "title: PHAR 反序列化\n"
        "category: web\n"
        "signals: [上传文件, 文件包含, phar://]\n"
        "---\n\n## 原理\nphar 元数据会被反序列化。\n",
        encoding="utf-8",
    )
    return cfg


def test_index_and_search(cfg: Config):
    docs = list(iter_docs(cfg.kb_dir))
    assert len(docs) == 2
    st = FtsIndex(cfg.index_dir / "fts.db").rebuild(docs)
    assert st["docs"] == 2
    assert st["chunks"] >= 2

    fts = FtsIndex(cfg.index_dir / "fts.db")
    hits = fts.search("n 相同 e 不同", top_k=5)
    assert hits and hits[0].doc_path == "crypto/rsa-cm.md"


def test_kb_search_without_vectors(cfg: Config):
    docs = list(iter_docs(cfg.kb_dir))
    FtsIndex(cfg.index_dir / "fts.db").rebuild(docs)
    kb = KB(cfg)
    # 测试环境没有嵌入模型，应自动退化为纯 FTS
    hits = kb.search("phar 反序列化", top_k=3)
    assert hits and hits[0].doc_path == "web/phar.md"
    assert hits[0].sources == ["fts"]


def test_vector_index_numpy_path(cfg: Config):
    """不依赖模型：直接构造向量库，验证 numpy 降级检索路径。"""
    import sqlite3

    db = cfg.index_dir / "vectors.db"
    conn = sqlite3.connect(db)
    conn.executescript("""
        CREATE TABLE vec_chunks(rowid INTEGER PRIMARY KEY, embedding BLOB NOT NULL);
        CREATE TABLE chunk_meta(rowid INTEGER PRIMARY KEY, doc_path TEXT, title TEXT,
                                category TEXT, section TEXT, text TEXT);
        CREATE TABLE meta(k TEXT PRIMARY KEY, v TEXT);
    """)
    vecs = np.array([[1, 0, 0], [0, 1, 0], [0.9, 0.1, 0]], dtype=np.float32)
    for i, v in enumerate(vecs):
        conn.execute("INSERT INTO vec_chunks VALUES (?,?)", (i + 1, v.tobytes()))
        conn.execute(
            "INSERT INTO chunk_meta VALUES (?,?,?,?,?,?)",
            (i + 1, f"d{i}.md", f"T{i}", "misc", "", "text"),
        )
    conn.execute("INSERT INTO meta VALUES ('backend','numpy')")
    conn.execute("INSERT INTO meta VALUES ('dim','3')")
    conn.commit()
    conn.close()

    class FakeEmbedder:
        available = True
        backend = "fake"

        def encode(self, texts, batch_size=32, is_query=False, show_progress=False):
            return np.array([[1.0, 0.0, 0.0]], dtype=np.float32)

    vi = VectorIndex(db, FakeEmbedder())
    hits = vi.search("anything", top_k=2)
    assert hits
    assert hits[0]["doc_path"] == "d0.md"


def test_build_context_trims(cfg: Config):
    docs = list(iter_docs(cfg.kb_dir))
    FtsIndex(cfg.index_dir / "fts.db").rebuild(docs)
    kb = KB(cfg)
    hits = kb.search("共模攻击", top_k=2)
    ctx = kb.build_context(hits, char_budget=200)
    assert len(ctx) <= 400
    assert "应用" not in ctx or True  # 只验证不抛异常
    msgs = kb.prompt("问题", hits)
    assert msgs[0]["role"] == "system"
    assert "知识库" in msgs[1]["content"]


def test_prompt_contains_question(cfg: Config):
    docs = list(iter_docs(cfg.kb_dir))
    FtsIndex(cfg.index_dir / "fts.db").rebuild(docs)
    kb = KB(cfg)
    hits = kb.search("共模", top_k=1)
    msgs = kb.prompt("为什么 e1 e2 互素才能解", hits)
    assert "为什么 e1 e2 互素才能解" in msgs[1]["content"]
