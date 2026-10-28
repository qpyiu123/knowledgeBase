# 交接文档：项目当前状态

**写给**：下一个接手的人（GPT6.1Sol）
**日期**：2026-10-27
**项目**：`F:\CTFfiles\knowledgeBase`
**一句话**：一个本机离线的 CTF 知识库，覆盖 11 个赛道 1567 篇，
支持中文模糊检索 + 本地小模型问答，带 React 前端。

> 本文只写**当前事实**与**已确认的问题**。推理过程中的猜测都标了「待验证」。

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

### Web 服务（`tools/agent/server.py`，375 行）

标准库 `ThreadingHTTPServer` + `BaseHTTPRequestHandler`，无框架。

```
GET  /                托管 tools/agent/webapp/dist/（SPA 回退）
GET  /api/health      模型状态 + 文档数
GET  /api/stats       文档/分块/方向计数
POST /api/search      {q, top_k, category} → {hits, graph, ms}
GET  /api/doc?path=   单篇全文
POST /api/ask         {q, paths} → SSE
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
├── api.ts               fetch 封装 + SSE reader
├── pages/SearchPage.tsx 搜索 / 问模型 / 起点卡片
└── components/
    ├── Md.tsx           react-markdown + rehype-highlight + 复制按钮
    └── Reader.tsx       Drawer + 自建目录（h1-h3）
```

---

## 三、知识库内容

| 分区 | 篇数 | 质量 | 说明 |
|---|---|---|---|
| 手写条目 | 241 | ✅ 高 | 带 `signals`，结构统一（识别信号/原理/步骤/脚本/坑/来源） |
| `_imported/` | 266 | 🟡 中 | ctf-wiki 中文导入，**无 title 的有 21 篇** |
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
- 默认模型 `qwen3-4b-local:latest`（server.py 里硬编码）
- 实测 883 段 / 2144 字 / **105 秒** 一次完整回答
- 4B 在结构化判断上优于 7B：`docs/HINT.md` 记录了 7B 把正确方法判成「不适用」

### 图谱
- 1567 节点 / **26 条边**（8 条跨方向）
- 只有 17 篇手写文档带关系字段（约 7% 覆盖率）
- 扩展预算：1 跳 / 12 节点 / 扇出 4 / 120ms

### 前端
- `npx tsc -b` 通过
- `npx vite build` 通过，产物 JS 790KB（gzip 244KB）、CSS 207KB

---

## 五、已确认的问题（按严重度）

### 1. 🔴 前端可能整体白屏 —— 待验证

`SearchPage.tsx` 第 413、446 行用了 **`setImmediate`**：

```ts
setImmediate(() => runAsk());
setImmediate(() => runSearch());
```

`setImmediate` 是 **Node.js API，浏览器里没有**。
浏览器执行到这两行会抛 `ReferenceError`。

触发路径：
- 点结果卡片的「问模型」按钮 → 413 行
- 点首页三张起点卡片 → 446 行

**但 TypeScript 类型检查没报错**，因为 `tsconfig.json` 里
`"types": ["node"]` 引入了 Node 类型，把 `setImmediate` 当成合法全局。

> 严格说这是类型配置掩盖了运行时错误。
> 修法：换成 `setTimeout(fn, 0)` 或 `queueMicrotask`，并把 `types` 去掉 node。

**待验证**：开服务后用浏览器点起点卡片，看控制台是否报错。
（我这次只做了只读审查，没有实际运行浏览器。）

### 2. 🟡 SSE 错误事件前端收不到

后端 `_ask_stream` 发的错误事件是 `{"t":"err","v":"..."}`：

```python
yield 'data: {"t":"err","v":"没有可用的知识库内容"}\n\n'
```

前端 `api.ts` 只认 `ev.err`：

```ts
else if (ev.err) handlers.onError?.(ev.err);
```

字段名不匹配 → **后端报错时前端静默无感**，界面上看不到任何提示。
修法：前端加 `ev.t === 'err'` 分支，或后端改成 `{"err": ...}`。

### 3. 🟡 后端改了配置但没生效

- `config.toml` 的 `[ollama] model = "qwen2.5-coder-7b"`
- `server.py` 第 34 行硬编码 `MODEL = os.environ.get("AGENT_MODEL", "qwen3-4b-local:latest")`

**server.py 不读 config.toml 的模型配置**，两者不一致。
想换模型只能设 `AGENT_MODEL` 环境变量或改代码。

### 4. 🟡 `/api/ask` 没有并发保护

`_ask_stream` 每次都直连 Ollama 打 900 token。
4GB 显存下同时两个请求会互相挤爆。当前没有队列、没有限流、没有取消传播
（前端 AbortController 断开连接后，后端 `_ask_stream` 仍会继续跑到结束，
只在写 socket 时才因 `BrokenPipeError` 退出）。

### 5. 🟡 检索排序有噪音

实测搜「SSTI」时，第 2、3 条是比赛 WP 卡片而不是专题文档；
搜「命令执行 过滤 绕过」，第 2 条是 `SQL` 文档。
原因：主题文档（`_des/topics`）与 cards 共享大量通用词，RRF 后没有类型加权。

修法方向：给 `_des/topics` 和手写条目加一点的排序加成，
或按 `kind` 做二次重排。

### 6. 🟢 根目录有 10 个临时脚本

```
_extract.py _jail_test.py _jar1..5.py _probe1..3.py
```
都是做 CTF 模拟测试时留下的，与主程序无关。应移到 `work/` 或删掉。

---

## 六、目录卫生

| 位置 | 状态 |
|---|---|
| `work/` | **43 MB / 1237 文件**，含截图、临时脚本、模拟报告 |
| `temp_newData/` | 原始导入语料，38 MB，导入完可归档 |
| `index/` | 175 MB（可重建，删了跑 `kb index` 约 4 分钟） |
| `models/` | bge + ollama，已 gitignore |
| `.git` | **不存在** —— 项目没有版本控制 |

**没有 git 是个隐患**：所有改动无历史，出问题没法回滚。

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

### 测试
`pytest.ini` 已配好（`pythonpath = tools`），`tests/` 下有 8 个测试文件。
**本次未运行**（只做了只读审查）。接手后建议先跑一遍确认基线。

### 前端开发
```powershell
cd tools\agent\webapp
npm run dev     # :5173 热更新，/api 代理到 :8765
npm run build   # 必须，Python 托管 dist
npm run check   # 仅类型检查
```

---

## 八、建议的接手顺序

1. **跑 `.\start.ps1`**，打开界面，点一张起点卡片 —— 验证问题 1 是否真的白屏
2. **跑 `pytest`** —— 确认基线，记下失败项
3. **修问题 1 和 2** —— 都是小改动，但一个影响可用性、一个影响可观测性
4. **决定要不要 `git init`** —— 没有版本控制，后面任何改动都不可回滚
5. 再考虑问题 5（排序）和 4（并发）

---

## 九、给下一位的提醒

- **PowerShell 脚本必须存 UTF-8 BOM**，否则 GBK 下中文乱码导致解析失败
- `config.py` 里显式按 UTF-8 读 toml，是为了绕开 Windows 默认 GBK
- Ollama 日志默认不记请求（`OLLAMA_DEBUG_LOG_REQUESTS:false`），
  想排查请求要改环境变量
- 索引重建 4 分钟，改知识库后记得重跑 `kb index`

**测试基线（2026-10-27 实测）**：`pytest` 82 passed，9.7 秒。
但 `server.py`（375 行）和整个前端**零测试覆盖**。

---

## 十、延伸阅读

本文只讲「现在是什么样」。**往哪走看 `docs/ROADMAP.md`**，
那里有主线判断、优先级排序，以及明确不做的事。
