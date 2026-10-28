# 开发计划（DEVELOPMENT_PLAN）

> 配合 `AGENTS.md` 与 `docs/PROJECT_MEMORY.md` 使用。
> 本文件只写计划与验收标准；当前事实与验证结果写进 PROJECT_MEMORY。

---

## P0（上一批，已授权，已完成 2026-10-28）

### 目标

把“能检索、能问模型”的核心路径做稳：不白屏、错误可见、取消诚实、
输入与路径有边界、生成串行、配置一致、核心端点有离线测试。

### 工作项

1. 项目记忆与协作约定：`AGENTS.md`、`docs/PROJECT_MEMORY.md`、本文件。
2. 版本控制：审查 `.gitignore`；`git init`；基线提交只含源码/知识数据/文档。
3. 前端：
   - 去掉 `setImmediate`，起点卡片与结果卡片使用显式参数，避免 stale closure。
   - TS 浏览器配置与 Vite Node 配置分离。
   - SSE 解析覆盖 `tok`/`err`/`done`、分块、UTF-8、空响应、取消、HTTP 错误。
4. 后端：
   - 统一 SSE 契约；正常结束发 `done`，错误发 `err`，空输出也可见。
   - `/api/ask` 串行/有界；忙碌返回 429 可见提示；断开时尽量关闭上游。
   - 模型/host/context 从 `config.toml` 读取，环境变量仅显式覆盖。
   - `/api/ask`、`/api/doc` 限定 `kb/` 内 Markdown；限制输入长度、paths 数、
     单文件大小、总上下文字符；`top_k` 有上限。
   - `/api/health` 分离 `model_ok` 与 `index_ok`。
5. 测试：
   - Python：server 核心端点离线 Mock（health、search、doc、ask 校验、
     SSE tok/err/done、路径越界、忙碌拒绝）。
   - 前端：SSE 契约测试 + SearchPage 显式参数组件测试。
6. 文档：修正已确认的事实错误；记录复现命令与测试局限。
7. 提交一个 P0 修复提交，更新记忆与本计划。

### 验收结果

- ✅ `pytest -o addopts="" -q` → 107 passed。
- ✅ `npm run check`、`npm test`（10 passed）、`npm run build` 全绿。
- ✅ 无 `setImmediate`；起点/结果卡片使用显式参数并有组件测试。
- ✅ 后端 `err` / 空响应 / 429 忙碌在前端可见；`done.info` 展示。
- ✅ `/api/ask` / `/api/doc` 限制在 `kb/` 内 `.md`；超长/超量输入 400。
- ✅ health 分离 `model_ok` / `index_ok`。
- ✅ 测试未启动真实模型、Ollama、Docker，可离线重复。

### 未完成 / 测试局限

- 真实浏览器手测、真实模型质量与耗时未纳入本批。
- 上游取消只能尽力关闭连接，不能保证 Ollama 瞬时停算。
- P1 已在下一节完成；P2–P4 未实现。

### 明确不做

- 不做检索排序重写/评测集建设（P1）。
- 不做前端附件上传（P2）。
- 不做题目工作区持久化（P3）。
- 不做三态条件、脚本工具架、Writeup 生成（P4）。
- 不换模型、不下载模型、不做架构重写、不无限扩展。

---

## 本批（P1，已授权，已完成 2026-10-28）

### 目标

让检索结果可解释、可按资料类型筛选、可反馈、可复现评测；
排序调整只依据固定评测集，不凭感觉改权重。

### 工作项

1. 命中段落与原因：`/api/search` 返回命中 chunk、章节、命中词、
   词面/向量/图谱来源与 RRF 贡献。
2. 检索候选修复：FTS 按文档只保留最好块；单源融合按文档去重；
   候选池设下限，避免 `top_k` 变化导致排序抖动；单数字 payload token
   与单字母前缀噪声清理。
3. 类型筛选与整理：`doc_type=topic|card`；结果带类型与计数；
   前端可筛选、显示类型徽章；图谱补入条目单独列为“关联阅读”。
4. 反馈记录：`POST /api/feedback`，有用/无用/采用追加到
   `work/feedback/feedback.jsonl`；限制输入且只校验 `kb/` 内 Markdown。
5. 可复现评测：`eval/search_queries.json` 固定查询集；
   `tools/eval_search.py` 输出 top1/hit@5/MRR/recall@5；
   记录 P0 → P1 基线对照。
6. 测试：Python 覆盖命中解释、类型筛选、反馈、文档级去重、评测指标；
   前端覆盖类型筛选、解释展示、反馈、图谱关联。
7. 文档：更新记忆、计划、交接、UI 与评测说明。

### 验收结果

- ✅ `pytest -o addopts="" -q` → 132 passed。
- ✅ `npm run check`、`npm test`（14 passed）、`npm run build` 全绿。
- ✅ `/api/search` 返回命中段落、章节、命中词与 `fts/vec/graph` 原因。
- ✅ `doc_type` 筛选与计数；前端可在搜索前切换专题/比赛卡片。
- ✅ 反馈写入本地 JSONL，非法输入 400 且不落盘。
- ✅ 固定集 hybrid：top1=1.0000，hit@5=1.0000，MRR=1.0000，recall@5=1.0000。
- ✅ 同一集 FTS-only：top1=0.9091，hit@5=1.0000，MRR=0.9545，
  recall@5=1.0000；保留 hybrid 有评测依据。
- ✅ 改动前 → 改动后：top1 0.9545→1.0000，MRR 0.9697→1.0000。
- ✅ 未启动真实 Ollama/LLM；评测只读本地索引。

### 未完成 / 测试局限

- 评测集 22 条为人工固定样例，不代表全库分布；扩集需另立任务。
- 反馈已记录但尚无汇总/导出 UI，也未用于排序。
- 未做真实浏览器手测；组件测试 + 生产构建通过。
- 图谱价值仍未证明；固定集没有支持“图谱提权”的证据。

### 明确不做

- 不调 RRF/BM25 权重凑分；固定集已无可测提升空间，等更大评测集再说。
- 不做附件上传、题目工作区、三态条件、脚本工具架、Writeup 生成（P2–P4）。
- 不换模型、不下载模型、不做架构重写。

---

## P2（已授权，已完成 2026-10-28）

### 目标

只读附件分析：不执行附件，不调用外部命令，结果结构化、可复现评测；
前端上传入口按计划留到 P3 一起接。

### 工作项

1. `tools/agent/attachment.py`：类型/扩展名不符、雕刻、PNG/WAV/ZIP 结构、
   异常、base64/hex/url 解码、关键字符串、脚本警告、`executed=false`。
2. `POST /api/analyze?name=`：原始字节、大小/名字限制、隔离落盘、
   文件名清洗防路径穿越；`/api/health` 暴露 `attachment.max_bytes`。
3. 固定样例评测 `eval/attachment_cases.json` + `tools/eval_attachments.py`，
   样例现场生成，不提交二进制。

### 验收结果

- ✅ `pytest -o addopts="" -q` → 151 passed。
- ✅ `tests/test_attachment.py tests/test_server_api.py` → 55 passed。
- ✅ `python tools/eval_attachments.py` → 5/5 通过（pass_rate=1.0000）。
- ✅ 超限 413 且不写盘；空附件/超长名字 400；脚本只警告不执行。
- ✅ 前端未改，沿用 P1 的 14 passed / 构建结果（上批未重跑前端）。

### 未完成 / 测试局限

- 只做静态结构/字符串/编码嗅探，不反编译、不模拟执行、不沙箱运行。
- ZIP 只列目录不解压；加密 ZIP 只提示需要密码。
- `work/attachments/` 暂无自动清理策略。
- P2 时未接入 React 上传入口，P3 已补。

### 明确不做

- 不调用 `binwalk`/`exiftool`/`strings` 等外部命令，不执行上传内容。
- 不做反编译、动态调试、沙箱运行。

---

## P3（已授权，已完成 2026-10-28）

### 目标

把附件分析接入搜索页，并新增纯本地 JSON 的题目工作区：
事实 / 尝试 / 资料收藏 / 时间线，可导出 Markdown，不引入数据库框架。

### 工作项

1. **附件上传入口**：搜索页选择/拖拽文件，读取原始字节，
   `POST /api/analyze?name=`；按 `health.attachment.max_bytes` 预检，超限不发请求；
   报告按文件/类型/雕刻/结构/异常/解码/字符串/警告分节折叠；不执行、不预执行。
2. **工作区存储**：`tools/agent/workspace.py`，`work/workspaces/<id>.json`；
   用户可指定 ID（默认 uuid）与标题；原子落盘；时间线只读自动追加。
3. **工作区 API**：创建/列出/读取/改名/状态/删除；事实增删；尝试增删改状态；
   收藏增删；时间线读取；Markdown/JSON 导出下载。
4. **前端工作区页**：创建/选择/改名/状态/删除、加事实/尝试/收藏、
   改尝试状态、看时间线、导出 Markdown；当前工作区 `localStorage`。
5. **与搜索打通**：搜索结果「收藏到工作区」；附件报告「附到工作区」。
6. **报告入库**：完整报告 JSON 存进 `reference.report`（上限 256 KiB），
   Markdown 导出渲染摘要；`/api/analyze?workspace=` 可直接登记。
7. **测试**：新增 `tests/test_workspace.py`、前端附件与工作区测试；
   原附件/server 测试不回退。
8. **文档**：更新 PROJECT_MEMORY、HANDOVER、UI、本计划。

### 验收结果

- ✅ `pytest -o addopts="" -q` → **179 passed**（P2 的 151 + 新增 28）。
- ✅ `pytest tests/test_workspace.py -q` → 28 passed。
- ✅ 附件/server 回归 → 55 passed；附件评测仍 5/5。
- ✅ `npm run check`、`npm test`（4 files / 23 tests）、`npm run build` 全绿。
- ✅ 构建：JS 838.63 kB（gzip 258.46 kB），CSS 207.25 kB（gzip 31.31 kB）。
- ✅ 冒烟：创建 → 加事实 → 加尝试 → 收藏 kb 文档 → 导出 Markdown，
  各节与时间线正确（详见 PROJECT_MEMORY 第 9 节）。
- ✅ 工作区只写本地 JSON；`work/` 与冒烟数据未入库。

### 未完成 / 测试局限

- 单机单用户、无登录/权限；同进程 RLock 串行写，跨进程并发未加文件锁。
- Markdown 导出只渲染附件报告摘要；完整 strings 在 JSON 导出中。
- 未做真实浏览器逐路径手测；依据组件测试 + 生产构建。
- 工作区无版本历史/撤销，删除即删本地 JSON。

### 明确不做

- 不引入数据库/Web 框架；不做多用户、同步、云存储。
- 不执行附件，不做动态分析。
- 不做 P4 的三态条件、脚本工具架、Writeup 生成。

## P4（未实现）

- 适用条件三态：已知 / 未知 / 不满足。
- 只读脚本工具架（禁止自动执行外部导入脚本）。
- 由真实记录生成可追溯 Writeup 草稿。
- 图谱可用性由评测决定，不以边数作为 KPI。
