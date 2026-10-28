---
title: "CCF BDCI 2022 二等奖 - TPU人群密度估计 ChaMd5-AI"
category: misc
tags: ["CCF BDCI 2022 (第十届CCF大数据与计算智能大赛)", "misc", "TPU", "人群密度估计", "FLOPs", "Network_Activations"]
signals: ["CCF BDCI 2022 (第十届CCF大数据与计算智能大赛) 2022", "TPU", "人群密度估计", "FLOPs", "Network_Activations", "遗传算法", "量化", "伪真值模型", "RegNet", "misc_unknown", "Network", "Activations", "VGG"]
difficulty: medium
source: "https://www.ctfiot.com/122999.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# CCF BDCI 2022 二等奖 - TPU人群密度估计 ChaMd5-AI

> 赛事：CCF BDCI 2022 (第十届CCF大数据与计算智能大赛) 2022 | 方向：misc | 难度：medium

## 一句话总结

华中科大博士用遗传算法+Network Activations在TPU人群密度估计上第3名,得分252.14。

## 攻击链

1. 粗指标(FLOPs+Network Activations)选VGG → 训练大尺度伪真值模型 → 量化转fp32bmodel → 遗传算法(200代/种群35/交叉0.4/变异0.2/格雷码)搜索超参数 → 适应度=粗指标+MSE对比伪真值

## 关键 payload

```
VGG + fp32bmodel + 格雷码遗传算法 + Network Activations访存指标
```

## 经验教训

TPU平台低FLOPs≠低推理时间 — depth-wise类(EfficientNet)在TPU上因访存带宽限制实际更慢;Network Activations(网络激活总量)作为访存代理指标更准;量化参数优化用遗传算法+伪真值模型比网格搜索更高效;大权重FLOPs+小权重Network Activations反sigmoid融合。

## 标签

TPU、人群密度估计、FLOPs、Network_Activations、遗传算法、量化、伪真值模型、RegNet、VGG、算能芯片

## 参考来源

- https://www.ctfiot.com/122999.html
- 原文件：【二等奖方案】基于TPU平台实现人群密度估计赛题「ChaMd5-AI」团队解题思路.full.md
