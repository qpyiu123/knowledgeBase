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
- P1–P4 已在后续各节完成；本批只记录 P0 当时的边界。

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

## P4（已授权，已完成 2026-10-28）

### 目标

把检索从“命中什么”推进到“前提是否成立”，收敛只读脚本工具架，并让工作区
记录直接生成可追溯的 Writeup 草稿。不换模型、不改排序参数、不引入新依赖。

### 工作项

1. **适用条件三态**：新增 `tools/kb/applicability.py` 与
   `tools/kb/applicability_rules.json`。规则完全确定性：
   - `requires` front matter：前提资料是否在本次检索上下文，或查询是否点名；
   - 关键词规则（含否定词）：支持线索→known，否定线索→unsatisfied，
     无证据→unknown；
   - glibc 版本区间规则：区间内 known、区间外 unsatisfied、未给版本 unknown。
2. **检索解释入口**：`/api/search` 每个命中新增 `applicability`
   （整体状态、条件明细、`hint`、规则/requires 计数），响应顶层给出三态计数；
   搜索页显示“前提：已知/未知/不满足”和“缺少前提：…（unknown）”提示。
3. **ask 提示入口**：`/api/ask` 生成前用同一套规则检查引用资料，把
   “缺少前提 / 不满足 / 参见路径”写进系统提示，明确要求模型不要假设前提成立；
   判定失败只降级为提示，不阻断问答。
4. **只读脚本工具架**：新增 `tools/scripts/`，按 `crypto/`、`forensics/`、
   `misc/` 分类；公共 `_shared.py` 只做 stdio/JSON/整数解析。脚本声明只读、
   不执行输入、不联网、不自动执行、不做武器化。`tools/scripts/README.md`
   列出每个脚本的用途、输入与输出。
5. **可追溯 Writeup 草稿**：`WorkspaceStore.export_writeup()`
   由事实/尝试/资料/时间线生成模板：题目名、方向、事实、按时间排序的
   尝试（方向→结果→结论）、kb 资料引用（路径+章节锚，能校验时标注是否存在）、
   Flag、时间线。每条信息带 `来源 #entry-id` 与隐藏 `entry:` 标记。
   后端新增 `GET /api/workspaces/<id>/export?format=md&mode=writeup`。
6. **前端**：工作区导出增加「摘要 / Writeup 草稿」选择；资料收藏可填写
   可选章节锚点；搜索页展示适用条件三态。
7. **测试**：新增 `tests/test_applicability.py`、`tests/test_scripts.py`，
   扩展 `tests/test_workspace.py`、`tests/test_server_api.py` 与前端测试。
8. **文档**：更新本计划、PROJECT_MEMORY、HANDOVER、UI。

### 验收结果

- ✅ `pytest -o addopts="" -q` → **198 passed**（P3 的 179 + P4 新增 19）。
- ✅ `eval_search.py` → 22 条，hybrid top1 / hit / MRR / recall 均为 **1.0000**。
- ✅ `eval_attachments.py` → **5/5 通过**（pass_rate=1.0000）。
- ✅ `npm run check`、`npm test`（4 files / 26 tests）、`npm run build` 全绿。
- ✅ 构建：JS 839.79 kB（gzip 258.76 kB），CSS 207.25 kB（gzip 31.31 kB）。
- ✅ 脚本库 3 个样例脚本用临时数据实跑通过；只读标记为 `true`，均不执行输入。
- ✅ Writeup 导出每条信息可回溯到条目 ID；kb 路径锚点与存在性校验可复现。

### 未完成 / 测试局限

- 适用条件仍是**规则/特征驱动**的有限覆盖；未登记的题型返回 unknown，
  不会自动学习新规则；规则文件需要人工维护。
- 检索排序未改；三态只作为解释与提示，不参与打分。
- Writeup 只汇总工作区已有记录，不自动补写未记录内容；Flag 识别仅匹配
  `flag{...}` 形式。
- 脚本库仍是静态只读探针，不做解压、动态调试、反编译或沙箱执行。
- 自动化测试全部离线，未在真实浏览器逐项录制交互。

### P5 语义纠偏（2026-10-28）

P4 的三态实现存在“把未知粉饰成已知”的偏差，本批只改判定语义，不动检索与排序：

1. **无规则不再假已知**：有 front matter 的资料型条目若没有命中任何规则或
   `requires`，返回 `unknown` + `尚未评估，无已知前提线索`，`trace` 仍为 0；
   没有 front matter 的杂项才保持 `known` / `无额外适用前提`。
2. **检索命中前提 ≠ 前提已满足**：`requires` 目标只在本次上下文中出现时降级为
   `unknown`，提示“是否已掌握由你确认；参见 kb/...”；只有查询显式点名该前提
   才判 `known`。
3. **版本按整数段比较**：新增 `_parse_version`（点分数字段，忽略非数字后缀），
   删除 `float` 路径；`2.31` 与 `2.31.0` 相等，`2.35.1` 视为越界，区间仍为闭区间。
   规则 `min/max` 解析失败返回 `unknown` + `规则版本区间无效`。
4. **正负线索冲突不强行满足**：关键词规则同时命中 `any` 与 `none` 时返回
   `unknown` + “线索冲突，请人工确认”；仅命中否定词仍为 `unsatisfied`。
5. **汇总同源**：`evaluate_paths` 把“有 front matter 但无规则”的条目也写进
   unknown 提示，避免 ask 系统提示说“所有前提均已知”。

验证：`pytest -o addopts="" -q` → **206 passed**（P4 后 200 + 新增 6）；
`eval_search.py` 仍 22/22、top1/hit/MRR/recall 均 1.0000；检索代码与排序未改。

### 明确不做

- 不用小模型自由判定适用条件，不让模型改写判定结果。
- 不自动执行 `tools/scripts/` 或用户上传内容，不做武器化输出。
- 不改检索权重、固定评测集、模型与索引。
- 不做多用户、云同步、数据库或新 Web 框架。

---

## 修复批（2026-10-28 晚，已授权，已完成）

### 目标

修复一键启动脚本在用户实测中暴露的三个问题：pid 记录错、端口被旧后端占用时
静默跳过、索引过期无人提示；不改变 8765/11434 的端口与路径规则。

### 工作项

1. pid 修正：启动后按端口反查真实监听进程写入 `logs/*.pid`；`-Stop` 先按端口
   关闭，再处理 pid 文件残留外壳；按命令行校验归属，避免误杀。
2. 旧后端提示：`/api/health` 增加 `build`（git 短 HEAD + 源码指纹）；
   端口被占用时比较运行中 build 与当前代码，缺字段或不一致明确提示
   `-Stop` / `-Start`，不静默跳过。
3. 索引新鲜度：`-Status` / `-Start` 比较 kb 最新 md 时间与 `fts.db` 时间，
   并比较 kb 文章数与 FTS `docs` 数；过期提示 `-Reindex`。
4. 新增 `-Reindex`：前台运行 `python tools\cli.py index`，显示进度。
5. 兼容与文档：Windows PowerShell 5.1 / pwsh 公共语法，`start.ps1` 保持
   UTF-8 BOM；同步 PROJECT_MEMORY、HANDOVER 与脚本注释。
6. 测试：pytest 全绿；server 测试断言 health `build`；用备用端口冒烟
   pid 反查、停止与 build 比较。

### 验收结果

- ✅ `pytest -o addopts="" -q` → **200 passed**（P4 198 + 新增 2）。
- ✅ `tests/test_server_api.py` → **46 passed**。
- ✅ 前端未改源码，`npm run check` / `npm test`（4 files / 26 tests）/ `npm run build` 仍通过。
- ✅ 备用端口 8799 冒烟：`logs\web.pid` 与端口 OwningProcess 一致；
  health 返回 `build`；`-Stop -Port 8799` 后端口释放，11434 未受影响。
- ✅ `-Status` 能识别现有旧后端（无 `build`）与索引 1568 vs 1567 的不一致。
- ✅ 没有停止/重启现有 8765/11434，没有新增依赖或改模型。

### 未完成 / 测试局限

- 自动化测试没有 Pester 覆盖 PowerShell；行为由 `-Status` 与备用端口手工冒烟验证。
- 本机未安装 pwsh，未实测；仅使用 5.1/pwsh 公共语法。
- `build` 不含 `config.toml` 与前端 `dist/`；索引新鲜度是时间+数量判断，无内容哈希。
- 本批未实际重建索引；需要用户执行 `-Stop` → `-Reindex` → `-Start`。

---

## P7（已授权，已完成 2026-10-28）

### 目标

缩短索引重建耗时并保护失败场景：用内容清单判断增删改，向量按块哈希复用，
正式索引采用临时文件 + 原子替换；向量不可用时不得打印“索引就绪”。
不改检索权重、评测集、模型、前端与 `graph.db`。

### 工作项

1. **内容清单**：新增 `tools/kb/manifest.py`。`scan(kb_dir)` 复用
   `parser.iter_md_paths` 的收录规则生成 `{rel_path: sha256}`；
   `diff(old, new)` 返回 added / removed / changed；清单原子写入
   `index/manifest.json`（`version: 1`）。`start.ps1` 的 `Get-IndexInfo`
   改为优先读 manifest 计数，消除脚本与 Python 两套规则漂移。
2. **向量块缓存**：新增 `index/vectors_cache.db`，键为
   `(rel_path, chunk_index)`，值为 chunk 文本 sha256 + 向量。重建时未改块复用，
   新增/变化块重新编码，删除块计入 `removed_chunks`；输出
   `reused / reencoded / removed_chunks / seconds`。
3. **原子切换与失败保护**：FTS、向量、缓存、manifest 先写 `.new`，全部成功后
   一次替换；失败删除临时文件、保留旧库、退出码 1、打印失败阶段。
   向量失败默认整体回滚；`--fts-only` 只刷新 FTS 与 manifest 并警告向量停留旧时间。
4. **可信结果**：`cli.py index` 最终行改为三态：
   `完整增量更新` / `仅 FTS` / `失败回滚`，并报告增量统计。
5. **测试**：新增 `tests/test_manifest.py`、`tests/test_reindex.py`，
   覆盖 scan/diff 增改删与过滤规则、manifest 读写/坏版本退化、改/加/删一篇后的
   向量复用、`--fts-only`、编码失败回滚、模型不可用报失败而非就绪。
6. **文档**：PROJECT_MEMORY、HANDOVER 追加增量重建节；本文件记录验收结果。

### 验收结果

- ✅ `pytest -o addopts="" -q` → **217 passed in 48.54s**（P4/P5/P6 基线 207 +
  本批新增 10）。
- ✅ `eval_search.py` → **22/22**，hybrid top1 / hit@5 / MRR / recall@5 均 **1.0000**。
- ✅ 新增 `tests/test_manifest.py`（6 个）与 `tests/test_reindex.py`（4 个），共 10 个。
- ✅ 首次无 manifest/无缓存自动退化为全量；旧索引仍可被旧代码读取。
- ✅ `start.ps1` 篇数改为 manifest 优先，KB 文件未改；本批只改文档与上述实现，
  未改检索排序、评测集、模型或前端。

### 未完成 / 测试局限

- FTS 仍是整库重建（只是先写临时文件），没有块级增量。
- `swap` 阶段逐个 `os.replace`；重试仍失败时不保证回滚已替换的文件，需重跑重建。
- `--fts-only` 会更新 manifest，导致篇数与最新 kb 一致但向量库可能陈旧；
  只能靠命令警告识别，`/api/health` 未单独暴露向量陈旧标志。
- `-Status` 的过期判断仍是 mtime + 篇数，不逐文件比较 manifest 哈希，
  只改内容且不动时间戳的变更可能不提示。
- 测试全部在 tmp 环境离线完成；本批未在真实 1567 篇库上执行耗时冒烟，
  真实增量耗时与“改一篇只重编码其分块”的规模效应待用户实测。

---

## P8（已授权，已完成 2026-10-28）

### 目标

单文件被防护软件/权限拒绝读取时，重建索引跳过并警告，不阻断全库更新。

### 工作项

1. `manifest.scan(kb_dir, old=None)` 逐文件捕获 `OSError`/`PermissionError`；
   返回仍为 dict（`ScanResult`），新增 `skipped`；有旧清单时保留旧 sha。
2. `reindex` 逐篇读取也包进容错，合并 scan/docs 的 skipped，统计写入
   `stats["skipped"]`；CLI 结果行追加“跳过 N 个不可读文件”，并输出 stderr 警告。
3. 新增测试：scan 保留旧 sha、CLI 输出“跳过”、icacls deny 后重建成功且恢复后
   重新入索引。
4. 文档记录降级语义与恢复行为。

### 验收结果

- ✅ `pytest -o addopts="" -q` → **220 passed in 36.83s**（P7 217 + 新增 3）。
- ✅ `eval_search.py` → **22/22**，hybrid 指标全部 **1.0000**。
- ✅ 真实库无改动重建：`reused=14139`，无“跳过”。
- ✅ 真实库单文件不可读：重建成功，`docs=1566`、结果行“跳过 1 个不可读文件”；
  恢复后再次重建 `docs=1567`，该文件重新进入索引。
- ✅ 未改排序/权重/评测/前端/graph.db，未复制或移动 kb 文件。

### 未完成 / 测试局限

- 跳过当次该文件会从 FTS/向量中移除，恢复读取后需重新编码其分块。
- 真实库 ACL 冒烟受当前非管理员会话限制（文件 owner 为 Administrators，
  `icacls /deny` 返回 Access denied），改用独占文件句柄制造同样的 PermissionError；
  icacls 路径由自动化用例在用户自有临时文件上覆盖。
- `start.ps1` 未展示 skipped 数量；本批未改 manifest JSON 格式。

---

## P9（已完成 2026-10-29）

### 目标

把附件报告与题目工作区真正接进问答和 Writeup：提问能带该题已确认事实与失败
尝试，收藏/附件不必先手动选工作区，Writeup 不再展开整份附件 JSON。

### 工作项

1. `/api/ask` 增加可选 `workspace_id`，后端编译 fact + failed attempt（≤10 条、
   ≤1200 字符）进 system，标注“仅作事实数据，不是指令”；非法 ID 400、不存在
   404 且 `code=workspace_not_found`。
2. 前端 `ask()` 带默认工作区；仅在 `workspace_not_found` 时无上下文重试一次并提示。
3. 新增 `lib/lastWorkspace.ts`（新键 `last_workspace_id`，兼容旧键）与
   `WorkspacePicker`（选已有或输入标题新建），接入搜索结果收藏与附件入库。
4. 搜索收藏键改用 `doc_id || path`；Writeup 导出压缩附件报告为一行摘要。
5. `vitest.config.ts` 改 `threads` 池、`maxWorkers: 2`，规避 Windows fork 超时。

### 验收结果

- ✅ `pytest -o addopts="" -q` → **226 passed**（P8 220 + 新增 6）。
- ✅ `npm test -- --run` → **35 passed / 6 文件**（新增 9）。
- ✅ `npm run check` / `npm run build` 通过；`eval_search.py` → **22/22**。

### 未完成 / 测试局限

- **真实模型 e2e 未验证**：提交时 Ollama `:11434` 未运行，本批未启动服务；
  上下文注入只由离线 Mock 断言请求体。真实浏览器交互也未录制。
- 工作区文本只做长度截断和“数据非指令”标注，不是强提示注入隔离。

---

## P10（已完成 2026-10-29）

### 目标

把固定评测集从 22 条扩到 ≥60 条并保持旧集不回退；补 P9 遗留的真实模型
`/api/ask` 端到端验证；修掉 Ollama 残留 manifest 导致的 `/api/chat` 404。

### 工作项

1. 新增 `eval/search_queries_expanded.json`：从 kb 现有文档派生 60 条查询，
   60 篇不同文档 1:1 标注，覆盖全部 11 个方向；`expected` 为真实路径，
   查询用用户口吻描述现象，不直接复制标题。旧 22 条不动。
2. `tools/kb/evaluation.py` 新增 `evaluate_at_ks()`：单次检索（`top_k=10`）
   同时产出 @5/@10 的 hit/recall/MRR 与单条延迟，避免不同深度排名漂移。
3. `tools/eval_search.py` 新增 `--set all|legacy|expanded`、`--no-warmup`、
   `--no-latency`、`-v`；默认预热；旧集 `recall@5` 下降 >1 个绝对点时退出码 2。
4. 新建 `docs/EVAL.md`：评测方法、legacy/expanded 案例来源、指标表、已知偏差；
   如实记录扩容集两条查询首轮未进前 5、人工改写措辞后命中的流程。
5. 修 `tools/agent/server.py`：`_resolve_model()` 按名称打分，多个同分候选用
   `/api/show` 探活，避开残留 manifest；health 的 `model_ok` 改用探活结果，
   `ok` 跟随 `model_ok`，不可用时给出可见错误。
6. 新增 `tools/e2e_ask.py`：标准库真实模型冒烟，建临时工作区注入 2 fact +
   1 failed attempt，带/不带 `workspace_id` 各问一次，断言 SSE 终态 `done`。

### 验收结果

- ✅ `pytest -o addopts="" -q` → **229 passed in 53.64s**（P9 226 + 新增 3）。
- ✅ `npm run check` / `npm test -- --run` / `npm run build` 全通过；
  前端 **6 files / 35 tests**，JS 849.49 kB（gzip 261.02 kB）。
- ✅ `eval_search.py`：legacy 22 条 top1/hit@5/MRR/recall@5 全 **1.0000**（未回退）；
  expanded 60 条 **top1=0.9833、hit@5=1.0000、MRR=0.9917、recall@5=1.0000**。
- ✅ 真实模型 e2e **PASS**（`work/e2e_ask_result.json`）：带工作区 135.2 s /
  `579 tok · 4.3 tok/s`，无上下文 131.6 s / `769 tok · 5.9 tok/s`，均无 err。
- ✅ 未改 kb 内容、未重建索引、未停止用户服务（pid 27888 保持运行）。

### 未完成 / 测试局限

- expanded 集有两条查询在首轮未命中后人工改写措辞（`expected` 未动），
  改写前原文未留档，指标偏乐观，且不是严格冻结盲测集。
- 查询从文档派生，存在词汇泄漏；每条只标 1 篇，同主题好文档会被判未命中。
- 未做图谱扩展/类型筛选的消融；平均延迟随本机负载波动。
- `tools/e2e_ask.py` 是一次性脚本，真实模型验证未纳入 pytest 自动化。

## P11（已完成 2026-11-01）

### 目标

真实浏览器全流程验收（含真实模型问答）；`backup.ps1` 备份 + 恢复演练；
把 day-one 状态显示补全（索引 manifest / 最近备份）；就地修复发现的缺陷。

### 工作项

1. `tools/e2e_browser.py`：Playwright（默认 Edge channel，绝不自动下载内核）
   五步真实浏览器流程 —— 首页加载/搜索/看全文抽屉、收藏到题目工作区、
   附件上传（假 PNG 实为 ZIP）与报告落库、问模型（附件+工作区上下文，
   `--skip-model` 或模型不可用时标 SKIP）、工作区 Writeup 导出（断言附件
   摘要行与 `来源 #id`）；截图入 `work/shots/`，结果 JSON 入
   `work/e2e_browser_result.json`；结束时删除测试工作区（`--keep-workspace` 保留）。
2. `backup.ps1`：staging 拷贝（规避 `graph.db` 等被占用的句柄）→
   `backup\ctf_kb_YYYYMMDD_HHMMSS.zip`，默认保留 3 份；只依赖
   Windows 自带 Compress-Archive。
3. `start.ps1 -Status` 新增 `Show-DataProtection`：只读展示索引 manifest
   `built_at`/篇数与最近备份文件（`backup\ctf_kb_*.zip` 最新一份）。
4. 修 `backup.ps1`：源目录补 `kb\_imported_cats\`（import0 批导入落盘处，
   原脚本只含 `kb\_imported\`）；文件重存为 UTF-8 BOM，否则 Windows
   PowerShell 5.1 按 GBK 解析中文串直接解析报错（与 start.ps1 同坑）。
5. `.gitignore` 增加 `backup/`（备份 zip 不入库）。

### 验收结果

- ✅ 浏览器 e2e **5 PASS / 0 SKIP / 0 FAIL**（含真实模型分支：回答 673 字符，
  1078b / 832 tok @ 35 tok/s，截图 7 张，`work/e2e_browser_result.json` status=PASS）。
- ✅ 备份：`ctf_kb_20261101_112314.zip`（94.05 MB），源目录确认
  `kb\_imported, kb\_imported_cats, index, work\workspaces`（`work\feedback`
  尚不存在，脚本优雅跳过并警告）；旧备份轮转后保留 3 份。
- ✅ 恢复演练：解压到临时目录后文件数三层全等（266 / 277 / 7）；
  用恢复出的 `index\fts.db` 直接检索「RSA 共模攻击」返回正确命中，
  stats `docs=1844, chunks=15564` —— 备份不只是文件齐全，恢复即可用。
- ✅ 索引一致性独立验证：manifest 哈希 vs 磁盘，543 个导入区文件
  0 缺失 / 0 多余 / 0 改动（`kb\_imported` + `kb\_imported_cats`）。
- ✅ `start.ps1 -Status` 三层全绿；增量 `cli.py index` 复跑
  `reused=15564, reencoded=0`（零改动，13.2s）。

### 过程记录（教训）

- 启动时 upgrade 提示「索引可能过期（kb 最新 20:44 晚于索引 20:33）」——
  mtime 陷阱：导入文件在重排后被触碰但内容未变。用 manifest 哈希比对
  证明索引一致后按增量索引刷新时间戳，`-Status` 恢复绿色。
  结论：mtime 警告只是启发式，判定以 manifest 哈希为准。
- `backup.ps1` 首发 GBK 解析报错，重存 BOM 后正常（老坑第 N 次重现：
  PowerShell 脚本必须 UTF-8 BOM）。

## P12 — DB-Q1 知识库只读质量审计

**目标**：在不改正文、不改索引、不启停服务的前提下，给 1844 篇语料一次可复核的
规模/质量/重复盘点，并冻结下一批人工确认与评测的协议。**本批不跑检索评测，
不声称任何指标提升。**

### 交付

1. `tools/audit_corpus.py`：只读审计 CLI。文档集合直接调 `kb.parser.iter_md_paths`
   （与索引同源，不另立 rglob 规则）；输出 inventory / duplicate_candidates /
   import_check / sample_plan / eval_protocol / run_meta / report；
   `--hash-before` + `compare-hash` 子命令自证输入未被改写。
2. `tests/test_audit_corpus.py`：23 个测试，全部基于合成语料（精确副本、近似副本、
   同模板不同解法、摘要卡包含、合法/未闭合/引用块/行内反引号围栏、缺元数据、
   YAML 语法错误、缺图、不可解码、类别越界、确定性、不写入输入、候选不截断、
   短文档不采信包含度、抽样可复现、compare-hash 检出变化）。
3. `docs/DB_QUALITY.md`：运行方法、实测规模、疑似分布、抽样结论、误报边界、Q2–Q4 计划。
4. `work/db_quality1/report.md` 与 `sample_review.md`（工作产物，gitignore）。

### 验收结果

- ✅ 覆盖：`docs=1844`，与预期一致（`kb/**/*.md` 1845 减去被 `_` 前缀排除的 `kb/_index.md`）。
- ✅ 只读自证：`kb/` 1845 个文件逐条 SHA-256 前后完全一致（`changed`/`added`/
  `removed` 全空），`compare-hash` 退出码 0；人工抽样读完后再取一次 live 快照仍一致。
  `index/` 7 个文件哈希前后一致（审计不重建索引）。
- ✅ 测试：新增 23 项全绿；全量 `pytest` **252 passed in 57.46s**（基线 229 + 23）。
- ✅ 统计：非法围栏 0、精确副本 0、近似候选对 230 / 簇 30（0.7500–0.9997）、
  同 URL 线索 3 组；front-matter YAML 语法错误 21；本地缺图 8 篇（47 个引用全缺）；
  无合法围栏 545（`_imported_cats` 275 / `_imported` 264 / `_des` 6）。
- ✅ 抽样：`_imported_cats` 18 层、种子 20261101、24 篇逐篇读完，证据带行号/短引文。

### 过程记录（教训）

- **别自己另写文档枚举规则**：`tools/kbcheck.py` 的 rglob+跳过 `_` 目录与索引
  `iter_md_paths` 不同源，直接调索引侧函数才保证"审计的篇数 = 索引的篇数"。
- **围栏识别要先剥引用前缀**：`> ``` ` 若不剥 `> `，整篇被判成"无围栏 + 围栏外散落
  ```"，5 篇误报。另外整行 4 空格缩进的 ``` 属缩进代码块，不能计数。
- **front-matter 解析失败 ≠ 缺少**：21 篇 `signals: [[Misc] …]`、`[RSA? cmd5!]`
  这类未加引号 flow 序列让 `yaml.safe_load` 抛错，早期实现把整块元数据当"不存在"。
  必须区分四类并回显原始报错行；实测这 21 篇 `source` 全空、其余 245 篇全非空。
- **去重候选不能按分数截断**：按"共享 shingle 排名取前 N 对"会漏掉分数最高但
  shingle 池较小的对——实测漏掉了 0.9997 的
  `_des/wp_summary/web/ctfshow-php特性.md` ↔ `ctfshow-命令执行wp.md`（两篇各 216 个围栏）。
  改为**逐对可证明下界**（jaccard≥t ⇒ shared ≥ t/(1+t)·max(|A|,|B|)；
  containment≥c ⇒ shared ≥ c·min(|A|,|B|)，取较小者），阈值以上的对全部评分。
- **包含度对短文档不可信**：短边 <50 shingle 时只认 jaccard，并显式打
  `tiny_doc_containment_ignored`。实测最小 shingle 集 144，该保护不排除任何真实文档。
- **同模板要挡在门外**：共用赛事模板、解法不同的两篇 jaccard 可到 0.667，
  默认阈值因此取 0.7 而不是 0.6。
- **argparse 子命令参数位置**：`--project-root/--kb-dir/--out-dir` 定义在主 parser 上，
  必须写在子命令**之前**，否则 `unrecognized arguments` 并退出 2（写测试时踩到）。
- **pytest 在 GBK 控制台读源码**：注释里出现非 GBK 字符会被替换成 U+FFFD 触发
  SyntaxError；`latin-1` 也无法编码中文，合成"不可解码文件"要先转义再 encode。

---

## DB-Q2（已授权，已完成 2026-11-02）

### 目标

在不改检索算法、不扩库、不开始 Q3 的前提下，完成三项最小干预：
修复 21 篇旧导入文档的 `signals` YAML 引号；逐对复核 25 对跨
`_imported` / `_imported_cats` 候选；回看 Q1 抽样里的题名错配/空壳/分类/缺图结论。

### 工作项

1. **基线与只读证据**：对 `kb/` 1845 个文件与 `index/` 7 个文件落 SHA256 基线；
   每阶段写 `work/db_quality2/progress.json`；保留 `work/db_quality1/` 原报告。
2. **可复跑修复工具**：新增 `tools/repair_signals.py` + 显式清单
   `tools/kb/signals_repair_manifest.json`。写入前校验原文件哈希，支持 `--dry-run`，
   重复运行无变化；只改 `signals` 一行，保留其它字段、CRLF 与正文。
3. **回归测试**：新增 `tests/test_repair_signals.py`，证明 21 篇字段解析成功、
   `source` 可读、正文哈希与修复前一致、原文确实曾 YAML 解析失败、哈希不符拒绝写入。
4. **25 对候选逐对裁决**：读全文并比较正规化正文与差异片段；默认保留，
   只有逐字等价且来源信息不丢失才建议合并；本批不删除/不合并任何文档。
5. **抽样更正**：区分“多题合并”与真实题名错配；确认缺图 8 篇/43 个去重 target、
   许可 `not_declared` 只记未核验；不伪造 parser 不支持的标签。
6. **重跑审计与索引**：审计到 `work/db_quality2/audit`；用既有增量
   `cli.py index` 与 `cli.py graph --build` 重建，保存输出。
7. **评测与回归**：`eval_search.py --set all`；全量 pytest；前端类型检查/测试/构建。
8. **文档**：`docs/DB_QUALITY.md` 追加 Q2 实测与更正；同步本文件与
   `docs/PROJECT_MEMORY.md`。

### 验收结果

- ✅ 21 篇修复：`dry-run=21`、第一次 `repaired=21`、第二次 `already_repaired=21`；
  kb 仅这 21 个文件变化，正文 SHA256 全部不变，修复前 index 哈希不变。
- ✅ 审计异常 21 → **0**，缺 `source` 21 → **0**，缺 `license` 1322 → **1301**；
  精确副本仍 0，近似候选仍 230 对/30 簇。
- ✅ 25 对：**4 对可合并建议**（#4/#5/#7/#12）、**21 对互补保留**、0 疑似、
  0 删除/合并；逐对证据见 `work/db_quality2/duplicate_review.md`。
- ✅ 抽样更正：Q1 的 10 篇“题名错配”实为标题等于首段题目的多题合并；
  3 篇“分类矛盾”同源；缺图按产物更正为 8 篇/43 个去重 target。
- ✅ 索引：`docs=1844, chunks=15564, reused=15396, reencoded=168, removed=0`；
  图谱 1844 节点/26 边/8 跨方向。
- ✅ 评测：legacy 22 条 top1/MRR/recall@5 全 1.0000；expanded 60 条
  top1=0.9833、MRR=0.9889、recall@5=1.0000，与导入后基线一致。
- ✅ 测试：`pytest` **257 passed**（252 + 5）；前端 check / 35 tests / build 通过。

### 未完成 / 测试局限

- 4 对“可合并”只是建议，Q2 不执行；是否移除需后续单独授权。
- 多题合并文件不拆分，不新增 parser 不支持的多题标签。
- 博客页眉噪声、折断表格、导入批重复句、43 个缺图均未修（需正文改写/重跑导入/下载）。
- 未做语义去重；未开始 Q3 冻结评测，未改 Q3 协议。

### 明确不做

- 不改检索算法/权重/评测查询集，不扩库，不启停用户服务，不碰 `F:\ctf`。
- 不删除任何文档，不合并正文，不下载远端图片，不宣称全库已获授权。
- 不开始 Q3、Q4。

## DB-Q3 Part B — 方法论卡片试点（2026-11-02）

目标：把"已验证的解题手法"沉淀成**可直接照抄执行**的方法卡，
每张卡都绑定一个可自检的脚本（或明确说明为什么不需要脚本），并纳入 pytest 回归。

### 交付内容

1. `kb/_methods/` 下 **12 张方法卡**（front-matter 含 `title/category/tags/signals/difficulty/source/tools`，
   正文七栏：适用场景 / 前置条件 / 步骤 / 立即可用脚本 / 手工示例 / 失效场景 / 相关文档）：

   | # | 卡片 | category | 脚本 |
   |---|---|---|---|
   | 1 | `rsa_common_modulus_attack.md` | crypto | `rsa_common_modulus.py` |
   | 2 | `rsa_shared_prime_attack.md` | crypto | `rsa_shared_prime.py` |
   | 3 | `rsa_hastad_broadcast.md` | crypto | `rsa_hastad_broadcast.py` |
   | 4 | `rsa_wiener_continued_fraction.md` | crypto | `rsa_wiener_continued_fraction.py` |
   | 5 | `lcg_parameter_recovery.md` | crypto | `lcg_parameter_recovery.py` |
   | 6 | `mt19937_untemper.md` | crypto | `mt19937_untemper.py` |
   | 7 | `vigenere_autocrack.md` | crypto | `vigenere_autocrack.py` |
   | 8 | `hash_length_extension.md` | crypto | `hash_length_extension.py` |
   | 9 | `enc_chain_decode.md` | misc | `enc_chain_decode.py` |
   | 10 | `decompress_chain.md` | misc | `decompress_chain.py` |
   | 11 | `zip_password_attack.md` | misc | `zip_password_attack.py` |
   | 12 | `onchain_base64_decode.md` | blockchain | `enc_chain_decode.py`（复用） |
   | 13 | `ejs_prototype_pollution_rce.md` | web | 无脚本（payload 速查） |

   注：卡数 = 12 张"含脚本链路" + 1 张无脚本的 payload 卡 = **13 个 md**，
   对外口径的 12 指方法（`onchain_base64_decode` 复用编码脚本，`ejs` 属速查卡）。

2. `kb/_methods/scripts/` 下 **11 个脚本**，全部支持 `--selftest`（纯标准库优先，RSA 类用 pycryptodome 生成素数），
   每个自检都在 3 秒内完成，输出一行 `selftest ok: N/M（…）`。
3. `tests/test_method_scripts.py`：对每个脚本 `subprocess` 调用 `--selftest`（timeout 30s，断言 exit 0 且输出含 `selftest ok`）。
4. `work/q3/method_backlog.json`：**53 个主题**的排期清单（`done=12`），每项带真实 kb 出处路径与脚本/卡片落点。
5. 文档：本文件、`docs/PROJECT_MEMORY.md` §18、`docs/DB_QUALITY.md` §12 同步记录。

### 关键决策

- **卡片文件名不带下划线前缀**：`tools/kb/parser.py` 的 `iter_md_paths` 会跳过名字以 `_` 开头的文件，
  卡片需要能被 `cli.py index` 收录并参与检索，因此用 `rsa_common_modulus_attack.md` 这种命名；
  脚本目录 `scripts/` 在 `_methods/` 下，文件名也均不以 `_` 开头（后缀 `.py`，不参与 md 收录）。
- **每张卡必须有"手工示例"且数值经过实跑**：本轮发生过两次返工（Håstad 玩具模数开根失败、
  Wiener 三四位模数不满足 `d < n^0.25/3`），因此卡片里同时写明"反例警示"。
- **无脚本卡要说清原因**：EJS 卡依赖目标运行时（Node 版本、query 解析器、出网能力），
  纯 Python 自检只能验证"字符串拼对了"，没有实战增量，故只给 payload 与识别信号。
- **`zip_password_attack.py` 的"字典命中"自检在无法回读加密流的环境跳过**：脚本会打印原因，
  其余 5 项真实执行；这是环境限制而非逻辑缺陷，卡片里已明示。

### 验收结果

- ✅ 11 个脚本 `--selftest` 全部 exit 0（lcg 5/5、mt19937 5/5、vigenere 5/5、rsa_common 4/4、hastad 5/5、
  shared_prime 5/5、wiener 4/4、hash_length_extension 6/6、enc_chain 9/9、decompress 8/8、zip 6/6）。
- ✅ 13 张卡片 front-matter 与七栏结构校验通过（脚本化检查，见本轮验证命令）。
- ✅ `method_backlog.json`：53 项、`done=12`、所有 `sources` 路径真实存在（0 缺失）。
- ✅ `pytest -q -o addopts=`：**279 passed in 70.94s**（266 基线 + 13 新增）。

### 明确不做

- 不改检索算法/权重/评测查询集；不重建索引（本批新增的卡片需后续 `cli.py index` 才进检索）。
- 不启停用户服务，不碰 `work/` 以外的其它批次产物，不 `git add -A`。
- 不改动 `kb/_methods/` 之外的 kb 文档。
