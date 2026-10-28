---
title: "ciscn 国赛华东南分区赛 WEB 方向 WriteUp 分享"
category: web
tags: ["CISCN", "web", "java", "deserialize", "xxe", "ssti"]
signals: ["CISCN 2023", "java", "deserialize", "xxe", "ssti", "fastapi", "jinja2", "time-blind", "websocket", "CISCN", "WEB", "Java", "PHP", "XXE"]
difficulty: medium
source: "https://www.ctfiot.com/125421.html"
tools: ["Flask", "Java", "PHP", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# ciscn 国赛华东南分区赛 WEB 方向 WriteUp 分享

> 赛事：CISCN 2023 | 方向：web | 难度：medium | 工具：Flask、Java、PHP、Python

## 一句话总结

CISCN 2023 华东南分区赛 8 道 WEB 官方 WP 集合，覆盖 Java 反序列化/PHP XXE/Python SSTI/Node WebSocket。

## 攻击链

1. 审计 Java 反序列化链
2. aspectj 写文件
3. 软链接读 flag
4. PHP 变量覆盖
5. XXE 注入
6. FastAPI 模板注入
7. Flask SSTI 多层 include
8. WebSocket + render 子域 RCE

## 关键 payload

```
SimpleCache$StoreableCachingMap 反序列化 + 软链接穿越
```

## 经验教训

现代 CTF WEB 越来越"工业化"——一题往往综合序列化+文件读写+反序列化链+沙箱绕过，单纯一类洞不够。

## 标签

java、deserialize、xxe、ssti、fastapi、jinja2、time-blind、websocket、render

## 参考来源

- https://www.ctfiot.com/125421.html
- 原文件：ciscn国赛华东南分区赛WEB方向WriteUp分享.full.md
