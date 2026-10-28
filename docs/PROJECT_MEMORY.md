# 项目记忆（PROJECT_MEMORY）

> 本文件记录当前可复现状态、关键决策、运行命令、已知问题、下一步与验证结果。
> 区分三类信息：**已验证事实 / 推断 / 未验证**。旧文档里的数字若未在本重复现，
> 不得当作结论复用。

**最后更新**：2026-10-28（P1 批次已完成，验证结果见第 7 节）

---

## 1. 用户要求（长期有效）

- 本批实现只指定 **DeepSeek（opencode-go/deepseek-v4.1-flash）** 完成；
  GPT-6.1-Sol 只做规划与验收，不写代码。
- 保留检索与自由提问两条核心路径。
- 项目、虚拟环境、模型、索引、缓存、测试依赖、构建产物放在 **F 盘项目内**，
  不扩大 C 盘占用。
- 一批工作一个提交；测试要可复现；事实与猜测必须区分。
- 不删除用户资料，不读取/提交认证密钥，不更改全局 Git / npm 配置，
  不停止无关服务，不碰其他项目。
- 后续方向：P1 检索可解释与评测；P2 前端附件分析；P3 题目工作区；
  P4 三态适用条件与可追溯 Writeup。图谱可用性由评测决定，不按边数凑指标。

---

## 2. 当前仓库状态

### 已验证事实（基线提交 `b9ebe89`）

- 项目原先没有 Git；已 `git init` 并创建基线提交：
  `b9ebe89 chore: baseline source, knowledge data and docs`。
- 基线提交 1638 个文件，工作树源码 + 知识库约 **3.2 MB**；
  `models/`、`index/`、`work/`、`temp_newData/`、`_happy/`、`node_modules/`、
  `dist/`、日志、缓存均未提交，并保留在本地。
- 本地工具链：Python 3.14.0（`.venv`）、Node v24.10.0、npm 11.6.1、Git 2.43。
- `index/fts.db` 可读，统计为 **1567 篇 / 14139 块**，`built_at=2026-10-24 09:31:46`。
  方向分布：web 447、misc 321、pwn 265、reverse 215、crypto 199、forensics 62、
  mobile/hardware/osint/ai/blockchain 分别 14/14/12/12/6。
- `models/ollama-models` 里实际存在 manifest 的名称包括：
  `qwen2.5-coder-7b:local`、`qwen25-coder-7b-local:latest`、
  `qwen25c7b-cpu0`、`qwen25c7b-gpu10`、`qwen25c7b-gpu14`。
  **没有** `qwen3-4b-local:latest` 的 manifest（旧 server 硬编码该名称）。
- `config.toml` 的 `[ollama] model` 为 `qwen2.5-coder-7b`，与实际模型家族一致。
- 基线 Python 测试：82 个用例通过；P0 后 107；P1 后 132。
- 前端 P0 起有 Vitest（SSE + SearchPage），P1 后 2 文件 / 14 用例。

### 旧文档中未验证的说法

- “1567 篇 / 14139 块”本次由 FTS 统计复现，算已验证。
- “0 篇空 title”本次全库扫描复现（原文档“21 篇无 title”已不成立）。
- “图谱 1567 节点 / 26 条边 / 8 条跨方向 / 17 篇源文档”本次直接查
  `index/graph.db` 复现；但图谱是否真的提升命中，仍应由 P1 评测决定。
- “883 段 / 105 秒回答”“AirLLM 0.006–0.026 tok/s”“4B 优于 7B”等性能/质量结论
  本批**未复现**，只能当作历史线索。
- “前端必然白屏”是旧文档的推断。本批已按代码审查确认 `setImmediate` 在浏览器
  不存在（类型配置曾用 `types:["node"]` 掩盖），但未在真实浏览器逐项复现全部路径。

---

## 3. P0 决策（上一批，2026-10-28）

1. **前端显式参数**：起点卡片/结果卡片“问模型”不再 `setState` 后依赖旧闭包，
   直接构造问题文本并作为参数传给 `runAsk`/`runSearch`。
2. **TS 配置分离**：`tsconfig.app.json`（浏览器，不含 Node 类型）和
   `tsconfig.node.json`（Vite 配置）通过根 `tsconfig.json` 引用。
3. **SSE 契约统一**：只发 `tok` / `err` / `done`；前端识别三者；
   `done.info` 展示为完成信息；空响应和上游错误都有可见提示。
4. **取消语义诚实**：前端按钮改称“停止接收”，提示“仅关闭本地接收，
   后端模型可能仍在收尾”；后端在写失败时主动关闭生成器/上游连接。
5. **串行生成**：`/api/ask` 用非阻塞锁限流，忙碌时返回 429 和明确错误，
   不排队堆积、不打爆显存。
6. **配置统一**：server 从 `config.toml` 读取 Ollama host、模型、context、
   max_tokens、temperature、timeout；`AGENT_MODEL`、`AGENT_OLLAMA`、
   `AGENT_NUM_CTX` 等环境变量只做显式覆盖。
7. **路径与输入边界**：`/api/ask` 与 `/api/doc` 只读 `kb/` 根目录内 `.md`；
   限制问题长度、paths 数量、单文件大小、总上下文字符数；`top_k` 有上限。
8. **其他入口同步**：`start.ps1` 不再强制 `AGENT_MODEL=qwen3-4b-local:latest`；
   `tools/agent/hint.py` 的 host/model 默认值也改为读 `config.toml` 并解析
   实际模型名，避免 CLI 继续指向不存在的模型。
9. **health 分离**：`model_ok` 与 `index_ok` 分开返回，`ok` 保持为模型可达
   以兼容前端，但不再用文档数冒充模型状态，也不把模型可达冒充索引可用。
10. **测试**：server 核心端点用离线 Mock；前端增加 SSE 契约测试与组件行为测试。

---

## 3b. P1 决策（本批，2026-10-28）

1. **命中段落而不是整篇摘要**：`/api/search` 的 `snippet` 改为真正命中的
   chunk（`FusedHit.best_text`），并返回 `section`；只有图谱补入、没有 chunk 的
   条目才退回 `_snip`。
2. **命中原因**：每个主结果带 `match`：
   - `sources` / `labels`：`fts`=词面命中、`vec`=语义相近、`graph:*`=图谱关联；
   - `terms`：查询分词里实际出现在命中段落中的词；
   - `rrf`：两路各自的 RRF 贡献。
3. **FTS 文档级去重**：`chunks` 每个块都拼了 title/signals 元数据，旧查询会让
   一篇长文档的所有块占满 top-N。`_fts_rows` 改用窗口函数按 `d.path` 分组，
   只保留 BM25 最好的那一块；`fuse_single_source` 也按文档去重。
4. **候选池下限**：FTS 至少取 60 篇、向量至少取 80 块，避免 `top_k=5` 与
   `top_k=10` 的排序不一致（只出现在单路深名次的文档会时有时无）。
5. **查询噪声**：`{{7*7}}` 这类单个数字 token 不再进 FTS；单字母 `n/e/c`
   仍保留，但改成精确匹配，不做 `"e"*` 前缀扩展。
6. **类型筛选**：`/api/search` 新增 `doc_type=topic|card`；结果带
   `doc_type` / `doc_type_label` / `counts`。专题文档 = 手写条目、`_imported`、
   `_des/topics|wp_summary|tools`；比赛卡片 = `_des/cards/`。
7. **相似结果整理**：前端结果卡片显示「专题文档 / 比赛卡片」徽章，
   可在搜索前按类型筛选；图谱补入条目单独显示为「关联阅读」，不混进主排名。
8. **反馈记录**：`POST /api/feedback`，`verdict ∈ useful|useless|adopted`，
   追加到 `work/feedback/feedback.jsonl`（可用 `[feedback].file` 或
   `AGENT_FEEDBACK_FILE` 覆盖）。只校验并记录 `kb/` 内已存在的 Markdown，
   不读任意路径；`work/` 不入库。
9. **可复现评测**：`eval/search_queries.json` 固定 22 条查询；
   `tools/eval_search.py` 输出 top1 / hit@k / MRR / recall@k，支持
   `--mode hybrid|fts`、`--no-expand`、`--json`、`--json-out`。
10. **排序调整由评测驱动**：本批只改候选生成/噪声 token，没有凭感觉改 RRF
    权重或列权重；基线 → P1 的指标见第 7 节。固定集上 top1/MRR 已到 1.0，
    没有证据支持再加类型权重，因此保持现有权重。

---

## 4. 运行命令

```powershell
# Python 回归（完整摘要）
.\.venv\Scripts\python.exe -m pytest -o addopts="" -q

# 仅 server 测试
.\.venv\Scripts\python.exe -m pytest -o addopts="" -q tests\test_server_api.py

# P1 检索评测（固定查询集；可加 --mode fts / --json / --json-out）
.\.venv\Scripts\python.exe tools\eval_search.py
.\.venv\Scripts\python.exe tools\eval_search.py --mode fts

# 前端
cd tools\agent\webapp
npm run check
npm test
npm run build

# 真实运行（不用于本批自动化测试）
.\start.ps1
.\start.ps1 -Status
.\start.ps1 -Stop
```

---

## 5. 已知问题 / 限制

- 旧 `README.md`、`docs/HINT.md`、`docs/GRAPH.md` 为 GBK 编码，工具链按 UTF-8
  读取会显示乱码；本批不整体转码，避免无意义大 diff。
- 全库扫描显示 0 篇空 title；“21 篇无 title”的旧说法已排除。
- P1 已降低“同一长文档占满结果”的噪音，但排序仍可能在泛化查询上偏向
  signals 很多的长文档；固定评测集只有 22 条，不能代表全部题型。
- 真实模型回答质量与耗时仍未纳入自动化；自动化测试全部离线 Mock。
- 反馈只落本地 JSONL，尚未做汇总/导出 UI；是否用于排序需后续评测决定。
- `work/` 与 `temp_newData/` 体积大（后者约 18.9 GB），只在本地保留，不入库。
- 外部导入脚本只允许静态审查，不在本批执行。

---

## 6. 下一步（不在本批实现）

- P1 已完成：命中段落/原因、类型筛选、图谱关联阅读、反馈记录、可复现评测。
- P2：前端附件分析（大小限制、隔离、默认不执行脚本）；与 P1 评测共用样例。
- P3：持久化题目工作区（事实/尝试/资料收藏）。
- P4：适用条件三态（已知/未知/不满足）、只读脚本工具架、由真实记录生成
  可追溯 Writeup 草稿。
- 图谱价值继续由评测决定，不以边数作为目标；P1 固定集没有显示图谱需要提权。

---

## 7. 验证结果（2026-10-28，P1）

以下均为本机实测，工作目录 `F:\CTFfiles\knowledgeBase`：

| 命令 | 结果 |
|---|---|
| `.\.venv\Scripts\python.exe -m pytest -o addopts="" -q` | **132 passed in 56.36s**（P0 的 107 + P1 新增 25；与前端测试并行跑） |
| `cd tools\agent\webapp; npm run check` | 通过（`tsc -b` 无输出） |
| `npm test` | **2 files / 14 tests passed**（P0 的 10 + P1 新增 4） |
| `npm run build` | 通过；JS 801.22 kB（gzip 247.94 kB），CSS 206.80 kB（gzip 31.24 kB） |
| `python tools\eval_search.py` | hybrid：22 条，top1=1.0000，hit@5=1.0000，MRR=1.0000，recall@5=1.0000 |
| `python tools\eval_search.py --mode fts` | fts：22 条，top1=0.9091，hit@5=1.0000，MRR=0.9545，recall@5=1.0000 |

P1 评测对照（同一固定集，改动前 → 改动后）：

| 指标 | 改动前（P0 代码） | 改动后（P1） |
|---|---|---|
| top1 | 0.9545 | **1.0000** |
| hit@5 | 1.0000 | 1.0000 |
| MRR | 0.9697 | **1.0000** |
| recall@5 | 1.0000 | 1.0000 |

- “改动前”是 P1 开始时的实测结果，唯一未进 top1 的是
  `ctfshow SSTI Flask Jinja2 题解`（expected `_des/wp_summary/web/ctfshow-SSTI.md`，
  当时第 3 名）。
- “改动后”在同一集上修好了该条；提升来自文档级最好块、候选池下限、查询噪声
  清理与单字母精确匹配，不是调 RRF 权重。
- 评测是**离线**的：只读本地 FTS/向量/图谱索引，不启动 Ollama，不调用生成。

测试覆盖点：

- server：P0 全部保留；新增 search 命中段落/章节/原因、`doc_type` 筛选与计数、
  非法类型 400、feedback JSONL 追加、query-level 反馈、非法 verdict/路径/超长
  note 拒绝且不落盘。
- 检索：FTS 文档级去重、命中章节、单数字 payload token 过滤、单源融合去重；
  命中段落清洗、命中词、文档类型。
- 评测：top1/MRR/recall 指标、重复结果去重、空 expected 校验、仓库固定查询集
  可加载。
- 前端：原有 SSE 与显式参数测试保留；新增类型筛选传参、命中原因/章节/命中词
  展示、反馈按钮调用与“已记录”、图谱关联阅读独立展示。
- 构建产物 `dist/` 已被 gitignore，不提交。

测试局限：

- 自动化测试不启动 Ollama、不调用真实生成；评测脚本会加载本地 ONNX 嵌入
  与向量索引，但不联网、不调用 LLM。
- 评测集 22 条是人工挑选的固定样例，覆盖常见方向但不代表全库分布。
- 未在真实浏览器手动点选全部路径；交互验证依据组件测试 + 生产构建。
- `/api/ask` 的上游取消仍是“尽力而为”，Ollama 可能短暂收尾。
