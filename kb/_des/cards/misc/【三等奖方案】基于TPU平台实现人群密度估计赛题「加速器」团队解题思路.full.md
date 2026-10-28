---
title: "CCF BDCI 2022 三等奖 - TPU 人群密度估计 加速器团队"
category: misc
tags: ["CCF BDCI 2022 (第十届CCF大数据与计算智能大赛)", "misc", "TPU", "VGG16", "模型加速", "输入尺度"]
signals: ["CCF BDCI 2022 (第十届CCF大数据与计算智能大赛) 2022", "TPU", "VGG16", "模型加速", "输入尺度", "batch_size", "BMODEL", "算能芯片", "图像预处理", "misc_unknown", "VGG", "batch", "size"]
difficulty: medium
source: "https://www.ctfiot.com/123014.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# CCF BDCI 2022 三等奖 - TPU 人群密度估计 加速器团队

> 赛事：CCF BDCI 2022 (第十届CCF大数据与计算智能大赛) 2022 | 方向：misc | 难度：medium

## 一句话总结

高级工程师单挑用VGG+精确尺寸组合在算能TPU上拿下三等奖。

## 攻击链

1. 选定VGG → 试不同batch size → 调整预处理图片最大/最小尺寸 → 调整模型输入尺寸 → 找到最佳组合

## 关键 payload

```
VGG + 预处理最大780×780 + 最小144×144 + 模型输入144×144
```

## 经验教训

模型加速首先选对基础模型 — 直接转FP32bmodel对比4个模型(CANNet/CSRNet/MCNN/VGG)选VGG;batch_size从1换8反而速度加倍,故放弃;预处理图片最大/最小尺寸+模型输入尺寸的组合对最终成绩影响最大。

## 标签

TPU、VGG16、模型加速、输入尺度、batch_size、BMODEL、算能芯片、图像预处理

## 参考来源

- https://www.ctfiot.com/123014.html
- 原文件：【三等奖方案】基于TPU平台实现人群密度估计赛题「加速器」团队解题思路.full.md
