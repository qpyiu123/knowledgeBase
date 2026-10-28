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
| 结构层 | chunk 长度 / CRC / 索引偏移 | 能识别但解析报错 | 重算长度和 CRC |
| 数据层 | 压缩流被截断/被 XOR | 花屏、缺失 | 重新拼接、尝试容错解码 |

**PNG**：签名固定 8 字节 `89 50 4E 47 0D 0A 1A 0A`；chunk 结构为 `length(4) type(4) data(type=='IHDR'?'13':length) crc(4)`，CRC 是对 `type+data` 计算的标准 CRC-32。所以**任何一处字节被改动，只要把 CRC 重算回去，图像就正常了**——这也是出题最常见的"修复题"。

**JPEG**：以 `FF D8` 起始、`FF D9` 结束（可用 `FF D9` 补尾）。段结构为 `FFxx len(2) payload`，其中 `xx∈[E0,EF]` 是 APP 段、`C0~C2` 是 SOF。SOF 里承载**宽(2) 高(2) 分量数(1)**，高度/宽度改动会让解码器分配错误的缓冲区，常见表现是"扫描到最后一行就崩"。

## 三、操作步骤

1. **先鉴定，不要先改**：`file`、`xxd | head -4`、`binwalk`。若 `binwalk` 在偏移 0 之后还有签名，说明文件前面被加了壳（常见"新增头部"型损坏）。
2. **比对标准头部**：从同格式的正常文件里 `xxd` 出前 32 字节做 diff，定位被改的字段。
3. **PNG 逐 chunk 走查**：用脚本按 `length` 遍历 chunk，打印每个 chunk 的类型、长度、CRC 是否匹配；定位第一个出错的 chunk。
4. **重算 CRC**：`zlib.crc32(type + data)` 写回。若 `length` 本身被改，会连锁导致整条链错位——此时用魔数 `IHDR/IDAT/IEND` 反查真实边界。
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
# PNG chunk 走查 + 自动重算 CRC + 坏 length 纠正
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
    while p + 8 <= len(d):
        ln = struct.unpack('>I', d[p:p+4])[0]
        typ = bytes(d[p+4:p+8])
        data = bytes(d[p+8:p+8+ln])
        crc = struct.unpack('>I', d[p+8+ln:p+12+ln])[0] if p+12+ln <= len(d) else None
        calc = zlib.crc32(typ + data) & 0xffffffff
        status = 'OK' if crc == calc else 'CRC-BAD(%s!=%s)' % (
            '%08x' % (crc or 0), '%08x' % calc)
        print('off=%06d type=%-4s len=%-7d %s' % (p, typ.decode('latin1'), ln, status))
        out += struct.pack('>I', ln) + typ + data + struct.pack('>I', calc)
        p += 12 + ln
        if typ == b'IEND':
            break
    if fix:
        open(path.replace('.', '_fixed.', 1), 'wb').write(bytes(out))
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
- **length 字段被改**：不要相信 length，用 `type` 的 4 字节 ASCII 去 `grep -abo` 定位下一个 chunk 的真实起点，反推正确长度。
- **PNG 尾部多余数据**：`IEND` 之后的数据删除前先 `binwalk` 一遍，很多题把真实内容附在尾巴上。
- **jpeg 的 `FF D9` 可能不止一个**：拼接图（两张 jpg 首尾相接）里第一个 `FF D9` 是干扰，第二张才是主体。
- **"新增头部"型损坏**：文件最前面多出 N 个字节垃圾，`binwalk` 显示真实内容在 offset=N，用 `dd if=in of=out bs=1 skip=N` 切掉即可。
- **CRC 碰撞陷阱**：`IHDR` 宽高被改且 CRC 被同步重算，此时 CRC 检查全绿但图是错的——改用"像素数据流长度是否与宽高吻合"来反推。
- **扩展名欺骗**：`.png` 实为 `.jpg` 或 zip，先 `file` 再谈修复。

## 六、参考来源

- [PNG 规范（W3C / ISO/IEC 15948）关于 chunk 与 CRC 的定义](https://www.w3.org/TR/png-3/)
- [libpng / pngcheck 官方工具与使用说明](http://www.libpng.org/pub/png/apps/pngcheck.html)
- [JPEG 文件结构（ITU-T T.81 段与 SOF 定义）](https://en.wikipedia.org/wiki/JPEG)
- [binwalk 官方仓库（签名扫描与提取）](https://github.com/ReFirmLabs/binwalk)
- [CTF-Wiki：Misc 中的文件修复思路](https://ctf-wiki.org/misc/introduction/)
