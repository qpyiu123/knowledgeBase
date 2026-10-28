---
title: "DataCon24漏洞赛道冠军分享：vuln_wp——大模型赋能的漏洞自动化分析全解析"
category: misc
tags: ["DataCon 2024 漏洞分析赛道冠军", "misc", "llm", "rag", "prompt-engineering", "voting"]
signals: ["DataCon 2024 漏洞分析赛道冠军 2024", "llm", "rag", "prompt-engineering", "voting", "race-condition", "sql-injection", "double-fetch", "buff-overflow", "iot", "DataCon24", "vuln_wp", "LLM", "RAG"]
difficulty: hard
source: "https://www.ctfiot.com/233750.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DataCon24漏洞赛道冠军分享：vuln_wp——大模型赋能的漏洞自动化分析全解析

> 赛事：DataCon 2024 漏洞分析赛道冠军 2024 | 方向：misc | 难度：hard

## 一句话总结

DataCon24冠军 vuln_wp：LLM+RAG+投票+多类型漏洞策略

## 攻击链

1. 0817iotg战队完整框架
2. BeautifulSoup4解析HTML过滤图片
3. 提示工程多维度输出+两次LLM调用
4. 内置投票机制剔除低置信度结果
5. 扩展：版本/修复建议/POC/EXP/图像
6. 文件大小排序+类型过滤+按语言函数切分
7. 提示工程初步筛查+种子函数深度解析
8. 不同漏洞类型(race condition/SQLi/double-fetch/buff-overflow/cmd-injection)不同策略
9. RAG技术+多轮提示+结果投票

## 关键 payload

```
RAG + 多次LLM调用 + 投票 + 漏洞类型策略
```

## 经验教训

漏洞分析LLM框架：HTML解析+提示工程+投票+RAG

## 标签

llm、rag、prompt-engineering、voting、race-condition、sql-injection、double-fetch、buff-overflow

## 参考来源

- https://www.ctfiot.com/233750.html
- 原文件：DataCon24漏洞赛道冠军分享：vuln_wp——大模型赋能的漏洞自动化分析全解析.full.md
