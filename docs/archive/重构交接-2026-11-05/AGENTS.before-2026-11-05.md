# AGENTS.md

本文件是本仓库的协作约定。任何自动化代理或接手工程师在改动前必须先读本文件，
再读 `docs/PROJECT_MEMORY.md` 与 `docs/DEVELOPMENT_PLAN.md`。

## 1. 角色与授权边界

- 用户指定：**DeepSeek 负责本批全部实现与测试**；规划与验收由 GPT-6.1-Sol 负责，
  规划/验收方不写代码、不代替实现。
- 用户已明确授权本批 P1 实现（P0 已完成）。不要因为“可能需要确认”而停下来询问代码细节。
- 只改本项目 `F:\CTFfiles\knowledgeBase`。不得修改其他项目、不得停无关服务。
- 不读取认证密钥、不提交密钥、不更改全局 Git / npm 配置。
- 不删除用户资料。`work/`、`temp_newData/`、`models/`、`index/` 即使被 gitignore
  也必须原样保留在本地。

## 2. 磁盘与依赖

- 项目、虚拟环境、模型、索引、缓存、测试依赖、构建产物一律放在 **F 盘项目内**，
  不扩大 C 盘占用。
- npm 安装使用项目内缓存，例如：
  `npm install --cache .npm-cache --no-audit --no-fund`
- 只安装必要的小量依赖。禁止为了“可能有用”引入框架。
- 不下载、不替换本地模型；不改动 `models/` 内容。

## 3. 版本控制

- 一批工作一个提交；提交前看 `git status`、`git diff --stat`。
- 禁止提交：模型、`.venv`、`node_modules`、`dist`、索引、缓存、日志、密钥、
  工作产物、大附件、`work/`、`temp_newData/`。
- 提交前检查暂存体积；基线源码 + 知识库约 3.2 MB。
- 不覆盖用户已有改动；发现冲突先停下记录，不要强推。

## 4. 事实与猜测

- 文档是线索，不是事实。旧文档中的性能数字、覆盖率、AirLLM 结论、
  “必然白屏/并发 OOM”等，若未在本批复现，一律标注“未验证”，不得当结论复用。
- 新结论必须给出可复现命令或测试。
- 区分：**已验证事实 / 推断 / 未验证**。

## 5. 工程约定

- 后端是标准库 `ThreadingHTTPServer`（`tools/agent/server.py`），不引入 Web 框架。
- 前端 `tools/agent/webapp/`：React 19 + TS + Vite + Mantine。
  改 `src/` 后必须 `npm run build`，Python 托管的是 `dist/`。
- TypeScript 浏览器配置与 Vite/Node 配置分离：浏览器代码不得依赖 Node 全局
  （如 `setImmediate`），`vite.config.ts` 单独使用 Node 类型。
- SSE 事件契约固定为：
  - `{"t":"tok","v":"..."}` 增量正文
  - `{"t":"err","v":"..."}` 可展示错误
  - `{"t":"done","info":"..."}` 正常结束
- `/api/ask` 只允许读取 `kb/` 根目录内的 Markdown；限制输入、`top_k`、正文体积；
  串行或有界生成，忙碌时返回可见提示。
- 模型名、host、context 统一从 `config.toml` 读取，环境变量只做显式覆盖。
- health 必须区分“模型可达”和“索引可用”，不得互相冒充。
- 不对真实模型、真实 Ollama、Docker 跑测试；核心端点用离线 Mock 验证。

## 6. 常用命令

```powershell
# Python 回归
.\.venv\Scripts\python.exe -m pytest -o addopts="" -q

# 检索评测（固定查询集，不启动模型）
.\.venv\Scripts\python.exe tools\eval_search.py

# 前端
cd tools\agent\webapp
npm run check          # 类型检查
npm test               # vitest（本批新增）
npm run build          # 生产构建

# 运行（真实使用，不用于本批自动化测试）
.\start.ps1
.\start.ps1 -Status
```

## 7. 完成标准

- 改动有测试或明确说明测试局限。
- 保留原测试，不通过删功能或忽略失败来变绿。
- 跑完 Python 回归、前端类型检查、前端测试、前端生产构建。
- 更新 `docs/PROJECT_MEMORY.md`、`docs/DEVELOPMENT_PLAN.md` 与相关交接/UI 文档。
- 提交一个 P1 提交，并在最终报告给出提交 hash 与未完成项。
