---
title: 工具矩阵与 WSL 常用命令（CyberChef/StegSolve/hex 工具箱）
category: misc
tags: [工具, wsl, cyberchef, binwalk, 环境搭建, 命令速查]
signals: [Windows 上没有 Linux 工具, 不想装虚拟机, 需要一次性环境, binwalk 报错, 命令找不到, 需要批量处理文件, 需要快速试多个解包器]
difficulty: easy
source: "CyberChef 官方 / Kali Linux 文档 / WSL 官方文档 / binwalk 与 foremost 文档"
tools: [wsl, cyberchef, binwalk, foremost, exiftool, zsteg, steghide, 010editor]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 队友发来 `steghide` 命令，你在 Windows 上执行提示"不是内部或外部命令"。
- `binwalk` 报 `OSError: [Errno 8] Exec format error` 或权限错误。
- 需要同时跑 `exiftool`、`zsteg`、`foremost`、`steghide`、`tesseract` 等一堆 Linux 工具。
- 题目要求批量处理 500 张图，手工点不动。
- 想把 Windows 的附件目录**直接在 Linux 环境里访问**。

## 二、原理

CTF Misc 工具生态基本是 **Linux 优先**（apt 一键装），而 Windows 上大量工具要么没有移植、要么版本老旧。**WSL2 是最好的折中**：

- WSL 里 `/mnt/e/CTF/...` 直接映射 Windows 盘符，不用来回拷贝。
- `wsl --cd` 可以从 Windows 端直接进入附件目录执行 Linux 命令。
- 图形工具（StegSolve/Audacity）留在 Windows 侧，命令行工具走 WSL，两条腿走路。

**CyberChef**（浏览器单文件应用）是"任何编码/加解密/格式转换"的瑞士军刀，`Magic` 操作能自动识别几十种变换，适合作为第一站。**010 Editor** 负责二进制手工修补，模板（.bt）能解析 PNG/ZIP/PDF 结构。

## 三、操作步骤

1. **装 WSL**：`wsl --install -d Ubuntu`，重启后设置用户名密码。
2. **一把梭装工具**（见第四节 `install-all`）。
3. **配置 Windows/WSL 互访**：`ln -s /mnt/e/CTF ~/ctf`。
4. **日常工作流**：WSL 里跑 `file/binwalk/zsteg/exiftool`，Windows 里开 StegSolve/CyberChef/Audacity。
5. **批量脚本**：`find + xargs -P` 并行跑，或写 Python 调 subprocess。
6. **别忘了 Windows 侧工具**：`winget install` 能装 `7zip`、`exiftool`、`ffmpeg`、`imagemagick`、`python`、`ghidra`。

## 四、命令/脚本

### WSL 安装与系统工具

```powershell
wsl --install -d Ubuntu                     # 首次安装
wsl --list --verbose                        # 查看发行版与版本
wsl --set-default-version 2
wsl --cd E:\CTF\knowledgeBase               # 直接进 Windows 目录
wsl -e bash -lc "cd /mnt/e/CTF && ls"
```

```bash
# 一次性装齐 Misc 常见工具（Ubuntu/Debian）
sudo apt update
sudo apt install -y file binwalk foremost foremost scalpel exiftool \
    pngcheck p7zip-full unzip zip fcrackzip steghide outguess \
    zbarimg-tools zbar-tools imagemagick ffmpeg sox audacity \
    tesseract-ocr tesseract-ocr-chi-sim python3-pip git gcc make \
    xxd hexedit qpdf pdfid poppler-utils libimage-exiftool-perl
```

```bash
# zsteg / stegseek / bkcrack / crc-tools 需要额外装
gem install zsteg
wget -q https://github.com/RickdeJager/stegseek/releases/download/v0.6/stegseek_0.6-1.deb \
  && sudo dpkg -i stegseek_0.6-1.deb
git clone https://github.com/kimci86/bkcrack && cd bkcrack && \
  cmake -S . -B build && cmake --build build && sudo cp build/bkcrack /usr/local/bin/
pip install pycryptodome Pillow numpy python-magic pyzbar
```

### 常用检查链（复制即用）

```bash
# 万能第一步
f="$1"; file "$f"; exiftool -a -u -g1 "$f" | head -40; binwalk "$f"
# 分离
binwalk -e --run-as=root "$f" && ls _$(basename "$f").extracted 2>/dev/null
foremost -i "$f" -o "out_$(basename "$f")"
# 文本线索
strings -n 6 -e l "$f" | grep -iE 'flag|ctf|pass|key' | head
strings -n 6 -e b "$f" | head          # UTF-16
# 压缩包
7z l "$f"; unzip -l "$f"; zipdetails "$f" | head -30
# 文档
pdfinfo "$f"; pdfdetach -list "$f"; 7z x -y -o"ext_$f" "$f"
# 图片
identify -verbose "$f" | head -30; pngcheck -vtp7 "$f"
# 音频
ffprobe -v error -show_streams "$f"
```

### 批量并行处理

```bash
find . -maxdepth 1 -type f -name '*.png' -print0 | \
  xargs -0 -P 8 -I{} sh -c 'echo "== {}"; zsteg -a "{}" 2>/dev/null | head -3'
# 批量 extract 到各自目录
for f in *.png; do binwalk -e --run-as=root "$f" >/dev/null 2>&1; done
ls -d _*.extracted 2>/dev/null
```

### Cygwin/Git-Bash 替代（不想装 WSL 时）

```bash
# Git for Windows 自带 GNU 工具，但没有 binwalk/zsteg
# winget 装原生 Windows 版本
winget install 7zip.7zip
winget install exiftool.exiftool
winget install Gyan.FFmpeg
winget install ImageMagick.ImageMagick
winget install Python.Python.3.12
winget search binwalk          # 没有官方包时走 python: pip install binwalk
pip install binwalk
```

### CyberChef 本地部署（离线可用）

```bash
# 下载单文件版，浏览器直接打开，无需联网
Invoke-WebRequest -Uri https://gchq.github.io/CyberChef/ -OutFile E:\CTF\tools\cyberchef.html
# 或从 GitHub Release 下载 CyberChef_v10.*.zip，解压后打开 index.html
```

常用配方（可直接粘贴到 `Recipe` 区）：

```
"Magic"  (Intensive mode)
"From Base64" -> "Raw Inflate" -> "Detect File Type"
"Strings" (min length 6, UTF-16LE) -> "Extract URLs"
"Render Image"  (把 data:image base64 直接可视化)
"XOR Brute Force" (key length 1, crib "flag{")
```

### 010 Editor / StegSolve 安装要点

```powershell
# Java 工具（StegSolve / ZipCenOp）
winget install Oracle.JDK.21
java -jar E:\CTF\tools\stegsolve.jar
# 010 Editor 装官方安装包后，Scripts 目录下的 PNG.bt / ZIP.bt 模板可直接运行
```

## 五、常见坑 / 变体

- **`binwalk -e` 报 `--run-as` 错误**：新版 binwalk 默认拒绝 root 运行，加 `--run-as=root`。
- **WSL 里访问 `E:\` 路径**：要写成 `/mnt/e/...`，Windows 反斜杠会解析失败。
- **文件权限**：`/mnt/e` 下的文件默认 `777`，`chmod` 无效，`steghide` 等对权限敏感的工具可能报错——把文件 `cp` 到 `~/` 再处理。
- **`zsteg` 装不上**：它依赖 Ruby，`apt install ruby` 后再 `gem install zsteg`；也可以直接用 Aperi'Solve 在线跑。
- **编码问题**：Windows 控制台默认 GBK，`chcp 65001` 或在 WSL 内操作，避免中文输出乱码。
- **镜像过大**：WSL 的 ext4.vhdx 只增不减，`wsl --shutdown` 后 `Optimize-VHD` 压缩。

## 六、参考来源

- [CyberChef 在线版与源码仓库](https://github.com/gchq/CyberChef)
- [WSL 官方安装文档 (Microsoft Learn)](https://learn.microsoft.com/windows/wsl/install)
- [binwalk 官方仓库与用法](https://github.com/ReFirmLabs/binwalk)
- [foremost 文件雕刻工具](https://foremost.sourceforge.net/)
- [Aperi'Solve 速查表（工具与命令对照）](https://www.aperisolve.com/cheatsheet)
- [exiftool 官方站](https://exiftool.org/)
