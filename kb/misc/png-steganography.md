---
title: PNG 图片隐写排查（binwalk/zsteg/CRC 宽高/LSB/IDAT）
category: misc
tags: [png, 隐写, binwalk, zsteg, 宽高CRC, IHDR]
signals: [给了一个 png, 打开图片被裁切, 图片下半部分全黑, 文件大小远大于像素数据, pngcheck 报 CRC 错误, zsteg 有可疑输出, IEND 之后还有数据, 宽高被改过]
difficulty: medium
source: "CTF-Wiki PNG 章节 / Aperi'Solve PNG checklist / pngcheck 文档 / libpng 规范"
tools: [binwalk, zsteg, pngcheck, stegsolve, aperisolve, pngfix, python]
updated: 2026-10-22
differs_from: [misc/jpg-steganography.md]
relates_to: [misc/lsb-analysis.md, misc/bmp-gif-tiff-stego.md]
---

## 一、识别信号（题面长什么样）

- 附件是一张 `.png`，题面暗示「图片被裁剪过」「看看完整的样子」。
- 用看图软件打开，图片**下半部分纯黑/纯白**，或者明显**比例不对**。
- `pngcheck -v` 输出 `CRC error in chunk IHDR`——高度或宽度被改过。
- 文件大小 5 MB，但 1000×1000 的图正常只有几百 KB。
- `strings` 或 `binwalk` 在 `IEND` 之后发现 `PK\x03\x04`、`flag{`。
- `zsteg -a` 输出了 `b1,rgb,lsb,xy .. text: "flag{"`。

## 二、原理

PNG 是**无损**格式，像素位可以被逐字节改写而肉眼无感，所以 LSB 类隐写在 PNG 上是主流。PNG 结构为 `8 字节签名 + 若干 chunk`，关键 chunk：

| Chunk | 作用 | 隐写要点 |
| --- | --- | --- |
| `IHDR` | 宽(4B) 高(4B) 位深 色彩类型… | 改宽高后 CRC 对不上；可用 CRC 反推真实宽高 |
| `PLTE` | 调色板（索引色） | 随机化调色板可能显现图案 |
| `IDAT` | zlib 压缩的扫描行数据 | 可逆压缩后手工分析、可藏 zip 片段 |
| `tEXt/iTXt/zTXt` | 文本元数据 | 常直接放 base64 或 flag |
| `IEND` | 结尾 | **之后的字节全部是追加数据**，binwalk 一炸一个准 |

**宽高 CRC 爆破原理**：`IHDR` 的 CRC 由「类型码 + 宽 + 高 + 位深…」计算。题目把宽高改小（比如把真实 800×200 改成 800×50），超出部分的像素就被裁掉。因为 CRC 字段通常没被同步修改，我们可以**枚举宽高组合，重新算 CRC，与文件中保存的 CRC 比对**，命中就是原始尺寸。

## 三、操作步骤

1. **结构体检**：`pngcheck -vtp7 target.png`，看是否有 `CRC error`、`truncated`。
2. **看元数据**：`exiftool -a -u -g1 target.png`，`strings -n 6 target.png | grep -iE 'flag|key|ctf'`。
3. **分离内嵌**：`binwalk -e target.png`，`foremost`；也试试 `unzip target.png`。
4. **LSB 扫描**：`zsteg -a target.png`，命中后 `zsteg -E 'b1,rgb,lsb,xy' target.png > out.bin`。
5. **CRC 宽高爆破**：若 IHDR 报错，见下方脚本，得到真实尺寸后改回。
6. **IDAT 还原**：解压 IDAT 看是否出现重复图案；或用 StegSolve 逐帧翻位平面。
7. **追加数据尾部**：`IEND` 后偏移用 `grep -abo 'IEND' target.png` 定位，`dd` 截取。

## 四、命令/脚本

### 标准排查链

```bash
pngcheck -vtp7 target.png                 # -v 详细 -t chunk 状态 -p 只显示错误 -7 显示多个
exiftool -a -u -g1 target.png             # 全部元数据（含内嵌缩略图）
exiftool -b -ThumbnailImage target.png > thumb.jpg
strings -n 6 target.png | grep -iE 'flag|key|ctf|pass'
zsteg -a target.png                       # 全组合扫描 LSB/MSB、各种位序
zsteg -E 'b1,rgb,lsb,xy' target.png > out.bin   # 提取命中的那一路
binwalk target.png && binwalk -e --run-as=root target.png
unzip -l target.png 2>/dev/null || true
```

### 宽高 CRC 爆破

```python
#!/usr/bin/env python3
# png_crc_fix.py —— 由 IHDR 保存的 CRC 反推真实宽高，并写回文件
import struct, zlib, sys

def fix(path):
    data = bytearray(open(path, 'rb').read())
    assert data[:8] == b'\x89PNG\r\n\x1a\n', 'not png'
    # 第一个 chunk 必须是 IHDR：长(4)+类型(4)+数据(13)+CRC(4)
    w, h = struct.unpack('>II', data[16:24])
    body = bytes(data[12:29])                     # 类型码 + IHDR 数据 13 字节
    crc_stored = struct.unpack('>I', data[29:33])[0]
    cur = zlib.crc32(body) & 0xffffffff
    print(f'[i] size {w}x{h}  crc_stored={crc_stored:08x} crc_calc={cur:08x}')
    if cur == crc_stored:
        print('[+] IHDR CRC 一致，宽高未被修改')
        return
    for nw in range(1, 5000):
        for nh in range(1, 5000):
            cand = body[:4] + struct.pack('>II', nw, nh) + body[12:]
            if zlib.crc32(cand) & 0xffffffff == crc_stored:
                print(f'[+] 真实尺寸: {nw} x {nh}')
                data[16:24] = struct.pack('>II', nw, nh)
                open(path.replace('.png', '_fixed.png'), 'wb').write(data)
                return
    print('[-] 未命中，尝试只枚举高度或直接用宽高最大公约数');

if __name__ == '__main__':
    fix(sys.argv[1])
```

> 4 万次以上的两层循环在纯 Python 下偏慢，实战可先固定一个维度（常见只改高）只枚举另一个；或用 `pypng`/`ping` 库，或用 Aperi'Solve 的 PCRT。

### 解压 IDAT 手工分析

```python
#!/usr/bin/env python3
# idat_dump.py —— 把 IDAT 数据解 zlib，并按行输出首字节以识别 LSB 图案
import struct, zlib, sys, collections
d = open(sys.argv[1], 'rb').read()
i, chunks = 8, []
while i < len(d):
    ln = struct.unpack('>I', d[i:i+4])[0]
    typ = d[i+4:i+8]
    if typ == b'IDAT':
        chunks.append(d[i+8:i+8+ln])
    if typ == b'IEND':
        break
    i += 12 + ln
raw = zlib.decompress(b''.join(chunks))
print('decompressed', len(raw), 'bytes; head', raw[:16].hex())
print(collections.Counter(raw[:2000]).most_common(8))
```

### 提取 IEND 之后的数据

```bash
python - <<'PY'
d = open('target.png','rb').read()
off = d.find(b'IEND') + 8              # IEND 类型4 + CRC4
tail = d[off:]
open('tail.bin','wb').write(tail)
print('tail size', len(tail))
PY
file tail.bin
```

## 五、常见坑 / 变体

- **zsteg 什么都没发现**：换 `-b 1..8`、`-o xy/yx/XY`，试 **MSB**、**取反**、**列优先**，以及 **alpha 通道**（`b8,rgba,lsb,xy`）——这是最经典的漏检点。
- **修复后再隐写**：`pngcheck -f target.png` 修好 CRC 再跑 zsteg，否则 zsteg 直接退出。
- **PLTE 索引色图**：zsteg 效果差，要重排调色板看假彩色图，或用 StegSolve 的 Random Color Map。
- **tEXt 里的 base64 套娃**：拿到 `iVBORw0KGgo...` 说明是另一张 PNG，直接续写进 `.png` 文件。
- **alpha 通道藏图**：StegSolve 选 `Alpha plane 0`，或 Python 把 alpha 通道单独导出成灰度图。
- **加密 LSB**：位平面看起来像随机噪声 → 常见工具是 `cloacked-pixel`、`OpenStego`、`LSBSteg`，需要密码，密码常在题面/metadata/文件名。
- **misc 与 forensics 交叉**：同一手法也出现在流量包里——从 pcap 导出的 PNG 一样要过这一整套。

## 六、参考来源

- [CTF Wiki - PNG 图片分析](https://ctf-wiki.org/misc/picture/png/)
- [Aperi'Solve 速查表（PNG/BMP 决策分支）](https://www.aperisolve.com/cheatsheet)
- [zsteg - LSB steganography detector](https://github.com/zed-0xff/zsteg)
- [pngcheck 官方文档](http://www.libpng.org/pub/png/apps/pngcheck.html)
- [PNG 规范 (W3C)](https://www.w3.org/TR/png-3/)
- [PCRT - PNG Check & Repair Tool](https://github.com/Hedroed/png-parser)
