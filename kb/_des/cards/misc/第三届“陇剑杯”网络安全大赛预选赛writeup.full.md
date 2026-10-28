---
title: "第三届\"陇剑杯\"网络安全大赛预选赛writeup"
category: misc
tags: ["第三届陇剑杯预选赛", "misc", "陇剑杯预选赛", "RC5-32/12/b", "Z3多约束", "popcount"]
signals: ["第三届陇剑杯预选赛 2025", "陇剑杯预选赛", "RC5-32/12/b", "Z3多约束", "popcount", "XXTEA", "pickle反序列化", "Wazuh应急", "PTH哈希传递", "misc_unknown", "writeup", "RC5", "pickle", "Wazuh"]
difficulty: hard
source: "https://www.ctfiot.com/282099.html"
tools: ["Z3"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第三届"陇剑杯"网络安全大赛预选赛writeup

> 赛事：第三届陇剑杯预选赛 2025 | 方向：misc | 难度：hard | 工具：Z3

## 一句话总结

第三届陇剑杯预选赛（另一版writeup）：RC5+Z3+XXTEA+pickle+Wazuh（与同篇WP同主题重复）

## 攻击链

1. RC5-32/12/b→Z3约束求解(22字节flag+popcount)→XXTEA解密→pickle反序列化CHIKAWA→Wazuh日志分析

## 关键 payload

```
flag{7ac1d3e59f0b2468};flag{cbee3251-9cff-4542-bf15-337bb8df7f3f};RC5-32/12/b;Z3多约束+popcount;XXTEA;PSEXESVC
```

## 经验教训

同一比赛不同作者写的writeup会有不同侧重点，可互为补充

## 标签

陇剑杯预选赛、RC5-32/12/b、Z3多约束、popcount、XXTEA、pickle反序列化、Wazuh应急、PTH哈希传递、PSEXESVC

## 参考来源

- https://www.ctfiot.com/282099.html
- 原文件：第三届“陇剑杯”网络安全大赛预选赛writeup.full.md
