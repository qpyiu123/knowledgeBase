---
title: "小样本专利数据分类 CCF BDCI 2022 一等奖方案"
category: misc
tags: ["CCF-BDCI", "misc", "NLP", "few-shot", "patent-classification", "Nezha"]
signals: ["CCF-BDCI 2022", "NLP", "few-shot", "patent-classification", "Nezha", "ERNIE-Gram", "Bert-for-patents", "AWP", "SWA", "misc_unknown", "CCF", "BDCI", "title", "assignee"]
difficulty: medium
source: "https://www.ctfiot.com/133251.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 小样本专利数据分类 CCF BDCI 2022 一等奖方案

> 赛事：CCF-BDCI 2022 | 方向：misc | 难度：medium

## 一句话总结

5 个中文+英文预训练模型集成 + 领域预训练 + AWP/SWA + 伪标签，小样本专利分类 CCF BDCI 2022 一等奖。

## 攻击链

1. 数据：958 条专利训练 + 20839 测试 + 20890 复赛，36 类脱敏标签，长尾分布
2. 短文本（title+assignee+abstract 拼接 ≤ 657 字符）
3. 5 个模型 Nezha / Ernie-Gram-zh / Ernie-3.0-xbase-zh / Bert-for-patents / Chinese-RoBERTa-wwm-ext-large
4. 阶段 1：通用预训练 → 阶段 2：领域预训练（用测试集增量 MLM）→ 阶段 3：领域微调
5. Bert-for-patents 翻译为英文后 5 段输入（title+assignee+head+body+tail）
6. 优化：AWP Embedding+model 双扰动 + SWA 局部最优集成 + Multi-Sample Dropout
7. 集成：加权平均（Ernie-gram/xbase 权重小）+ 二阶段伪标签（先训练集训练模型集成生成第一阶段伪标签）
8. 第二阶段伪标签：训练集 + 初赛 70% 伪标签 + 复赛 70% 伪标签训练 Nezha 10 折集成
9. 最终 5 折 Ernie-Gram-zh + 伪标签数据训练
10. 复赛 macro F1 = 0.61387745 排名第一

## 关键 payload

```
macro F1 = 0.61387745 第一名, 模型 < 2GB
```

## 经验教训

小样本学习的关键是数据增强（伪标签）+ 模型多样性（5 个不同架构）+ 鲁棒性优化（AWP+SWA+MSD）。

## 标签

NLP、few-shot、patent-classification、Nezha、ERNIE-Gram、Bert-for-patents、AWP、SWA、multi-sample-dropout、pseudo-label、model-ensemble、CCF-BDCI

## 参考来源

- https://www.ctfiot.com/133251.html
- 原文件：【一等奖方案】小样本数据分类任务赛题「nlp小菜鸡」团队解题思路.full.md
