---
title: 元数据取证（EXIF / XMP / 文档属性溯源）
category: forensics
tags: [exif, 元数据, xmp, geo, gps, 溯源]
signals: [需要知道照片拍摄地点, 需要判断照片是否被编辑, 需要找设备型号, 元数据里有 GPS, 题面问拍摄时间, 文件名与时间戳矛盾]
difficulty: easy
source: "exiftool 官方文档 / CIPA EXIF 标准 / IPTC 元数据规范"
tools: [exiftool, exiv2, identify, mediainfo, python-piexif, metagoofil]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 题目给一张照片，问「在哪拍的」「什么时候拍的」。
- 需要判断图片是否被 PS 编辑过（Software 字段）。
- 附件是 docx/pdf，问「作者是谁」「用什么软件做的」。
- 题面提示「metadata」「look at the details」。

## 二、原理

元数据分三类标准：

- **EXIF**（相机写入）：`Make/Model`、`DateTimeOriginal`、`ExposureTime`、`GPSLatitude/GPSLongitude`（度分秒 DM）、`Software`、`Orientation`、`MakerNote`（厂商私有）。
- **IPTC/IIM**（新闻机构）：`Keywords`、`Caption`、`By-line`。
- **XMP**（Adobe 的 XML 扩展）：`xmp:CreatorTool`、`photoshop:History`（编辑步骤）、`dc:subject`。

**溯源价值**：
1. `Make+Model` → 设备型号（进而匹配厂商默认命名规则）。
2. `DateTimeOriginal` + `TimeZoneOffset` → 拍摄时刻。
3. `GPS*` → 经纬度（注意 DMS→十进制换算）。
4. `Software` = `Adobe Photoshop 25.0` → 被重新编辑过。
5. `MakerNote` → 更细的序列号/镜头信息。

## 三、操作步骤

1. **全量打印**：`exiftool -a -u -g1 file`（`-a` 全部、`-u` 未知标签、`-g1` 分组）。
2. **看关键字段**：Make/Model/DateTimeOriginal/GPS/Software/Artist/Comment。
3. **换算坐标**：DMS → 十进制，验证是否合理。
4. **检查一致性**：文件系统 mtime 与 `DateTimeOriginal` 是否矛盾。
5. **看缩略图**：`-b -ThumbnailImage` 导出原图。
6. **清除后再分析**：若被清过，看文件头/尾是否有残留（`-v3` 解析块结构）。

## 四、命令/脚本

### 基础全量

```bash
exiftool -a -u -g1 target.jpg
exiftool -time:all -a -G1 target.jpg          # 所有时间字段
exiftool -GPS* target.jpg                      # 只要坐标
exiftool -Make -Model -LensModel -SerialNumber target.jpg
exiftool -Software -Artist -Copyright target.jpg
exiftool -s -G1 -j target.jpg | python3 -m json.tool | head -40   # JSON 输出
```

### GPS 换算

```bash
exiftool -n -GPSLatitude -GPSLongitude -GPSAltitude target.jpg    # -n 直接给十进制
# 手工换算：DMS = DD MM SS，十进制度 = DD + MM/60 + SS/3600
python3 - <<'PY'
def dms2dd(d, m, s):
    return d + m / 60 + s / 3600
print(dms2dd(31, 13, 43.2), dms2dd(121, 28, 29.4))   # 上海某地示例
PY
# 生成地图链接（换成换算后的坐标）
echo 'https://www.google.com/maps?q=31.2289,121.4748'
echo 'https://www.openstreetmap.org/#map=17/31.2289/121.4748'
```

```python
#!/usr/bin/env python3
# exif_dump.py —— 全量元数据 + 可疑字段高亮
import sys, subprocess, json, re
out = subprocess.run(['exiftool', '-j', '-a', '-u', '-g1', sys.argv[1]],
                     capture_output=True, text=True).stdout
meta = json.loads(out)[0]
KEY = re.compile(r'(gps|model|make|software|artist|comment|author|creator|'
                 r'title|desc|date|time|serial|lens|history|flag|key)', re.I)
for k, v in meta.items():
    if KEY.search(k):
        print(f'{k:45s} = {v}')
print('--- 总字段数:', len(meta))
```

```bash
python exif_dump.py target.jpg
```

### 判断是否被编辑

```bash
exiftool -Software -HistoryAction -HistorySoftwareAgent -HistoryWhen target.jpg
# XMP 里有完整编辑步骤
exiftool -XMP -b target.jpg | python3 -c "import sys,re;
print('\n'.join(re.findall(r'<xmp:(?:History|CreatorTool)[^>]*>[^<]*', sys.stdin.read())))"
# ELA（错误级别分析）
pip install imagehash
python3 -c "
from PIL import Image, ImageChops
im = Image.open('target.jpg').convert('RGB')
im.save('resave.jpg', quality=90)
d = ImageChops.difference(im, Image.open('resave.jpg').convert('RGB'))
d = d.point(lambda p: min(255, p*15))
d.save('ela.png')"
```

### 文档元数据

```bash
exiftool -a -u -g1 report.docx
exiftool -a -u -g1 report.pdf
mediainfo video.mp4                          # 视频：编码器/时长/比特率
identify -verbose img.png | head -40          # ImageMagick 视角
exiv2 -pa target.jpg | head -40               # 另一个 EXIF 工具
```

### 清除与伪造（理解题目如何出题）

```bash
exiftool -all= -overwrite_original target.jpg        # 清空所有元数据（慎用）
exiftool -Comment='flag{PLACEHOLDER}' target.jpg     # 写入
exiftool -@ cmds.args target.jpg                     # 批量
```

### 隐藏数据在元数据里

```bash
# Comment 里常见 base64
exiftool -Comment -b target.jpg | base64 -d 2>/dev/null
exiftool -UserComment -b target.jpg | head -c 300
# PNG tEXt / iTXt
exiftool -TextualData -b target.png
# 所有字符串字段拼接
exiftool -a -u -s -G1 target.jpg | grep -vE 'Image (Size|Width|Height)' | cut -d: -f3- | tr -d '\n'
```

## 五、常见坑 / 变体

- **`-n` 与默认输出**：默认是带单位的字符串（`31 deg 13' 43.2"`），`-n` 才是数字。
- **南纬/西经**：`GPSLatitudeRef=S/W` 要取负。
- **时区**：`DateTimeOriginal` 常是**本地时间**（无时区），`OffsetTimeOriginal` 才有偏移。
- **缩略图不一致**：缩略图是未编辑的原图，`-b -ThumbnailImage` 导出来对比。
- **被清空后**：文件头里的 `Exif\0\0` 段可能残留部分数据，用 `-v3` 能看到原始字节。
- **微信/QQ 传输会清元数据**：题目若给"截图"通常没有 EXIF，转为看 XMP 或文件内容。
- **PDF/DOCX 的 XMP**：`pdfinfo` 只看基础信息，要 `exiftool` 或 `qpdf --qdf` 看原始 XMP 包。

## 六、参考来源

- [exiftool 官方文档与字段说明](https://exiftool.org/)
- [exiftool 标签大全（GPS/Exif/XMP 分组）](https://exiftool.org/TagNames/)
- [ExifTool - 元数据标签与标准实现参考](https://exiftool.org/TagNames/EXIF.html)
- [IPTC 照片元数据标准](https://iptc.org/standards/photo-metadata/)
- [exiv2 工具文档](https://exiv2.org/manpage.html)
- [CTF Wiki - 取证隐写前置技术](https://ctf-wiki.org/misc/prefix/)
