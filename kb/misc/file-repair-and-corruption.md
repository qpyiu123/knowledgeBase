---
title: 文件修复与损坏识别（手工重建头部、CRC 重算）
category: misc
tags: [file-repair, png, jpeg, header, crc, corruption]
signals: [文件打不开提示已损坏, file 命令识别不出类型或者识别成 data, 十六进制里文件头魔数被改了一两个字节, pngcheck 报 CRC error 或 truncated, 图片能打开但是下半部分花屏, 文件大小和画面内容严重不符, 题目直接说修复这张图]
difficulty: medium
source: "CTF-Wiki Misc / 官方文件格式规范（PNG ISO/IEC 15948, JPEG ITU-T T.81）/ file 魔数库"
tools: [python, xxd, pngcheck, pngfix, jpegtran, zlibcrc, file]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 双击打不开，看图软件提示"文件已损坏或格式不受支持"。
- `file target.bin` 输出 `data`，`binwalk` 也扫不到任何签名。
- `xxd target | head -2` 看到 `89 50 4E 47 0D 0A 1A 00` 之类**只差一个字节**的魔数。
- `pngcheck -v` 报 `CRC error in chunk IDAT` 或 `file is shorter than expected`。
- 图片 parcial 能显示（比如上半部分正常、下半部分花屏），说明像素数据被截断或压缩流出错。
- 文件头里高度比画面实际高度大，或者宽高两个字段互换。
- 题目描述里直接出现"修复""corrupted""broken image"。

## 二、原理

损坏分三个层级，处理手法完全不同：

| 层级 | 典型位置 | 表现 | 修复思路 |
| --- | --- | --- | --- |
| 签名层 | 文件前 2~8 字节 | `file` 无法识别 | 按规范写回魔数 |
| 结构层 | chunk 长度 / CRC / 索引偏移 | 能识别但解析报错 | 核对块边界和数据后再重算 CRC |
| 数据层 | 压缩流被截断/被 XOR | 花屏、缺失 | 重新拼接、尝试容错解码 |

**PNG**：签名固定 8 字节 `89 50 4E 47 0D 0A 1A 0A`；chunk 结构为 `length(4) type(4) data(length) crc(4)`，CRC 是对 `type+data` 计算的标准 CRC-32。CRC 只能检查块内容。先核对块边界、图像头、数据的真实编码，确认块内字节正确后再重算 CRC。比如 Miniscule 的 IDAT 使用 Zstandard；只改压缩方法字段和 CRC，标准 PNG 解码器仍读不出图。

**JPEG**：以 `FF D8` 起始、`FF D9` 结束。常见的 SOF 段在长度后依次写采样精度（1 字节）、高度（2 字节）、宽度（2 字节）、分量数（1 字节）。补结束标记不能补回丢失的压缩数据；改尺寸后也要用解码器检查整张图。

## 三、操作步骤

1. **先鉴定，不要先改**：`file`、`xxd | head -4`、`binwalk`。若 `binwalk` 在偏移 0 之后还有签名，说明文件前面被加了壳（常见"新增头部"型损坏）。
2. **比对标准头部**：从同格式的正常文件里 `xxd` 出前 32 字节做 diff，定位被改的字段。
3. **PNG 逐 chunk 走查**：用脚本按 `length` 遍历 chunk，打印每个 chunk 的类型、长度、CRC 是否匹配；定位第一个出错的 chunk。
4. **核对数据后重算 CRC**：块名只能用来找候选边界，不能单独确定边界。标准 PNG 的 IDAT 应能按 zlib 解压；对不交错的 8 位 RGB 图，行数据长度应为 `height * (3 * width + 1)`。其他色型、位深或交错图按各自布局核对。最后用独立解码器打开副本。
5. **JPEG 高度修复**：解析 SOF 段，手动改回高度或宽度（常见变体：高度被改小导致下半部分丢失，改回真实高度后图像下半部分是隐藏内容）。
6. **截断恢复**：对 PNG，被截断的 IDAT 流仍可能部分解压出来，用 `zlib.decompressobj` 然后忽略 `Incomplete` 异常，缺失行补 0 观察内容。
7. **最终验证**：`pngcheck -v`、`identify`、`exiftool` 三件套全过。

## 四、命令 / 脚本

```bash
# 1) 鉴定
file target.bin
xxd target.bin | head -4
binwalk target.bin
# 2) 已知格式核对魔数
printf '\x89PNG\r\n\x1a\n' | xxd
# 3) 官方修复工具
pngcheck -vt target.png
pngfix --verbose target.png out.png
jpegtran -copy all -outfile fixed.jpg broken.jpg
```

```python
#!/usr/bin/env python3
# 按现有边界列出校验；确认块内容正确后才用 -w 重算 CRC
import sys, zlib, struct

SIG = b'\x89PNG\r\n\x1a\n'
KNOWN = {b'IHDR', b'PLTE', b'IDAT', b'IEND', b'tEXt', b'zTXt', b'iTXt',
         b'gAMA', b'pHYs', b'tIME', b'sRGB', b'bKGD', b'cHRM', b'pHYs'}

def walk(path, fix=False):
    d = bytearray(open(path, 'rb').read())
    if bytes(d[:8]) != SIG:
        print('[!] 签名损坏:', bytes(d[:8]).hex())
    p = 8
    out = bytearray(SIG)
    typ = None
    while p + 12 <= len(d):
        ln = struct.unpack('>I', d[p:p+4])[0]
        typ = bytes(d[p+4:p+8])
        data = bytes(d[p+8:p+8+ln])
        if p + 12 + ln > len(d):
            raise ValueError('块长度超出文件，先核对真实边界')
        crc = struct.unpack('>I', d[p+8+ln:p+12+ln])[0]
        calc = zlib.crc32(typ + data) & 0xffffffff
        status = 'OK' if crc == calc else 'CRC-BAD(%s!=%s)' % (
            '%08x' % (crc or 0), '%08x' % calc)
        print('off=%06d type=%-4s len=%-7d %s' % (p, typ.decode('latin1'), ln, status))
        out += struct.pack('>I', ln) + typ + data + struct.pack('>I', calc)
        p += 12 + ln
        if typ == b'IEND':
            break
    if fix:
        if typ != b'IEND':
            raise ValueError('未找到完整的结束块')
        open(path + '.fixed.png', 'wb').write(bytes(out))
        print('[+] 已写出修复文件')

if __name__ == '__main__':
    walk(sys.argv[1], fix=('-w' in sys.argv))
```

```python
#!/usr/bin/env python3
# JPEG SOF 高度/宽度读取与改写
import sys, struct

def find_sof(d):
    p = 2
    while p < len(d) - 1:
        if d[p] != 0xFF:
            p += 1; continue
        m = d[p+1]
        if m in (0xD8, 0xD9, 0x01) or 0xD0 <= m <= 0xD7:
            p += 2; continue
        ln = struct.unpack('>H', d[p+2:p+4])[0]
        if m in (0xC0, 0xC1, 0xC2, 0xC3):
            h, w = struct.unpack('>HH', d[p+5:p+9])
            return p, h, w
        p += 2 + ln
    return None

d = bytearray(open(sys.argv[1], 'rb').read())
r = find_sof(d)
print('SOF at %s h=%s w=%s' % r if r else 'no SOF')
if r and len(sys.argv) >= 4:                 # 用法: script.jpg new_h new_w
    off, _, _ = r
    nh, nw = int(sys.argv[2]), int(sys.argv[3])
    d[off+5:off+9] = struct.pack('>HH', nh, nw)
    open('fixed.jpg', 'wb').write(bytes(d))
    print('[+] 写回 h=%d w=%d -> fixed.jpg' % (nh, nw))
```

## 五、常见坑 / 变体

- **只补魔数不改 CRC**：PNG 的 IHDR 被改后若不重算 CRC，解码器直接拒绝，看起来"还是坏的"。顺序永远是先修数据再重算 CRC。
- **length 字段被改**：块名只能帮助找候选位置。结合前后块边界、CRC 和解码结果，确认正确长度。
- **PNG 尾部多余数据**：`IEND` 之后的数据删除前先 `binwalk` 一遍，很多题把真实内容附在尾巴上。
- **jpeg 的 `FF D9` 可能不止一个**：拼接图（两张 jpg 首尾相接）里第一个 `FF D9` 是干扰，第二张才是主体。
- **"新增头部"型损坏**：文件最前面多出 N 个字节垃圾，`binwalk` 显示真实内容在 offset=N，用 `dd if=in of=out bs=1 skip=N` 切掉即可。
- **CRC 通过，尺寸仍可能有误**：改过的宽高也能配上正确 CRC。按色型、位深和交错方式核对解压长度，再试解码。
- **扩展名欺骗**：`.png` 实为 `.jpg` 或 zip，先 `file` 再谈修复。

## 六、参考来源

- [PNG 规范（W3C / ISO/IEC 15948）关于 chunk 与 CRC 的定义](https://www.w3.org/TR/png-3/)
- [libpng / pngcheck 官方工具与使用说明](http://www.libpng.org/pub/png/apps/pngcheck.html)
- [JPEG 文件结构（ITU-T T.81 段与 SOF 定义）](https://en.wikipedia.org/wiki/JPEG)
- [binwalk 官方仓库（签名扫描与提取）](https://github.com/ReFirmLabs/binwalk)
- [CTF-Wiki：Misc 中的文件修复思路](https://ctf-wiki.org/misc/introduction/)
