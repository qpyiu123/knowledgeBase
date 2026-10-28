---
title: "第三届\"数信杯\"数据安全大赛wp之ai模型"
category: misc
tags: ["第三届数信杯数据安全大赛", "misc", "数信杯", "AI模型", "MultimodalMLP", "3层MLP"]
signals: ["第三届数信杯数据安全大赛 2025", "数信杯", "AI模型", "MultimodalMLP", "3层MLP", "R通道mod10", "LSB隐写", "PyTorch", "27字符flag", "stego", "mod10", "MLP", "flag", "mod"]
difficulty: medium
source: "https://www.ctfiot.com/295618.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第三届"数信杯"数据安全大赛wp之ai模型

> 赛事：第三届数信杯数据安全大赛 2025 | 方向：misc | 难度：medium

## 一句话总结

第三届数信杯AI模型：图片R通道mod10提取20维特征+3层MLP推理+27字符flag

## 攻击链

1. 取图片左上角前20个像素R值→R mod 10得到20维特征→MultimodalMLP模型推理(20→64→32→27)→输出27个数值取整→chr()转为flag

## 关键 payload

```
MultimodalMLP:fc1=Linear(20,64) fc2=Linear(64,32) fc3=Linear(32,27) ReLU;R mod 10得20维特征;round(v.item())取整转ASCII;27字符flag
```

## 经验教训

AI隐写赛=特征提取(R通道mod10)+轻量MLP推理(3层Linear+ReLU)+输出转ASCII

## 标签

数信杯、AI模型、MultimodalMLP、3层MLP、R通道mod10、LSB隐写、PyTorch、27字符flag、stego

## 参考来源

- https://www.ctfiot.com/295618.html
- 原文件：第三届“数信杯”数据安全大赛wp之ai模型.full.md
