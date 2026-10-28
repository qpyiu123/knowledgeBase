---
title: "DataCon24供应链安全赛道亚军源码分享：MalNPMDetector NPM恶意软件包检测"
category: misc
tags: ["DataCon 2024 供应链安全赛道亚军", "misc", "npm", "supply-chain", "chatgpt", "static-rule"]
signals: ["DataCon 2024 供应链安全赛道亚军 2024", "npm", "supply-chain", "chatgpt", "static-rule", "taint-analysis", "dynamic-analysis", "malicious-package", "misc_unknown", "DataCon24", "MalNPMDetector", "ChatGPT", "prompt"]
difficulty: hard
source: "https://www.ctfiot.com/233929.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DataCon24供应链安全赛道亚军源码分享：MalNPMDetector NPM恶意软件包检测

> 赛事：DataCon 2024 供应链安全赛道亚军 2024 | 方向：misc | 难度：hard

## 一句话总结

DataCon24亚军 MalNPMDetector：静态规则+污点分析+ChatGPT+动态分析

## 攻击链

1. 第一步：高效静态规则匹配大样本初步过滤可疑包
2. 第二步：基于字符串的污点分析收缩范围
3. 第三步：构造prompt提交ChatGPT验证恶意性
4. 学习新恶意特征更新静态规则
5. 针对混淆包采用动态分析确认
6. https://gitee.com/jenniedn/mal-npmdetector.git

## 关键 payload

```
static_rule → taint_analysis → ChatGPT_verify → dynamic_analysis
```

## 经验教训

供应链安全需4步漏斗：粗筛+精筛+LLM+动态

## 标签

npm、supply-chain、chatgpt、static-rule、taint-analysis、dynamic-analysis、malicious-package

## 参考来源

- https://www.ctfiot.com/233929.html
- 原文件：DataCon24供应链安全赛道亚军源码分享：MalNPMDetector_NPM恶意软件包检测.full.md
