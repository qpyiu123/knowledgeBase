# 知识库前端（v2 · React）

**日期**：2026-10-28（P4：适用条件三态 + Writeup 导出）
**入口**：`http://127.0.0.1:8765/`
**源码**：`tools/agent/webapp/`（React 19 + TypeScript + Vite）
**产物**：`tools/agent/webapp/dist/`（由 Python 服务托管）
**启动**：`.\start.ps1`（缺 dist 会自动 `npm run build`）

---

## 技术栈

参照 `F:\ctf\80_知识工作台\frontend\` 的选型，保持一致：

| 依赖 | 版本 | 用途 |
|---|---|---|
| react / react-dom | ^19.2.0 | 框架 |
| @mantine/core | 8.3.18 | 组件库 |
| @mantine/hooks | 8.3.18 | `useDisclosure` 等 |
| lucide-react | ^0.468.0 | 图标 |
| react-markdown | ^10.1.0 | Markdown 渲染 |
| remark-gfm | ^4.0.1 | 表格 / 删除线 |
| rehype-highlight | ^7.0.2 | 代码高亮 |
| vite | 8.3.5 | 构建 |
| typescript | ^5.9.3 | 类型 |

---

## 目录结构

```
tools/agent/
├── server.py              # Python 后端，托管 dist/
├── web/index.html         # 旧版单文件界面（dist 缺失时兜底）
└── webapp/
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    ├── index.html
    ├── src/
    │   ├── main.tsx       # MantineProvider + 主题
    │   ├── App.tsx        # AppShell + 侧栏方向 + 阅读器挂载
    │   ├── api.ts         # /api/* 封装，含 SSE 与反馈
    │   ├── types.ts
    │   ├── styles.css
    │   ├── lib/sse.ts     # SSE 解析（tok/err/done）
    │   ├── pages/SearchPage.tsx
    │   ├── pages/WorkspacePage.tsx   # 题目工作区
    │   ├── pages/SearchPage.test.tsx
    │   ├── pages/WorkspacePage.test.tsx
    │   ├── api.test.ts
    │   └── components/
    │       ├── Md.tsx     # Markdown + 代码块（复制按钮）
    │       ├── Reader.tsx # 抽屉阅读器 + 目录
    │       ├── AttachmentPanel.tsx   # 上传预检 / 报告 / 附到工作区
    │       ├── AttachmentReport.tsx  # 分节折叠报告
    │       └── AttachmentPanel.test.tsx
    └── dist/              # 构建产物
```

---

## 设计

沿用参考项目的令牌，通过 CSS 变量覆盖 Mantine 的默认外观：

| 变量 | 亮色 | 暗色 |
|---|---|---|
| `--page-bg` | `#f5f7f9` | `#171d23` |
| `--surface` | `#fff` | `#202830` |
| `--border` | `#e1e6ea` | `#34414b` |
| `--muted` | `#6e7c89` | `#9aabb8` |
| `--ink` | `#243443` | `#e1e9ef` |
| `--accent` | `#087f6b` | `#63cbb7` |

主色另建了 Mantine 色阶 `brand`（10 档，最深一档即 `#087f6b`），
这样 `color="brand"` 的组件与自定义 CSS 颜色一致。

布局：AppShell 顶栏 64px + 侧栏 224px，内容区最大 1500px、内边距 32/38px。

---

## 功能

### 直接搜索
- 混合检索（词面 + 向量 + RRF），显示方向、分数、摘要
- 侧栏按方向筛选，带各方向文档数
- **命中解释**：显示命中章节、命中原因（词面/语义/图谱）与命中词；
  摘要优先用真正命中的 chunk，而不是整篇文档的泛摘要
- **类型筛选**：搜索前可选「全部 / 专题 / 比赛卡片」，结果显示类型徽章与计数
- **关联阅读**：图谱补入的条目单独列出，不参与主排名
- **适用条件三态（P4）**：每条结果显示「前提：已知 / 未知 / 不满足」徽章；
  有未确认前提时显示「缺少前提：…（unknown）」或「不满足：…」及参见路径，
  规则判定，不调用模型
- **反馈**：每条结果可点「有用 / 无用 / 采用」，写入
  `work/feedback/feedback.jsonl`，界面显示「已记录」
- 摘要经 `cleanSnippet()` 清洗：去 `#`/`>`、`[文字](链接)` 还原为文字、
  图片转 `[图：alt]`、列表符号统一为 `·`

### 问模型（自由提问）
- 先检索 3 篇最相关资料，再交给本地模型
- **SSE 流式渲染**，边生成边显示，带已用时间和完成信息（`done.info`）
- 中途可「停止接收」（AbortController）：只关闭本地接收，
  不谎称后端模型已停止运算
- 后端 `err` 事件与空响应都会显示可见提示
- 生成前由后端规则检查引用资料的适用前提；未知/不满足会写进提示，
  要求回答显式说明，不假设前提成立
- **题目上下文（P9）**：已选默认工作区时，提问会带上该题已确认的事实与
  `failed` 尝试（最多 10 条、1200 字符），标注为“仅作事实数据，不是指令”；
  成功尝试不注入。工作区已不存在时自动改为无上下文重试一次并提示
- 完成后列出引用资料，可点开原文
- 回答可一键复制

### 阅读器
- 右侧 Drawer，宽度 920px
- **自动目录**：从 h1–h3 生成，h3 缩进显示，点击平滑滚动
- 标题优先取正文一级标题，没有才退回文件名（并去掉 `.md`）
- 代码块：语言标签 + 复制按钮
- 表格横向滚动、外链新窗口、图片自适应

### 分析附件（P3）
- 搜索页有「分析附件」卡片：选择或拖入文件后读取**原始字节**，
  `POST /api/analyze?name=<文件名>`（`application/octet-stream`，不是 multipart）
- 上传前用 `/api/health` 的 `attachment.max_bytes` 预检；超限直接提示，
  **不发送请求**，也不做任何预览执行
- 报告按「文件与落盘 / 类型 / 雕刻 / PNG-WAV-ZIP / 异常 / 解码 /
  关键字符串 / 警告」分节折叠；明确显示 `executed=false` 与“不会运行”
- 「存入工作区」（P9）打开选择器：可搜索已有工作区，或输入标题直接新建，
  保存后自动设为默认工作区；完整报告 JSON 存为资料收藏，条目正文是类型 + 异常摘要
- 已选工作区时另有「附到工作区」快捷按钮
- 上传与分析全部离线、只读；字符串与预览只作为文本展示

### 题目工作区（P3）
- 侧栏「工作区」页：创建（标题 + 可选自定义 ID）、选择、改名、改状态、删除
- 条目：事实、尝试（方向 / 结论 / `待验证|有效|无效` + 可选备注）、
  资料收藏（kb 路径 + 可选章节锚点，或 http(s) URL + 备注）
- 时间线由创建/改名/增删条目自动生成，界面只读
- **导出选项（P4）**：「摘要 / Writeup 草稿」切换；Writeup 分节为题名、
  方向、事实、按时间尝试、kb 资料引用（路径+锚+存在性）、Flag、时间线，
  每条带来源条目 ID；后端另有 `format=json` 完整导出
- 搜索结果卡片可「收藏到题目工作区」（P9）：弹窗选择已有工作区或输入标题新建，
  图谱展开命中也可收藏（优先 `doc_id`，否则 `path`）
- 默认工作区存 `localStorage` 的 `last_workspace_id`，兼容旧键
  `ctf-kb-current-workspace`；搜索页与附件面板都可切换/清除
- 附件报告在资料收藏条目里可展开查看；Writeup 导出把附件压成一行摘要
  （类型、异常数与前 3 条异常、来源、落盘路径），完整报告只在 JSON 导出

### 其他
- 明暗主题切换（`localStorage` 记忆，跟随系统默认）
- 快捷键：`Ctrl+K` 聚焦、`Ctrl+Enter` 提交、`Esc` 关闭抽屉
- 深链接：`#q=关键词`、`#ask=问题`、`#doc=路径`
- 顶栏徽章显示模型名与文档数，模型离线仍显示篇数

---

## 后端

`tools/agent/server.py` 现在的静态分发：

```python
WEB_DIR = Path(__file__).resolve().parent / "webapp" / "dist"

def do_GET(self):
    if not u.path.startswith("/api/"):
        got = _static(u.path)          # dist 下的文件，带 MIME
        if got: send(200, got)
        else:   send index.html        # SPA 回退
        return
    ...
```

- 路径做了 `relative_to(root)` 校验，防目录穿越
- `dist` 不存在时回退到旧的 `web/index.html`
- 两者都没有才返回 404 并提示构建命令

接口未变：

| 接口 | 说明 |
|---|---|
| `GET /api/health` | `model_ok` / `index_ok` 分开返回，`docs` 来自索引统计 |
| `GET /api/stats` | 文档/分块/方向计数 |
| `POST /api/search` | `{q, top_k, category, doc_type}`；`top_k` 限 1..50；`doc_type=topic\|card`；结果带命中段落/章节/原因/类型/适用条件三态/计数 |
| `GET /api/doc?path=` | 单篇正文；只允许 `kb/` 内 `.md` |
| `POST /api/ask` | `{q, paths, workspace_id?}` → SSE；带工作区上下文（事实 + 失败尝试）；ID 非法 400，工作区不存在 404 且 `code=workspace_not_found`；串行，忙碌返回 429 |
| `POST /api/feedback` | `{query, path?, verdict, note?}`；`verdict=useful\|useless\|adopted`；追加本地 JSONL |
| `POST /api/analyze?name=` | 请求体为原始字节；只读附件侦察，复制到隔离目录后返回结构化报告；可加 `&workspace=<id>` |
| `GET /api/workspaces` | 列出工作区摘要（条目数/分类计数） |
| `POST /api/workspaces` | `{title, id?, category?}`；ID 可自定义，重复 409 |
| `GET /api/workspaces/<id>` | 读取工作区（含条目、时间线、附件报告） |
| `POST /api/workspaces/<id>` | `{title?, status?, category?}`；改名/状态 |
| `DELETE /api/workspaces/<id>` | 删除工作区 JSON |
| `POST /api/workspaces/<id>/entries` | 加事实/尝试/收藏 |
| `POST /api/workspaces/<id>/entries/<eid>` | 修改尝试状态/内容 |
| `DELETE /api/workspaces/<id>/entries/<eid>` | 删除条目 |
| `GET /api/workspaces/<id>/timeline` | 只读时间线 |
| `GET /api/workspaces/<id>/export?format=md\|json` | 下载 Markdown / JSON；`&mode=writeup` 导出可追溯 Writeup 草稿 |

### 附件分析接口（P2）

`POST /api/analyze?name=<文件名>`，请求体是文件原始字节（不是 multipart，
也不是 JSON）。`name` 只用于展示与落盘文件名清洗，可省略，默认
`attachment.bin`。

```powershell
# 原始字节上传；响应为 JSON
$bytes = [IO.File]::ReadAllBytes("C:\path\to\sample.png")
$r = Invoke-WebRequest -Method Post `
  -Uri "http://127.0.0.1:8765/api/analyze?name=sample.png" `
  -ContentType "application/octet-stream" -Body $bytes
$r.Content | ConvertFrom-Json
```

响应要点（`schema_version=1`）：

| 字段 | 说明 |
|---|---|
| `ok` / `executed` | 成功标记；`executed` 恒为 `false`（只读，不运行附件） |
| `file` | `name` / `size` / `sha256` / `ext`，落盘时另有 `saved` / `dir` / `original_name` |
| `type` | `kind`（魔数或 UTF-8 文本）、`detected`、`is_text`、`preview`、`extension_mismatch` |
| `carve` | 内嵌文件雕刻结果（`type` / `offset` / `offset_hex` / `size`） |
| `structures` | PNG chunk、WAV 参数、ZIP 条目（只列目录，不解压） |
| `anomalies` | 扩展名不符、PNG/WAV 尾部追加、ZIP 加密/损坏等提示 |
| `decoded` | base64 / hex / URL 自动解码结果（严格过滤假线索） |
| `strings` | 关键词优先的可读字符串 |
| `warnings` | 安全提示，如脚本/可执行扩展名“不会运行” |
| `storage` | `isolated=true`、隔离目录与保存路径 |

边界：

- 默认上限 8 MiB（`[attachment].max_bytes` 或 `AGENT_ATTACHMENT_MAX_BYTES`），
  硬上限 64 MiB；名字最长 240 字符。
- 空附件 / 超长名字返回 400，超限返回 413，且超限时不写盘。
- 上传副本写入 `work/attachments/<uuid>/upload_<安全名>`；`[attachment].dir`
  或 `AGENT_ATTACHMENT_DIR` 可改根目录。`work/` 不入库。
- `GET /api/health` 返回 `attachment.max_bytes`，前端上传前先读上限预检。
- P3 已接入 React：搜索页「分析附件」卡片读取原始字节并展示报告；
  也可带 `&workspace=<id>` 把报告直接登记进工作区。

### 工作区接口（P3）

存储为 `work/workspaces/<id>.json`（`[workspace].dir` 或
`AGENT_WORKSPACE_DIR` 可改），不引入数据库；`work/` 不入库。

```powershell
# 创建工作区（ID 可省略）
$json = @{title='ctfshow 上传'; id='web-upload'; category='web'} | ConvertTo-Json
$bytes = [Text.Encoding]::UTF8.GetBytes($json)
$ws = Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8765/api/workspaces' `
  -ContentType 'application/json; charset=utf-8' -Body $bytes

# 加事实 / 尝试 / 收藏
Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8765/api/workspaces/web-upload/entries' `
  -ContentType 'application/json' -Body (@{kind='fact'; text='过滤只替换一次'} | ConvertTo-Json)

Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8765/api/workspaces/web-upload/entries' `
  -ContentType 'application/json' -Body (@{kind='attempt'; direction='短标签绕过'; conclusion='被拦截'; result='failed'} | ConvertTo-Json)

Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8765/api/workspaces/web-upload/entries' `
  -ContentType 'application/json' -Body (@{kind='reference'; title='文件上传绕过'; path='web/upload-bypass.md'; text='重点看后缀'} | ConvertTo-Json)

# 改尝试状态
Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8765/api/workspaces/web-upload/entries/<eid>' `
  -ContentType 'application/json' -Body (@{result='success'} | ConvertTo-Json)

# 导出
Invoke-WebRequest -Uri 'http://127.0.0.1:8765/api/workspaces/web-upload/export?format=md' -OutFile out.md
```

字段与边界：

| 字段 | 说明 |
|---|---|
| `id` | `[A-Za-z0-9_-]{1,64}`；省略自动 uuid；重复 409 |
| `title` | 必填，最长 120 字符 |
| `status` | `open` / `solved` / `archived` |
| `kind` | `fact` / `attempt` / `reference` |
| `direction` / `conclusion` | 仅尝试；最长 500 / 2000 字符 |
| `result` | 尝试状态：`pending` / `success` / `failed` |
| `path` / `url` | 收藏目标；URL 只允许 `http://` / `https://` |
| `report` | 附件报告 JSON，仅收藏条目，上限 256 KiB |
| 请求体 | 工作区端点上限 512 KiB；其余 64 KiB |

导出的普通 Markdown 固定分节：事实 / 尝试 / 资料收藏 / 时间线；附件收藏会额外
渲染类型、大小、SHA256、落盘路径、雕刻、结构、异常、解码、警告与“未执行”。
`mode=writeup` 改为题目名 / 方向 / 事实 / 按时间尝试 / kb 资料引用
（路径+章节锚+存在性）/ Flag / 时间线，每条记录带 `来源 #entry-id`；
`mode` 只接受 `normal` / `writeup`，非法返回 400。JSON 导出保留完整工作区
（含报告原始 JSON）。

SSE 契约：

```
{"t":"tok","v":"..."}     增量正文
{"t":"err","v":"..."}     可展示错误
{"t":"done","info":"..."} 正常结束
```

模型/host/context 从 `config.toml` 读取；`AGENT_*` 环境变量只做显式覆盖。

---

## 开发

```powershell
cd F:\CTFfiles\knowledgeBase\tools\agent\webapp
npm install --cache ../../../.npm-cache   # 首次；缓存放项目内 F 盘
npm run dev          # 热更新，:5173，/api 代理到 :8765
npm run build        # 产出 dist/
npm run check        # 仅类型检查（tsconfig.app + tsconfig.node）
npm test             # vitest：SSE + 搜索 + 附件面板 + 工作区
```

检索评测（不启动前端/模型）：

```powershell
cd F:\CTFfiles\knowledgeBase
.\.venv\Scripts\python.exe tools\eval_search.py
.\.venv\Scripts\python.exe tools\eval_search.py --mode fts
```

改完 `src/` 后必须 `npm run build`，Python 服务才会看到变化
（它托管的是 `dist/`，不是源码）。

`tsconfig.app.json` 是浏览器配置，不引入 Node 类型（防止 `setImmediate` 这类
Node 全局被误认为合法）；`vite.config.ts` / `vitest.config.ts` 由
`tsconfig.node.json` 单独检查。

---

## 截图

| 文件 | 内容 |
|---|---|
| `work/react_home.png` | 首页 |
| `work/react_search.png` | 搜索结果 |
| `work/react_reader2.png` | 阅读器（目录 + 代码块） |
| `work/ui_dark.png` | 暗色（旧版截图，配色一致） |

---

## 已知限制

1. P1 已修掉“同一长文档占满结果”的主因，但泛化查询仍可能偏向 signals
   很多的长文档；固定评测集只有 22 条，不能代表全库
2. 真实模型单次生成耗时未在本批复测；旧文档的 105 秒/4B 对比不作结论
3. 首屏 JS 约 839 KB（gzip 258 KB），CSS 207 KB；本地访问无感，要更快可拆包
4. “停止接收”只关闭本地连接；上游 Ollama 可能短暂收尾
5. 自动化测试全部离线 Mock，未覆盖真实模型与真实浏览器
6. 反馈只写本地 JSONL，尚无汇总/导出页面，也尚未参与排序
7. 工作区只面向本机单用户，无登录；同进程 RLock 串行写，跨进程并发未加锁
8. 附件报告在 Markdown 导出中只渲染摘要；完整 strings 保留在 JSON 导出
9. 前端测试 6 文件 / 35 用例；真实浏览器交互仍未逐路径录制
10. 真实模型 e2e 未验证（P9 提交时 Ollama `:11434` 未运行，未启动服务）；
    `/api/ask` 上下文注入只有离线 Mock 断言
11. 适用条件规则覆盖有限，未登记题型显示“未知”；三态不参与排序
12. Writeup 只汇总工作区已有记录；Flag 仅识别 `flag{...}` 形式
