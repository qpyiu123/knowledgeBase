# 知识库前端（v2 · React）

**日期**：2026-10-27
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
    │   ├── pages/SearchPage.test.tsx
    │   ├── api.test.ts
    │   └── components/
    │       ├── Md.tsx     # Markdown + 代码块（复制按钮）
    │       └── Reader.tsx # 抽屉阅读器 + 目录
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
- 完成后列出引用资料，可点开原文
- 回答可一键复制

### 阅读器
- 右侧 Drawer，宽度 920px
- **自动目录**：从 h1–h3 生成，h3 缩进显示，点击平滑滚动
- 标题优先取正文一级标题，没有才退回文件名（并去掉 `.md`）
- 代码块：语言标签 + 复制按钮
- 表格横向滚动、外链新窗口、图片自适应

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
| `POST /api/search` | `{q, top_k, category, doc_type}`；`top_k` 限 1..50；`doc_type=topic\|card`；结果带命中段落/章节/原因/类型/计数 |
| `GET /api/doc?path=` | 单篇正文；只允许 `kb/` 内 `.md` |
| `POST /api/ask` | `{q, paths}` → SSE；串行，忙碌返回 429 |
| `POST /api/feedback` | `{query, path?, verdict, note?}`；`verdict=useful\|useless\|adopted`；追加本地 JSONL |

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
npm test             # vitest：SSE + SearchPage（解释/筛选/反馈/图谱关联）
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
3. 首屏 JS 约 801 KB（gzip 248 KB），本地访问无感；要更快可拆包
4. “停止接收”只关闭本地连接；上游 Ollama 可能短暂收尾
5. 自动化测试全部离线 Mock，未覆盖真实模型与真实浏览器
6. 反馈只写本地 JSONL，尚无汇总/导出页面，也尚未参与排序
