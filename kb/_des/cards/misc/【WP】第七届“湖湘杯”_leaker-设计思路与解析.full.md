---
title: "【WP】第七届\"湖湘杯\" leaker 设计思路与解析"
category: misc
tags: ["湖湘杯", "misc", "digital-watermark", "RGBA-alpha-LSB", "01-matrix-pattern", "period-76-rows"]
signals: ["湖湘杯 2021", "digital-watermark", "RGBA-alpha-LSB", "01-matrix-pattern", "period-76-rows", "2x4-block-ASCII", "leaker-source", "frequency-anti-trim", "stego_image", "leaker", "RGBA", "Alpha", "LSB", "ASCII"]
difficulty: medium
source: "https://www.ctfiot.com/15097.html"
tools: ["Stegsolve"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【WP】第七届"湖湘杯" leaker 设计思路与解析

> 赛事：湖湘杯 2021 | 方向：misc | 难度：medium | 工具：Stegsolve

## 一句话总结

第七届湖湘杯 leaker 数字水印题，RGBA Alpha LSB 提取 01 矩阵 + 2x4 块 ASCII 编码还原。

## 攻击链

1. 1. Stegsolve 读 RGBA 模式 + Alpha 通道只有 255/254 → 最低位藏数据/2. 行重复周期 76 行 + 隔两行重复 → 缩小分析范围/3. 2x4 0 矩阵之间是相同信息 + 每隔 4 位为 0（ASCII 最高位）/4. 解读：1,3,5,7 行 + 2,4,6,8 列 + END 结束

## 关键 payload

```
Alpha LSB 255/254  周期 76 行  2x4 矩阵 ASCII 编码
```

## 经验教训

数字水印 = 抗修改隐写术，重复填充实现任意位置可读；RGBA Alpha 通道 255/254 区分是 LSB 隐写信号；2x4 0 矩阵作为分隔符是常见水印编码方式。

## 标签

digital-watermark、RGBA-alpha-LSB、01-matrix-pattern、period-76-rows、2x4-block-ASCII、leaker-source、frequency-anti-trim

## 参考来源

- https://www.ctfiot.com/15097.html
- 原文件：【WP】第七届“湖湘杯”_leaker-设计思路与解析.full.md
