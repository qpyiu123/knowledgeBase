---
title: "【Hardware】CrewCTF 2024 Sniff One && Sniff Two"
category: misc
tags: ["CrewCTF", "misc", "hardware", "logic-analyzer", "Saleae", "SPI-sniff"]
signals: ["CrewCTF 2024", "hardware", "logic-analyzer", "Saleae", "SPI-sniff", "RGB-encoding", "two-bit-plane", "color-decode", "numpy-packbits", "misc_unknown", "CrewCTF", "Sniff", "One", "Two"]
difficulty: hard
source: "https://www.ctfiot.com/213017.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【Hardware】CrewCTF 2024 Sniff One && Sniff Two

> 赛事：CrewCTF 2024 | 方向：misc | 难度：hard

## 一句话总结

CrewCTF 2024 硬件题 Sniff One/Two，逻辑分析仪抓 SPI 信号 + numpy 双 bit 平面重组 136x249 RGB 图像。

## 攻击链

1. Saleae 逻辑分析仪抓 SPI/MOSI 信号 + 解析时钟 + 双 bit 平面 (黑/红) numpy 重组 + 136x249 RGB 图像还原 + 隐藏 flag 在色块内容中

## 关键 payload

```
width=136 height=249  buf_a 黑平面 buf_b 红平面  color_mapping = {0: 白, 1: 黑, 2: 红}
```

## 经验教训

Saleae Logic 2 导出 raw binary 后用 numpy packbits/unpackbits 重组位平面；RGB 双通道编码（黑/红）是硬件 LCD 显示常见方案；136x249 是常见电子墨水屏分辨率。

## 标签

hardware、logic-analyzer、Saleae、SPI-sniff、RGB-encoding、two-bit-plane、color-decode、numpy-packbits、PIL-Image

## 参考来源

- https://www.ctfiot.com/213017.html
- 原文件：【Hardware】CrewCTF_2024_Sniff_One_&&_Sniff_Two.full.md
