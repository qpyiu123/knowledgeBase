# 检索评测（P1）

固定查询集 + 可复现指标。评测只读本地 `index/`，不启动 Ollama，不调用 LLM。

## 运行

```powershell
cd F:\CTFfiles\knowledgeBase
.\.venv\Scripts\python.exe tools\eval_search.py
.\.venv\Scripts\python.exe tools\eval_search.py --mode fts
.\.venv\Scripts\python.exe tools\eval_search.py --top-k 10 --json
.\.venv\Scripts\python.exe tools\eval_search.py --json-out work\eval.json
```

- `--mode hybrid`（默认）：FTS + 向量 + RRF + 图谱扩展（实际 API 路径）。
- `--mode fts`：只看词面检索，用于对照。
- `--no-expand`：关闭图谱扩展。
- `--json` / `--json-out`：机器可读输出。

## 指标

- **top1**：第 1 名命中任一 `expected` 文档。
- **hit@k**：前 k 名命中任一 `expected`（默认 k=5）。
- **MRR**：第一个命中的名次倒数，未命中记 0。
- **recall@k**：前 k 名覆盖了多少 `expected` 文档。

同一文档的多个 chunk 不重复计数。

## 固定集

`search_queries.json` 当前 22 条，覆盖 crypto / web / pwn / misc / forensics /
tools / 比赛卡片。`expected` 是人工确认的主文档；改查询或标签要单独说明理由。

## 基线（2026-10-28）

| 版本 / 模式 | top1 | hit@5 | MRR | recall@5 |
|---|---|---|---|---|
| P0 代码，hybrid | 0.9545 | 1.0000 | 0.9697 | 1.0000 |
| P1，hybrid | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| P1，fts-only | 0.9091 | 1.0000 | 0.9545 | 1.0000 |

P1 的提升来自：FTS 文档级最好块、候选池下限、单数字 payload token 过滤、
单字母精确匹配。**没有调整 RRF/BM25 权重**。

## 局限

- 22 条是人工固定样例，不代表全库分布；扩集应另立任务。
- 评测依赖本地索引与嵌入模型；索引重建后需重跑并更新基线。
- `expected` 只标主文档，不评价“排第 2 但同样有用”的情况。
