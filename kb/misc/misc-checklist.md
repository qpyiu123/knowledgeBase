---
title: 杂项通用检查清单（file → strings → binwalk → 分离 → 分析）
category: misc
tags: [checklist, 思路, 排查顺序, misc, 方法论, 流程图]
signals: [附件不知道从哪下手, 题目类型没写, 试了几个工具都没出, 时间不够想按套路走, 队友交接需要统一流程, 复盘时要写解题记录]
difficulty: easy
source: "Aperi'Solve 方法论 / CTF-Wiki 杂项 / StegOnline checklist"
tools: [file, strings, binwalk, foremost, exiftool, aperisolve, cyberchef]
updated: 2026-10-22
relates_to: [ai/ai-ctf-checklist.md, osint/osint-checklist.md]
---

## 一、识别信号（题面长什么样）

- 附件类型很杂（一个 `.bin`、一个 `.dat`、一张图、一个压缩包），题面只有一句话。
- 打开发现「什么都没提示」，只能靠通用套路。
- 试了两三个工具都没出结果，需要按标准顺序复盘一遍。
- 赛时多人协作，需要一个**统一的检查顺序**避免重复劳动。

## 二、原理

Misc 的绝大多数题都遵循**同一套数据流**：

```
拿到文件
  ├─ 1. 确定真实类型（file / 魔数）
  ├─ 2. 找明文线索（strings / exiftool / 元数据）
  ├─ 3. 分离内嵌（binwalk / foremost / unzip）
  ├─ 4. 按类型分支（图片/音频/文档/压缩包/流量/可执行）
  ├─ 5. 解码套娃（CyberChef / 手工脚本）
  └─ 6. 失败则回到 1，但换视角（结构、元数据、行为、侧信道）
```

**关键思想**：前 3 步几乎零成本、命中率最高，**必须当成肌肉记忆**；第 4 步开始才需要判断分支；第 6 步是"没出结果"时的保底——绝大多数卡题是**漏了一个视角**（例如没想到查 alpha 通道、没想到查 EXIF 缩略图、没想到看文件尾部）。

## 三、操作步骤

1. **第 0 分钟**：`file` + `xxd | head` + `ls -la`（看大小与时间戳）。
2. **第 1 分钟**：`exiftool -a -u -g1` + `strings -n 6 | grep -i ctf`。
3. **第 2 分钟**：`binwalk`（有望就 `-e`）+ `unzip -l` + `foremost`。
4. **第 5 分钟**：按类型进分支（见第四节表格）。
5. **第 20 分钟**：仍无进展 → 换视角清单（第五节）。
6. **全过程**：把每一步输出去写进 `notes.txt`，便于交接与复盘。

## 四、命令/脚本

### 一键体检脚本（bash）

```bash
#!/usr/bin/env bash
# triage.sh —— misc 通用体检，输出到 triage_<file>.txt
set -u
f="$1"; out="triage_$(basename "$f").txt"
exec > >(tee "$out") 2>&1
echo "==== [0] BASIC ===="
ls -la "$f"; sha256sum "$f"; date
echo "==== [1] TYPE ===="
file "$f"; xxd -l 64 "$f"
echo "==== [2] META ===="
exiftool -a -u -g1 "$f" 2>/dev/null | head -50
echo "==== [3] STRINGS ===="
strings -n 6 "$f" | head -40
strings -n 6 -e l "$f" | grep -iE 'flag|ctf|pass|key|secret' | head -20
echo "==== [4] EMBED ===="
binwalk "$f" 2>/dev/null | head -30
unzip -l "$f" 2>/dev/null | head -20
echo "==== [5] TAIL ===="
tail -c 64 "$f" | xxd
echo "==== DONE: $out ===="
```

```bash
chmod +x triage.sh && ./triage.sh attachment.bin
```

### 按类型的"下一步"表

| 判定结果 | 下一步 |
| --- | --- |
| PNG/BMP | `pngcheck -vtp7`、`zsteg -a`、宽高 CRC、StegSolve 位平面、Aperi'Solve |
| JPEG | `exiftool`、`steghide info`、`stegseek rockyou`、`outguess -r`、尾部追加 |
| GIF | `ffmpeg -vsync 0` 拆帧、帧时长序列、调色板 |
| WAV/MP3 | 频谱图（Audacity/sox）、DTMF/摩斯、LSB、声道差分、ID3 标签 |
| ZIP/RAR/7z | 伪加密、`bkcrack` 明文攻击、CRC 撞库、字典 |
| PDF | `pdfid`、`pdfdetach -list`、`qpdf --qdf`、`mutool extract`、旧版本 |
| docx/pptx/xlsx | `7z x` 后翻 `word/media`、`docProps`、批注 |
| pcap/pcapng | `capinfos`、会话统计、`--export-objects`、追踪流 |
| ELF/PE | `strings`、`checksec`、静态反编译、花指令/pyjail |
| 纯文本 | 字符集判定 → CyberChef `Magic` → 套娃解码器 |
| 未知二进制 | `binwalk -e`、`foremost`、`trid`、`binvis` 可视化 |

### 常用"换视角"清单

```bash
# 1. 元数据（EXIF 缩略图）
exiftool -b -ThumbnailImage "$f" > thumb.jpg 2>/dev/null && file thumb.jpg
# 2. 文件尾部
python -c "d=open('$f','rb').read(); import re; print([m.start() for m in re.finditer(b'PK\x03\x04|IEND|\xff\xd9', d)])"
# 3. 隐藏文件（白名单外的）
7z l "$f" 2>/dev/null; zipinfo "$f" 2>/dev/null
# 4. 大小异常：与理论大小对比
python -c "print(round(__import__('os').path.getsize('$f')/1024,1),'KB')"
# 5. 零宽字符 / 同形字
python -c "
import collections
t=open('$f',encoding='utf8',errors='ignore').read()
print(collections.Counter(t).most_common(12))"
# 6. 时间戳
exiftool -time:all -a -G1 "$f" | head -20
```

### Windows 侧对照命令（PowerShell）

```powershell
Get-FileHash .\attachment.bin -Algorithm SHA256
Format-Hex -Path .\attachment.bin -Count 64
(Get-Item .\attachment.bin).Length
# 用 wsl 调用 Linux 工具链
wsl -e bash -lc "cd /mnt/e/CTF/chal && ./triage.sh attachment.bin"
```

### 复盘记录模板

```markdown
## 题目：<名字>
- 附件：<文件名> <大小> <sha256>
- 真实类型：<file 输出>
- 关键线索：<在哪个步骤发现的>
- 解法链：file → exif → binwalk → xxx → base64 → flag
- 卡点：<浪费时间的步骤，下次怎么避免>
- 耗时：<分钟>
```

## 五、常见坑 / 变体

- **只信扩展名**：一定先 `file`，很多题就是改后缀。
- **只跑一遍 tools**：`binwalk` 对某些压缩格式不敏感，务必补 `foremost`/`7z l`。
- **不看文件尾**：`IEND`/`FFD9` 之后的数据是最高频的藏点。
- **忘记换工具**：PNG 用 zsteg、JPEG 用 steghide，用错工具等于没试。
- **不记录**：赛时交接必须留笔记，否则重复劳动。
- **时间管理**：单题超过 25 分钟没进展，换人或先做别的题。

## 六、参考来源

- [Aperi'Solve 速查表（总决策树与"卡住时检查什么"）](https://www.aperisolve.com/cheatsheet)
- [CTF Wiki - 杂项简介](https://ctf-wiki.org/misc/introduction/)
- [CTF Wiki - 取证隐写前置技术](https://ctf-wiki.org/misc/prefix/)
- [StegOnline CTF 图像检查清单](https://georgeom.net/StegOnline/checklist)
- [binwalk 官方仓库](https://github.com/ReFirmLabs/binwalk)
- [exiftool 官方文档](https://exiftool.org/)
