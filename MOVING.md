# 迁移到其它盘 / 目录

本项目**整体可移动**，直接复制整个 `knowledgeBase` 目录即可，不需要重装依赖。

## 需要一起搬的东西

| 路径 | 大小 | 是否必需 | 说明 |
|---|---|---|---|
| `knowledgeBase/` | ~13.3 GB | ✅ | 主体，含 kb / index / models / .venv |
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
.\.venv\Scripts\python.exe tools\cli.py doctor
```

期望输出里 `根目录` 指向新路径，且 `FTS 索引` / `向量索引` 都是 `[OK]`。

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

## venv 的注意事项

`.venv/pyvenv.cfg` 里记录的是 **Python 解释器位置**（`C:\Python314`），不是项目路径，
所以直接复制 venv 到别的盘**仍然可用**（已实测）。

但有两种情况需要重建：

- 换了 Python 版本或 Python 安装位置
- 从别的电脑复制过来

重建命令：

```powershell
cd <新路径>/knowledgeBase
C:\Python314\python.exe -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

> binwalk 需要用源码目录安装，且依赖一个 `imp` 兼容层（Python 3.12+ 已移除该模块）：
> ```powershell
> .\.venv\Scripts\python.exe -m pip install ..\tools\binwalk-2.3.1 --no-build-isolation
> ```
> `imp.py` 兼容层见 `.venv/Lib/site-packages/imp.py`，重建 venv 后需要重新放一份。

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
