---
title: 杂项冷门题型（时间戳/元数据/隐写音频/文件时间线）
category: misc
tags: [冷门题, 时间戳, 元数据, 老旧格式, 画中画, unicode隐写]
signals: [题目只给了一张图和几个数字, 附件是一堆文件没有内容, 文件名里有奇怪的时间, 元数据里有可疑字段, 音频里有极高频内容, 需要还原一帧被删掉的画面]
difficulty: medium
source: "CTF-Wiki 杂项 / exiftool 字段说明 / Covert 与 unicode 隐写社区 writeup"
tools: [exiftool, python-datetime, zoneinfo, stegseek, sox, binwalk, CyberChef]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 题面给一串 Unix 时间戳 / UUID /哈希，要求"找规律"。
- 附件是一堆同目录小文件，文件名带时间（`1969-12-31_23_59_59.txt`）。
- 图片元数据里 `CreateDate` 和 `ModifyDate` 差了很多年。
- 音频听不出但高频段有内容，或低频 0~100Hz 有问题。
- 题面只给「nothing here」「look closer」这类废话。

## 二、原理

冷门题往往是**把信息藏在"没人会去看的字段"**里：

| 藏点 | 常见手法 |
| --- | --- |
| 元数据 | `Comment`/`UserComment`/`XPComment`/`MakerNote`/`DocumentID` 里放 base64 |
| 时间戳 | mtime/atime/ctime 编码，或"每个文件的时间戳最后一秒对应一个字符" |
| 时区 | `DateTimeOriginal` 带 `+08:00` 偏移，隐含地理位置 |
| 文件名 | 排序后取首字母；文件名是 hex/unicode 编码 |
| 结构字段 | PNG `tIME` chunk、WAV `LIST INFO`、ZIP 注释、EXIF `Software` |
| 极高频 | 16~22 kHz 频谱绘图 |
| 极低频 | 0~50 Hz 段藏摩斯或低频调制 |
| Unicode | 同形字（Cyrillic а 替 Latin a）、零宽字符、变体选择符 |

难点不在工具，而在于**先意识到去查这些字段**。

## 三、操作步骤

1. **先把元数据全量打印**，逐字段看，不要只看前几个。
2. **时间戳**：`stat` 每个文件，导出所有时间，按时间排序，把差异画出来或转 ASCII。
3. **文件名**：排序、取首字符、看长度分布、hex 解码。
4. **结构字段**：`exiftool -v3` 会解析二进制结构，能列出 chunk。
5. **频谱扫描全覆盖**：0~200Hz 与 15~22kHz 各自出一张图。
6. **Unicode**：`unicodedata` 检查同形字/零宽字符。

## 四、命令/脚本

### 元数据全量与字段解析

```bash
exiftool -a -u -g1 target.jpg                 # 全部标签（含未知/私有）
exiftool -v3 target.png | head -60            # 解析二进制块结构（PNG chunk 级）
exiftool -XMP -b target.jpg                   # 只打印 XMP
exiftool -a -G1 -s target.jpg | grep -iE 'comment|desc|title|artist|id|tag'
# 提取全部字符串字段
exiftool -a -u -s -G1 -csv target.jpg | tr ',' '\n' | sort -u | head -60
```

### 时间戳编码

```bash
# 1) 列出全部文件时间（精确到纳秒）
stat -c '%y  %n' * | sort
find . -type f -printf '%T@ %p\n' | sort -n
# 2) 时间戳末位按 ASCII 拼字
find . -maxdepth 1 -type f -printf '%T@\n' | sort -n | cut -d. -f2 | cut -c1 | tr -d '\n'
# 3) 时间戳当 Unix 秒转字符
python -c "import datetime;print(chr(int('$(date +%s)') % 128))"
```

```python
#!/usr/bin/env python3
# ts_decode.py —— 文件 mtime 的"秒差/纳秒/秒数本身"三种常见编码都试一遍
import os, glob, itertools

files = sorted(glob.glob('*.txt') + glob.glob('files/*'))
ts = [(os.stat(f).st_mtime, os.stat(f).st_mtime_ns, os.stat(f).st_size, f) for f in files]
print('n =', len(ts))
for name, key in [('epoch', 0), ('ms', 0), ('ns_tail', 1), ('size', 2)]:
    if name == 'epoch':
        vals = [int(t[0]) for t in ts]
        # 方案 A：秒数 % 128
        s1 = ''.join(chr(v % 128) if 32 <= v % 128 < 127 else '?' for v in vals)
        # 方案 B：相邻差值
        diffs = [vals[i+1] - vals[i] for i in range(len(vals)-1)]
        s2 = ''.join(chr(d) if 32 <= d < 127 else '?' for d in diffs)
        print(f'[{name}] mod128 :', s1[:200])
        print(f'[{name}] diffs  :', s2[:200])
    elif name == 'ns_tail':
        print('[ns]', ''.join(chr(int(str(t[1])[-7]) + 48) for t in ts)[:60])
    elif name == 'size':
        sizes = [t[2] for t in ts]
        print('[size]', ''.join(chr(s) if 32 <= s < 127 else '?' for s in sizes)[:200],
              '| uniq:', sorted(set(sizes))[:12])
```

### 文件名与排序隐写

```bash
ls | sort | cut -c1 | tr -d '\n' | fold -w 40      # 取首字母
ls -v | wc -l                                      # 顺序是否自然
for f in *.txt; do printf '%s ' "$(cat "$f" | wc -c)"; done   # 长度序列
python -c "
import glob,os
names=sorted(glob.glob('*'))
print(''.join(chr(int(n.split('.')[0],16)) for n in names if '.' in n)[:200])"
```

### 频谱全覆盖

```bash
sox target.wav -n spectrogram -o spec_low.png -X 3000 -Y 1025 -z 100 -r lowpass 500
sox target.wav -n spectrogram -o spec_hi.png  -X 3000 -Y 1025 -z 100 -r highpass 15000
# 频段裁剪后再看
sox target.wav low.wav lowpass 200 && sox low.wav -n spectrogram -o low2.png -X 4000 -Y 600
```

### Unicode 同形字 / 零宽字符

```python
#!/usr/bin/env python3
# unicode_scan.py —— 找出零宽字符与同形字，并尝试解码
import unicodedata, collections, sys
t = open(sys.argv[1], encoding='utf8', errors='replace').read()
bad = [(i, hex(ord(c)), unicodedata.name(c, '?'))
       for i, c in enumerate(t) if ord(c) in (0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF,
                                              0x00AD) or 0xE0000 <= ord(c) <= 0xE007F]
print('zero-width / variation:', bad[:20], '... total', len(bad))
cnt = collections.Counter(t)
print('top chars:', cnt.most_common(12))
# 同形字检测：混入 Cyrillic / Greek 字母
homoglyph = [c for c in t if '\u0400' <= c <= '\u04ff' or '\u0370' <= c <= '\u03ff']
print('homoglyph count:', len(homoglyph))
# 把零宽序列按二进制解码
bits = ''.join('0' if c == '\u200b' else '1' for c in t if c in '\u200b\u200c')
print('bits:', len(bits))
print(bytes(int(bits[i:i+8], 2) for i in range(0, len(bits) - 7, 8))[:80])
```

### PNG `tIME` / WAV `LIST INFO` / ZIP 注释

```bash
# PNG tIME chunk
python -c "
import struct
d=open('target.png','rb').read()
i=d.find(b'tIME')
if i>0:
    print(struct.unpack('>HBBBBB', d[i+4:i+11]))"
# ZIP 注释
unzip -z target.zip
zipinfo -z target.zip
# WAV INFO
exiftool -a -u -g1 target.wav | grep -iA3 'INFO'
```

## 五、常见坑 / 变体

- **`exiftool -a` 不够**：私有 MakerNote 需要 `-u`（未知标签）才能看到。
- **时间戳被 touch 覆写**：如果作者导出时 `touch` 过，mtime 就无效了，转而看 **ctime / atime / EXIF DateTimeOriginal**。
- **文件名大小写**：Windows 不区分大小写会丢信息，在 WSL/ext4 下看。
- **同形字**：肉眼几乎看不出来，一定要用脚本统计非 ASCII 字符。
- **极低频**：很多扬声器放不出 20 Hz 以下，但频谱图上看得到。
- **冷门格式**：`.it`/`.xm`/`.mod` 模块音乐、`.nsf` 芯片音乐也可能藏数据，`strings` 后再看 pattern。
- **组合题**：冷门点常常只是入口，链式结构（元数据 → base64 → 二维码 → 隐写图）要耐心。

## 六、参考来源

- [CTF Wiki - 杂项（图片/音频/归档分支）](https://ctf-wiki.org/misc/introduction/)
- [exiftool 全标签说明](https://exiftool.org/TagNames/)
- [PNG 规范（tIME/tEXt chunk）](https://www.w3.org/TR/png-3/)
- [Aperi'Solve 速查表（卡住时的检查项）](https://www.aperisolve.com/cheatsheet)
- [Unicode 隐写之零宽字符（Unicode 官方字符数据库）](https://www.unicode.org/charts/)
- [SoX effects 文档](https://sox.sourceforge.net/)
