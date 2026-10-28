---
title: 文件头识别与常见魔数速查
category: misc
tags: [文件头, 魔数, file, 010editor, binwalk, 文件修复]
signals: [附件没有后缀名, 改了后缀打不开, 文件提示 corrupted, 打开是乱码, 题面给了 base64 文本, 需要判断真实文件类型, 文件头被改过, 一个文件能打开两种软件]
difficulty: easy
source: "CTF-Wiki / Aperi'Solve 速查表 / Gary Kessler 文件签名库"
tools: [file, xxd, 010editor, binwalk, trid, CyberChef]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件下载下来是个 `flag`、`data`、`attachment` 之类**没有扩展名**的文件。
- 附件叫 `xxx.png`，但 `file` 说它是 `Zip archive data`。
- 题目描述只有一句「这是什么文件？」「修复这张图片」。
- 打开显示「文件已损坏」，但大小看起来很正常。
- 文件头明显是 `FF D8 FF E0` 但后半段有 `PK\x03\x04`——**polyglot（多格式文件）**。
- 用 `strings` 能看到 `GIF89a`、`%PDF-1.7` 之类关键字，说明中间还嵌了一个文件。

## 二、原理

绝大多数文件格式在**固定偏移**处写有「魔数」（magic number / file signature），解析器靠它判断类型，而不靠扩展名。所以：

1. **扩展名可以随便改**，文件头才是权威；`file` 就是查这张表。
2. 文件头**被故意改坏**（如 PNG 的 `89 50 4E 47` 改成 `89 50 4E 44`），软件就打不开——把正确的魔数写回去即可修复。
3. 文件**尾部追加**另一个文件是 CTF 最常见的「藏东西」手法，`binwalk` 就是按特征串扫描整个文件，找出所有内嵌格式的起始偏移。
4. 两个格式的魔数**互不冲突**时可以拼成一个文件（PDF/ZIP、GIF/JS、JPEG/ZIP），称为 polyglot。

## 三、操作步骤

1. **先看真实类型**：`file target`，再用 `xxd target | head -5` 看前 64 字节。
2. **对照魔数表**（见第四节）判断应该是哪种格式。
3. **找内嵌文件**：`binwalk target` 列出偏移，`binwalk -e target` 直接分离；失败就用 `foremost`/`scalpel`。
4. **修文件头**：用 010 Editor / `hexedit` 把偏移 0 处的字节改回正确值，再看能否打开。
5. **验证**：`pngcheck -v`、`unzip -l`、`pdfinfo`、`ffprobe` 各取其一，确认结构完好。
6. **最后一步**：`strings -n 6 target | grep -iE 'flag|ctf'`，很多题到这一步就出了。

## 四、命令/脚本

### 常用魔数速查表

| 格式 | 十六进制头（偏移 0） | ASCII |
| --- | --- | --- |
| PNG | `89 50 4E 47 0D 0A 1A 0A` | `\x89PNG....` |
| JPEG | `FF D8 FF E0/E1/E2/DB` | 以 `FFD8FF` 开头、`FFD9` 结尾 |
| GIF | `47 49 46 38 39 61` | `GIF89a` / `GIF87a` |
| BMP | `42 4D` | `BM` |
| TIFF | `49 49 2A 00` / `4D 4D 00 2A` | II / MM |
| WebP | `52 49 46 46 .. .. .. .. 57 45 42 50` | `RIFF....WEBP` |
| ZIP/DOCX/APK/JAR | `50 4B 03 04` | `PK..` |
| RAR5 | `52 61 72 21 1A 07 01 00` | `Rar!....` |
| 7z | `37 7A BC AF 27 1C` | `7z..'.` |
| GZIP | `1F 8B 08` | |
| TAR | 偏移 257 处 `75 73 74 61 72` | `ustar` |
| PDF | `25 50 44 46 2D` | `%PDF-` |
| SQLite | `53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00` | `SQLite format 3` |
| ELF | `7F 45 4C 46` | `\x7fELF` |
| PE (exe/dll) | `4D 5A` | `MZ`，偏移 60 处为 `PE\0\0` |
| Mach-O | `FE ED FA CE` / `CF FA ED FE` | |
| WASM | `00 61 73 6D` | `\0asm` |
| PCAP | `D4 C3 B2 A1` / `A1 B2 C3 D4` | 字节序区分 |
| PCAPNG | `0A 0D 0D 0A` | |
| RIFF WAV/AVI | `52 49 46 46 .... 57 41 56 45` | `RIFF....WAVE` |
| OGG | `4F 67 67 53` | `OggS` |
| FLAC | `66 4C 61 43` | `fLaC` |
| MP4 | 偏移 4 处 `66 74 79 70` | `....ftyp` |
| ISO 9660 | 偏移 32769 处 `43 44 30 30 31` | `CD001` |
| VMDK | `4B 44 4D` | `KDM` |
| VHD | 尾部 `63 6F 6E 65 63 74 69 78` | `conectix` |
| E01 | `45 56 46 32 0D 0A 81 00` | `EVF2` |
| JSON 日志/杂项 | `5B 7B` | `[{` |

### 离线识别与修复

```bash
file target                       # 判断真实类型
xxd target | head -n 4            # 看文件头
tail -c 32 target | xxd           # 看文件尾（判断截断）
binwalk target                    # 扫描内嵌格式
binwalk -e --run-as=root target   # 分离（新版必须加 --run-as）
foremost -i target -o out/        # binwalk 失败时换 foremost
trid target                       # 3000+ 种格式概率匹配
xxd -l 16 target                  # 只打印前 16 字节
dd if=target of=fixed.png bs=1 count=8 conv=notrunc
```

### 修复被改坏的魔数（Python）

```python
#!/usr/bin/env python3
# fix_magic.py —— 把偏移 0 处的文件头替换成正确的魔数
import sys

SIGS = {
    'png':  bytes.fromhex('89504e470d0a1a0a'),
    'jpg':  bytes.fromhex('ffd8ffe0'),
    'gif':  b'GIF89a',
    'zip':  bytes.fromhex('504b0304'),
    'pdf':  b'%PDF-1.7',
    'rar':  bytes.fromhex('526172211a070100'),
}

src, fmt, dst = sys.argv[1], sys.argv[2].lower(), sys.argv[3]
data = bytearray(open(src, 'rb').read())
sig = SIGS[fmt]
data[:len(sig)] = sig
open(dst, 'wb').write(data)
print(f'[+] {src} -> {dst}, magic set to {fmt}: {sig.hex()}')
```

```bash
python fix_magic.py broken.bin png fixed.png && pngcheck -v fixed.png
```

### 从 Base64 文本还原二进制（题面给一串字符时）

```bash
# 去掉干扰字符后解码，并自动判断类型
tr -d '\n\r ' < key.txt | base64 -d > blob.bin 2>/dev/null; file blob.bin
# 或者用 CyberChef 的 "From Base64" -> "Detect File Type" 流水线，一次性可视化
python -c "import base64,pathlib;p=pathlib.Path('key.txt').read_text();open('blob.bin','wb').write(base64.b64decode(p))"
```

## 五、常见坑 / 变体

- **文件被截断**：`tail -c 32` 看不到 `FFD9`/`IEND` 说明尾巴被切，需要根据结构补齐或从镜像/流量里找回。
- **头被抹成 0x00**：有的题把头整体置零，此时靠 `binwalk` 的特征串定位真实起点，再用 `dd if=target of=new.bin bs=1 skip=OFFSET` 截取。
- **CTF 常见「改后缀」陷阱**：`.png` 其实是 ZIP、`.docx` 其实是 RAR、`.jpg` 其实是 TAR，改回正确后缀直接解压。
- **polyglot**：`file` 只报第一种，需手动搜索所有魔数：`grep -aboP '\x89PNG|PK\x03\x04|%PDF' target`。
- **E01/VHD 需要工具**：`ewfmount` 挂载 E01，`qemu-nbd -c /dev/nbd0 disk.vhd` 挂载 VHD，不能靠改后缀。
- **反取证变体**：偏移 0 处放诱饵头，真数据在尾部——始终用 `binwalk -e` 复查一遍。

## 六、参考来源

- [CTF Wiki - 杂项简介](https://ctf-wiki.org/misc/introduction/)
- [Aperi'Solve Steganography Cheatsheet（Tell → Tool 对照表）](https://www.aperisolve.com/cheatsheet)
- [Gary Kessler 文件签名库](https://www.garykessler.net/library/file_sigs.html)
- [Corkami 文件格式海报](https://corkami.github.io/)
- [file(1) man page — magic 文件格式说明](https://man7.org/linux/man-pages/man1/file.1.html)
