---
title: "CCF BDCI 2022 三等奖 - AI漏洞数据分类 susy战队"
category: misc
tags: ["CCF BDCI 2022 数字安全公开赛", "misc", "CVE", "漏洞分类", "TF-IDF", "词向量"]
signals: ["CCF BDCI 2022 数字安全公开赛 2022", "CVE", "漏洞分类", "TF-IDF", "词向量", "集成模型", "LightGBM", "NLP", "privilege_required", "misc_unknown"]
difficulty: medium
source: "https://www.ctfiot.com/125871.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# CCF BDCI 2022 三等奖 - AI漏洞数据分类 susy战队

> 赛事：CCF BDCI 2022 数字安全公开赛 2022 | 方向：misc | 难度：medium

## 一句话总结

北工大硕士+中大博士用TF-IDF+集成学习做CVE漏洞三级分类,线上第3。

## 攻击链

1. 加载数据 → TF-IDF构造词向量 → 降维 → 提取CVE编号特征 → 词向量+人工特征拼接 → 三个字段分别训练分类器 → 阈值调整 → 合并结果

## 关键 payload

```
TF-IDF(降维) + LightGBM分类 + 三级标签分开训练
```

## 经验教训

漏洞分类三级标签分开训练比合并训练效果好;TF-IDF降维既降内存又加速训练;集成模型相对深度网络速度更快、性能更稳定;换榜后不易过拟合。

## 标签

CVE、漏洞分类、TF-IDF、词向量、集成模型、LightGBM、NLP、privilege_required、attack_vector、impact

## 参考来源

- https://www.ctfiot.com/125871.html
- 原文件：【三等奖方案】基于人工智能的漏洞数据分类赛题「susy」团队解题思路.full.md
