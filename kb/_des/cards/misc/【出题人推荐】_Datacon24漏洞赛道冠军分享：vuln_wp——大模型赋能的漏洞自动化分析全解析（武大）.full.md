---
title: "【出题人推荐】Datacon24 漏洞赛道冠军分享 vuln_wp 大模型赋能的漏洞自动化分析全解析"
category: misc
tags: ["DataCon", "misc", "大模型-AI", "BeautifulSoup4-HTML-parse", "多轮LLM调用", "投票机制"]
signals: ["DataCon 2024", "大模型-AI", "BeautifulSoup4-HTML-parse", "多轮LLM调用", "投票机制", "RAG检索增强", "函数级别切分", "race-condition", "SQLi", "sqli", "DataCon", "IOTG", "BeautifulSoup4", "HTML"]
difficulty: hard
source: "https://www.ctfiot.com/233200.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【出题人推荐】Datacon24 漏洞赛道冠军分享 vuln_wp 大模型赋能的漏洞自动化分析全解析

> 赛事：DataCon 2024 | 方向：misc | 难度：hard

## 一句话总结

DataCon 2024 漏洞分析赛道冠军（武大 0817 IOTG）大模型赋能漏洞自动化分析全套方案。

## 攻击链

1. 1. BeautifulSoup4 解析 HTML 过滤图片/2. 多轮大模型调用 + 投票机制降低误报/3. 文件大小排序 + 类型过滤 + 函数级别切分/4. 提示工程初筛种子函数/5. 不同漏洞类型 (race condition / SQLi / double-fetch / buff overflow / command injection) 不同分析策略/6. RAG + 多轮提示 + 结果投票

## 关键 payload

```
0817iotg  datacon24_vuln_wp  multi-LLM-call + voting
```

## 经验教训

大模型 + 投票机制 + RAG + 多轮提示是 AI 漏洞挖掘黄金组合；BeautifulSoup 解析 + 函数级切分 + 类型过滤是预处理三件套；多漏洞类型差异化策略。

## 标签

大模型-AI、BeautifulSoup4-HTML-parse、多轮LLM调用、投票机制、RAG检索增强、函数级别切分、race-condition、SQLi、double-fetch、buff-overflow、command-injection

## 参考来源

- https://www.ctfiot.com/233200.html
- 原文件：【出题人推荐】_Datacon24漏洞赛道冠军分享：vuln_wp——大模型赋能的漏洞自动化分析全解析（武大）.full.md
