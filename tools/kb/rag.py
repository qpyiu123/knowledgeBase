"""检索增强问答（RAG）。

流程：查询 → FTS + 向量双路召回 → RRF 融合 → 组装上下文 → 本地模型生成。
上下文按 token 预算裁剪，避免 4GB 显存下 KV cache 吃满。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .config import Config
from .fts import FtsIndex
from .fusion import FusedHit, fuse_single_source, rrf_fuse
from .llm import BaseBackend, LLMError, get_backend
from .vectors import Embedder, VectorIndex

SYSTEM_PROMPT = (
    "你是 CTF 解题助手。用户会描述题目或贴题面特征，你要：\n"
    "1) 先判断题目所属方向（misc/crypto/reverse/pwn/web/forensics/mobile/blockchain/hardware/osint/ai）；\n"
    "2) 指出命中的识别信号；\n"
    "3) 给出分步解题思路；\n"
    "4) 给出可直接运行或略作修改即可使用的脚本/payload。\n"
    "优先使用【知识库】中的方法。如果知识库不足以覆盖，明确说明「知识库未覆盖」，"
    "再给出你的通用经验，并标注这是推演而非知识库结论。不要编造不存在的工具选项。\n"
    "用中文回答，代码块标注语言。"
)


@dataclass
class RagAnswer:
    answer: str
    hits: list[FusedHit]
    backend: str
    model: str
    stats: dict[str, Any]


class KB:
    """统一入口：装配 FTS + 向量 + 图谱 + LLM。"""

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.fts = FtsIndex(cfg.index_dir / "fts.db")
        onnx_dir = cfg.resolve(str(cfg.get("embed", "onnx_dir", "models/bge-small-zh-v1.5-onnx")))
        self.embedder = Embedder(
            cfg.resolve(str(cfg.get("embed", "model_dir"))),
            query_prefix=str(cfg.get("embed", "query_prefix", "")),
            onnx_dir=onnx_dir,
        )
        self.vec = VectorIndex(cfg.index_dir / "vectors.db", self.embedder)
        self._llm: BaseBackend | None = None
        self._graph = None
        from .library import LibraryCatalog
        self.library = LibraryCatalog(cfg.kb_dir, cfg.index_dir / "fts.db")

    # ---------- 图谱 ----------
    def graph(self):
        """惰性加载图谱；索引没建过就返回 None（检索照常工作）。"""
        if self._graph is None:
            try:
                from .graph import Graph
                p = self.cfg.index_dir / "graph.db"
                if p.exists():
                    self._graph = Graph(p)
            except Exception:  # noqa: BLE001
                self._graph = None
        return self._graph

    # ---------- 检索 ----------
    def search(self, query: str, top_k: int | None = None, category: str | None = None,
               mode: str = "or", expand: bool = True,
               hops: int = 1, doc_type: str | None = None,
               retrieval: str = "hybrid") -> list[FusedHit]:
        from .explain import doc_type as type_of

        k = int(top_k or self.cfg.get("search", "top_k", 8))
        rrf_k = int(self.cfg.get("search", "rrf_k", 60))
        # 候选池要比最终条数宽：FTS 已按文档返回最好块，但向量路仍是 chunk 级，
        # 且按类型筛选时可能在融合后才过滤。多取一些，避免相关文档进不了候选。
        # 设下限是为了让 top_k=5 与 top_k=10 的排序一致：候选池太小会让
        # 只在单路深名次出现的文档时有时无。
        fuse_k = k * 4 if doc_type else k
        fts_fetch = max(k * 4, 60)
        vec_fetch = max(k * 6, 80)
        fts_hits = self.fts.search(query, top_k=fts_fetch, category=category, mode=mode)
        if retrieval not in ("fts", "hybrid"):
            raise ValueError("检索方式只能是 fts 或 hybrid")
        vec_hits = (self.vec.search(query, top_k=vec_fetch, category=category)
                    if retrieval == "hybrid" else [])
        if not vec_hits:
            base = fuse_single_source(fts_hits, fuse_k)
        else:
            base = rrf_fuse(fts_hits, vec_hits, k=rrf_k, top_k=fuse_k)
        if doc_type:
            base = [h for h in base if type_of(h.doc_path) == doc_type][:k]
        else:
            base = base[:k]
        if not expand:
            return base
        return self._expand_hits(base, k, hops=hops, doc_type=doc_type)

    def _expand_hits(self, hits: list[FusedHit], k: int,
                     hops: int = 1, doc_type: str | None = None) -> list[FusedHit]:
        """在图上有界扩展，把关联但没被词面/向量召回的知识点补进来。

        严格遵守原设计：
        - 只有 boosting 类关系（requires / uses_tool / illustrated_by）
          补进来的条目才获得一定名次加成；
        - relates_to / analogous_to / differs_from 补进来的只排到尾部，
          标成"可对照阅读"，不参与主排名；
        - 扩展受跳数/节点/扇出/耗时预算约束，截断会体现在 note 里。
        """
        g = self.graph()
        if g is None or not hits:
            return hits
        seeds = [h.doc_path for h in hits[:4]]
        try:
            exp = g.expand(seeds, hops=hops, max_nodes=12, max_fanout=4,
                           budget_ms=120)
        except Exception:  # noqa: BLE001
            return hits
        if not exp.nodes:
            return hits

        have = {h.doc_path for h in hits}
        # 图谱补入的条目不提升到前 k，只补在 k 之后作为"关联阅读"，
        # 这样主结果的可信度不受影响。
        type_of = None
        if doc_type:
            from .explain import doc_type as type_of  # noqa: F811
        extra: list[FusedHit] = []
        for n in exp.nodes:
            if n.key in have:
                continue
            if type_of is not None and type_of(n.key) != doc_type:
                continue
            have.add(n.key)
            try:
                path = self.cfg.kb_dir / n.key
                if not path.exists():
                    continue
                fh = FusedHit(doc_path=n.key, title=n.title or n.key,
                              category=n.category, score=0.0,
                              sources=[f"graph:{n.via}"], best_text="")
            except Exception:  # noqa: BLE001
                continue
            # 标记用途：boosting 的可以靠前，reading 的只做对照
            setattr(fh, "graph_via", n.via)
            setattr(fh, "graph_hop", n.hop)
            setattr(fh, "graph_boost", n.via in
                    ("requires", "uses_tool", "illustrated_by"))
            extra.append(fh)

        if not extra:
            return hits
        # boosting 插到结果中间偏后，reading 放最后
        boost = [h for h in extra if getattr(h, "graph_boost", False)]
        read = [h for h in extra if not getattr(h, "graph_boost", False)]
        merged = hits[:k] + boost + read
        return merged

    def expand(self, seeds: list[str], hops: int = 1) -> dict:
        """对外暴露的图扩展接口，方便调试。"""
        g = self.graph()
        if g is None:
            return {"note": "图谱未建立"}
        return g.expand(seeds, hops=hops).to_dict()

    # ---------- 上下文组装 ----------
    def build_context(self, hits: list[FusedHit], char_budget: int = 7000, query: str = '') -> str:
        blocks: list[str] = []
        used = 0
        code_paths = set()
        for i, h in enumerate(hits, 1):
            body = ""
            root = self.cfg.kb_dir.resolve()
            f = (root / h.doc_path).resolve()
            if not f.is_relative_to(root):
                continue
            if f.exists():
                body = f.read_text(encoding="utf-8", errors="replace")
                # 去掉 front-matter，省 token
                if body.startswith("---"):
                    end = body.find("\n---", 4)
                    if end != -1:
                        body = body[end + 4:]
            elif h.best_text:
                body = h.best_text
            from .excerpts import select_excerpt
            excerpt = select_excerpt(body, query, getattr(h, 'section', '') or '', limit=1600)
            tag = ""
            gv = getattr(h, "graph_via", None)
            if gv:
                kind = "关联" if getattr(h, "graph_boost", False) else "对照"
                tag = f"  [图谱{kind}: {gv}]"
            block = f"[{i}] {h.title}  (路径: {h.doc_path}){tag}\n{excerpt}"
            from .excerpts import paired_code
            script = paired_code(root, h.doc_path, getattr(self, 'library', None))
            if script and script['path'] not in code_paths:
                meta = f"\n第三方导入：{', '.join(script['dependencies']) or '无'}；脚本参数：{' '.join(script['arguments'])}\n"
                code_header = f"\n\n【代码片段：{script['path']}】" + meta
                room = min(4000, max(0, char_budget - used - len(block) - len(code_header)))
                if room:
                    code = script['body'][:room]
                    kind = '完整代码' if len(code) == len(script['body']) else '代码片段'
                    block += f"\n\n【{kind}：{script['path']}】" + meta + code
                    code_paths.add(script['path'])
            if used + len(block) > char_budget:
                remain = char_budget - used
                if remain < 400:
                    break
                block = block[:remain]
            blocks.append(block)
            used += len(block)
        return "\n\n---\n\n".join(blocks)

    def prompt(self, question: str, hits: list[FusedHit], char_budget: int = 7000) -> list[dict[str, str]]:
        ctx = self.build_context(hits, char_budget, question)
        user = (
            f"【知识库】（共 {len(hits)} 条，按相关度排序）\n{ctx}\n\n"
            f"【题目 / 问题】\n{question}\n\n"
            "请给出：方向判断 → 识别信号 → 解题步骤 → 可运行脚本。"
        )
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user},
        ]

    # ---------- 生成 ----------
    def backend(self, force: str | None = None) -> BaseBackend | None:
        if force is not None or self._llm is None:
            try:
                self._llm = get_backend(self.cfg, force)
            except LLMError:
                raise
        return self._llm

    def ask(self, question: str, top_k: int | None = None, category: str | None = None,
            force_backend: str | None = None, max_tokens: int | None = None) -> RagAnswer:
        hits = self.search(question, top_k=top_k, category=category)
        be = self.backend(force_backend)
        if be is None:
            return RagAnswer(
                answer="", hits=hits, backend="none", model="",
                stats={"note": "未启用模型，仅返回检索结果"},
            )
        msgs = self.prompt(question, hits)
        res = be.chat(msgs, max_tokens=max_tokens)
        return RagAnswer(
            answer=res.text, hits=hits, backend=res.backend, model=res.model,
            stats={
                "prompt_tokens": res.prompt_tokens,
                "completion_tokens": res.completion_tokens,
                "seconds": res.seconds,
                "tokens_per_sec": res.tokens_per_sec,
            },
        )

    def ask_stream(self, question: str, top_k: int | None = None,
                   category: str | None = None, force_backend: str | None = None):
        hits = self.search(question, top_k=top_k, category=category)
        be = self.backend(force_backend)
        if be is None:
            raise LLMError("未启用模型后端")
        msgs = self.prompt(question, hits)
        return hits, be.stream(msgs)


def _trim_md(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit].rsplit("\n", 1)[0] + "\n...(截断)"
