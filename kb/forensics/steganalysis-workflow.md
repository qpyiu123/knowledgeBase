---
title: 隐写取证综合（Aperi'Solve 全流程与批量分析）
category: forensics
tags: [steganalysis, aperisolve, batch, steghide, zsteg, outguess]
signals: [给了一大批图片要求逐张找出藏了内容的那张, 题目说对所有图片跑一遍隐写分析, 单张图 binwalk zsteg steghide 都没有结果, 需要判断 steghide 有没有密码或者密码是空, 图片里存在密码学参数比如 hint 或 key, 题目要求提交被隐写过的文件名而不是 flag 本身]
difficulty: medium
source: "Aperi'Solve 开源项目 / zsteg 与 steghide 官方文档 / 隐写取证批量实践"
tools: [python, aperisolve, zsteg, steghide, stegseek, outguess, binwalk, exiftool]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 附件是一个目录，里面几十到几百张图片，题目问"哪一张被隐写过"。
- 单张分析时 `zsteg -a` 无输出、`binwalk` 无嵌入、`strings` 也没有，但文件大小异常。
- 题目说"密码是图片的某个属性"或"hint 藏在别的地方"。
- 有 Windows 和 Linux 混合产物：既有 `steghide` 也有 `zsteg` 能识别的内容。
- 要求输出"被隐写的图片文件名"作为答案，而不是 flag。
- 目录里有一张图的 EXIF 与其他图明显不同。

## 二、原理

**Steg 分析的完整链路不是"一个工具"，而是"一组正交探测 + 证据合并"：**

| 层 | 工具 | 找什么 |
| --- | --- | --- |
| 容器/文件层 | `binwalk`、`foremost`、`unzip -l` | 追加数据、内嵌文件 |
| 元数据层 | `exiftool`、`strings` | `tEXt`、`XPComment`、注释 |
| 文件名/尾部 | `xxd` 看 `IEND` 后、`EOF` 后 | 尾部追加 |
| 像素 LSB | `zsteg`、`stegsolve` | 位平面数据 |
| 变换域 | `stegdetect`、Aperi'Solve 的 jphide/outguess | DCT 域 |
| 口令隐写 | `steghide`、`stegseek`、`outguess` | 需要口令的隐写载体 |
| 视觉 | Aperi'Solve 的图层、颜色通道、ELA | 肉眼可见的拼接 |

**批量分析的核心是"归一化输出"**：每个工具返回 `(是否命中, 证据摘要)`，把所有证据聚成表；只有命中率极低时才需要人为细看。

## 三、操作步骤

1. **文件级筛选**：按大小排序，找"尺寸远大于内容"的图（PNG 尤其明显）。
2. **Aperi'Solve 跑单图**：上传后看 `zsteg`、`steghide`、`outguess`、`binwalk`、`exiftool` 标签页的输出。
3. **批量脚本**：遍历目录，逐图跑 `file/binwalk/zsteg/steghide`，把命中写到 `report.csv`。
4. **口令处理**：`steghide` 先用空口令试，再用 `stegseek` + 词表爆破（steghide 口令爆破比暴力快几个数量级）。
5. **交叉验证**：命中多个工具同位置的，优先下载查看。
6. **收尾**：把"看起来正常但大小异常"的图再跑一次 Aperi'Solve 的图层分析。

## 四、命令 / 脚本

```bash
# 单图全流程手工链
exiftool -a -u -g1 img.png
binwalk img.png
pngcheck -vt img.png 2>/dev/null || true
zsteg -a img.png | head -20
steghide info img.png -p ''
stegseek img.png rockyou.txt            # 空口令 + 爆破
outguess -r img.jpg out.txt 2>/dev/null
strings -n 8 img.jpg | grep -iE 'flag|key|hint'
# 尾部数据
grep -abo 'IEND' img.png | tail -1
```

```python
#!/usr/bin/env python3
"""批量隐写取证：目录内所有图片跑一遍，输出结构化报告"""
import csv, os, subprocess, sys, glob

def run(cmd, timeout=90):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout + r.stderr)
    except Exception as e:
        return -1, str(e)

def analyze(path):
    ev = {}
    rc, out = run(['file', '-b', path]);            ev['file'] = out.strip()
    rc, out = run(['binwalk', path]);               ev['binwalk'] = out.strip().replace('\n', ' | ')[:200]
    rc, out = run(['exiftool', '-q', '-a', '-u', path]); ev['exif'] = out.strip()[:200]
    rc, out = run(['zsteg', '-a', path]);           ev['zsteg'] = out.strip()[:300]
    rc, out = run(['steghide', 'info', '-p', '', path]); ev['steghide_empty'] = ('OK' if rc == 0 else 'fail')
    size = os.path.getsize(path)
    ev['size'] = size
    return ev

def main(root):
    files = [f for f in glob.glob(os.path.join(root, '**', '*'), recursive=True)
             if os.path.isfile(f) and f.lower().endswith(
                 ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tif', '.tiff', '.webp'))]
    print('共 %d 个图片文件' % len(files))
    rows = []
    for f in files:
        ev = analyze(f)
        hit = any(k in ev.get('zsteg', '')      \
                  or k in ev.get('binwalk', '') \
                  for k in ('flag', 'text:', 'ZIP archive', 'gzip'))
        rows.append([f, ev['size'], ev['steghide_empty'], 'HIT' if hit else '',
                     ev['zsteg'], ev['binwalk']])
        print('%-50s size=%-9d steghide=%-4s %s' %
              (os.path.basename(f), ev['size'], ev['steghide_empty'], 'HIT' if hit else ''))
    with open('stego_report.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['file', 'size', 'steghide_empty', 'hit', 'zsteg', 'binwalk'])
        w.writerows(rows)

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '.')
```

```bash
# stegseek 的口令猜解（比 steghide 暴力快，一次可跑上百万次/秒级）
stegseek --crack -sf img.jpg -wl rockyou.txt
# 用图像内容推导口令（例：口令是图片的 CRC 或文件名）
for f in *.jpg; do
  base="${f%.*}"
  steghide extract -sf "$f" -p "$base" -f 2>/dev/null && echo "hit: $base"
done
```

## 五、常见坑 / 变体

- **`steghide` 只支持 jpg/bmp/wav 等**，对 png 直接报 `unsupported`，别误判为"没有隐写"。
- **`zsteg -a` 输出巨长**：只保留含 `text:`、`meta`、`file:` 的行，否则淹没关键信息。
- **`stegseek` 只解 jpg**：不同工具支持的载体不同，批量脚本要按扩展名分派。
- **Aperi'Solve 的结果要看图层顺序**：某些内容只在"红色平面"或"灰度平面"下可见。
- **批量跑要限并发**：`zsteg -a` 对大图很慢，50 张图串行可能跑十几分钟，用 `xargs -P4`。
- **容易漏的隐蔽点**：ICC profile、缩略图、`tEXt` 的 keyword 被改、多帧 GIF 的单帧。
- **变体**：`outguess`（jpg）、`jphide/jpseek`、`f5`（DCT 系数隐写）、`mp3stego`（音频）。

## 六、参考来源

- [Aperi'Solve：在线多层隐写分析平台](https://www.aperisolve.com/)
- [Zeecka/AperiSolve 开源仓库（工具链与实现）](https://github.com/Zeecka/AperiSolve)
- [zsteg：PNG/BMP 位平面隐写检测](https://github.com/zed-0xff/zsteg)
- [steghide 官方文档与载体支持说明](https://steghide.sourceforge.net/)
- [stegseek：steghide 口令高速猜解](https://github.com/RickdeJager/stegseek)
