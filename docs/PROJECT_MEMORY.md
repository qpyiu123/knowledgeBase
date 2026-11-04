# 2026-11-05：R3.1 当前目标与失败原因

- R2 已提交 `b9f6f9e`。工作区在现有信息区增加当前目标、待验证假设、待查项；JSON 兼容旧格式，读取旧文件不自动写回。
- 无效尝试分为运行出错、前提已排除、原因待确认；普通导出、题解草稿和模型上下文同步。运行错误可以排错后重试，假设独立标记为待验证。
- Python 419 项、前端 49 项、类型检查、生产构建和 Edge 保存/重载/修改/导出通过。详情见 R3-实施记录.md。
- 用户最新模型决定：默认 Qwen3.5-9B，可选 Qwen3.5-4B，不再使用 Qwen3；后续迁移可删除未选模型节省空间。当前仅保留文件，R3 后续接回 Vulkan，R5 按保留清单迁移。
- 下一批：当前卡点检索比较，以及两份 Qwen3.5 的统一按需解释与取消。

---

# 2026-11-05：R2 少量方法条件关联

- R1.3 已提交 `13b88ee`。R2 沿用原索引、布局和合并卡，先登记 RSA 共模、标准广播、单密文 k=0 开根三条路径。
- 网页“显示条件关联”默认关闭；展开后可查证据、未知项、核对方法、相近路径和原文小节。requires 单列阅读依赖，命中或点名资料不再改变技术条件。
- 固定 30 条原查询和排序一致，目标前五 30/30，状态与逐项预期错误均 0；26 项缺项保留未知。独立 Python 重复查询中位 A 34.57 ms / AB 40.98 ms，峰值工作集 49.7 MiB，生成调用 0。
- Python 407 项、前端 46 项、类型检查、生产构建和 Edge 检查通过；R1 及原 22/60 检索结果保持不变。详见 R2-实施记录.md。
- 下一批 R3：当前目标/假设/待查项，局部卡点资料比较，接旧模型按需解释。小指数原文的 `c < n^(1/e)` 步骤表述待 R4 资料修订；指南已采用整数根精确性条件。

---

# 2026-11-05：R1.3 独立 Python 与环境切换

- 用户补充 R1 的运行环境要求。复用旧项目已下载的官方 Python 3.13.17，当前项目 runtime/python-portable 已准备完成，依赖和许可随该目录移动；旧项目和 .venv 保留。
- 选择顺序：-PythonExe → KB_PYTHON → config.toml 的 runtime.python → 便携 Python / .venv。启动、索引、备份及激活命令均已接入。
- -CheckEnvironment 显示路径、版本与缺项；-NoModel 跳过模型启动和健康探测，解释接口返回明确关闭提示。
- 去掉系统 Python PATH、移动运行环境到带中文空格目录后，HTTP 查询、阅读、保存、语义查询和 52 个脚本自检通过；实际 PowerShell 5.1 启动通过，测试服务已关闭。
- Python 回归 365 项、前端 41 项通过；类型检查与构建通过。源码、准备脚本和清单入 Git，运行环境不入 Git。
- 详情见 R1.3-运行环境记录.md。R1.2 提交为 400f85c。
- 用户已确认 R2 先做少量方法条件关联；现有合并卡保持原样，不再等待此项确认。

---

# 2026-11-05：R1.2 完整文档、精确查询与原文代码关联

- R1.1 提交 `fa9d23d`。R1.2 接收旧库中 base64/json/re 的 Python 3.9 完整中文正文，保留来源、版本、许可与正文核对记录。
- 当前索引 1915 篇 / 15917 块，新增 3 篇、编码 95 块；54 张方法卡与 52 个脚本仍通过验收。
- 完整标识符和引号内错误原文先精确匹配。原文结果可直接访问引用它的方法卡及配套代码；来源关系从已有索引读取，查询不重建索引。
- Python 351 项、前端 41 项通过，类型检查、生产构建、HTTP 和 Edge 检查通过。三篇正文、许可与索引备份恢复通过。
- 固定 30 条：前五直接找到 29 条，另 1 条可通过第二条原文进入目标方法卡。旧 22/60 条 recall@5 均保持 1.0；详细命令见 R1-实施记录.md。
- R2 条件关联前，需要确认先做少量单方法规则，还是先拆分合并卡；已向用户询问。条件关联不得把阅读来源当作题目具备的技术前提。

---

# 2026-11-05：R1.1 关键词先返回与只读代码

- R0 提交 `2d025e8`，应用仍为 2.0.0。R1.1 沿用现有 Mantine 页面，未增加独立页面。
- 网页默认只走 FTS；语义补充可选，FTS 先显示，补充失败保留结果，新查询取消旧请求。
- 方法卡独立筛选，来源可点击；结果与抽屉均可打开配套代码，`/api/code` 静态读取、描述与复制。
- Python 347 项、前端 40 项通过，类型检查/构建通过；实际 HTTP 与本机 Edge 验收通过，生成调用 0。
- 混合检索结果与 R0 一致；FTS 方法特征前五 11/12，前十 12/12。完整命令与单次计时见 R1-实施记录.md。
- 下一步 R1.2：先接少量完整的官方语言文档，固定标识符/错误原文样例，补源文档到配套代码的关联，再比较同源展示。

---

# 2026-11-05：R0 恢复与方法卡接收

- 交接起点提交 `9dd3ed7`；R0 实施和命令见 [R0 实施记录](R0-实施记录.md)。
- 已保护并接收原有 41 张卡片、41 个脚本。原件 ZIP、旧虚拟环境保存在 backup 中，没有删除模型、资料或个人记录。
- 当前开发环境：项目 .venv / Python 3.12.0；直接依赖记录在 requirements-dev.txt。
- 当前索引：1912 篇、15822 块，方法卡 54 篇；结构验收 54/54、脚本自检 52/52。
- Python 回归 337 项、前端 35 项通过，类型检查及生产构建通过。实际 HTTP 查询、阅读、保存题目时生成调用为 0。
- 完整备份恢复验证 106 个方法文件与 14 个附件，数据库检查通过。恢复入口只写新空目录。
- 旧集与扩展集前五条命中均为 100%；新卡排在原文前面使 top1 下降，完整对比见实施记录。R1 先处理同源展示和纯关键词/代码快查。
- QR 仅作结构演示，Coppersmith CLI 为小范围枚举；实验格函数留待独立验收。

---

# 2026-11-05：接续开发交接

用户已将 E:/knowledgeBase 定为主开发和分发来源，优先无生成模型的资料、语言文档、代码查询与条件关联。比赛机为 8845HS / 24GB，继续使用用户验证过的旧模型与 Vulkan。

当前计划见 [长期开发计划](长期开发计划-离线比赛版.md)，首次接手见 [交接文档](新会话交接-2026-11-05.md)，语言与 GUI 规则见 [开发规范](开发规范.md)。R0 尚待新会话实施：恢复环境、验收 41 套新增成果、修复三张 YAML、更新索引与备份。每完成一个版本默认提交本地 Git。

本次只写交接和计划，应用代码、资料、模型和索引保持原样。下面保留历史记录。

---

# 项目记忆（PROJECT_MEMORY）

> 本文件记录当前可复现状态、关键决策、运行命令、已知问题、下一步与验证结果。
> 区分三类信息：**已验证事实 / 推断 / 未验证**。旧文档里的数字若未在本重复现，
> 不得当作结论复用。

**最后更新**：2026-10-31（import0：导入授权中文赛事 WP 散文 277 篇；见第 14 节）

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
- 后续方向：P1 检索可解释与评测（已完成）；P2 附件分析入口（已完成）；
  P3 持久化题目工作区 + 附件上传 UI（已完成）；P4 三态适用条件、只读脚本库与
  可追溯 Writeup 草稿（已完成）。图谱可用性由评测决定，不按边数凑指标。

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
- 基线 Python 测试：82 个用例通过；P0 后 107；P1 后 132；P2 后 151；
  P3 后 179；P4 后 **198**（新增适用条件、脚本库、Writeup 与端点用例 19 个）。
- 前端 P0 起有 Vitest（SSE + SearchPage），P1 后 2 文件 / 14 用例；
  P3 后 4 文件 / 23 用例；P4 后 **4 文件 / 26 用例**（新增三态展示与 Writeup 导出）。

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

## 3c. P2 决策（本批，2026-10-28）

1. **只读附件侦察**：新增 `tools/agent/attachment.py`，只解析字节，不执行
   附件中的脚本/可执行文件，也不调用 `binwalk`/`exiftool`/`strings` 等外部命令；
   结构解析复用 `agent.carve`，字符串与解码复用 `agent.recon`。
2. **隔离落盘**：`POST /api/analyze` 把原始字节复制到
   `work/attachments/<uuid>/upload_<安全名>`。文件名只保留最后一段、去掉控制
   字符与 Windows 非法字符，防路径穿越；`[attachment].dir` 或
   `AGENT_ATTACHMENT_DIR` 可改根目录。
3. **大小与名字边界**：默认上限 8 MiB（`[attachment].max_bytes` 或
   `AGENT_ATTACHMENT_MAX_BYTES` 覆盖，硬上限 64 MiB）；名字最长 240 字符；
   空附件、超长名字、超大附件分别返回 400/400/413，且超限时不写盘。
4. **结构化结果**：返回 `file`（大小/SHA256/扩展名）、`type`（真实类型、
   是否文本、预览、扩展名不符）、`carve`（内嵌雕刻）、`structures`
   （PNG/WAV/ZIP）、`anomalies`、`decoded`（base64/hex/url）、`strings`、
   `warnings`、`storage`，以及恒为 `false` 的 `executed`。
5. **安全提示不拦截**：可执行/脚本扩展名只给警告（“不会运行”），不拒绝上传；
   扩展名与真实内容不符只作为异常提示，不改写文件。
6. **兼容旧入口**：`analyze_probe()` 保留原文本格式，供 hint/CLI 继续复用；
   新增 `analyze_path` / `analyze_bytes` / `analyze_upload` 结构化入口。
7. **可复现评测**：`eval/attachment_cases.json` 固定 5 个代表性样例
   （PNG 追加 ZIP+base64、伪装 PNG 的 ZIP、纯文本 base64、WAV 尾部追加、
   脚本警告），由 `tools/eval_attachments.py` 的 `BUILDERS` 现场生成，
   pytest 与 CLI 共用同一份 manifest，不提交二进制。
8. **健康检查**：`GET /api/health` 增加 `attachment.max_bytes`，方便前端/调用方
   在发请求前就知道上限；原有 `model_ok` / `index_ok` 语义不变。
9. **前端范围**：本批不改 React 源码；接口与 PowerShell 调用方式补在
   `docs/UI.md`，后续可由前端直接接上传入口。

---

## 3d. P3 决策（本批，2026-10-28）

1. **纯本地文件存储**：新增 `tools/agent/workspace.py`，每个工作区一个 JSON
   文件，默认 `work/workspaces/<id>.json`（`[workspace].dir` 或
   `AGENT_WORKSPACE_DIR` 覆盖）；不引入数据库框架。
2. **ID 与标题可控**：创建时标题必填，ID 可省略（自动 uuid）或用户指定；
   ID 只允许 `[A-Za-z0-9_-]{1,64}`，已存在返回 409，路径穿越在校验阶段拒绝。
3. **条目模型**：`fact`（正文）、`attempt`（方向 + 结论 + `pending/success/failed`
   状态 + 可选备注）、`reference`（kb 路径或 `http(s)` URL + 备注）。
   文本、标题、路径、URL、方向、结论都有长度上限，条目数上限 500。
4. **时间线只读**：创建工作区、改元信息、增删条目、修改尝试状态都会自动追加
   `{ts, kind, summary}`；只提供读取接口，不提供时间线写入/删除接口。
5. **原子落盘**：同目录临时文件 + `os.replace`，Windows 上对短暂
   `PermissionError` 重试，避免杀软/索引服务占用导致半截 JSON。
6. **HTTP API 对齐现有 server.py**：`GET/POST/DELETE /api/workspaces...`；
   请求体沿用 JSON + 长度限制；工作区请求体上限 512 KiB（附件报告可能较大），
   其余端点仍为 64 KiB。错误码：400 输入非法、404 不存在、409 ID 冲突。
7. **导出**：`GET /api/workspaces/<id>/export?format=md|json`，Markdown 按
   事实 / 尝试 / 资料收藏 / 时间线模板拼装，带 `Content-Disposition` 可下载；
   JSON 导出保留完整工作区（含附件报告原始 JSON）。
8. **附件报告入库**：附件分析报告的完整 JSON 存入 `reference.report`
   （上限 256 KiB），Markdown 导出渲染类型、大小、SHA256、落盘路径、雕刻、
   结构、异常、解码、警告与“未执行”；`POST /api/analyze?workspace=<id>`
   可分析后直接登记为工作区资料。
9. **前端入口**：搜索页新增「分析附件」卡片，选择/拖拽后读取原始字节，
   先按 `/api/health` 的 `attachment.max_bytes` 预检，再
   `POST /api/analyze?name=`；报告按文件/类型/雕刻/PNG-WAV-ZIP/异常/解码/
   字符串/警告分节折叠展示。结果卡片可「收藏到工作区」。
10. **工作区页面**：侧栏新增「工作区」，支持创建/选择/改名/状态/删除，
    添加事实/尝试/收藏、修改尝试状态、删除条目、查看只读时间线、导出 Markdown；
    当前工作区存 `localStorage`，与搜索页共享。
11. **测试**：新增 `tests/test_workspace.py`（存储 + HTTP API + 导出 + 报告）
    与前端 `AttachmentPanel.test.tsx`、`WorkspacePage.test.tsx`；
    原有附件与 server 测试全部保留。

---

## 3e. P4 决策（本批，2026-10-28）

1. **三态判定只用规则**：`tools/kb/applicability.py` 不调用模型。整体状态取
   所有条件的最高严重度：有 unsatisfied 即 unsatisfied，否则有 unknown 即
   unknown，全部 known 才是 known。没有登记条件的资料视为 known 且无提示。
2. **`requires` 是硬前提**：解析 front matter 的 `requires`，把目标文档解析成
   kb 相对路径；只有“在本次检索上下文里”或“查询直接点名”才算 known，
   否则一律 unknown，不假设满足。目标不唯一/找不到时保留原始名字并标 unknown。
3. **规则文件可维护**：`applicability_rules.json` 每条规则含 `id`、`paths`、
   `label`、`kind`（keywords/version）、`any`/`none` 或 `min`/`max`、`source`
   （kb 路径+章节锚）。否定线索优先于支持线索，命中即 unsatisfied。
4. **解释与提示同源**：`/api/search` 的 `applicability`、`/api/ask` 的系统提示、
   评测都复用同一函数；`evaluate_paths` 把未确认前提格式化为
   “缺少前提：…（unknown）”或“不满足：…（unsatisfied）”，并附 `参见 kb/...`。
5. **排序不变**：三态仅用于解释/提示，不进入 RRF、BM25 或图谱加权；
   固定评测集与参数不动。
6. **只读脚本库**：`tools/scripts/` 按主题分目录，显式声明 `read_only=true`、
   `executed=false`；`--json` 稳定输出。README 列出用途与输入输出。
   根目录旧探针保留原样（gitignore），不删除用户资料、不自动执行。
7. **Writeup 可追溯**：`export_writeup()` 只用工作区真实条目生成；每条信息带
   `来源 #entry-id` 与隐藏 `entry:` 标记；kb 引用输出 `kb/<path>#<anchor>`，
   能拿到 kb 根目录时校验文件存在并标注“存在/未找到/未校验”。
8. **导出模式**：`GET /api/workspaces/<id>/export?format=md&mode=writeup`；
   `mode` 仅接受 normal/writeup，非法返回 400；文件名加 `-writeup` 后缀。
9. **前端**：工作区页增加「摘要 / Writeup 草稿」导出选择与章节锚点输入；
   搜索页显示“前提：已知/未知/不满足”和可操作提示。
10. **测试**：新增 `tests/test_applicability.py`、`tests/test_scripts.py`；
    扩展 workspace/server 与前端测试，覆盖三态、规则、脚本实跑、可追溯导出。

---

## 3f. 修复批决策（2026-10-28 晚）

1. **pid 记录真实监听者**：`start.ps1` 启动后轮询
   `Get-NetTCPConnection -LocalPort ... -State Listen` 的 `OwningProcess`，
   覆盖写入 `logs/web.pid` / `logs/ollama.pid`；不再保存 `Start-Process -PassThru`
   得到的外壳 pid。`-Stop` 先按端口关闭，再核对 pid 文件里的残留外壳进程。
2. **不误杀**：按端口停止前用 `Win32_Process.CommandLine` 校验命令行属于本项目；
   pid 文件里的进程若不属于本项目，只警告并删除记录，不发 `Stop-Process`。
3. **端口占用可解释**：`GET /api/health` 新增 `build`（git 短 HEAD +
   源码指纹）；端口已被占用时 `start.ps1 -Start` / `-Status` 读取运行中后端的
   `build` 并与当前代码比较。缺字段（旧后端）或不一致时黄字提示
   “检测到旧版本后端正在运行，建议先 .\start.ps1 -Stop 再 -Start”，不静默跳过。
4. **代码指纹**：新增 `tools/agent/buildinfo.py`，对 `tools/agent/*.py`、
   `tools/kb/*.py` 与 `start.ps1` 做内容 SHA256（取前 8 位），git 可用时
   前缀短 HEAD。只读文件，不联网、不启动服务。
5. **索引新鲜度**：`-Status` / `-Start` 比较 `kb/` 最新 `.md` 的
   LastWriteTime 与 `index/fts.db` 的 LastWriteTime，并比较 kb Markdown 数
   与 FTS `docs` 数；任一不一致即黄字提示
   “索引可能过期，运行 .\start.ps1 -Reindex”。
6. **-Reindex**：前台执行 `python tools\cli.py index`（FTS + 向量），显示进度；
   后端仍在运行时提示重建后需 `-Stop` / `-Start` 才能让新索引生效。
7. **兼容性**：只使用 Windows PowerShell 5.1 与 pwsh 都支持的语法；
   `start.ps1` 保持 UTF-8 BOM；不新增依赖、不换模型、不动监听中的服务。

---

## 4. 运行命令

> 工具脚本清点见 `docs/TOOLS_INVENTORY.md`（P3 时 21 个可执行入口 + 6 个仅 import 模块 + 10 个根目录临时探针；P4 新增 `tools/scripts/` 3 个只读工具与 1 个公共模块）。

```powershell
# Python 回归（完整摘要）
.\.venv\Scripts\python.exe -m pytest -o addopts="" -q

# 仅 server / 附件测试
.\.venv\Scripts\python.exe -m pytest tests\test_server_api.py tests\test_attachment.py -q

# P3 工作区存储 + HTTP API
.\.venv\Scripts\python.exe -m pytest tests\test_workspace.py -q

# P4 适用条件 + 只读脚本库 + Writeup
.\.venv\Scripts\python.exe -m pytest tests\test_applicability.py tests\test_scripts.py -q

# 只读脚本样例（不联网、不执行输入）
.\.venv\Scripts\python.exe tools\scripts\crypto\rsa_factor_probe.py --n 143 --json
.\.venv\Scripts\python.exe tools\scripts\misc\filter_probe.py --blacklist "eval" --payload "{print(1)}" --json

# P2 附件侦察评测（固定样例；可加 --json / --json-out / --check）
.\.venv\Scripts\python.exe tools\eval_attachments.py
.\.venv\Scripts\python.exe tools\eval_attachments.py --json --json-out work/attachment_eval.json

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
.\start.ps1 -Reindex
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
- 附件分析只做静态结构/字符串/编码嗅探，不做反编译、模拟执行或沙箱运行；
  ZIP 只列目录不解压，加密 ZIP 只提示需要密码。
- 附件分析结果会写入 `work/attachments/`（默认保留），暂未做自动清理策略；
  `work/` 不入库。
- 工作区只面向本机单用户，无登录/权限；API 绑定默认 `127.0.0.1`。
  同一进程内用 RLock 串行写入，跨进程并发写同一工作区未做文件锁。
- 工作区导出 Markdown 渲染附件报告摘要（类型/雕刻/结构/异常/解码/警告/落盘），
  不倾倒全部 `strings`；完整报告 JSON 仍保存在工作区 JSON 与 `format=json` 导出中。
- 附件报告上限 256 KiB；超限会在登记工作区时返回 400，附件本身已分析完成。
- 适用条件只覆盖已登记规则与 `requires`；未登记题型一律 unknown，
  规则文件需人工维护，不做模型自学习。
- 三态不参与排序；固定评测集只有 22 条，不能代表全部题型。
- Writeup 只汇总工作区真实记录，不自动补写未记录内容；Flag 只识别
  `flag{...}` 形式。
- `tools/scripts/` 只做静态只读分析，不解压、不执行、不反编译、不做武器化。
- pid 归属依赖 `Win32_Process.CommandLine` 含项目根路径；命令行不可读或从别处
  启动、参数是相对路径时会被视为“非本项目”，此时 `-Stop` 只提示不改杀。
- `build` 只覆盖后端 Python 源码与 `start.ps1`；`config.toml`、前端 `dist/`
  变化不会改变指纹。端口被非本项目占用或 health 不可用时只能提示，不能判断版本。
- 索引新鲜度用“最新 md 时间 + 文章数”判断，不做内容哈希；只改内容且不改
  时间戳/数量的情况检测不到。
- 本批未实际重建索引（用户服务仍在运行）；需要用户执行
  `.\start.ps1 -Stop` → `.\start.ps1 -Reindex` → `.\start.ps1` 才能让新索引生效。
- `work/` 与 `temp_newData/` 体积大（后者约 18.9 GB），只在本地保留，不入库。
- 外部导入脚本只允许静态审查，不在本批执行。

---

## 6. 下一步（不在本批实现）

- P1 已完成：命中段落/原因、类型筛选、图谱关联阅读、反馈记录、可复现评测。
- P2 已完成：附件分析入口、隔离落盘、只读结构/解码嗅探、固定样例评测。
- P3 已完成：工作区 JSON 持久化、事实/尝试/收藏/时间线、Markdown/JSON 导出、
  附件分析 React 入口与报告展示、搜索结果收藏、附件报告附到工作区。
- P4 已完成：适用条件三态（已知/未知/不满足）、只读脚本工具架、
  由真实记录生成可追溯 Writeup 草稿。
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

---

## 8. P2 验证结果（2026-10-28）

以下均为本机实测，工作目录 `F:\CTFfiles\knowledgeBase`：

| 命令 | 结果 |
|---|---|
| `.\.venv\Scripts\python.exe -m pytest tests\test_attachment.py tests\test_server_api.py -q` | **55 passed** |
| `.\.venv\Scripts\python.exe -m pytest -o addopts="" -q` | **151 passed in 31.09s**（P1 的 132 + P2 新增 19） |
| `.\.venv\Scripts\python.exe tools\eval_attachments.py` | **5/5 通过（pass_rate=1.0000）** |

P2 评测样例与期望：

| id | 样例 | 关键期望 | 结果 |
|---|---|---|---|
| `png-appended-zip` | PNG + 尾部 base64 + 追加 ZIP | PNG、雕刻出 ZIP、解出 flag、IEND 异常 | PASS |
| `fake-png-zip` | `.png` 实际为 ZIP | 真实类型 ZIP、扩展名不符、列出条目 | PASS |
| `text-base64` | 纯文本 base64 | UTF-8 文本、解出 flag | PASS |
| `wav-tail` | WAV 尾部追加文本 | RIFF、尾部追加异常、WAV 结构 | PASS |
| `script-warning` | `.py` 脚本 | 文本类型、警告“不会运行”、`executed=false` | PASS |

测试覆盖点：

- attachment：PNG/类型/雕刻/解码、SHA256 与结构化 schema、伪装扩展名与 ZIP
  条目、严格 base64、脚本只警告不执行、文件名清洗、隔离目录落盘、
  `analyze_probe` 文本兼容、固定评测集全通过且样例可重复生成、
  未知 builder 拒绝、不联网/不调用模型。
- server：`/api/analyze` 正常上传并保存隔离副本、返回结构化报告；
  路径穿越名字清洗；空附件/超长名字 400；超限 413 且不写盘；
  `health` 暴露附件上限。
- 本批未改 React 源码；前端类型检查/测试/构建沿用 P1 结果，未重新执行。

---

## 9. P3 验证结果（2026-10-28）

以下均为本机实测，工作目录 `F:\CTFfiles\knowledgeBase`：

| 命令 | 结果 |
|---|---|
| `.\.venv\Scripts\python.exe -m pytest -o addopts="" -q` | **179 passed in 36.04s**（P2 的 151 + P3 新增 28） |
| `.\.venv\Scripts\python.exe -m pytest tests\test_workspace.py -o addopts="" -q` | **28 passed in 3.80s** |
| `.\.venv\Scripts\python.exe -m pytest tests\test_attachment.py tests\test_server_api.py -q` | **55 passed**（附件/server 不回退） |
| `.\.venv\Scripts\python.exe tools\eval_attachments.py` | **5/5 通过（pass_rate=1.0000）** |
| `cd tools\agent\webapp; npm run check` | 通过（`tsc -b` 无输出） |
| `npm test` | **4 files / 23 tests passed**（P1 的 14 + P3 新增 9） |
| `npm run build` | 通过；JS 838.63 kB（gzip 258.46 kB），CSS 207.25 kB（gzip 31.31 kB） |

手动冒烟（备用端口 8799，`AGENT_WORKSPACE_DIR=work/p3_smoke`，结束后清理）：

1. 创建 `smoke-p3`（标题 `P3 冒烟：RSA 共模`，方向 crypto）；
2. 加事实 `题目给了同一个 n 和两组密文`；
3. 加尝试 `先试共模攻击 / 能恢复明文 / success`；
4. 收藏 kb 文档 `crypto/rsa-common-modulus-attack.md`；
5. 导出 Markdown，得到：

```markdown
# P3 冒烟：RSA 共模

- 方向：crypto
- 状态：open

## 事实
- [2026-10-28T09:06:41+00:00] 题目给了同一个 n 和两组密文

## 尝试
- [2026-10-28T09:06:41+00:00] `success` 方向：先试共模攻击；结论：能恢复明文

## 资料收藏
- [2026-10-28T09:06:41+00:00] 弱 RSA 共模攻击 — `crypto/rsa-common-modulus-attack.md`：冒烟收藏

## 时间线
- [2026-10-28T09:06:41+00:00] 创建工作区「P3 冒烟：RSA 共模」
- [2026-10-28T09:06:41+00:00] 事实：题目给了同一个 n 和两组密文
- [2026-10-28T09:06:41+00:00] 尝试（success）：先试共模攻击
- [2026-10-28T09:06:41+00:00] 资料收藏：冒烟收藏
```

测试覆盖点：

- workspace 存储：创建/列出/读取/改名/状态/删除、自定义 ID、重复 ID 409、
  非法 ID、空/超长标题、事实/尝试/收藏增删、尝试状态修改、草稿校验、
  时间线自动追加与只读、Markdown 导出模板、附件报告存库/渲染、报告体积上限。
- workspace HTTP：CRUD、列表、时间线、导出下载、409 冲突、400 校验、
  通过 `/api/analyze?workspace=` 把真实分析报告登记进工作区并出现在导出中。
- 前端：附件超限预检不发请求、原始字节上传与报告展示、报告附到工作区、
  无工作区时不提供附着；工作区创建/选择、加事实、加尝试（方向+结论+状态）、
  时间线与导出链接、已附报告展示。
- `work/workspaces/` 与冒烟目录都不入库；构建产物 `dist/` 仍被 gitignore。

---

## 10. P4 验证结果（2026-10-28）

以下均为本机实测，工作目录 `F:\CTFfiles\knowledgeBase`：

| 命令 | 结果 |
|---|---|
| `.\.venv\Scripts\python.exe -m pytest -o addopts="" -q` | **198 passed in 37.89s**（P3 的 179 + P4 新增 19） |
| `.\.venv\Scripts\python.exe -m pytest tests\test_applicability.py tests\test_scripts.py -o addopts="" -q` | **11 passed**（三态规则 + 3 个脚本实跑） |
| `.\.venv\Scripts\python.exe tools\eval_search.py` | 22 条；hybrid **top1/hit/MRR/recall = 1.0000** |
| `.\.venv\Scripts\python.exe tools\eval_attachments.py` | **5/5 通过（pass_rate=1.0000）** |
| `cd tools\agent\webapp; npm run check` | 通过（`tsc -b` 无输出） |
| `npm test` | **4 files / 26 tests passed**（P3 的 23 + P4 新增 3） |
| `npm run build` | 通过；JS 839.79 kB（gzip 258.76 kB），CSS 207.25 kB（gzip 31.31 kB） |

测试覆盖点：

- applicability：`requires` 未知→上下文/点名后已知、关键词支持/否定、版本区间
  内/外/缺失、`evaluate_paths` 汇总、目标路径唯一性；search 返回三态与计数；
  ask 提示含“适用前提检查 / 缺少前提 / unknown”。
- scripts：`rsa_factor_probe`、`zip_inspect`、`filter_probe` 用临时数据实跑；
  校验 `read_only=true`、`executed=false`、不落盘。
- writeup：事实/尝试/资料/Flag/时间线分节；`来源 #id` 与 `entry:` 标记；
  路径锚点 `kb/crypto/rsa.md#...`；kb 存在/未找到校验；非法 mode 400。
- 前端：搜索页三态徽章与提示；工作区 Writeup 导出切换；带章节锚点收藏。

冒烟数据：本批脚本/评测输出只写临时目录，`work/p4_eval_search.json` 等
中间文件已删除；`work/`、`dist/` 继续由 gitignore 排除。

---

## 11. 修复批验证结果（2026-10-28 晚）

以下均为本机实测，工作目录 `F:\CTFfiles\knowledgeBase`：

| 命令 / 操作 | 结果 |
|---|---|
| `.\.venv\Scripts\python.exe -m pytest -o addopts="" -q` | **200 passed in 40.76s**（P4 的 198 + 新增 build 用例 2） |
| `.\.venv\Scripts\python.exe -m pytest tests\test_server_api.py -o addopts="" -q` | **46 passed** |
| `cd tools\agent\webapp; npm run check` / `npm test` / `npm run build` | 全通过；**4 files / 26 tests**；JS 839.79 kB、CSS 207.25 kB（本批未改前端源码） |
| `.\start.ps1 -Status`（现有 8765/11434） | Web pid=41332、Ollama pid=42712；识别到旧后端缺 `build` 并给出 `-Stop`/`-Start` 提示；识别 kb 1568 篇 vs 索引 1567 篇 |
| 备用端口 8799 冒烟 | `logs\web.pid` 写入 42696，与 `:8799` 的 OwningProcess 一致；`/api/health` 返回 `build`；`-Stop -Port 8799` 后 8799 释放、11434 仍在监听 |

测试覆盖点：

- server：health 在模型可达/不可达两条路径都返回 `build`，值等于
  `server.BUILD_ID`；`buildinfo` 对同一源码稳定、对源码变更敏感。
- `start.ps1`：语法解析通过；`-Status` 能读真实端口 pid、比较后端 build、
  比较 kb/索引时间与文章数；备用端口实测 pid 反查与停止逻辑。
- 未引入新依赖；未改检索、模型、端口规则；现有 8765/11434 服务未被停止或重启。

局限：没有 Pester 自动化用例，PowerShell 行为由上述 `-Status` 与备用端口
手工冒烟验证；未在 pwsh 上实测（本机未安装 pwsh），但语法只用 5.1/pwsh 公共子集。
本批未重建索引。

---

## 13. 增量重建（P7，2026-10-28）

索引重建现在走 `tools/kb/reindex.py`：FTS 仍整库重写，向量按分块哈希复用，
内容清单与向量缓存都落盘，失败时不谎报“索引就绪”。

### 13.1 命令

```powershell
# 完整增量更新（FTS + 向量）
.\.venv\Scripts\python.exe tools\cli.py index

# 只刷新 FTS；向量保持旧状态，会醒目警告
.\.venv\Scripts\python.exe tools\cli.py index --fts-only

# 启动脚本的前台重建入口（等同完整增量更新）
.\start.ps1 -Reindex
```

最终行固定为三态之一：`完整增量更新` / `仅 FTS` / `失败回滚`。
成功时报告 `docs/chunks/reused/reencoded/removed_chunks/seconds`，以及
新增/修改/删除篇数；失败时打印失败阶段（扫描 / FTS / 向量 / manifest / 切换）。

### 13.2 落盘位置

| 文件 | 内容 |
|---|---|
| `index/manifest.json` | `version: 1`；`files` 为 `{kb 相对 POSIX 路径: sha256}`，另含 `built_at`、`count` |
| `index/vectors_cache.db` | `chunk_cache(rel_path, chunk_index, sha256, dim, embedding)` + `meta(dim/backend/built_at/count)`，按块复用 |
| `index/fts.db` / `index/vectors.db` | 与旧版相同的正式索引，重建时先写 `.new` 再替换 |
| `index/graph.db` | 本批不动 |

清单收录规则与 `parser.iter_md_paths` 同源（跳过 `_` 前缀文件与
`_templates/.obsidian/.git/node_modules`），`tools/kb/manifest.py` 只调用这一处，
避免 PowerShell 与 Python 各算一套导致篇数漂移。`start.ps1` 的 `Get-IndexInfo`
在 `index/manifest.json` 存在且 `version=1` 时直接读清单计数，缺失时才退回本地扫描。
无 manifest / 无缓存（首次运行或旧索引）自动退化为全量，行为与旧版一致。

### 13.3 失败回滚语义

- 先写临时文件：`fts.db.new`、`vectors.db.new`、`vectors_cache.db.new`、
  `manifest.json.new`。FTS、向量编码、缓存、清单全部成功后才依次 `os.replace`。
- FTS / 编码 / 写库 / 写清单任一阶段失败：删除全部临时文件，保留旧正式库，
  退出码 1，并打印失败阶段；不得打印“索引就绪”。
- 向量模型不可用视为失败（阶段 `vectors`），不再静默跳过；若确实只需要检索，
  用户可显式 `--fts-only`，此时只替换 FTS 与 manifest，向量索引停留在旧时间，
  命令输出 `仅 FTS` 并警告“向量索引停留在旧时间”。
- 切换阶段（`swap`）对 Windows 短暂占用做重试；若重试仍失败会报 `swap`。
  该阶段已开始逐个替换，**不保证自动回退已替换的文件**，需重新运行重建恢复一致。
- `--fts-only` 会更新 manifest，因此 `start.ps1` 的篇数会与最新 kb 一致，
  但 `index/vectors.db` 可能仍是旧内容；这是已知的有意取舍，必须靠输出警告区分。
- 单文件不可读（权限拒绝、被独占打开）会跳过并警告，不阻断重建；有旧清单时
  保留旧 sha，避免被误判为 changed。该文件本次不进入 FTS/向量结果，恢复读取后
  下一次重建会自动补回并重编码其分块。
- 增量统计按 chunk 文本 sha256 复用：未改块计入 `reused`，新增/变化块计入
  `reencoded`，已删除块计入 `removed_chunks`。

### 13.4 验证结果（本机实测）

| 命令 | 结果 |
|---|---|
| `.\.venv\Scripts\python.exe -m pytest -o addopts="" -q` | **220 passed in 36.83s**（P7 的 217 + P8 新增 3） |
| `.\.venv\Scripts\python.exe tools\eval_search.py` | **22/22**，top1=hit@5=MRR=recall@5=1.0000 |

新增 `tests/test_manifest.py`（6 个）与 `tests/test_reindex.py`（4 个），共 10 个测试：
覆盖 scan/diff 增改删与收录过滤、manifest 读写与坏版本退化、全量后改/加/删一篇的
增量复用、`--fts-only` 保留旧向量、编码失败回滚旧索引、模型不可用报失败而非就绪。
P8 在 `tests/test_reindex.py` 再新增 3 个：scan 保留旧 sha 并记录 skipped、CLI 结果行
含“跳过 N 个不可读文件”、icacls deny 后重建仍成功且恢复后重新入索引。

局限：FTS 仍是整库重建（只是写临时文件），没有做 FTS 块级增量；切换阶段的部分
替换失败不会自动回滚；`-Status` 的“过期”判断仍用 mtime + 篇数，不逐文件比
manifest 哈希，因此只改内容且不动时间戳的变更仍可能不提示；不可读文件在跳过那次
会被移出 FTS/向量，恢复后需要重新编码其分块（manifest 因保留旧 sha 不会报 changed）。

---

## 12. 启动诊断分层（P6，2026-10-28）

`start.ps1` 是唯一启动入口，`.\start.ps1` 与 `.\start.ps1 -Start` 等价。
`-Status` 与启动后的健康提示都按三层独立输出，任意一层失败不阻断其他层：

- **[Web]** 端口 `:8765` 是否监听、真实监听 pid、`/api/health` 的 `build`
  是否等于当前代码指纹；旧后端缺 `build` 或 build 不一致时提示
  `-Stop` 后重启。`config` 不一致只提示“配置或前端产物已变，建议重启”，
  与 build 分开判断。
- **[索引]** `Get-IndexInfo` 统计 `kb/` 下 Markdown 篇数（跳过 `_` 前缀文件与
  `_templates/.obsidian/.git/node_modules`），对比 FTS `docs` 数，并比较
  `index/fts.db` 的修改时间与 kb 最新修改时间。
- **[模型]** GET `http://127.0.0.1:11434/api/tags`：可达且有模型→OK；
  11434 未监听→“Ollama 未启动，Web 检索仍可用但问模型不可用”；
  已监听但无模型→列出 `config.toml` 中 `[ollama].model` 期望模型名并指向
  `tools\setup_ollama.ps1`。

`buildinfo.py` 的 `build` 指纹仍只覆盖 `tools/agent`、`tools/kb` 的 `.py`
与 `start.ps1`。新增 `config_id()`：对 `config.toml` 内容 +
`tools/agent/webapp/dist/index.html` 的 mtime/size 做 sha256，
`/api/health` 新增 `config` 字段（不可读时为 `"unknown"`）。
`python tools\agent\buildinfo.py --config` 输出该指纹，供 `start.ps1` 比较。

启动失败（Start-Process 异常或端口等待超时）时，Ollama/Web 分别打印
`logs\ollama.log`、`logs\web.log`（含对应 `.err.log`）的最后 15 行，
并提示换端口（`-Port` / `-OllamaPort`）、查看完整日志、检查杀毒/防火墙；
日志不存在会明说。

**P6 验证（2026-10-28）**：

| 命令 / 操作 | 结果 |
|---|---|
| `.\.venv\Scripts\python.exe -m pytest -o addopts="" -q` | **207 passed in 38.04s**（本批新增 `config_id` 用例 1 个 + server health 的 `config` 断言） |
| `.\.venv\Scripts\python.exe -m pytest tests\test_server_api.py -o addopts="" -q` | **47 passed**（含 `config` 字段断言） |
| `.\start.ps1 -Status`（现有 8765/11434） | 三层均输出；Web 识别旧后端 build=`e423dad-950fc14e` vs 当前 `c918d2d-dc7b7408`，并提示旧后端无 `config`；索引 kb 1567 篇 = FTS 1567 篇；Ollama 列出 7 个模型 |
| 备用端口 8799 冒烟 | 临时启动 `server.py`（AGENT_PORT=8799），`Get-NetTCPConnection` pid=8632 与 `-Status -Port 8799` 一致；health `build=c918d2d-dc7b7408`、`config=0303b36e...8c8a`，三层全部 OK；仅结束该临时 pid，8765/11434 未动 |
| `start.ps1` 文件头 | 字节 `239,187,191`（UTF-8 BOM）；`Parser::ParseFile` 语法通过 |

局限：没有 Pester 用例；启动失败日志分支未真实制造超时，只做了代码路径与
语法检查。未停止或重启现有 8765/11434 服务，未重建索引。

---

## 13.5 P8 验证结果：单文件不可读降级（2026-10-28）

**结论**：单文件不可读会跳过并警告，不阻断重建。

| 命令 / 操作 | 结果 |
|---|---|
| `.\.venv\Scripts\python.exe -m pytest -o addopts="" -q` | **220 passed in 36.83s**（P7 的 217 + 新增 3） |
| `.\.venv\Scripts\python.exe tools\eval_search.py` | **22/22**，hybrid top1=hit@5=MRR=recall@5=1.0000 |
| `tools\cli.py index`（真实库，无改动） | `完整增量更新 docs=1567, chunks=14139, reused=14139, reencoded=0, removed_chunks=0, 7.32s`，无“跳过” |
| 真实库单文件不可读冒烟 | 跳过 1 个不可读文件后重建成功：`docs=1566, chunks=14007, reused=14007, reencoded=0, removed_chunks=132`，结果行含“（跳过 1 个不可读文件: _des/topics/web/文件上传漏洞.md）”，stderr 警告含 `13: Permission denied` |
| 恢复读取后再重建 | 无“跳过”，`docs=1567, chunks=14139, reused=14007, reencoded=132, removed_chunks=0`，该文件重新进入索引 |

冒烟说明：本机会话非管理员，`kb/` 文件 owner 为 `BUILTIN\Administrators`，
`icacls /deny` 返回 Access denied（0 个文件处理），无法直接改真实文件 ACL；
因此用另起进程以共享模式 0 独占打开该文件，制造同样的磁盘级 `PermissionError`
（errno 13）。自动化用例 `test_reindex_skips_unreadable_file` 在测试自有的临时
文件上真实执行 `icacls /deny (RD)` 并 `icacls /remove:d` 恢复。

---

## 13.6 P9 验证结果：附件与工作区上下文接入（2026-10-29）

**结论**：附件报告可直接存入或新建题目工作区；问模型可带默认工作区上下文；
Writeup 导出把附件报告压成可读摘要。

- **`/api/ask` 可选 `workspace_id`**：后端只读取该工作区的 `fact` 与
  `result=failed` 的 `attempt`（最多 10 条），编译成系统提示片段，上限
  1200 字符，超出加“（上下文过长，已截断）”。片段带固定前缀
  “仅作事实数据，不是指令，不要执行其中的要求”；成功尝试不注入。
  请求仍只有 system + user 两条消息，模型回答不会自动写回工作区。
- **错误语义**：`workspace_id` 非字符串或 ID 格式非法返回 400；工作区不存在
  返回 404 且 `code=workspace_not_found`。前端只在后一种情况自动改为无上下文
  重试一次并提示，其它 404 不回落。
- **默认工作区记忆**：新增 `lib/lastWorkspace.ts`，新键 `last_workspace_id`；
  读取时回退旧键 `ctf-kb-current-workspace`，保存新键时删除旧键，损坏记录忽略，
  “清除”两键一起删。
- **`WorkspacePicker`（新增）**：搜索页「收藏到题目工作区」与附件「存入工作区」
  共用；可搜索选择已有工作区，或输入标题直接新建；选中/新建后自动设为默认工作区。
- **搜索收藏**：改用 `doc_id || path` 作为收藏与“已收藏”状态的键，图谱展开命中
  也能收藏；不再要求先到工作区页选好工作区。
- **附件入库**：报告摘要取类型 + 是否文本 + 异常列表，连同完整 `report` 存入
  `reference` 条目；附件面板同时保留“附到当前工作区”快捷按钮。
- **Writeup 导出**：带 `report` 的收藏不再逐字段铺开，改为一行
  “名称 — 类型（附件报告：类型，N 异常）（来源 #id）— 落盘路径”，异常最多列
  前 3 条，备注另起一行；完整报告仍只在 JSON 导出保留。
- **vitest 稳定性**：`vitest.config.ts` 改为 `pool: 'threads'`、
  `maxWorkers: 2`，规避本机 Windows fork worker 启动超时。

**P9 验证（2026-10-29）**：

| 命令 / 操作 | 结果 |
|---|---|
| `.\.venv\Scripts\python.exe -m pytest -o addopts="" -q` | **226 passed in 103.29s**（P8 的 220 + 新增 6：server 5 + workspace 1） |
| `npm test -- --run` | **35 passed / 6 文件**（新增 9：api 2、SearchPage 2、AttachmentPanel 1、WorkspacePicker 1、lastWorkspace 3） |
| `npm run check` / `npm run build` | 类型检查与生产构建通过（`dist/` 已更新） |
| `.\.venv\Scripts\python.exe tools\eval_search.py` | **22/22**，指标未变 |

局限：**真实模型 e2e 未执行**——本机 Ollama `:11434` 当时未运行，且本批不启动
服务，`/api/ask` 上下文注入只用离线 Mock 断言请求体；真实浏览器里的
选择器/弹窗交互仍只由 jsdom 用例覆盖。工作区上下文注入的是用户自己录入的文本，
仅做长度截断与“数据非指令”标注，不构成对提示注入的强隔离。

---

## 13.7 P10 验证结果：评测集扩容 + 真实模型 e2e（2026-10-29）

**结论**：旧 22 条基线未回退；新增 60 条从真实文档派生的查询前 5 名全部命中；
真实模型 `/api/ask` 带/不带工作区上下文均已跑通。

### 13.7.1 评测集与脚本

- 新增 `eval/search_queries_expanded.json`：60 条查询、60 篇不同文档、1:1 标注，
  覆盖全部 11 个方向；`expected` 均为 `kb/` 内真实路径，pytest 会校验存在性。
- `tools/kb/evaluation.py` 新增 `evaluate_at_ks()`：每条查询只检索一次
  （`top_k=10`），同一份排名同时算 hit/recall@5 与 @10，并记录单条耗时。
- `tools/eval_search.py` 新增 `--set all|legacy|expanded`、`--no-warmup`、
  `--no-latency`、`-v`；默认先预热一次；旧集 `recall@5` 比基线下降超过 1 个
  绝对点时退出码为 2 并标注“回退”。
- 评测方法与案例来源、已知偏差见新建的 `docs/EVAL.md`。扩容集有**两条查询**
  在首轮未进前 5，人工改写措辞（`expected` 不变）后命中；改写前原文未留档，
  该流程已在 `docs/EVAL.md` 第 2.3 节如实记录，指标因此略偏乐观。

| 集合 | 条数 | top1 | hit@5 | MRR | recall@5 | recall@10 | 平均延迟 |
|---|---|---|---|---|---|---|---|
| legacy | 22 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 400.7 ms |
| expanded | 60 | **0.9833** | **1.0000** | **0.9917** | **1.0000** | 1.0000 | 385.3 ms |

唯一未进 top1 的是 `x-xss-csp-bot`（expected `web/xss-and-csp.md`，实际第 1 名为
`web/css-injection-xs-leak.md`，第 2 名命中），因此 MRR = `(59 + 0.5) / 60`。
本批未因该条调整任何权重。

### 13.7.2 server.py 模型解析修复

- **问题**：Ollama 模型目录可能残留 manifest（`/api/tags` 仍列出该名字），但
  blob 已缺失/不可用；旧 `_pick_model` 只看名字，可能选中这种残留项，
  随后 `/api/chat` 返回 **404**。
- **修复**：`_resolve_model()` 先按归一化名称打分（精确 > 忽略 `._-` 后相等 >
  前缀 > 包含）；只有一个最高分候选时保持旧行为、不额外发请求；多个候选同分时
  用 `/api/show` 逐个探活，返回第一个 200 的模型。全部探活失败时返回首选名并
  标记不可用。
- **health 语义**：`model_ok` 改为 `_resolve_model()` 的探活结果，`ok` 跟随
  `model_ok`；不可用时附带
  “Ollama 有模型标签，但没有可用的模型（/api/show 探测失败）”。`index_ok`
  独立，不再用“有模型标签”冒充模型可用。
- `/api/ask` 仍通过 `_ask_model() → _pick_model()` 取同一个解析结果，避免
  health 说可用、实际 chat 却打到坏 manifest。

### 13.7.3 真实模型 e2e

- 新增 `tools/e2e_ask.py`：标准库实现，建临时工作区 → 注入 2 条 fact + 1 条
  failed attempt → 带 `workspace_id` 调 `/api/ask` → 再不带上下文调一次；
  断言 SSE 终态 `done`、有 tok、无 err；结果可 `--out` 落盘。
- 既有 SSE 契约固定为 `tok/err/done`，没有 `start` 事件；脚本把“首个非 tok 为
  start”如实标 **SKIP** 并说明原因，`done` 仍按硬要求断言。
- 实测结果（`work/e2e_ask_result.json`，服务 `:8765` pid 27888，未停止）：
  **STATUS: PASS**。带工作区：566 个事件、135.2 s、`579 tok · 4.3 tok/s`；
  无上下文：756 个事件、131.6 s、`769 tok · 5.9 tok/s`。两次均无 err，
  临时工作区已清理。

### 13.7.4 回归

| 命令 | 结果 |
|---|---|
| `.\.venv\Scripts\python.exe -m pytest -o addopts="" -q` | **229 passed in 53.64s**（P9 的 226 + 新增 3：扩容集加载/存在性、`evaluate_at_ks` 多截断点与延迟） |
| `cd tools\agent\webapp; npm run check` | 通过（`tsc -b` 无输出） |
| `npm test -- --run` | **6 files / 35 tests passed** |
| `npm run build` | 通过；JS 849.49 kB（gzip 261.02 kB），CSS 207.25 kB（gzip 31.31 kB） |
| `.\.venv\Scripts\python.exe tools\eval_search.py` | legacy 22 条全 1.0000；expanded 60 条见上表 |

局限：expanded 集仍有词汇泄漏与两条人工改写带来的偏乐观；平均延迟随本机负载
波动；`tools/e2e_ask.py` 不是 pytest 用例，真实模型结果依赖本机 Ollama 状态；
未做图谱/类型筛选的消融实验。

---

## 14. 导入批 import0：授权中文赛事 WP 正文（2026-10-31）

### 14.1 来源与范围

- 来源：`F:\ctf\CTF知识库\80_知识工作台\data\evidence.sqlite3`，**只读**
  （`sqlite3.connect("file:<路径>?mode=ro", uri=True)`），全程未写 `F:\ctf`。
- 只导 `kind='source_prose'`（574 个 source / 5113 段）。**`user_prose` 整批不导**：
  其 metadata 没有 `license`/`verification_status` 字段（13058 段全缺），只用
  `review_status` 表达审核状态；内容与本地书 PDF、语言官方文档、`CTF大赛WP集合`
  快照高度重合（同一份存量资料，重复收录对检索是噪声），许可无法逐篇追溯。
- `source_code`（21626 段）与 `technique_guide`（26 段）本批不导。

### 14.2 脚本与落盘

- 脚本 `tools/import_cat_prose.py`（标准库 + 既有依赖；无新增 pip 依赖）。
  `--dry-run/--limit N/--full/--resume`，每 100 篇落 `work/import_cats/progress.json`。
- 输出 `kb/_imported_cats/<category>/<title>__<source_id>.md`，**277 篇**
  （misc 84 / crypto 61 / reverse 48 / web 46 / pwn 38），正文合计 672,341 字。
- manifest：`work/import_cats/manifest.json`（277 条，含 content_sha256/source_url/
  body_sha256/passages/chars）；报告 `work/import_cats/import_report.json`。
- 段落重叠剪枝：同一 source 的相邻段是带重叠的抽取窗口，拼接前剪掉重叠，
  共剪 155,122 字（首段全保留，正文无丢失）。
- 许可保留：`license/attribution/source_url/event/year/content_sha256` 既进
  front-matter 的 `origin_*` 字段，也**原样**写进 `origin_meta`（整份 JSON 全部键），
  还在正文顶部"来源/许可/署名/核验状态/正文 sha256/收录说明"元信息块里重复一遍。

### 14.3 去重（269 个 source 跳过 / 31 个 source 并入首篇）

| 判据 | 数量 | 说明 |
|---|---|---|
| 同 source_url（既有 kb 已收录） | 244 | 既有 `_imported/` 已按方向拆篇收过同一 WP |
| 同标题（既有 kb） | 14 | 既有条目同名 |
| 正文 sha256 相同 | 11 | 本批已保留篇目正文完全一致 |
| 同 source_url（本批）→ 并入首篇 | 31 | 抽取器把一篇 WP 按方向拆成多个 source_id |

- 修正的坑：源库 `content_sha256` 实为**每段**哈希，NewStar/Hello-CTF 的首页段
  只有 `---\ncomments: true\n---` 之类的样板，最大的一组有 88 篇不同 source 共享
  同一哈希。按它做文档级去重会误杀 300+ 篇，故改为「正文两两比对相同才判重」。

### 14.4 重建与指标（实测）

| 项 | 导入前 | 导入后 |
|---|---|---|
| FTS doc / chunk | 1567 / 14139 | **1844 / 15564** |
| graph 节点 | 1567 | 1844 |
| legacy 22 条 top1 / MRR / recall@5 | 0.9091 / 0.9545 / 1.0 | **1.0000 / 1.0000 / 1.0000** |
| expanded 60 条 top1 / MRR / recall@5 | 0.9833 / 0.9917 / 1.0 | **0.9833 / 0.9889 / 1.0000** |

- reindex：`python tools\cli.py index` → `docs=1844, chunks=15564, reused=14139,
  reencoded=1425, removed_chunks=0, 96.75s`。注意**必须用 `.venv` 的 Python**
  （系统 python 没有 onnxruntime/llama_cpp，走向量阶段会失败回滚）。
- 回退如实记录：expanded `MRR 0.9917 → 0.9889`（-0.0028），仅 `x-xss-csp-bot`
  一条从 rank1 掉到 rank3（新增 `NewStar CTF 2025 / 小 E 的留言板` 插到第 2），
  top1/recall@5/hit@10 均未变；legacy 22 条稳在 1.0，`regressions: []`。
  平均延迟由 108/120 ms 升到 348/457 ms（语料增 ~18%、候选池更大）。
- pytest：`.\.venv\Scripts\python.exe -m pytest` → **229 passed in 67.64s**（零改动基线）。

### 14.5 已知限制

- 全新导入篇目没有手写 `relates_to/requires` 关系，图谱只有 26 条边不变，
  `kb/_index.md` 未改（不发明新簿）。
- 中文文件名较长（标题__source_id），Windows 路径长度需注意。
- 检索质量实测只有固定集（82 条），新增 277 篇是否覆盖真实提问面未验证。

## 15. P11 验证结果：浏览器 e2e + 备份恢复（2026-11-01）

### 15.1 交付

- `tools/e2e_browser.py`：Playwright 真实浏览器五步验收（Edge channel，
  不下载内核；`--skip-model` 分支；截图 + JSON 结果；自清理工作区）。
- `backup.ps1`：staging 拷贝 + Compress-Archive，保留 3 份；
  源补 `kb\_imported_cats`；重存 UTF-8 BOM。
- `start.ps1 -Status` 新增只读「索引 manifest + 最近备份」展示段。
- `.gitignore` + `backup/`。

### 15.2 实测

- 浏览器 e2e：**5 PASS / 0 SKIP / 0 FAIL**，含真实模型问答
  （673 字符回答，832 tok @ 35 tok/s；截图 `work/shots/06_ask_answer.png`
  显示附件 ZIP 徽章/异常警示/目录树与模型"判断依据→解题步骤→可运行脚本"）。
- 备份 `ctf_kb_20261101_112314.zip` 94.05 MB（266 + 277 导入 md + index 7 文件
  + workspaces 空目录如实打包）；`work\feedback` 不存在被优雅跳过。
- 恢复演练：临时目录解压后三层文件数与在线全等；**直接用恢复出的 fts.db
  检索成功**（docs=1844/chunks=15564，"RSA 共模攻击"返回正确命中）——
  恢复可用的证据，不只是文件齐全。

### 15.3 新增坑与规则

1. **mtime ≠ 内容**：索引过期警告以 mtime 为启发式；导入批文件被触碰
   （内容不变）即可误报。判定一律以 `index\manifest.json` 哈希比对为准，
   复跑 `cli.py index` 增量（reused=15564, reencoded=0）即自动消警。
2. **PowerShell 脚本必须 UTF-8 BOM**（又一次由 backup.ps1 验证；
   `powershell -File` 在 Windows PowerShell 5.1 下无 BOM 时按 GBK 解析）。
3. 当前工作区存储 `work\workspaces` 为空（历史工作区未随项目迁移，
   e2e 工作区自清理），备份如实打包空目录；`work\feedback` 同理。

### 15.4 未做 / 后续

- e2e 未纳入 pytest（依赖真实 Edge 与运行中的服务，保持一次性脚本定位）。
- 新 277 篇导入的真实查询面覆盖仍未验证（P1 盲测待用户拍板）。
- 464 方法卡试点同样待用户拍板。

## 16. P12 / DB-Q1：知识库只读质量审计（2026-11-01）

### 16.1 交付

- `tools/audit_corpus.py`：只读审计 CLI（`--out-dir`、`--min-jaccard`、
  `--min-containment`、`--max-pairs`、`--sample-size`、`--seed`、`--hash-before`、
  `compare-hash` 子命令）。文档集合调 `kb.parser.iter_md_paths`，与索引同源。
- `tests/test_audit_corpus.py`：23 个合成语料测试。
- `docs/DB_QUALITY.md`：运行方法 / 实测 / 疑似分布 / 抽样 / 误报边界 / Q2–Q4 计划。
- `work/db_quality1/{inventory.jsonl, duplicate_candidates.json, import_check.json,
  sample_plan.json, eval_protocol.json, run_meta.json, report.md, sample_review.md,
  hash_before.json, hash_after.json}`（gitignore，不入库）。

### 16.2 实测（已验证事实）

| 项 | 值 |
|---|---|
| 覆盖篇数 | **1844**（`kb/**/*.md` 1845 − 被 `_` 前缀排除的 `kb/_index.md`） |
| 耗时 | 20.1 s（盘点 3.7 s / 去重 10.4 s） |
| 解析/读取异常 | 21（全部 front-matter YAML 语法错误，0 解码失败） |
| 精确正文副本 / 近似候选 | **0 组** / **230 对（30 簇，0.7500–0.9997）** |
| 同 URL 线索组 | 3 |
| 有合法围栏 / 无合法围栏 | 1299 / 545（`_imported_cats` 275、`_imported` 264、`_des` 6） |
| 本地缺图 | 8 篇 / 47 个引用（**全部**不存在，全在 `_des/`） |
| 缺 `license` 字段 / `verification` unknown | 1322 / 1567 |
| 只读自证 | `kb/` 1845 文件前后哈希逐条一致，`compare-hash` 退出码 0；`index/` 7 文件哈希不变 |

三个结构性结论：
1. **21 篇 YAML 缺陷是旧批遗留**：全部在 `_imported/`，全是 `signals: [[Misc] …]`、
   `[RSA? cmd5!]` 这类未加引号的 flow 序列；实测这 21 篇 `source` 全空，
   同批其余 245 篇无一为空。
2. **导入批是无代码的散文正文**：`_imported_cats` 277 篇中仅 2 篇有合法围栏，
   正文第 3 行固定声明"阶段 1，仅散文，代码段未导入"。检索命中该批不能指望可运行 exp。
3. **近似候选 230 对里 202 对是 `_imported_cats` 内部**：导入器把同一赛事页多篇
   writeup 合进一个文件并追加 `## 【来源分段】`，段落互相包含 → `a_subset_of_b` 大量命中，
   **大概率不是重复**。真正待裁的是 **25 对 `_imported` ↔ `_imported_cats` 同题双份**；
   `_des`/`_imported` 内部各只有 1 对。

### 16.3 人工抽样（`_imported_cats`，18 层，种子 20261101，24 篇逐篇读完）

内容可用 6、参考/摘要类 3、空壳导读 7、**标题与正文题目不一致 10**、
类别与导向矛盾 3、一文件合多方向 2、博客页眉噪声 2、表格折断 1、重复行 4、
`origin_license: not_declared` 已收录 2。证据（行号 + 短引文）在
`work/db_quality1/sample_review.md`。

### 16.4 新增坑与规则

1. **别自造文档枚举规则**：`tools/kbcheck.py` 的 rglob+跳过 `_` 目录与索引
   `iter_md_paths` 不同源；审计必须直接调索引侧函数。
2. **围栏要先剥 `> ` 引用前缀**（最多 3 层），否则引用块围栏被误判成"整篇无围栏"；
   整行 4 空格缩进的 ``` 属缩进代码块，不计入散落标记；只有奇数个 ``` 才是散落。
3. **front-matter 解析失败 ≠ 缺少**：必须区分缺失 / 未闭合 / YAML 语法错误 /
   非键值映射，并回显原始报错行。
4. **去重候选不能按分数截断**：按"共享 shingle 排名取前 N 对"会漏掉 0.9997 的
   `ctfshow-php特性.md` ↔ `ctfshow-命令执行wp.md`。改用逐对可证明下界
   （jaccard≥t ⇒ shared ≥ t/(1+t)·max(|A|,|B|)；containment≥c ⇒ shared ≥ c·min(|A|,|B|)，
   取较小者），阈值以上的对全部评分；`--max-pairs` 只作内存保险并在报告里告警。
5. **包含度对短文档不可信**：短边 <50 shingle 只认 jaccard（实测最小 shingle 集 144，
   该保护不排除任何真实文档）。
6. **同模板 ≠ 重复**：共用赛事模板、解法不同可到 jaccard 0.667，默认阈值取 0.7 而非 0.6。
7. **argparse 主参数必须在子命令前**：`--project-root/--kb-dir/--out-dir` 写在
   `compare-hash` 之后会 `unrecognized arguments` 并退出 2。
8. **导入批 `body_sha256` 必然"不一致"**：清单记的是段落正文，落盘文件含 front-matter
   与来源分段标题；不能用它判断事后编辑。
9. **pytest 在 GBK 控制台读源码**：注释含非 GBK 字符会被替换成 U+FFFD 触发
   SyntaxError；`latin-1` 无法编码中文，合成"不可解码文件"需先转义再 encode。

### 16.5 未做 / 后续

- **未跑检索评测**，不声称任何指标提升；`eval_protocol.json` 仅是协议草案。
- 未修改任何 `kb/` 正文、未改 `index/`、未启停服务、未联网核验源站与远端图片。
- 未做语义/向量去重，只做字符 shingle。
- Q2：25 对同题双份逐对裁决、修 21 篇 `signals` 引号、补/标记 47 个缺图、
  给题名错配等打结构化标签（改正文须 Q2 单独授权）。
- Q3：先建冻结查询集与标注规则，再在**不改语料**前提下比较切块/排序策略。
- Q4：`index/` 备份改走 SQLite 在线备份 API / `VACUUM INTO` 并验证可打开与行数一致。

## 17. DB-Q2：语料元数据最小修复与重复复核（2026-11-02）

### 17.1 交付（已验证事实）

- `tools/repair_signals.py`：按显式清单修复 21 篇 `signals` YAML 引号；
  写入前校验原文件 SHA256，支持 `--dry-run`，重复运行 `already_repaired`。
- `tools/kb/signals_repair_manifest.json`：21 条，含原/新文件 SHA256、
  正文 SHA256、`signals` 原行/新行/期望解析值。
- `tests/test_repair_signals.py`：5 个回归测试（清单覆盖、当前解析、仅一行变化、
  dry-run/幂等、哈希不符拒绝）。
- 工作产物（gitignore）：`work/db_quality2/` 下基线哈希、`progress.json`、
  `audit/`、`duplicate_review.md`、`sample_review_corrections.md`、
  `repair_evidence.json`、`eval_search.json`、重建/测试日志。

### 17.2 21 篇修复（已验证事实）

- 修复前：21 篇 front-matter YAML 解析失败（`signals` 未加引号的 flow 序列）；
  第二次运行全部 `already_repaired`，无写入。
- 修复只改 `signals` 一行：kb 1845 文件中仅 21 个哈希变化，`added=0/removed=0`，
  正文 SHA256 全部与清单记录一致；修复前 `index/` 7 个文件哈希不变。
- 修复后 parser 能读到 `source` 与 `signals`；审计 YAML 异常 **21→0**、
  缺 `source` **21→0**、缺 `license` **1322→1301**。
- **Q1 更正**：这 21 篇不是“原文缺 `source`”，而是解析失败导致整块元数据被丢弃；
  修复后同 URL 线索组由 3 增至 24，原因是 21 篇 `source` 首次可读。

### 17.3 25 对跨批候选（已验证事实 + 人工判断）

- 逐对读全文，剥离标题/引用元信息后正规化正文比较：**4 对可合并建议**
  （#4 `不经意的逆转`、#5 `神秘计算器`、#7 `随机数生成器`、#12 `大整数类`），
  正文逐字相等且新篇保留来源信息；**21 对互补/保留**；**0 疑似**。
- 互补原因：旧篇多含 `〔原图省略〕` 且正文更干净，新篇带 source/origin/license/
  附件元信息并常含导入器重复句；`_imported/misc/misc.md` 与
  `_imported/crypto/crypto.md` 是同一 CISCN 博客的方向分段，新篇把两段合并，
  属互补而非纯副本。
- **本批未删除、未移动、未合并任何文档**；4 对只是报告建议。
- 证据：`work/db_quality2/duplicate_review.md`（25 行分数/包含度/差异片段/结论）。

### 17.4 抽样复核更正（已验证事实 + 人工判断）

- Q1 的“题名错配 10 篇”是误判：10 篇标题都等于**第一个来源分段**的题目，
  后面还有 1–4 个不同题目的 `## 【来源分段】`，属“一文件合并多题”。
- Q1 的“分类矛盾 3 篇”同源：主分类对应首段，后续分段来自其他方向。
- “空壳导读 7 篇”是明写“仅短导读”的资料类型，不是导入失败。
- 本地缺图按 Q1/Q2 inventory 为 **8 篇 / 43 个去重 target**（Q1 文档写 47，
  未能复现）；全部在 `_des/`，本批不下载、不虚构恢复。
- `origin_license: not_declared` 只记录为未核验，不推断侵权，也不宣称全库授权。
- 证据：`work/db_quality2/sample_review_corrections.md`。

### 17.5 索引、评测、测试（已验证事实）

| 命令 | 结果 |
|---|---|
| `tools\cli.py index` | `docs=1844, chunks=15564, reused=15396, reencoded=168, removed_chunks=0, 29.01s`；修改 21 篇 |
| `tools\cli.py graph --build` | 1844 节点 / 26 边 / 8 跨方向（与导入后基线一致） |
| `tools\eval_search.py --set all` | legacy 22 全 1.0000；expanded top1=0.9833、MRR=0.9889、recall@5=1.0000 |
| `pytest -o addopts="" -q` | **257 passed in 73.27s**（252 + 5） |
| 前端 `npm run check` / `npm test -- --run` / `npm run build` | 均通过；6 文件 / 35 用例；JS 849.49 kB（gzip 261.02 kB） |

- expanded 唯一非 top1 仍为 `x-xss-csp-bot`（第 3 名，expected `web/xss-and-csp.md`），
  与导入后基线一致；未改查询措辞、未改排序。
- 本批提交信息：`feat: repair verified corpus metadata and document duplicate review`。

### 17.6 未做 / 待决定

- 4 对“可合并”不执行；移除旧篇需后续单独授权。
- 不拆分 10 篇多题合并文件，不新增 parser 不支持的多题标签。
- 博客页眉噪声、折断表格、导入批重复句、43 个缺图未修。
- 未做语义去重；未开始 Q3，未改 Q3 协议。

## 18. DB-Q3 Part B：方法论卡片试点（2026-11-02）

### 18.1 结论先行（已验证事实）

- `kb/_methods/` 现有 **13 个 md 卡片** + **11 个 `--selftest` 脚本** + `scripts/` 子目录。
- 全量回归：`pytest -q -o addopts=` → **279 passed in 70.94s**（266 基线 + 13 新增）。
- `work/q3/method_backlog.json`：**53 个主题**，`done=12`，出处路径 0 缺失。

### 18.2 关键事实与坑（写在这里避免下次踩）

- `tools/kb/parser.py:135-147`：`SKIP_DIRS = {"_templates", ".obsidian", ".git", "node_modules"}`，
  且 `if p.name.startswith("_"): continue` —— **只跳过以 `_` 开头的文件**，
  `kb/_methods/*.md` 只要文件名不带 `_` 前缀就会被收录；`_methods` 目录本身不在 SKIP_DIRS 里。
- `category` 必须在 `['ai','blockchain','crypto','forensics','hardware','misc','mobile','osint','pwn','reverse','web']` 内，
  否则解析器会给"未知 category"警告。
- **手工拼 zip 头不可靠**：本机环境下 `struct` 的长格式串（含 `4B/4H`）经工具通道易被改写，
  且 CPython 3.14 `zipfile` 无法回读手工构造的 ZipCrypto 流（12 字节加密头落盘是明文）。
  结论：**不要用"造加密 zip 再回读"验证字典攻击**；`zip_password_attack.py` 的自检因此跳过了该项。
- `sympy.factorint` 对 192 位半素数会跑几十分钟，**不要**用它验证大模数；Wiener 卡改用
  `wiener()` 自身还原的 `p*q == n` 作验证。
- PowerShell 把 UTF-8 中文显示成 GBK 乱码，判断文件内容一律用 read 工具；写文件只用 write/edit。

### 18.3 卡片清单（13 个）

`rsa_common_modulus_attack.md`、`rsa_shared_prime_attack.md`、`rsa_hastad_broadcast.md`、
`rsa_wiener_continued_fraction.md`、`lcg_parameter_recovery.md`、`mt19937_untemper.md`、
`vigenere_autocrack.md`、`hash_length_extension.md`、`enc_chain_decode.md`、`decompress_chain.md`、
`zip_password_attack.md`、`onchain_base64_decode.md`、`ejs_prototype_pollution_rce.md`。

### 18.4 脚本自检矩阵（本机实测）

| 脚本 | 自检 | 备注 |
|---|---|---|
| `lcg_parameter_recovery.py` | 5/5 | 模数还原/预测/c=0/输出不足/xorshift |
| `mt19937_untemper.py` | 5/5 | 624 字克隆、错位采样拒绝 |
| `vigenere_autocrack.py` | 5/5 | IoC 峰值可能落在 2k，卡片已注明 |
| `rsa_common_modulus.py` | 4/4 | — |
| `rsa_hastad_broadcast.py` | 5/5 | 需 `prod(n) > m^e` |
| `rsa_shared_prime.py` | 5/5 | — |
| `rsa_wiener_continued_fraction.py` | 4/4 | 需 `d < n^0.25/3` |
| `hash_length_extension.py` | 6/6 | `forge()` 的 `orig_sig` 要传 bytes |
| `enc_chain_decode.py` | 9/9 | 只认纯 hex，需先去掉 `0x` 与补零 |
| `decompress_chain.py` | 8/8 | zip 取首成员 |
| `zip_password_attack.py` | 6/6 | 字典命中项因环境限制跳过 |

### 18.5 未做 / 待决定

- 53 个 backlog 主题只完成 12，其余（Coppersmith、ECDSA 格、SSTI、PHP filter chain、pickle、栈溢出等）留待后续批次。
- 新增卡片尚未重建索引；是否把 `_methods` 纳入评测查询集待定。
- 不合并、不删除任何既有 kb 文档。

