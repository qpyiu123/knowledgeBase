---
title: "DataCon 2023漏洞分析赛题二官方题解"
category: misc
tags: ["DataCon 2023 漏洞分析", "misc", "openwrt", "codeql", "joern", "cypher"]
signals: ["DataCon 2023 漏洞分析 2023", "openwrt", "codeql", "joern", "cypher", "strcat", "memmove", "system", "popen", "misc_unknown", "DataCon", "OpenWrt", "CodeQL"]
difficulty: hard
source: "https://www.ctfiot.com/148134.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DataCon 2023漏洞分析赛题二官方题解

> 赛事：DataCon 2023 漏洞分析 2023 | 方向：misc | 难度：hard

## 一句话总结

DataCon 2023漏洞分析题二：OpenWrt魔改+CodeQL参数特征查询

## 攻击链

1. OpenWrt源码魔改题目
2. 设置3种固定漏洞模式
3. 第一种: strcat第二参数是变量
4. match (n:identifier) where n.callee="strcat" and n.index=1
5. 第二种: memmove第三参数是变量且不基于size申请
6. match (n:identifier) where n.callee="memmove" and n.index=2
7. 第三种: system/popen第一参数是变量
8. 漏洞1+2: odhcpd
9. 0x000036A9 odhcpd
10. 0x000035F9

## 关键 payload

```
match (n:identifier) where n.callee="strcat" and n.index=1
```

## 经验教训

CodeQL+Joern按callee+index查询是漏洞分析高效模式

## 标签

openwrt、codeql、joern、cypher、strcat、memmove、system、popen、odhcpd

## 参考来源

- https://www.ctfiot.com/148134.html
- 原文件：DataCon_2023漏洞分析赛题二官方题解.full.md
