# 项目记忆（PROJECT_MEMORY）

> 本文件记录当前可复现状态、关键决策、运行命令、已知问题、下一步与验证结果。
> 区分三类信息：**已验证事实 / 推断 / 未验证**。旧文档里的数字若未在本重复现，
> 不得当作结论复用。

**最后更新**：2026-10-28（P0 批次已完成，验证结果见第 7 节）

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
- 基线 Python 测试：82 个用例通过（本批修改前运行）。
- 前端当前有 `node_modules/` 与 `dist/`，但基线无前端测试。

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

## 3. 本批 P0 决策

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

## 4. 运行命令

```powershell
# Python 回归（完整摘要）
.\.venv\Scripts\python.exe -m pytest -o addopts="" -q

# 仅 server 测试
.\.venv\Scripts\python.exe -m pytest -o addopts="" -q tests\test_server_api.py

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
- 检索排序噪音（专题文档 vs 比赛卡片）本批未改，留待 P1 评测驱动。
- 真实模型回答质量与耗时本批未测；自动化测试全部离线 Mock。
- `work/` 与 `temp_newData/` 体积大（后者约 18.9 GB），只在本地保留，不入库。
- 外部导入脚本只允许静态审查，不在本批执行。

---

## 6. 下一步（不在本批实现）

- P1：检索命中段落/命中原因、类型筛选、相似结果整理、反馈记录 + 可复现评测。
- P2：前端附件分析（大小限制、隔离、默认不执行脚本）。
- P3：持久化题目工作区（事实/尝试/资料收藏）。
- P4：适用条件三态（已知/未知/不满足）、只读脚本工具架、由真实记录生成
  可追溯 Writeup 草稿。
- 图谱价值由评测决定，不以边数作为目标。

---

## 7. 验证结果（2026-10-28）

以下均为本机实测，工作目录 `F:\CTFfiles\knowledgeBase`：

| 命令 | 结果 |
|---|---|
| `.\.venv\Scripts\python.exe -m pytest -o addopts="" -q` | **107 passed in 34.26s**（原 82 + server 25） |
| `cd tools\agent\webapp; npm run check` | 通过（`tsc -b` 无输出） |
| `npm test` | **2 files / 10 tests passed**（67.91s，jsdom 环境启动慢） |
| `npm run build` | 通过；JS 791.18 kB（gzip 245.12 kB），CSS 206.80 kB（gzip 31.24 kB） |
| `git diff --cached` 体积检查 | 基线 1638 文件约 3.2 MB；大目录均忽略 |

测试覆盖点：

- server：health 模型/索引分离、模型名解析、search 命中与非法输入、doc 路径越界
  与非 Markdown、ask 参数校验、路径穿越不泄露、429 忙碌拒绝、
  SSE `tok/tok/done`、模型异常 `err`、空输出 `err`。
- 前端：SSE 分块/UTF-8/CRLF、`err`、空响应、429、取消传播；
  SearchPage 起点卡片显式搜索、结果卡片显式提问、错误可见、`done.info` 展示。
- 构建产物 `dist/` 已被 gitignore，不提交。

测试局限：

- 未加载真实嵌入模型、未启动 Ollama、未调用真实生成。
- 未在真实浏览器手动点选全部路径；白屏修复依据代码审查 + 组件测试。
- `/api/ask` 的上游取消是“尽力而为”，Ollama 可能短暂收尾。
- 真实回答质量、耗时、图谱边数、无 title 篇数本批未复测。
