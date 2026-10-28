---
title: "【WP】2023年春秋杯冬季赛 WEB、PWN 类题目解析"
category: web
tags: ["春秋杯", "web", "customer-broker-merchant", "message-queue", "webhook", "PHP-deserialize"]
signals: ["春秋杯 2023", "customer-broker-merchant", "message-queue", "webhook", "PHP-deserialize", "Redis-Rogue-Server", "dict-protocol", "exp.so-module", "picup-SSRF", "deserialize", "Web", "Pwn", "PHP", "Redis"]
difficulty: medium
source: "https://www.ctfiot.com/159161.html"
tools: ["PHP", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【WP】2023年春秋杯冬季赛 WEB、PWN 类题目解析

> 赛事：春秋杯 2023 | 方向：web | 难度：medium | 工具：PHP、Python

## 一句话总结

2023 春秋杯冬季赛 Web/Pwn WP，customer-broker-merchant 队列系统 + PHP 反序列化 Redis Rogue Server + picup SSRF。

## 攻击链

1. Active-Takeaway 三个组件 customer 生成订单/broker 队列/merchant 接单向 webhook 发/ezezez_php 4 步链 dict:// Redis module load exp.so system.exec + redis-rogue-server.py 攻击/picup 抓包 302 /login.php + 404 页面收集 + SSRF

## 关键 payload

```
redis-rogue-server.py --server-only  dict://127.0.0.1:6379/config:set:dir:/tmp
```

## 经验教训

消息队列三件套 customer/broker/merchant 漏洞多在 webhook 重放或订单伪造；PHP 反序列化可用 dict:// Redis module 加载 exp.so 实现 RCE；redis-rogue-server.py 是 SSRF → Redis RCE 经典工具。

## 标签

customer-broker-merchant、message-queue、webhook、PHP-deserialize、Redis-Rogue-Server、dict-protocol、exp.so-module、picup-SSRF

## 参考来源

- https://www.ctfiot.com/159161.html
- 原文件：【WP】2023年春秋杯冬季赛WEB、PWN类题目解析.full.md
