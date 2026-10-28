---
title: "第三届\"陇剑杯\"网络安全大赛预选赛 WP"
category: misc
tags: ["第三届陇剑杯预选赛", "misc", "陇剑杯预选赛", "RC5-32/12/b算法", "Z3约束求解", "多约束校验"]
signals: ["第三届陇剑杯预选赛 2025", "陇剑杯预选赛", "RC5-32/12/b算法", "Z3约束求解", "多约束校验", "XXTEA", "pickle反序列化", "Wazuh日志分析", "PTH哈希传递", "deserialize", "RC5-32", "pickle", "Wazuh", "key_schedule"]
difficulty: hard
source: "https://www.ctfiot.com/270386.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第三届"陇剑杯"网络安全大赛预选赛 WP

> 赛事：第三届陇剑杯预选赛 2025 | 方向：misc | 难度：hard

## 一句话总结

第三届陇剑杯预选赛：RC5-32/12/b+Z3多约束+XXTEA+pickle反序列化+Wazuh应急响应

## 攻击链

1. RC5-32/12/b key_schedule→decrypt_buffer→PKCS#7去填充→Z3约束求解(22字节flag+5个mvals+7个xvals+32位popcount)→XXTEA解密→pickle反序列化CHIKAWA→Wazuh日志分析

## 关键 payload

```
RC5-32/12/b rol32/ror32/0xB7E15163;flag{7ac1d3e59f0b2468};flag{cbee3251-9cff-4542-bf15-337bb8df7f3f};PSEXESVC;data.win.system.eventID:7045;hash attack事件ID=1734511987.34749419
```

## 经验教训

RC5算法key_schedule+decrypt块解密；Z3约束+popcount处理32位校验

## 标签

陇剑杯预选赛、RC5-32/12/b算法、Z3约束求解、多约束校验、XXTEA、pickle反序列化、Wazuh日志分析、PTH哈希传递、PSEXESVC

## 参考来源

- https://www.ctfiot.com/270386.html
- 原文件：第三届“陇剑杯”网络安全大赛预选赛_WP.full.md
