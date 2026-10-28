"""知识图谱：跨方向关系存储与有界扩展。

设计借鉴 temp_newData 项目的《图谱架构与人工搜索工作台》：

核心原则（原文的几条硬约束，这里逐条落实）：

1. **关系必须分级，不能混用。**
   - `relates_to`     弱关联，只扩大阅读面
   - `analogous_to`   类比，相似但不同，**不传递适用性**
   - `differs_from`   易混淆项，用于区分
   - `requires`       前置条件
   - `uses_tool`      确实用到某工具
   - `illustrated_by` 案例证据

   正文里出现某个词最多算 `mentions`，不能自动升级成 `uses_tool`
   或 "方法已验证"。

2. **图扩展必须有界。**
   限跳数、限节点数、限扇出、限耗时，用访问集合防环。
   截断必须可见（返回值里带 truncated 标记）。

3. **类比边不提升排名。**
   `analogous_to` 产生的候选只标为"可对照阅读"，不进入主结果。

4. **重建不丢人工内容。**
   关系存在关系表里，索引重建时从 front-matter 重新读取，
   但如果人工在 curation 表里改过，以人工为准（这里先留接口）。
"""
from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path

# 关系类型及其默认行为
RELATION_KINDS = {
    "relates_to":     {"weight": 0.3, "boost": False,
                       "doc": "弱关联，仅扩大阅读面"},
    "analogous_to":   {"weight": 0.2, "boost": False,
                       "doc": "类比，相似但不同，不传递适用性"},
    "differs_from":   {"weight": 0.2, "boost": False,
                       "doc": "易混淆，用于区分"},
    "requires":       {"weight": 0.6, "boost": True,
                       "doc": "前置条件，满足才适用"},
    "uses_tool":      {"weight": 0.5, "boost": True,
                       "doc": "确实使用该工具"},
    "illustrated_by": {"weight": 0.5, "boost": True,
                       "doc": "案例证据"},
}

# 只有这些关系允许参与"扩张候选"（提升排名）
BOOSTING = {k for k, v in RELATION_KINDS.items() if v["boost"]}


@dataclass
class Node:
    key: str                  # 文档路径或知识卡 key
    title: str = ""
    category: str = ""
    hop: int = 0
    via: str = ""             # 通过哪条边到达
    parent: str = ""

    def to_dict(self) -> dict:
        return {"key": self.key, "title": self.title, "category": self.category,
                "hop": self.hop, "via": self.via, "parent": self.parent}


@dataclass
class Expansion:
    """一次图扩展的结果。"""
    nodes: list[Node] = field(default_factory=list)
    # 可直接用于提升排名（来自 requires / uses_tool / illustrated_by）
    boosting: list[Node] = field(default_factory=list)
    # 仅供对照阅读（来自 relates_to / analogous_to / differs_from）
    reading: list[Node] = field(default_factory=list)
    truncated: bool = False
    elapsed_ms: float = 0.0
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "boosting": [n.key for n in self.boosting],
            "reading": [n.key for n in self.reading],
            "truncated": self.truncated,
            "elapsed_ms": round(self.elapsed_ms, 1),
            "note": self.note,
        }


class Graph:
    """SQLite 属性图。表结构刻意保持简单，够用即可。

    nodes(key, title, category, path)
    edges(src, dst, kind, weight, evidence)
    """

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.con = sqlite3.connect(str(self.db_path))
        self.con.row_factory = sqlite3.Row
        self._init()

    def _init(self) -> None:
        self.con.executescript("""
        CREATE TABLE IF NOT EXISTS nodes(
            key      TEXT PRIMARY KEY,
            title    TEXT DEFAULT '',
            category TEXT DEFAULT '',
            path     TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS edges(
            src      TEXT NOT NULL,
            dst      TEXT NOT NULL,
            kind     TEXT NOT NULL,
            weight   REAL DEFAULT 0.3,
            evidence TEXT DEFAULT '',
            PRIMARY KEY(src, dst, kind)
        );
        CREATE INDEX IF NOT EXISTS idx_edges_src ON edges(src);
        CREATE INDEX IF NOT EXISTS idx_edges_dst ON edges(dst);
        CREATE TABLE IF NOT EXISTS meta(
            k TEXT PRIMARY KEY, v TEXT
        );
        """)
        self.con.commit()

    # ---------------------------------------------------------------- 建图
    def rebuild(self, docs: list) -> dict:
        """从文档的 front-matter 重建图。docs 是 parser.Doc 列表。"""
        cur = self.con.cursor()
        cur.execute("DELETE FROM nodes")
        cur.execute("DELETE FROM edges")

        known = {}
        for d in docs:
            known[d.path] = d
            cur.execute(
                "INSERT OR REPLACE INTO nodes(key,title,category,path) VALUES(?,?,?,?)",
                (d.path, d.title, d.category, d.path))

        n_edges = 0
        unresolved: list[str] = []
        for d in docs:
            for kind, targets in d.relations().items():
                if kind not in RELATION_KINDS:
                    continue
                w = RELATION_KINDS[kind]["weight"]
                for t in targets:
                    dst = self._resolve(t, known)
                    if dst is None:
                        unresolved.append(f"{d.path} -{kind}-> {t}")
                        continue
                    cur.execute(
                        "INSERT OR REPLACE INTO edges(src,dst,kind,weight) VALUES(?,?,?,?)",
                        (d.path, dst, kind, w))
                    n_edges += 1
        self.con.commit()
        cur.execute("INSERT OR REPLACE INTO meta(k,v) VALUES('built_at',?)",
                    (str(int(time.time())),))
        self.con.commit()
        return {
            "nodes": len(docs),
            "edges": n_edges,
            "unresolved": unresolved[:20],
            "unresolved_count": len(unresolved),
        }

    @staticmethod
    def _resolve(target: str, known: dict) -> str | None:
        """把关系目标解析成文档路径。

        支持几种写法：
          crypto/rsa-common-modulus-attack.md   完整路径
          rsa-common-modulus-attack             文件名
          弱 RSA 共模攻击                        标题
        """
        t = target.strip()
        if t in known:
            return t
        # 文件名 / 标题匹配
        for p, d in known.items():
            if p.rsplit("/", 1)[-1] == t or p.rsplit("/", 1)[-1].replace(".md", "") == t:
                return p
            if d.title == t:
                return p
        # 宽松：忽略大小写与扩展名
        tl = t.lower().replace(".md", "")
        for p, d in known.items():
            if p.lower().replace(".md", "").endswith(tl):
                return p
            if d.title.lower() == tl:
                return p
        return None

    # ---------------------------------------------------------------- 查询
    def neighbors(self, key: str, kinds: list[str] | None = None) -> list[dict]:
        sql = "SELECT dst, kind, weight FROM edges WHERE src=?"
        args: list = [key]
        if kinds:
            sql += " AND kind IN (" + ",".join("?" * len(kinds)) + ")"
            args.extend(kinds)
        rows = self.con.execute(sql, args).fetchall()
        return [dict(r) for r in rows]

    def expand(self, seeds: list[str], hops: int = 1,
               max_nodes: int = 24, max_fanout: int = 6,
               budget_ms: int = 200,
               kinds: list[str] | None = None) -> Expansion:
        """有界 BFS 扩展。

        借鉴原设计的四条限制：跳数、节点数、扇出、耗时。
        任一限制触发都设置 truncated=True，让调用方知道结果不完整。
        """
        t0 = time.time()
        res = Expansion()
        visited: set[str] = set()
        frontier = [(s, 0, "") for s in seeds if s]
        allowed = kinds if kinds else list(RELATION_KINDS)

        while frontier:
            if time.time() - t0 > budget_ms / 1000:
                res.truncated = True
                res.note = f"超出时间预算 {budget_ms}ms"
                break
            if len(res.nodes) >= max_nodes:
                res.truncated = True
                res.note = f"达到节点上限 {max_nodes}"
                break

            key, hop, via = frontier.pop(0)
            if key in visited or hop >= hops:
                continue
            visited.add(key)

            try:
                nbrs = self.neighbors(key, allowed)
            except Exception:  # noqa: BLE001
                continue
            if len(nbrs) > max_fanout:
                nbrs = nbrs[:max_fanout]
                res.truncated = True

            for nbr in nbrs:
                dst = nbr["dst"]
                if dst in visited:
                    continue
                node = self._node(dst, hop + 1, nbr["kind"], key)
                if node is None:
                    continue
                res.nodes.append(node)
                if nbr["kind"] in BOOSTING:
                    res.boosting.append(node)
                else:
                    res.reading.append(node)
                frontier.append((dst, hop + 1, nbr["kind"]))
                if len(res.nodes) >= max_nodes:
                    break

        res.elapsed_ms = (time.time() - t0) * 1000
        return res

    def _node(self, key: str, hop: int, via: str, parent: str) -> Node | None:
        r = self.con.execute(
            "SELECT title, category FROM nodes WHERE key=?", (key,)).fetchone()
        if not r:
            return None
        return Node(key=key, title=r["title"], category=r["category"],
                    hop=hop, via=via, parent=parent)

    # ---------------------------------------------------------------- 统计
    def stats(self) -> dict:
        n_nodes = self.con.execute("SELECT COUNT(*) c FROM nodes").fetchone()["c"]
        n_edges = self.con.execute("SELECT COUNT(*) c FROM edges").fetchone()["c"]
        by_kind = {r["kind"]: r["c"] for r in self.con.execute(
            "SELECT kind, COUNT(*) c FROM edges GROUP BY kind").fetchall()}
        # 跨方向边数：src 与 dst 的 category 不同
        cross = self.con.execute("""
            SELECT COUNT(*) c FROM edges e
            JOIN nodes a ON a.key=e.src
            JOIN nodes b ON b.key=e.dst
            WHERE a.category != b.category
        """).fetchone()["c"]
        return {"nodes": n_nodes, "edges": n_edges,
                "by_kind": by_kind, "cross_category": cross}

    def close(self) -> None:
        self.con.close()
