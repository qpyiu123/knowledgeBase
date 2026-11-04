---
title: 方法卡 · EXIF/文档元数据取证
category: forensics
tags: [exif, 元数据, xmp, gps, 溯源, 文档属性]
signals:
  - "题面问照片在哪拍的、什么时候拍的"
  - "需要判断图片是否被编辑过（Software 字段）"
  - "附件是 docx/pdf，要问作者是谁、用什么软件做的"
  - "题面提示 metadata、look at the details"
  - "GPS 显示 31 deg 13' 43.2\" 这种度分秒格式"
  - "缩略图与主图内容不一致"
difficulty: easy
source: kb/forensics/exif-metadata.md
updated: 2026-11-03
tools: [python3, exiftool, exiv2, mediainfo]
---
## 适用场景

题目给照片/文档，问题落在"谁、何时、何地、用什么做的"。EXIF 是相机写入的拍摄参数，
XMP 是 Adobe 的 XML 扩展（记录编辑历史），Office/PDF 有 docProps 与 /Info 字典。
这三处经常残留作者、设备、坐标、编辑软件，是取证题的第一落点。

## 前置条件

- 拿到**原始文件**：微信/QQ 传输会清元数据，截图基本没有 EXIF。
- `exiftool` 可用时优先全量打印：`exiftool -a -u -g1 file`。
- 无 exiftool 时用本卡脚本（纯标准库），可解析 JPEG APP1(Exif)、PNG tEXt/iTXt、
  PDF /Info 与 XMP 字面量、DOCX core.xml。

## 步骤

1. **认容器**：JPEG 看 APP1 段 `Exif\0\0`；PNG 看 tEXt/iTXt；DOCX 是 zip，
   元数据在 `docProps/core.xml`；PDF 看 `/Info` 与 `xmpmeta`。
2. **打印关键字段**：Make/Model/DateTimeOriginal/GPS*/Software/Artist/Comment。
3. **换算坐标**：EXIF 里 GPS 是度分秒有理数，十进制度 = DD + MM/60 + SS/3600；
   `GPSLatitudeRef=S/W` 要取负。换算完再拼地图链接核对是否合理。
4. **判一致性**：`DateTimeOriginal` 是本地时间，只有 `OffsetTimeOriginal` 才带偏移；
   文件 mtime 与拍摄时间矛盾、缩略图和主图不一致，都说明图被改过。
5. **判编辑痕迹**：`Software = Adobe Photoshop 25.0` 说明被重新编辑过；
   XMP `photoshop:History` 会列出每一步操作；APP12/Ducky 段常见于加水印的图。
6. **找隐藏数据**：Comment/ImageDescription 里常是 base64 或 flag 明文，
   解一层再交给 `enc_chain_decode`。

## 立即可用脚本

`kb/_methods/scripts/exif_metadata.py`（纯标准库，只读）

```
python exif_metadata.py --file photo.jpg
python exif_metadata.py --file photo.jpg --gps
python exif_metadata.py --file doc.docx --keyword author,creator
python exif_metadata.py --dms 31 13 43.2 --ref S
python exif_metadata.py --selftest
```

参数：

- `--file`：目标文件（JPEG/PNG/PDF/DOCX，按文件头判断，忽略扩展名）。
- `--keyword`：逗号分隔前缀过滤，例如 `gps,software`。
- `--gps`：只打印 GPS 相关字段（含换算后的十进制度）。
- `--dms D M S --ref N|S|E|W`：手算换算，S/W 自动取负。
- `--selftest`：内置断言。

失败行为：认不出格式、TIFF 头非法、分秒越界、docx 缺 core.xml，都在 stderr 打印
`失败：…` 并返回 2；自检通过打印 `selftest ok: …` 返回 0。

## 手工示例

```
$ exiftool -GPS* -n target.jpg
GPS Latitude Ref  : South
GPS Latitude      : 31.228667
GPS Longitude     : 121.474833
$ python exif_metadata.py --file target.jpg --gps
格式: jpeg
  GPSLatitude           = (31.0, 13.0, 43.2)
  GPSLatitudeDD         = -31.228667      # Ref=S 已取负
  GPSLongitudeDD        = 121.474833
  ! Software=Adobe Photoshop → 被重新编辑/生成过
```

## 失效场景

- 文件经过社交软件转发、截图、EXIF 清除工具处理：字段为空，只能转 XMP/内容分析。
- 坐标是伪造的或 Ref 缺失：只能结合画面地标判断，不能单凭元数据下结论。
- 加权平均：`GPSLatitude` 有时只存度分（两元素），换算要按实际元素个数处理。
- 加密 PDF / 加固 docx：/Info 与 core.xml 读不到，需要先解密/解压。

## 相关文档

- `kb/forensics/steganalysis-workflow.md`：元数据层在隐写流程中的位置。
- `kb/forensics/file-carving.md`：元数据被删后如何从镜像里回捞。
- `kb/_methods/enc_chain_decode.md`：Comment 里解出的编码继续逐层解。

## 目录与收录说明

- 卡片：`kb/_methods/exif-metadata.md`；脚本：`kb/_methods/scripts/exif_metadata.py`。
- 对应 backlog 项 `exif-metadata`（category=forensics），源文档 `kb/forensics/exif-metadata.md`。
