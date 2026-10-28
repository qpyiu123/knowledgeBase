---
title: "DataCon2024解题报告WriteUp—网络基础设施安全赛道"
category: misc
tags: ["DataCon 2024", "misc", "dns", "open-resolver", "isc-bind", "geoip2"]
signals: ["DataCon 2024 2024", "dns", "open-resolver", "isc-bind", "geoip2", "libjson", "features", "attack", "misc_unknown", "DataCon2024", "DNS", "Bind"]
difficulty: hard
source: "https://www.ctfiot.com/224743.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DataCon2024解题报告WriteUp—网络基础设施安全赛道

> 赛事：DataCon 2024 2024 | 方向：misc | 难度：hard

## 一句话总结

DataCon2024 DNS开放解析器识别：Bind编译选项+功能版本

## 攻击链

1. 题目1: DNS开放解析器识别+攻击利用
2. 9.16/9.18 Bind版本
3. 胶水缓存存在/弃用
4. 陈旧缓存开启/弃用
5. --disable-silent-rules（可选/不可选）
6. --enable-backtrace（可选/不可选）
7. --enable-shared
8. --enable-native-pkcs11
9. --with-geoip2 功能失效但可选
10. --with-libjson 功能失效但可选

## 关键 payload

```
--with-geoip2 --with-libjson  # Bind 配置特征
```

## 经验教训

Bind编译参数+版本特征可用于识别DNS开放解析器

## 标签

dns、open-resolver、isc-bind、geoip2、libjson、features、attack

## 参考来源

- https://www.ctfiot.com/224743.html
- 原文件：DataCon2024解题报告WriteUp—网络基础设施安全赛道.full.md
