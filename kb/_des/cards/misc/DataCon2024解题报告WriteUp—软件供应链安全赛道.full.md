---
title: "DataCon2024解题报告WriteUp—软件供应链安全赛道"
category: misc
tags: ["DataCon 2024", "misc", "supply-chain", "npm", "pypi", "llm"]
signals: ["DataCon 2024 2024", "supply-chain", "npm", "pypi", "llm", "mphunter", "guarddog", "obs", "typosquatting", "misc_unknown", "DataCon2024", "PyPI", "LLM", "MPHunter"]
difficulty: hard
source: "https://www.ctfiot.com/224419.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DataCon2024解题报告WriteUp—软件供应链安全赛道

> 赛事：DataCon 2024 2024 | 方向：misc | 难度：hard

## 一句话总结

DataCon2024软件供应链：npm/PyPI恶意包检测+LLM辅助+MPHunter

## 攻击链

1. 第一章：赛题介绍
2. 第二章：总体思路
3. 第三章：解题详述
4. MPHunter：恶意PyPI包聚类
5. npm软件包文件结构分析
6. LLM对NodeJS代码威胁评分
7. OBS（Obfuscation）代码检测
8. PyPI恶意包相似性匹配
9. 基于多源规则拓展匹配
10. 第四章：未标注新恶意包样本
11. LLM 增强数据集 Maltracker
12. guarddog规则+LLM辅助
13. 高度相似依赖识别

## 关键 payload

```
LLM 评分NodeJS代码+多源规则匹配+相似性聚类
```

## 经验教训

LLM辅助+规则匹配+相似性聚类是供应链安全3大武器

## 标签

supply-chain、npm、pypi、llm、mphunter、guarddog、obs、typosquatting

## 参考来源

- https://www.ctfiot.com/224419.html
- 原文件：DataCon2024解题报告WriteUp—软件供应链安全赛道.full.md
