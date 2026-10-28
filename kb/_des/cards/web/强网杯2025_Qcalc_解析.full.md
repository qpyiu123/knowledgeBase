---
title: "强网杯2025 Qcalc 解析 - Android Content URI授权+历史.yml反序列化"
category: web
tags: ["强网杯2025", "web", "Android", "ExploitActivity", "deeplink", "qiangcalc://"]
signals: ["强网杯2025 2025", "Android", "ExploitActivity", "deeplink", "qiangcalc://", "content://", "history.yml", "ContentResolver", "openOutputStream", "web_unknown", "Qcalc", "Content", "URI", "YAML"]
difficulty: hard
source: "https://www.ctfiot.com/287018.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 强网杯2025 Qcalc 解析 - Android Content URI授权+历史.yml反序列化

> 赛事：强网杯2025 2025 | 方向：web | 难度：hard

## 一句话总结

强网杯2025 Qcalc:Android Content URI授权链(YAML history.yml)绕过读flag,核心在1800ms divide-by-zero触发BridgeActivity+550ms读grantedUri。

## 攻击链

1. 构造deeplink qiangcalc://calculate?expression=Intent.toUri(带bridge_token) → 启动ExploitActivity存fallback → 延时1800ms触发1/0 divide-by-zero → 受害端进入BridgeActivity,授予content://.../history.yml读写并回调ExploitActivity → ExploitActivity写恶意YAML(覆盖包名+ExploitActivity) → 触发2+2让受害端loadHistory()->PingUtil读flag → 550ms后回调读grantedUri获取flag → nc外传

## 关键 payload

```
content://history.yml ContentResolver授权 + YAML反序列化 + 1800ms divide-by-zero异常触发
```

## 经验教训

Android Content URI授权漏洞利用链:deeplink触发+fallback Intent存储+divide-by-zero异常进入BridgeActivity+ContentResolver.openOutputStream写恶意YAML+回调读grantedUri;关键时序1800ms触发+550ms读取窗口;YAML反序列化通过改包名+ExploitActivity实现;flag外传用nc 111.229.198.6 6666。

## 标签

Android、ExploitActivity、deeplink、qiangcalc://、content://、history.yml、ContentResolver、openOutputStream、YAML反序列化、divide-by-zero异常、bridge_token、fallback Intent、Uri.encode、FLAG_ACTIVITY_CLEAR_TOP、Arahat0

## 参考来源

- https://www.ctfiot.com/287018.html
- 原文件：强网杯2025_Qcalc_解析.full.md
