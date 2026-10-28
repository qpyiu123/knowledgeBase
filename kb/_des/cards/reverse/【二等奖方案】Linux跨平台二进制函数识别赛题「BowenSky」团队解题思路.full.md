---
title: "CCF BDCI 2022 二等奖 - Linux跨平台二进制函数识别 BowenSky"
category: reverse
tags: ["CCF BDCI 2022 数字安全公开赛", "reverse", "二进制相似性", "图神经网络", "Bi-LSTM", "GatedGCN"]
signals: ["CCF BDCI 2022 数字安全公开赛 2022", "二进制相似性", "图神经网络", "Bi-LSTM", "GatedGCN", "度量学习", "MS_loss", "ACFG", "孪生网络", "reverse", "NETSEC", "GatedGCN-E", "CFG", "Multi-Similarity"]
difficulty: hard
source: "https://www.ctfiot.com/124838.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# CCF BDCI 2022 二等奖 - Linux跨平台二进制函数识别 BowenSky

> 赛事：CCF BDCI 2022 数字安全公开赛 2022 | 方向：reverse | 难度：hard

## 一句话总结

上海交大NETSEC实验室用Bi-LSTM+GatedGCN+MS_loss在二进制函数相似性检测拿二等奖第4。

## 攻击链

1. 指令标准化 → Bi-LSTM提取基本块语义 → GatedGCN-E提取CFG结构 → Multi-Similarity采样 → MS损失反向传播 → 余弦相似度搜索

## 关键 payload

```
指令标准化(12532词表) + Bi-LSTM 2层128维 + GatedGCN 3层128维 + MS ε=0.1 α=2 β=50
```

## 经验教训

二进制函数相似性检测 = 度量学习;MS miner比Norm weighted miner更关注信息量大的样本对(0.883 vs 0.856);MS loss比Triplet loss更强(0.923 vs 0.883);Bi-LSTM+GatedGCN仅2.6M参数+11MB模型,CPU推理123ms/GPU 8ms;指令标准化大幅降词表。

## 标签

二进制相似性、图神经网络、Bi-LSTM、GatedGCN、度量学习、MS_loss、ACFG、孪生网络、jTrans、反汇编、跨平台

## 参考来源

- https://www.ctfiot.com/124838.html
- 原文件：【二等奖方案】Linux跨平台二进制函数识别赛题「BowenSky」团队解题思路.full.md
