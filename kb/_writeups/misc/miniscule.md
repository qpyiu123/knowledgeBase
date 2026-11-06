---
title: "Miniscule：PNG 的数据用了另一种压缩"
category: "misc"
kind: "writeup"
tags: ["PNG 修复", "IDAT", "Zstandard"]
signals: ["压缩方法 1", "28 B5 2F FD"]
source: "https://github.com/TJCSec/tjctf-2023-challenges/tree/main/forensics/miniscule"
origin_id: "r66-miniscule"
relates_to: ["misc/file-repair-and-corruption.md"]
verification: "本机原附件回验"
---

# Miniscule：PNG 的数据用了另一种压缩

TJCTF 2023 · 杂项 · [赛事目录](https://github.com/TJCSec/tjctf-2023-challenges/tree/main/forensics/miniscule)。本机已重建 800×800 图片，解码器可打开，图片底部能读到答案。

## 先看这一步

PNG 外壳无误，但 IDAT 里面是 Zstandard。先还原行数据，再用 PNG 要求的 zlib 重压；只改校验值打不开。

**适用时**：已确认真实压缩算法，且解压长度符合图像头。 **留意**：CRC 正确不能代替图像解码。

文件有正确的 PNG 签名，只含 `IHDR`（图像头）、`IDAT`（压缩图像数据）和 `IEND`（结束块）。图像头却把压缩方法写成 1。按 [PNG 规范](https://www.w3.org/TR/png/)，标准方法是 0，对应 zlib 包装的压缩数据。改一个字节再重算 CRC（校验值）不够，因为里面的数据仍按原算法压缩。

1. 读取 `IDAT` 开头，实际是 `28 B5 2F FD`，对应 Zstandard（另一种压缩格式）。
2. 解压后得到 1,920,800 字节，正好等于 `800*(800*3+1)`：每行 800 个 RGB 像素，各占 3 字节，行首还有一个滤波类型字节。
3. 把解压后的行数据用 zlib 重新压缩，图像头的方法改成 0，按块重写长度和 CRC。保留原图像尺寸、颜色类型和滤波数据。

最后用独立解码器打开重建的图片，确认能读出完整一帧。先验数据长度，再验解码；CRC 正确只说明块里的字节与校验值相符。

## 配套代码

`kb/_code/r66/misc_samples.py`。从代码所在目录运行 `python misc_samples.py miniscule 原附件 --zstd 动态库路径`。依赖见脚本开头；运行后会显示核对结果。
