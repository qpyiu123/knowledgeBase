# 工具脚本清单（TOOLS_INVENTORY）

> 状态：完成版 v2（2026-10-28）。只清点、只验证、只登记处置建议；
> 未移动、未删除、未改名、未修改任何脚本。
> P2 未提交文件保持原样，本文件只按现状登记。

本版补齐的三处缺口：

1. **计数口径**：区分“可执行入口”“仅 import 模块”“KB 库模块”，
   不再把库模块算进脚本数；补上 `tools/dsh-ollama-provider.yml`、
   旧前端页和 `webapp` 构建配置等非 Python 工具资源。
2. **可运行性验证**：对全部 Python 文件做语法编译，对库模块做 import，
   对安全的 CLI 做 `--help`，对 PowerShell 做解析，并实际运行
   `deepcheck` / `graphbuild --check` / `kbcheck --json`，记录结果。
3. **逐文件处置与覆盖差异**：给出保留/合并/归档/加保护的逐项结论，
   并补上 `kbcheck` 与 `deepcheck` 的覆盖差异、`graphbuild` 与 `kb graph`、
   `model_check` 与 `kb doctor` 的重叠，以及 `normalize_eol.py` 的真实风险。

---

## 1. 口径与复现方法

### 1.1 统计范围

代码与脚本：

- `tools/**/*.py`、`tools/**/*.ps1`、`tools/**/*.bat`
- 仓库根 `start.ps1`
- `tests/*.py`
- 仓库根 `_*.py`（被 `.gitignore` 的 `/_*.py` 忽略）

非 Python 工具资源：

- `tools/dsh-ollama-provider.yml`
- `tools/agent/web/index.html`（旧单文件前端）
- `tools/agent/webapp/` 的 `package.json`、`vite.config.ts`、`vitest.config.ts`、
  `tsconfig*.json`、`index.html`
- `pytest.ini`、`config.toml`
- `eval/search_queries.json`、`eval/attachment_cases.json`（P2 WIP）、`eval/README.md`

排除：`.venv/`、`node_modules/`、`models/`、`index/`、`work/`、
`temp_newData/`、`_happy/`、`logs/`、`dist/`、`.git/`。

### 1.2 行数口径

物理行数（含空行），用
`[System.IO.File]::ReadAllLines($path).Count`。
不要用 `Measure-Object -Line`，它不计空行。

### 1.3 复现命令

```powershell
$files = Get-ChildItem tools\*.py, tools\agent\*.py, tools\kb\*.py,
  tools\*.ps1, tools\*.bat, start.ps1, tests\*.py, _*.py
foreach ($f in $files) {
  "{0,-42} {1,5}" -f $f.FullName.Replace((Get-Location).Path + '\',''),
    [System.IO.File]::ReadAllLines($f.FullName).Count
}

# 语法（正确处理 BOM）
.\.venv\Scripts\python.exe -X utf8 -c @"
import pathlib, tokenize
for p in pathlib.Path('.').glob('tools/**/*.py'):
    with tokenize.open(p) as f: compile(f.read(), str(p), 'exec')
print('ok')
"@
```

---

## 2. 结论：分层计数（已验证）

“离散工具脚本”不能只报一个总数。按能否直接运行分层如下：

| 层级 | 文件数 | 物理行 | 说明 |
|---|---:|---:|---|
| 可执行入口 | **21** | 4,462 | 有 `__main__`、显式脚本参数或顶层执行 |
| 仅被 import 的 Agent 模块 | **6** | 3,207 | 不能独立运行 |
| `tools/kb/` 库模块 | 14 | 3,083 | 检索/生成实现层 |
| `tests/*.py` | 12 | 1,875 | 测试 |
| 根 `_*.py` 题场探针 | 10 | 138 | gitignore，不计入工具链 |
| 非 Python 工具资源 | 11 | 1,224 | 配置/构建/旧前端页 |
| 评测数据与说明 | 3 | 228 | 2 个 JSON + 1 个 README |

- `tools/` 内共 **40 个代码文件 / 10,496 行**；加根 `start.ps1` 为
  **41 个 / 10,752 行**。
- 41 = 21 个可执行入口 + 6 个 import 模块 + 14 个 KB 库模块。
- 扣掉 KB 库后为 **27 个非库代码文件 / 7,669 行**（21 + 6）。
- 加上 10 个题场探针才是 **37 个 / 7,807 行**，但它们不在工具链里。
- 21 个入口里有 **1 个是 P2 WIP**（`tools/eval_attachments.py`），
  其余 20 个与 P2 无关。

> 直接回答“仓库有多少离散工具脚本”：
> **21 个可执行入口**；另有 **6 个仅 import 的 Agent 模块**、
> **14 个 KB 库模块**、**12 个测试**、**10 个 gitignore 探针**。

---

## 3. 27 个非库文件逐项清单

### 3.1 可执行入口（21 个）

| # | 文件 | 行 | 类别 | 运行方式 | 引用/证据 | 状态 |
|---:|---|---:|---|---|---|---|
| 1 | `start.ps1` | 604 | 服务 | `.\start.ps1`（或 `-Start`） | README、AGENTS 常用命令 | 主入口（三层诊断） |
| 2 | `tools/agent/start.py` | 66 | 服务 | `python tools/agent/start.py` | `README.md:122,287` | 辅助入口 |
| 3 | `tools/agent/server.py` | 856 | 服务 | `python tools/agent/server.py` | `tests/test_server_api.py:15` | 主服务（有未提交改动） |
| 4 | `tools/cli.py` | 496 | CLI | `python tools/cli.py ...` | HANDOVER、README | 主 CLI |
| 5 | `tools/setup_env.ps1` | 231 | 安装 | `.\tools\setup_env.ps1` | `README.md:51,259` | README 指定 |
| 6 | `tools/setup_env.py` | 262 | 安装 | `python tools/setup_env.py` | 仅本清单 | 未接入 README |
| 7 | `tools/setup_ollama.ps1` | 168 | 安装 | `.\tools\setup_ollama.ps1` | README、MOVING、`setup_env.ps1:219` | 活跃 |
| 8 | `tools/activate.ps1` | 16 | 安装 | `. .\tools\activate.ps1` | `README.md:31` | 活跃 |
| 9 | `tools/activate.bat` | 7 | 安装 | `tools\activate.bat` | 无引用 | 备用 |
| 10 | `tools/fetch_models.py` | 445 | 安装 | `python tools/fetch_models.py` | `setup_env.ps1:192`、`cli.py:105` | 活跃 |
| 11 | `tools/gen_index.py` | 92 | 数据 | `python tools/gen_index.py` | `README.md:101,113,178` | 会写 `kb/_index.md` |
| 12 | `tools/graphbuild.py` | 116 | 数据 | `... [--check|--suggest]` | 无外部引用 | 可手动运行 |
| 13 | `tools/eval_search.py` | 139 | 评测 | `... [--mode fts]` | AGENTS、`eval/README.md` | 活跃 |
| 14 | `tools/eval_attachments.py` | 243 | 评测 | `... [--check] [--json]` | `eval/attachment_cases.json` | **P2 WIP** |
| 15 | `tools/kbcheck.py` | 237 | 体检 | `... [--json] [--strict]` | `README.md:112,176,331` | 活跃 |
| 16 | `tools/model_check.py` | 137 | 体检 | `... [--json]` | `README.md:114,261,332` | 活跃（有历史基准输出） |
| 17 | `tools/deepcheck.py` | 191 | 体检 | `python tools/deepcheck.py` | 无外部引用 | 只读 |
| 18 | `tools/fix_fence.py` | 75 | 一次性 | 直接运行 | 目标写死 `:22-28` | **写 `kb/`** |
| 19 | `tools/fix_indent.py` | 66 | 一次性 | 直接运行 | 目标写死 `:13-19` | **写 `kb/`** |
| 20 | `tools/normalize_eol.py` | 29 | 一次性 | 直接运行/import | 无 `__main__` 保护 | **写 1,349 个 md** |
| 21 | `tools/bench_gguf.py` | 334 | 历史基准 | `... --layers ...` | `setup_env.ps1:166,229` | 历史环境 |

合计 4,462 行。`tools/cli.py` 实际子命令为
`index/search/ask/show/cat/doctor/bench/lint/hint/graph/stats`
（`tools/cli.py:466-479`），比文件头注释多 3 个。

### 3.2 仅被 import 的 Agent 模块（6 个）

| 文件 | 行 | 用途 | 调用方 | 状态 |
|---|---:|---|---|---|
| `tools/agent/loop.py` | 1,043 | 单步 ReAct 循环 | `tests/test_agent_loop.py:10` | 未接入 `server.py` |
| `tools/agent/tools.py` | 336 | 查库/读文件/写文件 | `loop.py:12,528`、`tests/test_agent_tools.py` | 被 loop 使用 |
| `tools/agent/hint.py` | 320 | 侦察结果 → 方向建议 | `cli.py:121`、`recon.py:736` | 活跃 |
| `tools/agent/recon.py` | 767 | 类型/魔数/strings/内嵌侦察 | `attachment.py`、`hint.py`、`loop.py:530` | 有未提交改动 |
| `tools/agent/carve.py` | 326 | 雕刻/ZIP/PNG/EXIF/WAV | `recon.py:272`、`attachment.py:24` | 活跃 |
| `tools/agent/attachment.py` | 415 | 只读附件分析 | `server.py:329`、`tests/test_attachment.py` | **P2 WIP** |

合计 3,207 行。`tools/agent/` 没有 `__init__.py`，靠命名空间包 +
`sys.path` 工作；测试与入口都显式加了 `tools` 路径。

### 3.3 KB 库模块（14 个，不是脚本）

`__init__.py` 13、`_blas.py` 19、`config.py` 138、`parser.py` 312、
`fts.py` 339、`vectors.py` 203、`embedder.py` 286、`npbert.py` 447、
`fusion.py` 127、`graph.py` 291、`rag.py` 254、`llm.py` 353、
`explain.py` 138、`evaluation.py` 163。合计 3,083 行。

---

## 4. 非 Python 工具资源（14 个 / 1,452 行）

| 文件 | 行 | 用途 | 状态 |
|---|---:|---|---|
| `tools/dsh-ollama-provider.yml` | 69 | DSH 的本地 Ollama provider 配置 | YAML 可解析，顶层 1 项 |
| `tools/agent/web/index.html` | 964 | 旧单文件前端回退页 | 39,100 字节 |
| `tools/agent/webapp/package.json` | 37 | 定义 dev/build/check/test/format | 活跃 |
| `tools/agent/webapp/vite.config.ts` | 18 | Vite 配置 | 活跃 |
| `tools/agent/webapp/vitest.config.ts` | 13 | Vitest 配置 | 活跃 |
| `tools/agent/webapp/tsconfig.json` | 7 | 引用 app/node 配置 | 活跃 |
| `tools/agent/webapp/tsconfig.app.json` | 23 | 浏览器 TS 配置 | 活跃 |
| `tools/agent/webapp/tsconfig.node.json` | 20 | Node/Vite TS 配置 | 活跃 |
| `tools/agent/webapp/index.html` | 13 | Vite 入口 HTML | 活跃 |
| `pytest.ini` | 6 | Python 测试配置 | 活跃 |
| `config.toml` | 54 | 模型/host/context/反馈路径 | 有未提交改动 |
| `eval/search_queries.json` | 119 | 固定检索评测集 | 活跃 |
| `eval/attachment_cases.json` | 60 | P2 附件评测样例清单 | **P2 WIP** |
| `eval/README.md` | 49 | 评测用法说明 | 活跃 |

`package.json` 的脚本为：
`dev`、`build`（`tsc -b && vite build`）、`check`（`tsc -b`）、
`test`（`vitest run`）、`test:watch`、`format`。

---

## 5. 运行验证矩阵（2026-10-28 实测）

### 5.1 通过项

| 检查 | 方法 | 结果 |
|---|---|---|
| Python 语法 | `tokenize.open` + `compile`，58 个文件 | **0 错误** |
| KB 库 import | 导入 12 个 `kb.*` 模块 | 全部 OK |
| Agent 模块 import | 导入 `loop/tools/hint/carve/recon` | 全部 OK |
| PowerShell 解析 | `Parser::ParseFile`，4 个 `.ps1` | 全部 0 解析错误 |
| CLI `--help` | 8 个脚本 | **8/8 exit=0** |
| `deepcheck.py` | 只读全库扫描 | exit=0；1,567 文件 / 2,246 问题 / 6 类 |
| `graphbuild.py --check` | 只读 | exit=0；1,567 文档；17 篇有关系（1%） |
| `kbcheck.py --json` | 只读 | exit=0；241 文档；2 条 info |
| `dsh-ollama-provider.yml` | `yaml.safe_load` | 可解析，顶层 1 项 |

8 个 `--help` 通过项：`cli.py`、`eval_search.py`、`fetch_models.py`、
`graphbuild.py`、`kbcheck.py`、`model_check.py`、`setup_env.py`、`bench_gguf.py`。

`deepcheck` 的 6 类问题：
缺章节 1,325；正文过短 847；疑似截断 31；front-matter 解析失败 21；
python 语法错误 21；代码围栏不配对 1。

### 5.2 未运行项及原因

| 对象 | 原因 |
|---|---|
| `tools/agent/server.py`、`tools/agent/start.py`、根 `start.ps1` | 会启动常驻服务/占端口 |
| `tools/gen_index.py` | 会写 `kb/_index.md` |
| `tools/fix_fence.py`、`fix_indent.py`、`normalize_eol.py` | 会写 `kb/` |
| `tools/model_check.py` 全量、`tools/cli.py doctor` | 会探测真实 Ollama；AGENTS 要求不对真实 Ollama 跑测试 |
| `tools/fetch_models.py --check` | 会扫描大模型文件，非本次清点所需 |
| `tools/eval_search.py` 全量 | 会加载本地嵌入/向量；`--help` 已通过，评测不在本任务范围 |
| `tools/eval_attachments.py`、`tools/agent/attachment.py` | P2 WIP，只做静态登记，不执行 |

### 5.3 题场探针的特殊结果

10 个 `_*.py` 全部是 **UTF-8 with BOM**。Python 直接运行可接受 BOM；
但用 `read_text(encoding="utf-8")` 后 `compile()` 会报
`invalid non-printable character U+FEFF`。本清单用 `tokenize.open`
复核后确认 **10 个文件语法均正常**。

---

## 6. 覆盖差异、重复与文档漂移（重点）

### 6.1 [已验证] 两个体检工具的覆盖范围不同

- `kbcheck.py` 只统计 241 篇：它的扫描在
  `tools/kbcheck.py:150` 跳过路径中任何以 `_` 或 `.` 开头的目录段，
  因此排除了 `kb/_des/` 与 `kb/_imported/`。
- `deepcheck.py` 扫描 1,567 篇：它只在
  `tools/deepcheck.py:46` 跳过文件名以 `_` 开头的文件，不看目录名。
- 结果：`kbcheck` 报 2 条 info；`deepcheck` 报 2,246 条问题。
  **两者不是同一范围的重复检查，数字不能互相替代。**

### 6.2 [推断] `deepcheck` 的 2,246 条问题主要是模板期望造成的噪声

它要求“识别信号/原理/参考”等章节，并对正文长度设阈值；导入目录
（`_des`、`_imported`）本来就不按手写条目模板组织，所以
“缺章节 1,325 + 正文过短 847”占绝大多数。
其中 **21 条 front-matter 解析失败、21 条 python 语法错误、
1 条围栏不配对**值得人工复核，但**未逐条确认是真实错误**。
运行时还会输出若干 `SyntaxWarning`（KB 代码块里的无效转义），
这些是告警，不计入上述 6 类问题。

### 6.3 [已验证] `normalize_eol.py` 的前提已失效，且没有入口保护

- 文件头说“这 5 个 pwn 文件是 CRLF，其余是 LF”；实测 1,568 个 md 中
  有 1,349 个含 CRLF：`_des` 1,060、`_imported` 266、根 1、手写目录 22。
- 脚本没有 `if __name__ == "__main__":`，被 import 时就会立即执行。
- 运行会无提示地重写这 1,349 个文件；最终 Git diff 受 `core.autocrlf`
  影响，**未实测**。

### 6.4 [已验证] `fix_fence.py` 与 `fix_indent.py` 是同一批文件的重叠工具

两者目标列表完全相同（同样是 5 个 pwn 文件），都在做代码块反缩进：
`fix_fence.py:22-28` 与 `fix_indent.py:13-19`。
只读调用其内部函数实测，5 个文件当前均为 0 处待改，说明历史修复已应用；
但两个脚本仍保留写文件路径，属于冗余的一次性工具。

### 6.5 [已验证] 数据工具与 CLI 子命令重叠

- `tools/graphbuild.py`：建图、`--check`、`--suggest`。
- `tools/cli.py graph`：建图、统计、扩展（`tools/cli.py:149-173`）。
  两者在“建图/统计”上重叠；`graphbuild` 独有的是检查与建议。
- `tools/model_check.py` 与 `tools/cli.py doctor` 都检查模型、FTS/向量索引、
  Ollama、GPU。`doctor` 更偏全链路，`model_check` 更偏模型文件与 ID。

### 6.6 [已验证] `model_check.py` 会把历史性能数字当“本机实测”打印

`MEASURED` 写死在 `tools/model_check.py:27-35`（RTX 3050 Ti、
16.2/18.2/3.9 tok/s 等），并在 `:120-127` 每次都打印为“本机实测基准”。
这些数字本批**未复现**，按 AGENTS 只能算历史线索，不能当当前结论。

### 6.7 [已验证] 安装入口两份并存且参数不等价

`.ps1` 有 `-TryCuda`（`setup_env.ps1:40`），`.py` 没有；
`.py` 有 `--venv/--python/--no-deps`（`setup_env.py:215-223`），`.ps1` 没有。
`setup_env.py:216` 的默认解释器写死 `C:\Python314\python.exe`，
但创建的 venv 仍在项目内 `.venv/`。

### 6.8 [已验证] 文档漂移

- `tools/agent/server.py:1` 仍写“单文件，零前端构建”，
  实际已托管 `webapp/dist`，并在 `dist` 缺失时回退旧
  `tools/agent/web/index.html`（`server.py:663-666`）。
- `tools/agent/tools.py:3` 仍写工作区默认 `E:\CTF\knowledgeBase\work`，
  实际代码用 `ROOT = Path(__file__).resolve().parents[2]`（`:13-15`）。
- `tools/cli.py` 文件头少列 `hint/graph/stats`。
- `README.md` 的目录结构与测试数量未包含 `graphbuild.py`、`deepcheck.py`、
  `setup_env.py`、`activate.bat` 和 P2 新增文件。

### 6.9 [已验证] 体检脚本的退出码语义不一致

- `deepcheck.py` 无论发现多少问题都 `return 0`（`tools/deepcheck.py:146`）；
  本次 `exit=0` 只代表跑完，不代表干净。
- `kbcheck.py` 默认也返回 0，只有 `--strict` 且存在 error 时才返回 1
  （`tools/kbcheck.py:226-228`）。
- 因此“exit=0”只能证明脚本可运行，不能证明知识库没有质量问题。

### 6.10 其他登记项

- `tools/agent/loop.py` 只被测试导入，`server.py` 无任何 `loop` 引用。
- `tools/dsh-ollama-provider.yml` 是有效配置，但 README 未提。
- 根目录 10 个探针把 `F:\CTFfiles\knowledgeBase\work\...` 写死，
  只能在本机路径下使用。

---

## 7. 逐文件处置建议（未执行）

| 处置 | 文件 | 理由 |
|---|---|---|
| 保留为入口 | `start.ps1`、`tools/agent/start.py`、`tools/agent/server.py`、`tools/cli.py` | 当前产品路径 |
| 保留为安装 | `setup_env.ps1`、`setup_ollama.ps1`、`activate.ps1`、`activate.bat`、`fetch_models.py` | 安装/环境 |
| 保留为数据/评测/体检 | `gen_index.py`、`eval_search.py`、`kbcheck.py`、`model_check.py`、`deepcheck.py`、`graphbuild.py` | 仍需使用；需补文档 |
| 保留为 Agent 能力 | `loop.py`、`tools.py`、`hint.py`、`recon.py`、`carve.py` | 被 CLI/测试/附件复用 |
| 收敛入口 | `setup_env.py` | 与 `.ps1` 重叠；归档或在 README 说明差异 |
| 合并/去重 | `graphbuild.py`、`model_check.py` | 与 `kb graph` / `kb doctor` 重叠；先文档化分工 |
| 归档 | `fix_fence.py`、`fix_indent.py`、`normalize_eol.py`、`bench_gguf.py` | 历史状态工具，成品库不应再跑 |
| 加保护后再留 | `normalize_eol.py`（若暂不归档） | 必须加 `__main__` guard、显式根路径、dry-run |
| 去历史数字 | `model_check.py` | 不再把 `MEASURED` 当当前实测打印 |
| 明确去留 | `tools/agent/web/index.html` | 旧前端回退页；`dist` 缺失时才用 |
| 补文档 | `dsh-ollama-provider.yml`、`graphbuild.py`、`deepcheck.py`、`setup_env.py`、`activate.bat` | README 未列出 |
| 不纳入工具链 | 根 `_*.py` 10 个 | 题场探针，已 gitignore |
| P2 WIP，保持原样 | `eval_attachments.py`、`agent/attachment.py`、`tests/test_attachment.py`、`eval/attachment_cases.json` | 不得改动/提交 |

---

## 8. 建议的整理顺序（需规划方批准后另立批次）

1. 先归档 4 个一次性脚本，给 `normalize_eol.py` 加 guard 或直接归档。
2. 收敛安装入口，README 只留一个主入口，另一个标注“Python 等价实现”。
3. 明确旧 `web/index.html` 的回退策略，避免双前端长期并存。
4. 把 `graphbuild` / `model_check` 与 CLI 子命令的分工写进 README。
5. 让 `kbcheck` 与 `deepcheck` 的覆盖范围在文档中显式区分（241 vs 1,567）。
6. 每次整理后重跑 Python 回归、前端 `check/test/build`，并更新本文件。

本版**没有执行任何移动或修改**；原因是改名会影响 README/测试，
且工作树中存在必须保持原样的 P2 未提交文件。

---

## 9. P2 WIP 边界（本文件不做改动）

当前未提交、与本清点无关且保持原样的文件：

- `config.toml`
- `tests/test_server_api.py`
- `tools/agent/recon.py`
- `tools/agent/server.py`
- `eval/attachment_cases.json`
- `tests/test_attachment.py`
- `tools/agent/attachment.py`
- `tools/eval_attachments.py`

本文件只读取它们做登记；没有编辑、移动、回退或提交。


---

## 10. 非工具链脚本：work/ 与 temp_newData/（本批新增）

> 状态：2026-10-28 只读登记。未移动、未删除、未改名、未执行任何脚本；
> 本节只补文档，并配套生成 `work/script_inventory/inventory.json`。
> 两者都不计入第 2 节的 `tools/` 工具链计数。

### 10.1 范围与口径

- `work/`：登记 82 个 `.py/.sh/.js/.ts` 文件，共 6,995 行。包含根级一次性脚本、
  `ctf_test/` 离线题目样本、`docker_env/` 本地靶场、`judge/` 出题/裁判辅助。
- `temp_newData/`：作为外部原始数据项目，**只登记导入/维护辅助脚本的头部**，
  不深读、不执行、不纳入本站工具链。本批登记 37 个：
  `99_维护工具/` 16、`70_检索原型/` 9、`80_知识工作台/` 12。
- 明确排除：`temp_newData/CTF知识库/release/` 的重复快照、
  `temp_newData/Des-CTF-Knowledge-main/` 的资料/脚本合集、
  `60_新增资料/原始附件_只归档不执行/` 的题目附件。它们不是导入辅助脚本。
- 用途判断：Python 取 docstring 首行；无 docstring 时取文件头注释并结合
  `main`/顶层语句判断；仍不明确的按文件名与位置标注。
- 引用判断：对 `tools/`、`tests/`、`work/`、`temp_newData/` 代码做静态
  import / 文件名扫描。**“未发现引用”只代表静态扫描无命中，不等于运行时一定没人用。**
- 建议仅为处置建议，本批**未执行任何移动/删除**。

### 10.2 work/ 分类统计

| 建议 | 文件数 | 说明 |
|---|---:|---|
| 保留（离线测试样本） | 25 | `ctf_test/` 下的复现题、求解脚本、对照副本 |
| 保留（本地靶场） | 2 | `docker_env/pyjail/` |
| 归档（历史基准/造题脚本） | 12 | `bench_*`、`measure_context`、`run_bench`、`make_*` |
| 归档（一次性导入/审计脚本） | 11 | `des_import`、`import_newdata`、`audit_des*` 等 |
| 归档（一次性验证脚本） | 6 | `test_*` 验证脚本 |
| 归档（裁判/出题辅助） | 5 | `judge/` |
| 删除候选（补丁已应用） | 12 | `patch_*.py`，改动已落入源码 |
| 删除候选（一次性探针） | 9 | `tree_f*`、`kbdeep1_*`、`decode_flag`、`exp.py`、`diag_rank`、`ui_check`、`checkin.sh` |
| **合计** | **82** | 6,995 行 |

### 10.3 temp_newData/ 摘要

| 目录 | 文件数 | 行数 | 性质 |
|---|---:|---:|---|
| `CTF知识库/99_维护工具/` | 16 | 2,573 | 抓取、编译、策展、打包、校验的导入管线 |
| `CTF知识库/70_检索原型/` | 9 | 944 | 早期离线检索/HTTP 原型 |
| `CTF知识库/80_知识工作台/` | 12 | 1,045 | 外部工作台的打包/校验工具与启动脚本 |
| **合计** | **37** | **4,562** | 只登记头部，不深读 |

### 10.4 work/ 逐文件明细

#### work/ 明细（82 个）

| 文件 | 行 | main | 用途 | 引用 | 建议 |
|---|---:|:--:|---|---|---|
| `work/add_relations.py` | 175 | Y | 给知识库文档批量补充跨方向关系字段。 | 未发现引用（静态扫描） | 归档（一次性导入/审计脚本） |
| `work/analyze_des.py` | 50 |  | 分析 Des-CTF-Knowledge 的资料结构，为导入做分类映射。 | 未发现引用（静态扫描） | 归档（一次性导入/审计脚本） |
| `work/analyze_quality.py` | 54 |  | 检查 quality / one_liner / lesson 字段，决定导入筛选策略。 | 未发现引用（静态扫描） | 归档（一次性导入/审计脚本） |
| `work/audit_des.py` | 152 |  | Des-CTF-Knowledge 内容质量审查（导入前）。 | 未发现引用（静态扫描） | 归档（一次性导入/审计脚本） |
| `work/audit_des2.py` | 95 |  | 深入审查：利用 frontmatter 自带的质量元数据做全量画像。 | 未发现引用（静态扫描） | 归档（一次性导入/审计脚本） |
| `work/audit_des3.py` | 93 |  | 最终审查汇总：分区质量对比 + 影响面量化。 | 未发现引用（静态扫描） | 归档（一次性导入/审计脚本） |
| `work/bench_agent.py` | 90 |  | P3：Agent 端到端性能测试（单题）。 | 未发现引用（静态扫描） | 归档（历史基准/造题脚本） |
| `work/bench_ctx.py` | 66 |  | 对比不同 num_ctx 下的生成速度与显存占用，确认 8192 是否可接受。 | 未发现引用（静态扫描） | 归档（历史基准/造题脚本） |
| `work/bench_embed.py` | 21 |  | 实测向量化速度，估算全量导入耗时。 | 未发现引用（静态扫描） | 归档（历史基准/造题脚本） |
| `work/bench_exclusive.py` | 75 |  | 独占显存场景下，探索能进一步榨出多少性能。 | 未发现引用（静态扫描） | 归档（历史基准/造题脚本） |
| `work/bench_tps.py` | 62 |  | 量化 Agent 每一步的模型调用性能（墙钟 / 生成 token / tok/s）。 | 未发现引用（静态扫描） | 归档（历史基准/造题脚本） |
| `work/checkin.sh` | 16 | Y | docker 镜像挂载/进入的临时 shell 片段 | 未发现引用（静态扫描） | 删除候选（一次性探针） |
| `work/ctf_test/qw7_babyrsa/task.py` | 60 |  | 强网杯 babyrsa 题目生成脚本（复数 RSA） | 静态扫描命中：work/ctf_test/writeups_archive/round1_235610/scratch/_v.py、work/judge/gen_discrete_log.py | 保留（离线测试样本，勿当生产工具） |
| `work/ctf_test/qw7_discrete_log/task.py` | 21 |  | 强网杯 discrete_log 题目生成脚本 | 静态扫描命中：work/ctf_test/writeups_archive/round1_235610/scratch/_v.py、work/judge/gen_discrete_log.py | 保留（离线测试样本，勿当生产工具） |
| `work/ctf_test/qw7_misc_html/bot/index.ts` | 66 |  | misc-html 题目的 puppeteer bot 服务 | 未发现引用（静态扫描） | 保留（离线测试样本，勿当生产工具） |
| `work/ctf_test/qw7_misc_html/front/src/editor.ts` | 34 |  | 题目前端 Monaco 编辑器封装 | 静态扫描命中：work/ctf_test/qw7_misc_html/front/src/index.ts、work/ctf_test/qw7_misc_html/front/vite.config.ts | 保留（离线测试样本，勿当生产工具） |
| `work/ctf_test/qw7_misc_html/front/src/html.js` | 343 |  | misc-html 题目的 html 怪机器解释器 | 静态扫描命中：work/ctf_test/writeups_archive/round1_235610/scratch/harness.js | 保留（离线测试样本，勿当生产工具） |
| `work/ctf_test/qw7_misc_html/front/src/index.ts` | 27 |  | 题目前端入口 | 未发现引用（静态扫描） | 保留（离线测试样本，勿当生产工具） |
| `work/ctf_test/qw7_misc_html/front/vite.config.ts` | 27 |  | 题目前端 Vite 配置 | 静态扫描命中：tools/agent/webapp/package.json、tools/agent/webapp/tsconfig.node.json | 保留（离线测试样本，勿当生产工具） |
| `work/ctf_test/qw7_pyjail/main.py` | 86 |  | pyjail 题目沙箱入口（黑名单演示） | 未发现引用（静态扫描） | 保留（离线测试样本，勿当生产工具） |
| `work/ctf_test/scratch_w1/driver.py` | 18 |  | babyrsa 求解驱动，调用 solve1b.check | 未发现引用（静态扫描） | 保留（离线测试样本，勿当生产工具） |
| `work/ctf_test/scratch_w1/solve1.py` | 102 | Y | discrete_log 的 DFS/格思路求解尝试 | 未发现引用（静态扫描） | 保留（离线测试样本，勿当生产工具） |
| `work/ctf_test/scratch_w1/solve1b.py` | 100 | Y | discrete_log 的 hex 字符集求解尝试 | 静态扫描命中：work/ctf_test/scratch_w1/driver.py | 保留（离线测试样本，勿当生产工具） |
| `work/ctf_test/scratch_w2/client.py` | 38 | Y | pyjail 本地交互客户端（socket 发送 payload） | 静态扫描命中：temp_newData/CTF知识库/99_维护工具/fetch_official_events.py | 保留（离线测试样本，勿当生产工具） |
| `work/ctf_test/writeups_archive/round1_235610/_t1.py` | 11 |  | discrete_log 的 p-1 因子试探 | 未发现引用（静态扫描） | 保留（离线测试样本，勿当生产工具） |
| `work/ctf_test/writeups_archive/round1_235610/_t2.py` | 14 |  | discrete_log 参数一致性核验 | 未发现引用（静态扫描） | 保留（离线测试样本，勿当生产工具） |
| `work/ctf_test/writeups_archive/round1_235610/contamination/testrun/main.py` | 86 |  | pyjail 题目副本（污染对照） | 未发现引用（静态扫描） | 保留（离线测试样本，勿当生产工具） |
| `work/ctf_test/writeups_archive/round1_235610/contamination/testrun/t.py` | 13 |  | pyjail payload 回归测试 | 未发现引用（静态扫描） | 保留（离线测试样本，勿当生产工具） |
| `work/ctf_test/writeups_archive/round1_235610/scratch/_k.py` | 19 |  | babyrsa 低位 k 关系假设验证 | 未发现引用（静态扫描） | 保留（离线测试样本，勿当生产工具） |
| `work/ctf_test/writeups_archive/round1_235610/scratch/_v.py` | 35 |  | babyrsa/discrete_log 两条假设验证 | 未发现引用（静态扫描） | 保留（离线测试样本，勿当生产工具） |
| `work/ctf_test/writeups_archive/round1_235610/scratch/harness.js` | 75 |  | html 解释器的离线 Mini-DOM 测试框架 | 未发现引用（静态扫描） | 保留（离线测试样本，勿当生产工具） |
| `work/ctf_test/writeups_archive/round1_235610/scratch/html.js` | 343 |  | html 解释器副本 | 静态扫描命中：work/ctf_test/writeups_archive/round1_235610/scratch/harness.js | 保留（离线测试样本，勿当生产工具） |
| `work/ctf_test/writeups_archive/round1_235610/scratch/main.py` | 86 |  | pyjail 题目副本 | 未发现引用（静态扫描） | 保留（离线测试样本，勿当生产工具） |
| `work/ctf_test/writeups_archive/round1_235610/scratch/pty.py` | 3 |  | pty.spawn 的空桩实现 | 静态扫描命中：work/ctf_test/qw7_pyjail/main.py、work/ctf_test/writeups_archive/round1_235610/contamination/testrun/main.py、work/ctf_test/writeups_archive/round1_235610/scratch/main.py、work/docker_env/pyjail/main.py | 保留（离线测试样本，勿当生产工具） |
| `work/ctf_test/writeups_archive/round1_235610/scratch/q1_babyrsa.py` | 167 | Y | 强网杯 babyrsa 求解脚本（评测样本） | 未发现引用（静态扫描） | 保留（离线测试样本，勿当生产工具） |
| `work/ctf_test/writeups_archive/round1_235610/scratch/q2_discrete_log.py` | 105 | Y | 强网杯 discrete_log 求解脚本（评测样本） | 未发现引用（静态扫描） | 保留（离线测试样本，勿当生产工具） |
| `work/ctf_test/writeups_archive/round1_235610/scratch/t.py` | 13 |  | pyjail payload 回归测试 | 未发现引用（静态扫描） | 保留（离线测试样本，勿当生产工具） |
| `work/decode_flag.py` | 5 |  | 硬编码 base64 flag 的解码探针 | 未发现引用（静态扫描） | 删除候选（一次性探针） |
| `work/des_import.py` | 355 | Y | 把 Des-CTF-Knowledge 导入本知识库。 | 静态扫描命中：work/patch_titles.py | 归档（一次性导入/审计脚本） |
| `work/diag_rank.py` | 33 |  | 诊断：为什么 Top-1 命中不到期望条目。 | 未发现引用（静态扫描） | 删除候选（一次性探针） |
| `work/docker_env/pyjail/main.py` | 86 |  | 本地 pyjail 靶场入口 | 未发现引用（静态扫描） | 保留（本地靶场） |
| `work/docker_env/pyjail/tcpserve.py` | 66 | Y | 极简 TCP 服务：把每个连接 dup 成子进程的 stdin/stdout，然后跑 main.py。 | 未发现引用（静态扫描） | 保留（本地靶场） |
| `work/eval_newdata.py` | 128 |  | 评估 temp_newData 知识库的整合价值。 | 未发现引用（静态扫描） | 归档（一次性导入/审计脚本） |
| `work/exp.py` | 18 |  | RSA 共模攻击模板（真实参数未填） | 未发现引用（静态扫描） | 删除候选（一次性探针） |
| `work/find_bad_titles.py` | 27 |  | 找出标题被代码块内 `#` 注释污染的文档。 | 未发现引用（静态扫描） | 归档（一次性导入/审计脚本） |
| `work/import_newdata.py` | 206 | Y | 从 temp_newData 精选文档，整理成当前知识库的 md 格式。 | 未发现引用（静态扫描） | 归档（一次性导入/审计脚本） |
| `work/judge/gen_babyrsa.py` | 108 |  | 为 babyrsa 生成固定实例的 n / e / c（裁判用）。 | 未发现引用（静态扫描） | 归档（裁判/出题辅助，已完成使命） |
| `work/judge/gen_discrete_log.py` | 72 |  | 为 discrete_log 生成**可验证**的实例（裁判用）。 | 未发现引用（静态扫描） | 归档（裁判/出题辅助，已完成使命） |
| `work/judge/ui.js` | 141 |  | 评测/演示用前端页面脚本 | 未发现引用（静态扫描） | 归档（裁判/出题辅助，已完成使命） |
| `work/judge/verify_q1.py` | 90 |  | 验证 discrete_log 是否可解（裁判用，不进题目目录）。 | 未发现引用（静态扫描） | 归档（裁判/出题辅助，已完成使命） |
| `work/judge/verify_q2.py` | 32 |  | 核验子代理给的 pyjail payload 能否通过黑名单（裁判用）。 | 未发现引用（静态扫描） | 归档（裁判/出题辅助，已完成使命） |
| `work/kbdeep1_check.py` | 53 | Y | 抽取 KB 的 Python 代码块并逐块试运行 | 未发现引用（静态扫描） | 删除候选（一次性探针） |
| `work/kbdeep1_fm.py` | 91 |  | 批量检查 KB front-matter（yaml 解析） | 未发现引用（静态扫描） | 删除候选（一次性探针） |
| `work/make_attachments.py` | 68 |  | 造几个模拟真实 CTF 的附件，测试侦察能力。 | 未发现引用（静态扫描） | 归档（历史基准/造题脚本） |
| `work/make_bench.py` | 81 | Y | 构造一套「真实题目」测试集。 | 未发现引用（静态扫描） | 归档（历史基准/造题脚本） |
| `work/make_complex.py` | 95 |  | 造几个「题面全是套话」的复杂题目，用来测试真实场景。 | 未发现引用（静态扫描） | 归档（历史基准/造题脚本） |
| `work/measure_context.py` | 94 |  | 量化上下文占用：用 Ollama 真实的 prompt_eval_count 来测。 | 未发现引用（静态扫描） | 归档（历史基准/造题脚本） |
| `work/patch_final.py` | 57 |  | 收尾：标题回退去掉 .md；服务端 dist 缺失时回退旧页面。 | 未发现引用（静态扫描） | 删除候选（补丁已应用，仅留档） |
| `work/patch_hint_tool.py` | 66 |  | 把 suggest_directions 工具加进 recon.py。 | 未发现引用（静态扫描） | 删除候选（补丁已应用，仅留档） |
| `work/patch_react_ui.py` | 76 |  | React 版小修：Badge 禁止大写 + 深链接（#q / #ask / #doc）。 | 未发现引用（静态扫描） | 删除候选（补丁已应用，仅留档） |
| `work/patch_react_ui2.py` | 44 |  | 修正深链接：让 runSearch / runAsk 接受可选文本参数。 | 未发现引用（静态扫描） | 删除候选（补丁已应用，仅留档） |
| `work/patch_serve_dist.py` | 92 |  | 改为托管 webapp/dist（React 构建产物）。 | 未发现引用（静态扫描） | 删除候选（补丁已应用，仅留档） |
| `work/patch_server_ui.py` | 89 |  | 把 server.py 里的内嵌 HTML 换成外部文件，并加 /api/stats。 | 未发现引用（静态扫描） | 删除候选（补丁已应用，仅留档） |
| `work/patch_start_ps1.py` | 62 |  | 在 start.ps1 里插入前端构建检查（dist 缺失时自动 npm run build）。 | 未发现引用（静态扫描） | 删除候选（补丁已应用，仅留档） |
| `work/patch_titles.py` | 61 |  | 修 des_import.py 的标题提取：跳过代码块内的 # 注释。 | 未发现引用（静态扫描） | 删除候选（补丁已应用，仅留档） |
| `work/patch_ui2.py` | 55 |  | 修补前端：插入 cleanSnippet 并确认被正确调用。 | 未发现引用（静态扫描） | 删除候选（补丁已应用，仅留档） |
| `work/patch_ui3.py` | 32 |  | 阅读器标题：优先用文档里的 H1，而不是文件名。 | 未发现引用（静态扫描） | 删除候选（补丁已应用，仅留档） |
| `work/patch_ui4.py` | 33 |  | 加 #ask= 深链接（自动用问模型模式）。 | 未发现引用（静态扫描） | 删除候选（补丁已应用，仅留档） |
| `work/patch_ui5.py` | 48 |  | 摘要清洗：把 Markdown 链接/图片还原成纯文本。 | 未发现引用（静态扫描） | 删除候选（补丁已应用，仅留档） |
| `work/run_bench.py` | 134 | Y | 性能测试脚本：检索 + Agent 端到端。 | 未发现引用（静态扫描） | 归档（历史基准/造题脚本） |
| `work/summary.py` | 47 |  | 汇总性能报告：把 P1 检索延迟 + P2 准确率 + 各 Agent 单题结果合成一份。 | 未发现引用（静态扫描） | 归档（历史基准/造题脚本） |
| `work/test_arch_b.py` | 145 | Y | 对比两种架构：模型独立判断 vs 模型只做排序、知识库提供候选。 | 未发现引用（静态扫描） | 归档（一次性验证脚本） |
| `work/test_ask.py` | 43 |  | 测试 /api/ask 的 SSE 流式输出。 | 未发现引用（静态扫描） | 归档（一次性验证脚本） |
| `work/test_complex.py` | 97 |  | 用「题面全是套话」的复杂题目测试 agent。 | 未发现引用（静态扫描） | 归档（一次性验证脚本） |
| `work/test_hint.py` | 122 | Y | 测试：完全没思路时，模型能给出多少有效方向。 | 未发现引用（静态扫描） | 归档（一次性验证脚本） |
| `work/test_state_model.py` | 118 | Y | 测试：小模型能否可靠地输出「候选/排除/尝试」结构化状态。 | 未发现引用（静态扫描） | 归档（一次性验证脚本） |
| `work/test_vague.py` | 47 |  | 验证：当题面几乎没有信息时，当前 agent 会怎样。 | 未发现引用（静态扫描） | 归档（一次性验证脚本） |
| `work/tree_f.py` | 103 |  | 输出 F 盘文件树（带大小、文件数）。 | 未发现引用（静态扫描） | 删除候选（一次性探针） |
| `work/tree_f2.py` | 87 |  | 输出 F 盘文件树（过滤噪声目录）。 | 未发现引用（静态扫描） | 删除候选（一次性探针） |
| `work/ui_check.js` | 517 |  | 旧前端页面的交互/完整性检查脚本 | 静态扫描命中：work/patch_ui2.py、work/patch_ui3.py、work/patch_ui4.py、work/patch_ui5.py | 删除候选（一次性探针） |
| `work/verify_ctx.py` | 75 |  | 验证改动效果：上下文占用 + 生成速度。 | 未发现引用（静态扫描） | 归档（历史基准/造题脚本） |
| `work/verify_des.py` | 55 |  | 导入后检索效果对比测试。 | 未发现引用（静态扫描） | 归档（一次性导入/审计脚本） |

#### temp_newData/ 明细（37 个）

| 文件 | 行 | main | 用途 | 引用 | 建议 |
|---|---:|:--:|---|---|---|
| `temp_newData/CTF知识库/70_检索原型/asset_index.py` | 39 |  | Filename/path metadata search for inert archive objects. No binary decoding. | 静态扫描命中：temp_newData/CTF知识库/70_检索原型/cn_kb.py、temp_newData/CTF知识库/70_检索原型/server.py、temp_newData/CTF知识库/70_检索原型/test_cn.py、temp_newData/CTF知识库/99_维护工具/package_chinese_kb.py | 保留（外部检索原型，仅登记） |
| `temp_newData/CTF知识库/70_检索原型/cn_kb.py` | 48 | Y | Primary Chinese collection entry point, separate from the old Google corpus. | 静态扫描命中：temp_newData/CTF知识库/70_检索原型/test_cn.py、temp_newData/CTF知识库/99_维护工具/package_chinese_kb.py、temp_newData/CTF知识库/99_维护工具/verify_chinese_package.py、temp_newData/CTF知识库/99_维护工具/write_official_overview.py | 保留（外部检索原型，仅登记） |
| `temp_newData/CTF知识库/70_检索原型/code_index.py` | 62 |  | Original code as inert searchable text. No eval/import/compile/exec of samples. | 静态扫描命中：temp_newData/CTF知识库/70_检索原型/cn_kb.py、temp_newData/CTF知识库/70_检索原型/server.py、temp_newData/CTF知识库/70_检索原型/test_cn.py、temp_newData/CTF知识库/99_维护工具/package_chinese_kb.py | 保留（外部检索原型，仅登记） |
| `temp_newData/CTF知识库/70_检索原型/collection_merge.py` | 32 |  | Merge only explicitly registered local collections; code is inert JSON text. | 静态扫描命中：temp_newData/CTF知识库/70_检索原型/cn_kb.py、temp_newData/CTF知识库/99_维护工具/package_chinese_kb.py | 保留（外部检索原型，仅登记） |
| `temp_newData/CTF知识库/70_检索原型/kb.py` | 365 | Y | Offline lexical/hybrid retrieval. Reads only the newly curated corpus. | 静态扫描命中：temp_newData/CTF知识库/70_检索原型/asset_index.py、temp_newData/CTF知识库/70_检索原型/cn_kb.py、temp_newData/CTF知识库/70_检索原型/code_index.py、temp_newData/CTF知识库/70_检索原型/collection_merge.py | 保留（外部检索原型，仅登记） |
| `temp_newData/CTF知识库/70_检索原型/server.py` | 70 | Y | Read-only localhost UI, no raw file serving or source code execution. | 静态扫描命中：tools/agent/server.py、temp_newData/CTF知识库/70_检索原型/cn_kb.py、temp_newData/CTF知识库/70_检索原型/kb.py | 保留（外部检索原型，仅登记） |
| `temp_newData/CTF知识库/70_检索原型/test_cn.py` | 148 | Y | Chinese KB smoke tests; never print, execute or analyze sample code. | 静态扫描命中：temp_newData/CTF知识库/99_维护工具/package_chinese_kb.py、temp_newData/CTF知识库/99_维护工具/verify_chinese_package.py | 保留（外部检索原型，仅登记） |
| `temp_newData/CTF知识库/70_检索原型/test_http.py` | 64 | Y | Localhost smoke test. Starts only the authored read-only knowledge server. | 未发现引用（静态扫描） | 保留（外部检索原型，仅登记） |
| `temp_newData/CTF知识库/70_检索原型/test_kb.py` | 116 | Y | Self-contained tests; fixture vectors are not a real embedding-model benchmark. | 未发现引用（静态扫描） | 保留（外部检索原型，仅登记） |
| `temp_newData/CTF知识库/80_知识工作台/tools/audit_corpus.py` | 105 | Y | Read all indexed text/code as inert data; never import or execute samples. | 未发现引用（静态扫描） | 保留（外部打包/校验工具，不纳入本站工具链） |
| `temp_newData/CTF知识库/80_知识工作台/tools/make_knowledge_patch.py` | 75 | Y | Cumulative source-only 1.1 patch since v1.0.0; no corpus or private state. | 未发现引用（静态扫描） | 保留（外部打包/校验工具，不纳入本站工具链） |
| `temp_newData/CTF知识库/80_知识工作台/tools/make_release.py` | 96 | Y | Create a portable ZIP64 package from registered data and verified local models. | 未发现引用（静态扫描） | 保留（外部打包/校验工具，不纳入本站工具链） |
| `temp_newData/CTF知识库/80_知识工作台/tools/make_startup_patch.py` | 47 | Y | Package only tracked source changes since v1.0.0; no models or private data. | 未发现引用（静态扫描） | 保留（外部打包/校验工具，不纳入本站工具链） |
| `temp_newData/CTF知识库/80_知识工作台/tools/prepare_models.py` | 150 | Y | Explicit online provisioning only; never imported by the offline service. | 未发现引用（静态扫描） | 保留（外部打包/校验工具，不纳入本站工具链） |
| `temp_newData/CTF知识库/80_知识工作台/tools/prepare_python39_test.py` | 35 | Y | Download an isolated official Python 3.9 runtime for compatibility testing only. | 未发现引用（静态扫描） | 保留（外部打包/校验工具，不纳入本站工具链） |
| `temp_newData/CTF知识库/80_知识工作台/tools/seed_knowledge_guides.py` | 234 | Y | Author-maintained Chinese guide seeds. Produces metadata, not solver programs. | 未发现引用（静态扫描） | 保留（外部打包/校验工具，不纳入本站工具链） |
| `temp_newData/CTF知识库/80_知识工作台/tools/smoke_models.py` | 41 | Y | Explicit local model smoke test. Outputs metadata and owned test questions only. | 未发现引用（静态扫描） | 保留（外部打包/校验工具，不纳入本站工具链） |
| `temp_newData/CTF知识库/80_知识工作台/tools/verify_guidance.py` | 96 | Y | Live workbench QA. Calls local retrieval/models; never runs sample programs. | 未发现引用（静态扫描） | 保留（外部打包/校验工具，不纳入本站工具链） |
| `temp_newData/CTF知识库/80_知识工作台/tools/verify_startup_fix.py` | 59 | Y | Explicit live smoke test against the same localhost API used by the GUI. | 未发现引用（静态扫描） | 保留（外部打包/校验工具，不纳入本站工具链） |
| `temp_newData/CTF知识库/80_知识工作台/workbench.py` | 102 | Y | Offline CTF workbench; JSON CLI and localhost GUI. Python 3.9+. | 静态扫描命中：temp_newData/CTF知识库/80_知识工作台/tools/make_knowledge_patch.py、temp_newData/CTF知识库/80_知识工作台/启动知识库.cmd | 保留（外部原始数据项目，仅登记） |
| `temp_newData/CTF知识库/80_知识工作台/启动知识库.cmd` | 5 | Y | Windows 快捷启动脚本（调用 workbench.py） | 静态扫描命中：temp_newData/CTF知识库/80_知识工作台/tools/make_knowledge_patch.py、temp_newData/CTF知识库/80_知识工作台/tools/make_release.py、temp_newData/CTF知识库/80_知识工作台/tools/make_startup_patch.py | 保留（外部原始数据项目，仅登记） |
| `temp_newData/CTF知识库/99_维护工具/build_catalog.py` | 411 | Y | Build a metadata-only CTF catalog. Never open source file contents. | 静态扫描命中：temp_newData/CTF知识库/99_维护工具/test_catalog.py | 保留（外部导入/维护管线，不纳入本站工具链） |
| `temp_newData/CTF知识库/99_维护工具/compile_chinese_corpus.py` | 172 | Y | Compile licensed prose + honest short blog guides, with opaque original code blocks. | 静态扫描命中：temp_newData/CTF知识库/99_维护工具/compile_official_events.py、temp_newData/CTF知识库/99_维护工具/package_chinese_kb.py、temp_newData/CTF知识库/99_维护工具/verify_chinese_package.py | 保留（外部导入/维护管线，不纳入本站工具链） |
| `temp_newData/CTF知识库/99_维护工具/compile_official_events.py` | 178 | Y | Prepare prose and opaque code indexes from the downloaded official archives. | 静态扫描命中：temp_newData/CTF知识库/99_维护工具/package_chinese_kb.py、temp_newData/CTF知识库/99_维护工具/verify_chinese_package.py、temp_newData/CTF知识库/99_维护工具/write_official_overview.py | 保留（外部导入/维护管线，不纳入本站工具链） |
| `temp_newData/CTF知识库/99_维护工具/curate_cards.py` | 234 | Y | Author Chinese reading notes from acquired prose. Does not read legacy sources. | 静态扫描命中：temp_newData/CTF知识库/99_维护工具/package_new_collection.py | 保留（外部导入/维护管线，不纳入本站工具链） |
| `temp_newData/CTF知识库/99_维护工具/fetch_blog_code.py` | 76 | Y | Copy confirmed CC blog pre blocks as inert text; never print or run samples. | 静态扫描命中：temp_newData/CTF知识库/99_维护工具/package_chinese_kb.py | 保留（外部导入/维护管线，不纳入本站工具链） |
| `temp_newData/CTF知识库/99_维护工具/fetch_chinese_collection.py` | 144 | Y | Acquire Chinese, explicitly licensed documentation. No legacy reads or execution. | 静态扫描命中：temp_newData/CTF知识库/99_维护工具/compile_official_events.py、temp_newData/CTF知识库/99_维护工具/package_chinese_kb.py | 保留（外部导入/维护管线，不纳入本站工具链） |
| `temp_newData/CTF知识库/99_维护工具/fetch_official_events.py` | 302 | Y | Acquire public official event archives as inert files, no git hooks or execution. | 静态扫描命中：temp_newData/CTF知识库/99_维护工具/compile_official_events.py、temp_newData/CTF知识库/99_维护工具/package_chinese_kb.py、temp_newData/CTF知识库/99_维护工具/write_official_overview.py | 保留（外部导入/维护管线，不纳入本站工具链） |
| `temp_newData/CTF知识库/99_维护工具/fetch_public_docs.py` | 117 | Y | Explicit opt-in acquisition of licensed Markdown; no archives or scripts. | 静态扫描命中：temp_newData/CTF知识库/99_维护工具/fetch_representative_assets.py、temp_newData/CTF知识库/99_维护工具/package_new_collection.py | 保留（外部导入/维护管线，不纳入本站工具链） |
| `temp_newData/CTF知识库/99_维护工具/fetch_representative_assets.py` | 110 | Y | Download selected source/attachment bytes without opening or running them. | 静态扫描命中：temp_newData/CTF知识库/99_维护工具/package_new_collection.py | 保留（外部导入/维护管线，不纳入本站工具链） |
| `temp_newData/CTF知识库/99_维护工具/inspect_chinese_blogs.py` | 130 | Y | Read public article prose, omit code/scripts, preserve license evidence. | 静态扫描命中：temp_newData/CTF知识库/99_维护工具/package_chinese_kb.py | 保留（外部导入/维护管线，不纳入本站工具链） |
| `temp_newData/CTF知识库/99_维护工具/package_chinese_kb.py` | 90 | Y | Package only the new Chinese KB. Raw samples copied as bytes, never executed. | 未发现引用（静态扫描） | 保留（外部导入/维护管线，不纳入本站工具链） |
| `temp_newData/CTF知识库/99_维护工具/package_new_collection.py` | 76 | Y | Package only new collection + authored retrieval code; never execute assets. | 未发现引用（静态扫描） | 保留（外部导入/维护管线，不纳入本站工具链） |
| `temp_newData/CTF知识库/99_维护工具/prepare_close_reading.py` | 259 | Y | Publish eight paragraph-by-paragraph prose translations, not executable solutions. | 静态扫描命中：temp_newData/CTF知识库/99_维护工具/package_new_collection.py | 保留（外部导入/维护管线，不纳入本站工具链） |
| `temp_newData/CTF知识库/99_维护工具/test_catalog.py` | 158 | Y | Verify generated catalog and run a guarded metadata-only rebuild. | 未发现引用（静态扫描） | 保留（外部导入/维护管线，不纳入本站工具链） |
| `temp_newData/CTF知识库/99_维护工具/verify_chinese_package.py` | 53 | Y | Verify a fresh isolated extraction using only authored entry points. | 静态扫描命中：temp_newData/CTF知识库/99_维护工具/package_chinese_kb.py | 保留（外部导入/维护管线，不纳入本站工具链） |
| `temp_newData/CTF知识库/99_维护工具/write_official_overview.py` | 63 | Y | Generate an honest inventory from acquisition and compilation metadata. | 静态扫描命中：temp_newData/CTF知识库/99_维护工具/package_chinese_kb.py | 保留（外部导入/维护管线，不纳入本站工具链） |


### 10.5 机器可读清单

`work/script_inventory/inventory.json` 覆盖三处脚本，共 **181** 条：

| scope | 条目 | 行数 |
|---|---:|---:|
| `tool` | 62 | 14,195 |
| `work` | 82 | 6,995 |
| `temp_newData` | 37 | 4,562 |
| **合计** | **181** | **25,752** |

每条字段：`path` / `scope`(tool|work|temp_newData) / `lines` / `has_main` /
`purpose` / `refs` / `suggestion`。JSON 顶层为数组，`python -c "json.load(...)"`
可解析；`work/` 虽在 `.gitignore` 中，本清单按用户明确要求强制登记并提交。
清单不含模型、索引、附件正文或任何密钥。

> 口径说明：清单的 `tool` 范围比第 3/4 节宽，额外包含 `webapp/src` 的
> 前端源码与构建配置，所以 14,195 行不能与第 2 节的工具链行数直接相加。

### 10.6 复核命令

```powershell
.\.venv\Scripts\python.exe -c "import json; d=json.load(open('work/script_inventory/inventory.json',encoding='utf-8')); print(len(d))"
# 期望输出 181

git status --porcelain
# 确认只新增 docs/TOOLS_INVENTORY.md 与 work/script_inventory/inventory.json，
# 不改动第 9 节列出的 8 个 P2 WIP 文件
```

---

## 11. P4 只读脚本工具库（2026-10-28）

P4 新增 `tools/scripts/`，把根目录/`work/` 的临时探针收敛为可测试的只读工具。
旧探针仍保留原样（`.gitignore` 的 `/_*.py`），未删除、未移动用户文件。

| 脚本 | 用途 | 输入 | 输出 |
|---|---|---|---|
| `tools/scripts/_shared.py` | stdio/JSON/整数解析公共函数 | — | 被其他脚本 import |
| `tools/scripts/crypto/rsa_factor_probe.py` | 小因子试除、位长、余因子素性 | `--n/--n-file`、`--limit`、`--check-prime` | `n_bits`、`small_factors`、`cofactor*` |
| `tools/scripts/forensics/zip_inspect.py` | ZIP/JAR 清单、顶层目录、名称/内容检索 | `--zip`、`--top`、`--grep`、`--max-bytes` | `entry_count`、`top_dirs`、`name_hits`、`content_hits` |
| `tools/scripts/misc/filter_probe.py` | 黑名单静态比对（不执行输入） | `--blacklist(-file)`、`--payload(-file)` | `hit_count`、`hits`、`executed=false` |

共同约定：只读、不写盘、不联网、不执行输入、不自动执行、不做武器化；
均支持 `--json`。详细说明见 `tools/scripts/README.md`，测试见
`tests/test_scripts.py`（3 个脚本均用临时数据实跑）。
