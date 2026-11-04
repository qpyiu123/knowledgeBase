# CTF 知识库

离线查询编程文档、CTF 方法、题型和配套代码。关键词结果先显示，语义检索与模型解释按需使用。

2026-11-05：索引 1915 篇，包含 54 张方法卡；项目内提供独立 Python 3.13.17，也可切换到自己的 Python 环境。

---

## 一键启动（推荐）

```powershell
.\start.ps1 -NoModel
```

使用项目内 Python 启动查询界面并打开浏览器，不启动生成模型。正常运行无需安装系统 Python。

```powershell
.\start.ps1 -Status     # 看状态
.\start.ps1 -Stop -NoModel  # 停止查询服务
.\start.ps1             # 同时启动原有 Ollama 服务
```

界面是**搜索引擎样式**：输入题面特征 → 出结果卡片 → 卡片可「看全文」「问模型」。
地址 http://127.0.0.1:8765/

## Python 环境选择

```powershell
.\start.ps1 -CheckEnvironment                    # 查看实际路径、版本与依赖
.\start.ps1 -NoModel -PythonExe '.venv/Scripts/python.exe'
$env:KB_PYTHON = 'D:/my-python/python.exe'         # 仅当前终端生效
```

选择顺序：`-PythonExe` → `KB_PYTHON` → `config.toml` 的 `[runtime].python` → 自动选择。
自动模式优先 `runtime/python-portable/python.exe`，其次项目 `.venv`。配置路径相对项目目录解析；指定的环境有错时会提示具体原因。

长期使用某个环境时，修改 `config.toml` 已有的 `[runtime]`：

```toml
[runtime]
python = "auto"  # 也可填 ".venv/Scripts/python.exe" 或完整路径
```

便携运行文件不提交 Git。从源码准备环境时，复用已有的官方嵌入 ZIP 和兼容 wheel：

```powershell
.\.venv/Scripts/python.exe tools/prepare_portable_python.py --archive <Python-3.13-embed-amd64.zip> --wheel-dir <已有wheel目录> --install-deps
```

该命令只向项目 `runtime/` 安装运行依赖，不下载模型，不改全局 Python。已有完整 wheel 时加 `--offline`。
移动硬盘使用方法见 [迁移说明](MOVING.md)，准备与验收记录见 [R1.3 运行环境记录](docs/R1.3-运行环境记录.md)。

---

## 命令行快速开始

```powershell
# 1. 激活（当前 PowerShell 会话）
. .\tools\activate.ps1

# 2. 建/更新索引（约 45 秒）
kb index

# 3. 模糊检索 —— 直接拿题面特征去搜
kb search "题目给了同一个n，e1=3 e2=65537，两组密文"
kb search "图片里好像藏了东西，文件大小比看起来大"
kb search "checksec 有canary 但无PIE"

# 4. 让本地模型给思路（检索 + 生成）
kb ask "附件是 pyc，代码看不懂像被花指令打乱，还检测调试器"

# 5. 完全没思路时：侦察附件 + 给方向
kb hint 附件.png

# 6. 环境自检
kb doctor
```

第一次用：`python tools\setup_env.ps1` 装依赖和模型，`.\start.ps1` 启动服务。

---

## 知识库覆盖

| 方向 | 篇数 | 代表性条目 |
|---|---|---|
| **Web** | 42 | SQLi/WAF 绕过、PHP/Java/Pickle/PHAR 反序列化、Log4Shell、Shiro-550、Fastjson、JWT、SSRF、SSTI、XXE、Spring4Shell + 4 篇 CVE 专题 |
| **Pwn** | 36 | ret2text/libc/syscall/SROP/CSU、canary 绕过、格式化字符串、栈迁移、tcache/fastbin/unsortedbin/House of Force、FSOP、内核 pwn、seccomp ORW、CVE-2021-4034/Dirty Pipe |
| **Crypto** | 25 | RSA 共模/小e/维纳/广播/Fermat/dp 泄露/Coppersmith/Padding Oracle、AES CBC/ECB、LCG、LFSR+BM、ECC 小阶、哈希长度扩展、MT19937、格攻击 LLL |
| **Reverse** | 30 | 工具链、反调试、UPX 脱壳、VM 保护、花指令/平坦化、angr、z3、Golang/Rust/pyc/WASM/Electron/.NET |
| **Misc** | 28 | 文件头、PNG/JPG/LSB 隐写、ZIP 伪加密、二维码、编码套娃、音频隐写、pyjail、Lua/bash 沙箱逃逸、花指令 |
| **Forensics** | 22 | pcap、TCP 重组、HTTP2/QUIC、磁盘/内存取证、Volatility、注册表 EVTX、DNS/ICMP 隧道、文件雕刻 |
| **Blockchain** | 6 | 重入、整数溢出、权限/初始化、Solana、存储槽、SWC 汇总 |
| **Mobile** | 14 | apktool/jadx、Frida Hook、SSL Pinning 绕过、iOS、签名校验 |
| **Hardware** | 14 | 逻辑分析仪、UART/JTAG/SWD、侧信道、固件分析、CAN、RFID/NFC |
| **OSINT** | 12 | 地理定位、社媒溯源、域名/证书、图片反查、Google dork |
| **AI 安全** | 12 | 提示词注入、越狱、RAG 投毒、对抗样本、Agent 工具滥用 |

每篇都带 **`signals` 字段**（题面里会出现的特征短语 5~10 条），这是做题时反查的真正入口。

---

## 命令一览

| 命令 | 说明 |
|---|---|
| `kb index` | 重建 FTS + 向量索引 |
| `kb search "查询"` | 双路召回 + RRF 融合 |
| `kb search "查询" --fts-only` | 只走关键词（最快，~50ms） |
| `kb search "查询" --vec-only` | 只走语义向量 |
| `kb search "查询" -c crypto` | 限定方向 |
| `kb search "查询" --mode and` | 严格模式（所有词都要命中） |
| `kb ask "问题"` | 检索 + 模型作答 |
| `kb ask "问题" --stream` | 流式输出 |
| `kb ask "问题" --backend llama_cpp` | 不启动 Ollama 直连 GGUF |
| `kb show crypto/rsa-common-modulus-attack` | 查看条目 |
| `kb cat crypto` | 列出一个方向全部条目 |
| `kb lint` | 校验所有 md 的 front-matter |
| `kb stats` / `kb bench` / `kb doctor` | 索引统计 / 测速 / 环境自检 |

---

## 目录结构

```
knowledgeBase/
├── config.toml             # 全部可调参数
├── kb/                     # 知识库正文（Markdown + YAML front-matter）
│   ├── _index.md           # 自动生成的导航页（python tools/gen_index.py）
│   ├── {misc,crypto,reverse,pwn,web,forensics,
│   │     mobile,blockchain,hardware,osint,ai}/
├── index/                  # 索引（可删，重建即可）
│   ├── fts.db              # SQLite FTS5
│   └── vectors.db          # sqlite-vec 向量索引
├── models/                 # 本地模型（已加入 .gitignore）
│   ├── bge-small-zh-v1.5-onnx/   # 嵌入模型（ONNX，~23MB int8）
│   └── gguf/                     # 生成模型 GGUF
├── tools/
│   ├── cli.py              # 命令行入口
│   ├── kbcheck.py          # 知识库质量自检
│   ├── gen_index.py        # 生成 _index.md
│   ├── model_check.py      # 模型与环境核对
│   ├── fetch_models.py     # 下载模型（幂等，支持镜像）
│   ├── setup_env.ps1       # venv + 依赖 + 模型
│   ├── setup_ollama.ps1    # 启动 Ollama 并导入本地 GGUF
│   ├── agent/              # 轻量 agent（Web UI + 3 个工具）
│   │   ├── server.py       # HTTP 服务 + 内嵌前端
│   │   ├── loop.py         # ReAct 循环 + 小模型兜底解析
│   │   ├── tools.py        # search_kb / read_file / write_file
│   │   └── start.py        # 一键启动
│   └── kb/                 # 检索引擎
│       ├── parser.py       # front-matter / 分块 / 查询分词
│       ├── fts.py          # FTS5（含 CJK 二元切分）
│       ├── vectors.py      # 向量索引（sqlite-vec / numpy 降级）
│       ├── embedder.py     # 嵌入后端（ONNX 优先）
│       ├── npbert.py       # 纯 NumPy BERT 前向（兜底，精度有瑕疵）
│       ├── fusion.py       # RRF 融合
│       ├── llm.py          # Ollama / llama.cpp 双后端
│       └── rag.py          # 检索增强问答
└── tests/                  # 107 个单元/集成测试
```

---

## 知识库文件格式

每道题/每个技法一个 `.md`，**必须**带 YAML front-matter：

```markdown
---
title: 弱 RSA 共模攻击
category: crypto
tags: [rsa, 共模攻击, 扩展欧几里得]
signals: [n 相同, e 不同, 两组密文, 一个明文加密两次, 题目给了 c1 c2 e1 e2]
difficulty: easy
source: "XCTF / CTF-Wiki"
tools: [python, gmpy2, SageMath]
---

## 一、识别信号（题面长什么样）
## 二、原理
## 三、解题步骤
## 四、可直接运行的脚本
## 五、常见坑 / 变体
## 六、参考来源
```

| 字段 | 必需 | 说明 |
|---|---|---|
| `title` | ✔ | 条目标题 |
| `category` | ✔ | `misc`/`crypto`/`reverse`/`pwn`/`web`/`forensics`/`mobile`/`blockchain`/`hardware`/`osint`/`ai` |
| `signals` | ✔ | **最重要**：题面里会出现的特征短语 |
| `tags` / `difficulty` / `source` / `tools` | 建议 | 辅助检索与筛选 |

**写新条目的三条建议**

1. `signals` 写"你眼睛看到的东西"，不是概括。写「给了 libc.so.6」而不是「有 libc」。
2. 脚本要能跑，用占位符标出需替换处（`OFFSET`、`TARGET`）。
3. 记录坑点，那是最省时间的部分。

写完执行：

```powershell
python tools\kbcheck.py        # 质量报告（重复标题、死链、空壳、覆盖度）
kb index                       # 更新索引
python tools\gen_index.py      # 更新导航页
```

---

## 检索是怎么工作的

```
查询
 ├─ 分词：英文整词 + 技术词子串 + 中文 2-gram
 ├─ FTS5：中文先切成二元组写入索引（否则中文永远 0 命中）
 │        列权重 title 12 / signals 9 / tags 6 / path 3 / body 1
 │        命中不足时退到 AND 模式，再退到 LIKE 子串
 └─ 向量：bge-small-zh（512 维，ONNX）语义召回
         ↓
       RRF 融合：score = Σ 1/(60 + rank)
         ↓
      Top-K → 拼接上下文 → 本地模型
```

**为什么中文要特殊处理**：SQLite FTS5 的 `unicode61` 分词器不切中文，整句中文会被当成单个 token，导致任何中文查询都是 0 命中。入库时把中文串切成「共模 模攻 攻击」这样的二元组，查询时同样切分，BM25 才能正常工作。

---

## 实测性能

### 推理（RTX 3050 Ti 4GB）

| 配置 | 速度 | 显存峰值 |
|---|---|---|
| **Ollama + num_gpu=16（推荐）** | **18.2 tok/s** | — |
| Ollama 默认自动分配 | 14~16 tok/s | 3662 / 4096 MB |
| Ollama + num_gpu=14 | 14.0~15.0 tok/s | 3752 MB |
| Ollama + num_gpu=20 | 3.9 tok/s ⚠️ | 3937 MB（超显存掉回 CPU） |
| Ollama + num_gpu=0（纯 CPU） | 7.8~9.7 tok/s | 1562 MB |
| llama-cpp-python 直载 | 9.6 tok/s | 0（pip wheel 是 CPU-only） |

> **4GB 显存的甜点区是 num_gpu=14~16**。超过 18 层就超显存，Ollama 会把剩余的层退回 CPU，速度反而暴跌。

### 嵌入

| 方案 | 速度 | 状态 |
|---|---|---|
| ONNX int8（当前默认） | **~1.3 ms/条** | 采用 |
| ONNX fp32 | ~2 ms/条 | 可用 |
| 纯 NumPy BERT | ~85 ms/条 | 仅兜底，精度有瑕疵（见下） |

### 索引重建

| 嵌入后端 | 耗时（1390 块） |
|---|---|
| ONNX | **43.5 秒** |
| 纯 NumPy | 232 秒 |

---

## 踩过的坑（重要）

这些都是实测出来的，值得记住：

1. **FTS5 的 `MATCH` 在 JOIN 后会失效**。`SELECT ... FROM chunks JOIN docs d ON ... WHERE chunks MATCH ?` 会永远返回 0 行——FTS5 把 `MATCH` 当成了普通比较。必须先只用 `chunks` 过滤出 rowid，再回连。
2. **子查询里 `rowid AS rid` 会变成 NULL**。FTS5 的 rowid 是未声明列，必须写 `chunks.rowid AS rid`。
3. **`bm25()` 的参数个数必须等于列数**（本表 6 列）。传错个数抛 `OperationalError`，若被 `except` 吞掉就表现为"永远 0 命中"。
4. **`x @ W.T` 比预转置慢 10 倍**。`W.T` 是 F-contiguous 视图，OpenBLAS 每次都要重新打包权重。
5. **BLAS 线程数要跟着"权重是否预转置"走**。没预转置时 1 线程最快；预转置后 12 线程快 1.8 倍。
6. **手写 NumPy BERT 前向精度不够**。它能输出 512 维归一化向量，但同义/无关文本的余弦间隔只有 0.03（ONNX 是 0.11~0.13），语义检索基本失效。因此默认只走 ONNX，NumPy 版需 `KB_ALLOW_NUMPY_EMBED=1` 显式启用。
7. **ONNX 编码必须补上 `[CLS]`/`[SEP]`**。按 tokenizer 输出长度定宽会漏掉特殊 token，导致批量与单条编码不一致。
8. **`config.toml` 必须显式 UTF-8 解码**。Windows 上普通 `open()` 走 GBK，中文前缀会静默变乱码并失效。
9. **Ollama 模型名不能含 `.`**。`qwen2.5-coder-7b:local` 能 `create` 成功但 `generate` 报 `not found`。已改用 `qwen25-coder-7b-local`，且 `llm.py` 会自动按 name/digest 探测出真正可用的标识。

---

## 模型

| 用途 | 模型 | 大小 |
|---|---|---|
| 嵌入 | `BAAI/bge-small-zh-v1.5`（ONNX int8） | 23 MB |
| 生成 | `Qwen2.5-Coder-7B-Instruct` Q4_K_M | 4.47 GB |
| 备用 | `Qwen2.5-Coder-3B-Instruct` Q4_K_M | 1.84 GB |

```powershell
python tools\setup_env.ps1        # 建 venv + 装依赖 + 下模型
.\tools\setup_ollama.ps1          # 启动 Ollama 并导入本地 GGUF
python tools\model_check.py       # 核对
```

---

## 常见问题

**Q: `kb ask` 报 "Ollama 里找不到匹配的模型"**
先 `kb doctor` 看解析到的实际 ID。修改 `config.toml` 的 `[ollama] model`，或直接写 digest（`ollama list` 可见）。

**Q: 不想启动 Ollama**
`kb ask "..." --backend llama_cpp`（纯 CPU，约 9.6 tok/s），或把 `config.toml` 的 `llm.backend` 改成 `llama_cpp`。

**Q: 中文搜不到东西**
先 `kb index`，再 `kb lint` 看有没有缺 `signals` 的条目。

**Q: 想加快检索**
`kb search "..." --fts-only` 只走关键词，约 50ms。

---

## Agent UI（浏览器里带工具对话）

除了 `kb ask` 的单次问答，还带一个轻量 agent：它**真的会调用工具**，能查知识库、读文件、写脚本。

```powershell
python tools\agent\start.py      # 自动启动并打开 http://127.0.0.1:8765
```

界面里能看到完整过程：思考 → 调用 `search_kb` → 读取条目全文 → 给出脚本。

**三个工具，刻意做得很少**（工具定义越少，6K 上下文留给内容越多）：

| 工具 | 作用 |
|---|---|
| `search_kb(query, category?)` | 查知识库，返回标题+路径+要点摘要 |
| `read_file(path, max_lines?)` | 读知识库条目或 `work/` 里的文件 |
| `write_file(path, content)` | 写脚本到 `work/` |

**安全边界**：读写都被限制在 `work/`（读额外允许 `kb/`、`index/` 只读），拒绝 `..` 穿越和绝对路径越界；二进制扩展名不可读写。

### 让本地小模型可靠调用工具的五道补丁

用 4GB 显存跑 7B 时，原生 function calling 基本不可用。下面每一条都是实测出来的：

| 现象 | 根因 | 补法 |
|---|---|---|
| 工具调用被当**普通文本**吐出来 | 小模型不走 `tool_calls` 通道 | 从 ```json 块 / 裸 JSON 里捞，兼容 `name`/`tool`/`function` 三种键 |
| 回传结果时 **400**：`can't find closing '}'` | **Ollama 要 `arguments` 是对象，OpenAI 规范要字符串** | 回传前把字符串反序列化成对象 |
| 调用写成 **Python 函数语法**<br>`write_file("work/exp.py", ...)` | 7B 把调用当成"要展示的代码" | `_parse_python_call()` 按括号匹配解析（content 里可能含 `print(1)`） |
| 一上来就**反问**「请提供具体参数」 | 小模型倾向澄清而非行动 | 首轮没用工具就注入强制指令，逼它调 `search_kb` |
| 写完文件后**重复写**同一文件直到步数耗尽 | 模型不会判断"已完成" | 同工具同参数去重 + 首次重复即用已有结果自动收尾 |

另外两个隐蔽 bug：

- 模型传来的 `content` 常是**双重转义**（`\\n` 而非 `\n`），直接落盘会把整段脚本写成一行 → `_unescape_body()` 还原。
- 模型会丢掉 `kb/` 前缀，读文件失败后**凭记忆编造错误公式**（看起来完全像对的）→ `_fuzzy_find()` 按文件名在 `kb/` 下找回。

实测一次完整任务约 **40 秒**：查知识库 1.0s → 读全文 0.005s → 写脚本 0.014s → 收尾。

### 局限（如实说明）

本地 7B 在 6K 上下文下**仍会偶发不稳定**：可能多绕一步、或把示例数据当成真实数据。它适合「查知识库 + 生成脚本模板」，不适合长链路任务。需要稳定 agent 能力时，用 DSH 的 DeepSeek 模型。

---

## 测试

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q   # 107 个测试
python tools\kbcheck.py                          # 知识库质量（当前 241 篇，0 问题）
python tools\model_check.py                      # 模型与环境
```
