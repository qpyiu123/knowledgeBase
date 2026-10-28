---
title: BMP/GIF/TIFF 隐写进阶（调色板/帧延迟/扩展标签）
category: misc
tags: [stego, gif, bmp, tiff, palette, frame-delay]
signals: [给了一个 .bmp 或 .gif 或 .tif, 图片颜色明显变灰变脏有噪点, 调色板里出现大量重复或近似色, GIF 每帧延迟大量为 0, 帧数为奇数且最后一帧几乎全黑, TIFF 里有一堆没见过的 tag, 文件比同尺寸 jpg 大 10 倍以上, 题目说 flag 藏在颜色里]
difficulty: medium
source: "CTF-Wiki 图片隐写 / SAS CTF 2025 Lirili Larila 题解 / 文体规范 GIF89a、TIFF 6.0"
tools: [python, gifsicle, imagemagick, fidder, stegsolve, exiftool, tiffinfo]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 附件是 `.bmp` / `.gif` / `.tiff`，而绝大多数 misc 题给的是 png/jpg——**换格式本身就是提示**。
- GIF：`identify` 显示每帧 delay 都是 0 或 1/100 秒，说明"看起来是动图，其实是数据载体"。
- GIF：**全局调色板 + 每帧局部调色板**同时存在，局部调色板颜色数量明显多于画面实际用色。
- BMP：24 位图没有调色板，但 8 位/4 位 BMP 的调色板项顺序被打乱（EZ Stego 类算法）。
- TIFF：`tiffinfo` 输出里出现 `ImageDescription`、`XPComment`、多个 `SubIFD`，或者页面数 > 1。
- 图像肉眼可见**轻微色带/颗粒**，用 StegSolve 翻到某个位平面后噪点规律性极强。
- 题目说"flag 是按颜色编码的""把颜色读懂就懂了"。

## 二、原理

**BMP**：无压缩、无检验，`BITMAPINFOHEADER` 的 `biHeight` 为正表示自底向上存储；`biBitCount` 决定调色板存在性。因为每行按 4 字节对齐（padding），**行宽与像素宽度不等**，很多脚本按 `width*3` 逐行读取就会错位——这也是出题人埋坑的常见位置。

**GIF**：LZW 压缩 + 调色板索引。隐写有三类抓手：
1. **调色板 LSB / 重排序**（EZ Stego、Westfeld 奇偶性）：在调色板里把相邻两项按亮度排序，使 `P(2i)` 奇偶承载 1 bit。
2. **帧延迟字段**（GCE 的 2 字节 delay，单位 1/100 s）：每帧 delay 改 0/1 就是二进制流，最常见。
3. **帧数据 LZW 最小码长 / 多余帧**：最后一帧全黑却仍存在，通常是数据帧。

**TIFF**：tag-based 结构，`ImageDescription(270)`、`Software(305)`、`DocumentName(269)` 都是纯文本落脚点；`SubIFD`(330) 可以挂任意多个子图；strip/tile 偏移错位可以把数据藏在"图像之外"的位置。此外 TIFF 的 `Orientation` tag 被改后能骗过肉眼。

## 三、操作步骤

1. **统一摸结构**：`file`、`identify -verbose`、`exiftool -a -u -g1`，把格式特有的元数据先扫一遍。
2. **GIF 先看帧**：`identify -format "%s %T\n" x.gif` 打印帧序号与 delay，非 0 序列即数据。
3. **拆帧再逐帧分析**：`gifsicle --explode` 或 ImageMagick `-coalesce` 后拆帧，对每一帧跑 zsteg/StegSolve 的单帧分析。
4. **调色板分析**：把 GIF 调色板按出现顺序导出十六进制，观察"相邻两项是否仅差 1"，或按亮度排序后像素索引是否奇偶规律。
5. **BMP**：先确认位深与行对齐，再按 `padding = (4 - width*bytespp % 4) % 4` 正确取像素；8 位图直接看调色板与索引数组。
6. **TIFF**：`tiffinfo` 看 tag，再 `exiftool -D` 看 tag 号；多页用 `tiffsplit` 拆开。
7. **交叉验证**：把提取出的二进制用 `binwalk` 扫一遍，`file` 确认是否得到 png/zip。

## 四、命令 / 脚本

```bash
# 通用结构摸底
file target.bmp target.gif target.tiff
identify -verbose target.gif | head -80
gifsicle --info target.gif
tiffinfo target.tiff
exiftool -a -u -g1 -D target.gif

# GIF 帧延迟提取（delay 单位为 1/100s）
identify -format "%s:%T\n" target.gif

# GIF 拆帧
mkdir frames && cd frames
gifsicle --explode ../target.gif
for f in *.gif; do zsteg -a "$f" 2>/dev/null | head -5; done

# 也可以用 ImageMagick 合成后拆
convert target.gif -coalesce frame_%04d.png
```

```python
#!/usr/bin/env python3
# GIF 帧延迟 -> 二进制 -> 文本
import struct, sys

def gif_delays(path):
    data = open(path, 'rb').read()
    assert data[:6] in (b'GIF87a', b'GIF89a'), 'not gif'
    p = 6
    w, h, packed = struct.unpack('<HHB', data[p:p+5]); p += 5
    p += 2  # bg color idx, aspect
    if packed & 0x80:                      # 全局调色板
        p += 3 * (2 ** ((packed & 7) + 1))
    delays, frames = [], 0
    while p < len(data):
        b = data[p]; p += 1
        if b == 0x21 and data[p] == 0xF9:  # GCE
            size = data[p+1]
            delay = struct.unpack('<H', data[p+2:p+4])[0]
            delays.append(delay)
            p += 1 + size
            while data[p]: p += data[p] + 1
            p += 1
        elif b == 0x2C:                    # image descriptor
            frames += 1
            desc = data[p:p+9]; p += 9
            if desc[8] & 0x80:             # 局部调色板
                p += 3 * (2 ** ((desc[8] & 7) + 1))
            p += 1                         # LZW min code size
            while data[p]: p += data[p] + 1
            p += 1
        elif b == 0x3B:                    # trailer
            break
        else:
            break
    return delays, frames

if __name__ == '__main__':
    d, n = gif_delays(sys.argv[1])
    bits = ''.join('1' if x else '0' for x in d)
    print('frames=%d delays=%s' % (n, d[:64]))
    print('bits  =', bits)
    # 8bit 分组转字符
    txt = ''.join(chr(int(bits[i:i+8], 2)) for i in range(0, len(bits) - 7, 8))
    print('ascii =', txt)
```

```bash
# BMP 正确读取（含行对齐）后再做差异分析
python - <<'EOF'
import struct
d = open('target.bmp','rb').read()
off = struct.unpack('<I', d[10:14])[0]
w, h = struct.unpack('<ii', d[18:26])
bpp = struct.unpack('<H', d[28:30])[0] // 8
row = (w*bpp + 3) // 4 * 4
print('offset', off, 'size', w, h, 'bytespp', bpp, 'rowlen', row)
px = d[off:]
# 逐行取前 w*bpp 字节，跳过后面的 padding
raw = b''.join(px[i:i+w*bpp] for i in range(0, len(px), row))
open('raw_pixels.bin','wb').write(raw)
EOF
binwalk raw_pixels.bin && zsteg -a --dump-all target.bmp 2>/dev/null | head

# TIFF 多页 & tag
tiffsplit target.tiff out_
exiftool -D -u -g1 target.tiff
```

## 五、常见坑 / 变体

- **BMP 行对齐**：宽度不是 4 的倍数时，按 `width*3` 硬读会让所有 LSB 之差整体错位，出来的永远是垃圾。先算 padding。
- **GIF 帧 delay 单位**：GCE 里是 1/100 秒；有些库（PIL）读出来会乘成毫秒，写脚本时自己 parse 原始字节最稳。
- **GIF 全局 vs 局部调色板**：只分析全局调色板会漏掉局部调色板藏的信息，SAS CTF 2025「Lirili Larila」正是靠分开解析两层调色板解出。
- **GIF 最后一帧全黑**：可能是 `frame disposal` 造成的视觉效果，拆帧时务必 `--coalesce`，否则得到的是差分帧而不是完整画面。
- **TIFF 的 Orientation**：tag 6/8 旋转会让位平面分析结果完全错位，先归一化方向。
- **BMP 也有压缩变体**：`biCompression = 1` 是 RLE8，不能当平铺像素处理。
- **改帧延迟会破坏校验吗**：GIF 没有 CRC，随便改；但 PNG 有，所以两种格式的容错性完全不同。
- **变体**：APNG（扩展名还是 .png 但内部是帧序列）、WebP 动图，分析思路与 GIF 帧延迟同构。

## 六、参考来源

- [Aperi'Solve：多图层自动隐写分析平台](https://www.aperisolve.com/)
- [CTFtime / SAS CTF 2025 Quals — Lirili Larila 题解（GIF 全局/局部调色板）](https://ctftime.org/writeup/40254)
- [CTF Tidbits: Part 1 — Steganography](https://medium.com/@FourOctets/ctf-tidbits-part-1-steganography-ea76cc526b40)
- [Palette Steganography（EZ Stego / Westfeld 奇偶性原理说明）](https://stegotoolkit.com/steganography/palette-steganography-hider)
- [Zeecka/AperiSolve 源码仓库](https://github.com/Zeecka/AperiSolve)
