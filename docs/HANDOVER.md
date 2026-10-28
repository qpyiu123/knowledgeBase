# 交接文档：项目当前状态

**写给**：下一个接手的人（GPT6.1Sol）
**日期**：2026-10-27
**项目**：`F:\CTFfiles\knowledgeBase`
**一句话**：一个本机离线的 CTF 知识库，覆盖 11 个赛道 1567 篇，
支持中文模糊检索 + 本地小模型问答，带 React 前端。

> 本文只写**当前事实**与**已确认的问题**。推理过程中的猜测都标了「待验证」。

---

## 〇、2026-10-28 P0 更新（本批）

- 已建立 Git，基线提交 `b9ebe89`；**不再处于“无版本控制”状态**。
- `setImmediate` 已移除；起点卡片与结果卡片改为**显式传参**，不再读旧闭包。
- TS 已拆成 `tsconfig.app.json`（浏览器，无 Node 类型）与
  `tsconfig.node.json`（Vite/Vitest 配置）。
- SSE 契约统一为 `tok` / `err` / `done`；前端识别错误与完成信息。
- `/api/ask` 已串行限流：忙碌返回 429，不再并发挤爆显存。
  “停止接收”只关闭本地连接，不谎称后端已停止运算。
- server 的模型/host/context 改为读 `config.toml`，环境变量仅显式覆盖；
  实际模型名会按 `/api/tags` 解析（如 `qwen2.5-coder-7b` → `:local`）。
- `/api/ask`、`/api/doc` 限定 `kb/` 内 Markdown，并限制输入/文档/上下文体积。
- `health` 已拆分 `model_ok` 与 `index_ok`，不再互相冒充。
- 测试：Python **107 passed**；前端 **10 passed**；`npm run check` / `build` 通过。
  以上均为离线测试；真实模型质量与真实浏览器白屏未在本批复测。

---

## 〇之二、2026-10-28 P1 更新（本批）

- `/api/search` 现在返回命中 chunk、命中章节、命中词与原因：
  `match.sources` = `fts` / `vec` / `graph:*`，另带两路 RRF 贡献。
- FTS 结果按文档去重，只保留每篇文档 BM25 最好的一块；单源融合也按文档去重。
  候选池设下限（FTS 60 篇 / 向量 80 块），`top_k=5` 与 `top_k=10` 排序更一致。
- 查询噪声清理：`{{7*7}}` 里的单数字不再进 FTS；单字母 `n/e/c` 精确匹配，
  不再用 `"e"*` 前缀扫全库。
- `/api/search` 支持 `doc_type=topic|card`，返回 `doc_type` / `doc_type_label` /
  `counts`。前端可筛选，结果卡片显示「专题文档 / 比赛卡片」。
- 图谱补入条目单独显示为「关联阅读」，不混进主排名。
- 新增 `POST /api/feedback`：`useful|useless|adopted` 追加到
  `work/feedback/feedback.jsonl`（`[feedback].file` 可改）；本地文件，不入库。
- 新增可复现评测：`python tools/eval_search.py`，固定
  `eval/search_queries.json` 22 条，输出 top1 / hit@5 / MRR / recall@5。
- 测试：Python **132 passed**；前端 **14 passed**；`npm run check` / `build` 通过。
- 评测基线（同一固定集）：改动前 top1=0.9545 / MRR=0.9697；P1 后均为 1.0000。
  FTS-only 为 top1=0.9091 / MRR=0.9545，保留 hybrid 有数据依据。
- **未调 RRF/BM25 权重**；本批改的是候选生成与查询噪声，再由评测验证。

---

## 〇之三、2026-10-28 P2 更新（本批，已完成）

- 新增只读附件分析：`tools/agent/attachment.py`，只解析字节，不执行脚本/
  可执行文件，不调用 `binwalk`/`exiftool`/`strings` 等外部命令。
- 新增 `POST /api/analyze?name=<文件名>`：请求体为原始字节。默认上限 8 MiB
  （`[attachment].max_bytes` / `AGENT_ATTACHMENT_MAX_BYTES` 覆盖，硬上限
  64 MiB），名字最长 240 字符；空附件/超长名字/超限分别 400/400/413。
- 上传副本写入 `work/attachments/<uuid>/upload_<安全名>`，隔离目录可配置；
  文件名只保留最后一段并清洗非法字符，防路径穿越。
- 返回结构化报告：`file`、`type`、`carve`、`structures`（PNG/WAV/ZIP）、
  `anomalies`、`decoded`（base64/hex/url）、`strings`、`warnings`、`storage`；
  `executed` 恒为 `false`。脚本扩展名只警告“不会运行”，不拒绝上传。
- `GET /api/health` 增加 `attachment.max_bytes`；`model_ok` / `index_ok` 语义不变。
- 新增固定评测：`eval/attachment_cases.json` 5 个样例（PNG 追加 ZIP、伪装 PNG、
  文本 base64、WAV 尾部、脚本警告），样例由 `tools/eval_attachments.py`
  的 `BUILDERS` 现场生成，pytest 与 CLI 共用，不提交二进制。
- 测试：Python **151 passed**（P1 的 132 + P2 新增 19）；附件评测 **5/5**。
  本批未改 React 源码，前端检查/测试/构建沿用 P1 结果。
- 已知边界：只做静态结构/字符串/编码嗅探，不反编译、不模拟执行、不沙箱运行；
  ZIP 只列目录不解压；`work/attachments/` 暂无自动清理策略。

---

## 一、运行方式

```powershell
cd F:\CTFfiles\knowledgeBase
.\start.ps1            # 拉起 Ollama + Web，开浏览器
.\start.ps1 -Status    # 看状态
.\start.ps1 -Stop      # 全停
```

Web 界面：`http://127.0.0.1:8765/`

**当前状态（2026-10-27 21:12 实测）**：8765 和 11434 **都没有在监听**。
服务是停的。要验证任何东西，先跑 `.\start.ps1`。

`start.ps1` 会做这些：
1. 检查 venv / server.py
2. 检查前端 `dist/`，没有就 `npm install && npm run build`
3. 检查索引，没有就 `kb index`
4. 起 Ollama（`models/ollama-server/ollama.exe serve`），等待 `/api/version`
5. 起 Web 服务，写 pid 到 `logs/`

---

## 二、代码结构

```
knowledgeBase/
├── config.toml              全部可调参数
├── start.ps1                一键启动（UTF-8 BOM，勿丢）
├── kb/                      知识库正文
│   ├── {misc,crypto,web,pwn,reverse,forensics,
│   │     mobile,hardware,osint,ai,blockchain}/   手写 241 篇
│   ├── _imported/           ctf-wiki 导入 266 篇
│   └── _des/                Des-CTF-Knowledge 导入 1060 篇
├── index/                   fts.db 132MB / vectors.db 42MB / graph.db 0.4MB
├── models/                  bge ONNX + ollama-server + ollama-models
├── tools/
│   ├── cli.py               命令行入口
│   ├── kb/                  检索引擎
│   └── agent/               Web 服务 + React 前端
└── docs/                    GRAPH.md / HINT.md / IMPORT_DES.md / UI.md
```

### 检索引擎（`tools/kb/`）

| 文件 | 职责 |
|---|---|
| `parser.py` | front-matter 解析、分块（900 字 / 120 重叠）、CJK 二元分词 |
| `fts.py` | SQLite FTS5，列权重 `title > signals > tags > path > body` |
| `vectors.py` | sqlite-vec 向量索引，512 维 |
| `embedder.py` | ONNX bge-small-zh（1.3ms/条），不可用时降级 |
| `fusion.py` | RRF 融合，`rrf_k=60` |
| `graph.py` | 知识图谱，6 种关系，有界 BFS 扩展 |
| `rag.py` | `KB` 类：装配上面全部 + LLM |
| `llm.py` | Ollama / llama.cpp 双后端 |

### Web 服务（`tools/agent/server.py`，P0 后约 660 行）

标准库 `ThreadingHTTPServer` + `BaseHTTPRequestHandler`，无框架。

```
GET  /                托管 tools/agent/webapp/dist/（SPA 回退）
GET  /api/health      模型状态 + 索引状态（model_ok / index_ok 分离）
GET  /api/stats       文档/分块/方向计数
POST /api/search      {q, top_k, category, doc_type} → {hits, graph, counts, ms}
GET  /api/doc?path=   单篇全文
POST /api/ask         {q, paths} → SSE
POST /api/feedback    {query, path, verdict, note} → 追加本地 JSONL
```

- 静态文件有 `relative_to(root)` 防穿越
- dist 缺失时回退 `tools/agent/web/index.html`（旧单文件版，保底可用）

### 前端（`tools/agent/webapp/`）

React 19 + TS + Vite 8 + Mantine 8.3.18。
**改完 `src/` 必须 `npm run build`**，Python 托管的是 `dist/`。

```
src/
├── main.tsx             MantineProvider + brand 十档色阶
├── App.tsx              AppShell + 侧栏方向筛选 + Reader 挂载
├── api.ts               fetch 封装 + SSE + 反馈
├── types.ts             Hit / SearchResp / DocType / MatchInfo
├── lib/sse.ts           SSE 解析（tok/err/done）
├── pages/SearchPage.tsx 搜索 / 问模型 / 类型筛选 / 解释 / 反馈
├── pages/SearchPage.test.tsx
├── api.test.ts
└── components/
    ├── Md.tsx           react-markdown + rehype-highlight + 复制按钮
    └── Reader.tsx       Drawer + 自建目录（h1-h3）
```

---

## 三、知识库内容

| 分区 | 篇数 | 质量 | 说明 |
|---|---|---|---|
| 手写条目 | 241 | ✅ 高 | 带 `signals`，结构统一（识别信号/原理/步骤/脚本/坑/来源） |
| `_imported/` | 266 | 🟡 中 | ctf-wiki 中文导入；2026-10-28 全库扫描 **0 篇空 title** |
| `_des/topics` | 13 | ✅ 高 | SQL/SSRF/SSTI/PHP反序列化/命令执行/文件上传… 代码密度极高 |
| `_des/wp_summary` | 14 | ✅ 高 | ctfshow 系列 + 靶场汇总 |
| `_des/tools` | 6 | ✅ 高 | sqlmap/tshark/wireshark/内存取证 |
| `_des/cards` | 1027 | 🟡 中 | 比赛 WP 抽的「思路卡」，只有元数据不要正文 |
| **合计** | **1567** | | 分块 14139 |

**为什么 cards 只有元数据**：原始 WP 的图片 100% 被删（`images_removed: true`），
83% 正文在描述看不见的图。但 `one_liner` / `lesson` / `attack_chain` 是
高质量思路，且不受影响。详见 `docs/IMPORT_DES.md`。

---

## 四、已验证的结论（有实测数据）

### 检索
- FTS-only 约 50ms；带向量约 200–460ms
- P95 在 460ms 内

### 问答
- **P0 更新**：不再硬编码模型。默认读 `config.toml` 的
  `[ollama] model = "qwen2.5-coder-7b"`，并按 `/api/tags` 解析实际可用名。
  本机实际 manifest 包括 `qwen2.5-coder-7b:local` 等；
  未发现 `qwen3-4b-local:latest` 的 manifest。
- 旧记录“883 段 / 2144 字 / 105 秒”**本批未复现**，只能当历史线索。
- 旧记录“4B 优于 7B”来自 `docs/HINT.md` 的一次对比，**本批未复现**。

### 图谱
- 旧记录“1567 节点 / 26 条边 / 7% 覆盖率 / 1 跳 12 节点”**本批未复现**。
  图谱可用性应由评测决定，不以边数凑指标。

### 前端
- `npm run check` 通过（TS 拆分为 app/node 两个配置）
- `npm run build` 通过，产物 JS 约 791KB（gzip 245KB）、CSS 约 207KB（gzip 31KB）

---

## 五、已确认的问题（按严重度）

### 1. ✅ 已修复：前端 `setImmediate` 与旧闭包

旧代码在起点卡片和结果卡片里 `setState` 后用 `setImmediate(() => runAsk())`。
`setImmediate` 是 Node 全局，浏览器没有；同时回调还读旧 `q` 闭包。

P0 修复：
- 起点卡片直接 `runSearch(s.q)`；结果卡片构造 `question` 后 `runAsk(question)`。
- 删除全部 `setImmediate`（`grep` 已无匹配）。
- TS 拆分：`tsconfig.app.json` 不再引入 Node 类型，`vite.config.ts` 单独用 Node 类型。
- 组件测试覆盖“点击起点卡片用卡片自己的文本搜索”“结果卡片用卡片问题提问”。

**测试局限**：未在真实浏览器逐路径录制，只做了类型检查、组件测试和生产构建。

### 2. ✅ 已修复：SSE 错误/完成事件

统一契约：

```
{"t":"tok","v":"..."}    增量正文
{"t":"err","v":"..."}    可展示错误
{"t":"done","info":"..."} 正常结束
```

前端 `src/lib/sse.ts` 解析分块、UTF-8、CRLF、`tok/err/done`；空响应也会
显示“模型没有返回内容”。`done.info` 显示在回答卡片标题旁。
测试覆盖分块、UTF-8、错误、空响应、429、取消。

### 3. ✅ 已修复：模型/host/context 配置

`server.py` 启动时读 `config.toml`：
- `[ollama].host` → `OLLAMA`
- `[ollama].model` → `MODEL`
- `[llm].n_ctx / max_tokens / temperature / timeout / keep_alive` → 生成参数

环境变量 `AGENT_OLLAMA`、`AGENT_MODEL`、`AGENT_NUM_CTX`、`AGENT_MAX_TOKENS`、
`AGENT_TEMPERATURE`、`AGENT_TIMEOUT`、`AGENT_KEEP_ALIVE` 只做显式覆盖。
实际模型名通过 `/api/tags` 解析，例如配置 `qwen2.5-coder-7b` 会匹配到
`qwen2.5-coder-7b:local`；本机未发现 `qwen3-4b-local:latest` 的 manifest。

### 4. ✅ 已修复：串行生成与诚实取消

- `/api/ask` 用非阻塞锁串行生成；忙碌时返回 **429**
  `{"error":"模型正在处理上一条问题，请稍后再试"}`，前端可见。
- 客户端断开时捕获 `BrokenPipeError/ConnectionResetError`，并 `gen.close()`，
  让 `requests` 上游连接尽量释放。
- 前端按钮改为“停止接收”，提示“仅关闭本地接收，后端模型可能仍在收尾”，
  不再谎称已停止后端运算。
- **限制**：上游 Ollama 可能在连接关闭后短暂收尾，本机无法保证瞬时停算。

### 5. 🟡 部分改善：检索排序噪音

P1 修掉了“一篇长文档的所有 chunk 占满 top-N”的主因（FTS 文档级最好块 +
候选池下限 + 查询噪声清理）。固定 22 条评测集上 top1/MRR 从
0.9545/0.9697 提升到 1.0/1.0。

仍未解决：泛化查询下 signals 很多的长文档仍可能偏前；22 条集太小，
不能证明全库无噪音。**未调 RRF/BM25 权重**；下一步应扩评测集再决定。

### 6. 🟢 临时脚本

根目录 `_extract.py`、`_jail_test.py`、`_jar1..5.py`、`_probe1..3.py`
仍在本地；`.gitignore` 已忽略 `/_*.py`，不会提交。是否移到 `work/` 由用户决定，
本批不删除用户文件。

---

## 六、目录卫生

| 位置 | 状态 |
|---|---|
| `work/` | **约 45.6 MB / 1237 文件**，含截图、临时脚本、模拟报告；P2 上传副本落 `work/attachments/` |
| `temp_newData/` | **约 18.9 GB / 8609 文件**（2026-10-28 统计），已 gitignore |
| `index/` | 约 175 MB（fts 138.7 MB / vectors 44.0 MB / graph 0.44 MB，可重建） |
| `models/` | bge + ollama，已 gitignore，未提交 |
| `.git` | **已存在**；基线提交 `b9ebe89`，未提交大目录 |

**版本控制已建立**。禁止把模型、索引、缓存、`work/`、`temp_newData/` 提交进去。

---

## 七、可直接复用的东西

### 命令行
```powershell
.\.venv\Scripts\python.exe tools\cli.py search "查询"
.\.venv\Scripts\python.exe tools\cli.py show crypto/rsa-common-modulus-attack
.\.venv\Scripts\python.exe tools\cli.py hint 附件.png
.\.venv\Scripts\python.exe tools\cli.py graph --build
.\.venv\Scripts\python.exe tools\cli.py lint
```

### 测试与评测
`pytest.ini` 已配好（`pythonpath = tools`）。2026-10-28 P1 后：
- Python：`132 passed`（P0 的 107 + P1 的命中解释/类型筛选/反馈/评测指标）。
- 前端：`npm test` → 14 passed（SSE、显式参数、类型筛选、解释、反馈、图谱关联）。
- 类型/构建：`npm run check`、`npm run build` 通过。
- 检索评测：`python tools\eval_search.py` → 22 条，hybrid top1/MRR 均为 1.0；
  `--mode fts` 为 0.9091/0.9545，保留 hybrid 有数据依据。
- 真实模型、真实浏览器未纳入自动化；测试全部离线 Mock。

### 前端开发
```powershell
cd tools\agent\webapp
npm run dev     # :5173 热更新，/api 代理到 :8765
npm run build   # 必须，Python 托管 dist
npm run check   # 仅类型检查
```

---

## 八、建议的接手顺序

1. 先读 `docs/PROJECT_MEMORY.md` 与 `docs/DEVELOPMENT_PLAN.md`，确认本批状态。
2. 跑 `pytest -o addopts="" -q`、`npm run check`、`npm test`，确认基线全绿。
3. 若要真实验证：`.\start.ps1`，在浏览器点起点卡片/结果卡片“问模型”，
   观察错误提示与“停止接收”语义。注意本机当前 8765/11434 未监听。
4. P1、P2 已完成；下一步 P3 做持久化题目工作区，可顺带把附件上传接入 React。
   检索排序若要继续调，先扩 `eval/search_queries.json` 评测集，不要凭感觉改权重。

---

## 九、给下一位的提醒

- **PowerShell 脚本必须存 UTF-8 BOM**，否则 GBK 下中文乱码导致解析失败
- `config.py` 里显式按 UTF-8 读 toml，是为了绕开 Windows 默认 GBK
- Ollama 日志默认不记请求（`OLLAMA_DEBUG_LOG_REQUESTS:false`），
  想排查请求要改环境变量
- 索引重建 4 分钟，改知识库后记得重跑 `kb index`

**测试基线（2026-10-27）**：`pytest` 82 passed；server 与前端零测试覆盖。
**P0 后（2026-10-28）**：Python 107 passed（含 25 个 server 离线测试）；
前端 10 passed；`npm run check` / `npm run build` 通过。
**P1 后（2026-10-28）**：Python 132 passed；前端 14 passed；评测 22 条
hybrid top1/MRR 1.0。真实模型/真实 Ollama/真实浏览器仍未纳入自动化。
**P2 后（2026-10-28）**：Python 151 passed；附件评测 5/5（pass_rate=1.0）；
前端未改，沿用 P1 的 14 passed。附件分析全部离线、只读，不执行上传内容。

---

## 十、延伸阅读

本文只讲「现在是什么样」。**往哪走看 `docs/ROADMAP.md`**，
那里有主线判断、优先级排序，以及明确不做的事。
