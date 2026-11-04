# 迁移到其它盘 / 目录

查询环境随项目目录移动。使用 `runtime/python-portable` 时，不依赖原电脑安装的 Python。
移动时保留应用源码、网页 dist、kb、index、config.toml 和 runtime；语义查询还需要项目内已有的 BGE 编码模型。

## 需要一起搬的东西

| 路径 | 大小 | 是否必需 | 说明 |
|---|---|---|---|
| `knowledgeBase/` | 按当前目录计 | ✅ | 主体，含 kb / index / runtime；.venv 为开发环境，可保留 |
| `knowledgeBase/../tools/` | ~80 MB | ⭕ | 便携取证工具（exiftool / foremost / binwalk） |

`tools/` 是 `knowledgeBase` 的**同级目录**。目录布局应该长这样：

```
<任意盘符>:/
└── CTFfiles/            <- 名字随便
    ├── knowledgeBase/   <- 项目主体
    └── tools/           <- 便携工具
        ├── exiftool-13.27_64/
        ├── foremost/
        └── binwalk-2.3.1/
```

不搬 `tools/` 也能用，只是 `exiftool` / `foremost` / `binwalk` 会被标记为缺失，
系统会自动回退到纯 Python 实现（`tools/agent/carve.py`），功能少一些但核心流程照常。

## 搬完后怎么验证

```powershell
cd <新路径>/knowledgeBase
.\start.ps1 -CheckEnvironment
.\start.ps1 -NoModel
```

环境检查中的 executable、prefix、base_prefix 应指向新目录。网页能搜索、读文档和保存题目记录。
需要切换解释器时使用 `-PythonExe`、当前终端的 `KB_PYTHON`，或 config.toml 的 `[runtime].python`。

## 路径是怎么定位的（无需手动改配置）

**全部基于脚本自身位置推算，不写死盘符。** 搬目录后自动适配：

| 组件 | 定位方式 |
|---|---|
| `kb.config.ROOT` | `Path(__file__).parents[2]` |
| `agent.tools.ROOT` | 同上 |
| `agent.recon.ROOT` | 同上 |
| 便携工具目录 | 按优先级探测（见下） |
| Ollama 模型文件 | `setup_ollama.ps1` 里的 `$Root` |

### 便携工具目录的探测顺序

1. 环境变量 `KB_TOOLS_DIR`
2. `<项目根>/tools/_bin`
3. `<项目根的上一级>/tools` ← 默认布局
4. `E:\CTF\tools`（历史位置兜底）

想放到别处就设环境变量：

```powershell
$env:KB_TOOLS_DIR = "D:\my-tools"
```

## 便携 Python 与开发环境

`runtime/python-portable` 是独立 Python 3.13.17，运行依赖也在其中。搬项目时保留完整目录，不要只复制 python.exe。
默认自动选用它；`start.ps1 -CheckEnvironment -PythonExe '.venv/Scripts/python.exe'` 可以检查旧开发环境。

虚拟环境依赖创建它的 Python。R0 接手时的旧环境指向已缺失的 `C:/Python314`，
已保留到 `backup/.venv-before-r0-20261105`。开发环境现用 Python 3.12。
换机或基础 Python 位置变化后，保留旧环境，再按下面方式重建：

```powershell
cd <新路径>/knowledgeBase
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -X utf8 -m pip install --cache-dir .cache/pip -r requirements-dev.txt
```

这组依赖用于离线查询、方法脚本和回归测试，不安装或下载生成模型。
备份运行 `.\backup.ps1`；恢复使用 `-Restore <压缩包> -Destination <新空目录>`。
知识库、方法脚本、索引、工作区、反馈及上传附件都会保存，旧备份也会保留。

## Ollama 模型

Ollama 用的是**项目内**的便携版（`models/ollama-server/ollama.exe`），
模型也是本地 GGUF 直接导入，整个 `models/` 目录搬走即可。

前提是 Ollama 服务已启动：

```powershell
.\tools\setup_ollama.ps1          # 启动 + 导入模型
.\tools\setup_ollama.ps1 -Stop    # 停止
```

## 已知的小坑

1. **索引不用重建**。`index/` 里是 SQLite 库，内部存的是相对路径，
   搬盘后仍然可用（实测 `doctor` 全 OK）。

2. **`work/` 里的绝对路径**。之前跑过的输出 JSON 里可能残留旧盘符，
   这些只是历史记录，不影响使用，可随时清空 `work/_probe/`。

3. **网络路径（UNC）慎用**。如 `\\NAS\share\`，SQLite 和 venv 在部分场景下会出问题，
   建议先在本机盘验证。

4. **文件系统**。FAT32 单文件上限 4GB，而 `models/` 里的 GGUF 有 4.7GB，
   所以目标盘必须是 **NTFS / exFAT**。
