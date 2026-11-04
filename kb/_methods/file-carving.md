---
title: 方法卡 · 磁盘镜像文件雕刻与恢复
category: forensics
tags: [文件雕刻, foremost, binwalk, blkls, 数据恢复, 签名扫描]
signals:
  - "题目给磁盘镜像或内存 dump，说有一个文件被删了"
  - "fls 列不出目标文件，但 strings 能看到 PK、%PDF"
  - "文件系统损坏 mount 失败，只能按字节处理"
  - "binwalk -e 只分离出一部分，需要按签名扫全盘"
  - "镜像里有 PNG 头但 pngcheck 报 IEND 缺失"
  - "foremost 报告的偏移与审计日志对不上"
difficulty: medium
source: kb/forensics/file-carving.md, kb/misc/file-repair-and-corruption.md
updated: 2026-11-03
tools: [python3, foremost, scalpel, photorec, binwalk, blkls, pngcheck]
---
## 适用场景

文件被删、分区表损坏、内存 dump 里有 zip 片段——文件系统层已经不可信，
只能按**文件签名（magic）+ 结构长度**从原始字节流里切出文件。这就是文件雕刻：
不依赖目录项，只看"头在哪、尾在哪、中间长度自不自洽"。

## 前置条件

- 原始镜像（`dd` / `E01` 转换后的裸镜像），不要对已挂载的读写盘操作。
- 知道分区布局时先用 `mmls` 取分区起止，缩小搜索范围。
- 记录工作副本的 SHA-256，后续所有输出基于副本，保证可复现。
- 有 `foremost`/`scalpel` 时交叉验证；本卡脚本用于无工具环境和精确控制。

## 步骤

1. **定范围**：`mmls disk.img` 看分区；只想雕未分配区时
   `blkls -o START disk.img > unalloc.dd`，数据量能小一个数量级。
2. **先扫描后落盘**：本卡脚本 `--list` 只报偏移与大小，确认数量和位置合理再 `--out`。
3. **按类型定尾**：JPEG 看 `FF D9`，PNG 看 `IEND`+CRC，PDF 看 `%%EOF`，
   GZIP 用解压得到的 `unused_data` 反推真实结束，ZIP 必须回扫 EOCD
   （`PK\x05\x06` 之后 22 字节 + 注释长度才是文件尾）。
4. **拒绝脏文件**：头部命中但尾部找不到的结构直接跳过，不要产出半截文件去误导后续分析。
5. **验证**：`file`、`pngcheck -q`、`unzip -t`、`pdfinfo` 过一遍，只保留完整可用的。
6. **修复碎片**：单段切出损坏（CRC 错/解压失败）说明文件不连续，需要按簇序重排，
   这是研究级问题；先回到 blkls 看块序列，再考虑手工拼接。

## 立即可用脚本

`kb/_methods/scripts/file_carving.py`（纯标准库）

```
python file_carving.py --image disk.img --list
python file_carving.py --image disk.img --types png,jpg,zip --out out/
python file_carving.py --image mem.dump --types gzip --min-size 1024 --out out/
python file_carving.py --selftest
```

参数：

- `--image`：镜像/内存 dump 路径（必填，除非 `--selftest`）。
- `--types`：逗号分隔，支持 png/jpg/pdf/zip/gzip，默认全开。
- `--out`：输出目录（不给就只打印偏移与大小，不落盘）。
- `--min-size`：小于该字节数的候选丢弃，默认 1，负数报错。
- `--list`：强制只列偏移。
- `--selftest`：内置断言。

失败行为：类型不支持、`--min-size` 为负、镜像读不到，stderr 打印 `失败：…` 返回 2；
自检通过打印 `selftest ok: …` 返回 0。脚本只写 `--out` 目录内的新文件，不删不改输入。

## 手工示例

```
$ foremost -t png,zip -i unalloc.dd -o out/
$ cat out/audit.txt | head -5
00000037  png  324
000001ff  zip  158
$ python file_carving.py --image unalloc.dd --types png --list
png  off=37         size=324
共 1 个候选（仅列偏移）
$ python file_carving.py --image unalloc.dd --types png --out carved/
png  carved/png_0_25.png                         324 字节    # 偏移十六进制
```

## 失效场景

- 文件在磁盘上碎片化：单段切出会缺中间数据块，CRC/解压必然失败，需要按簇重组。
- 文件头被覆写（只残留尾标记）：只能靠尾标记反推，成功率低，改用 `photorec`。
- 压缩/加密容器（zip 加密、gzip 分段）：结构不可读时定位不到 EOCD 或结束位置。
- 与普通数据误判：镜像里本来就含大量 `PK\x03\x04` 的容器数据时，候选会暴增，
  需要结合 `--min-size` 与文件系统时间线过滤。

## 相关文档

- `kb/misc/file-repair-and-corruption.md`：切出来的半截文件如何按 CRC/宽高修复。
- `kb/forensics/steganalysis-workflow.md`：容器层与尾部追加数据的处理。
- `kb/_methods/decompress_chain.md`：gz/zip 多层嵌套继续解。

## 目录与收录说明

- 卡片：`kb/_methods/file-carving.md`；脚本：`kb/_methods/scripts/file_carving.py`。
- 对应 backlog 项 `file-carving`（category=forensics），源文档
  `kb/forensics/file-carving.md` 与 `kb/misc/file-repair-and-corruption.md`。
