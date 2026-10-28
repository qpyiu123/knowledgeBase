---
title: "乌托邦·王的实验室24——拼少少商城 Writeup"
category: web
tags: ["乌托邦·王的实验室 24", "web", "TOCTOU", "asyncio", "asyncio.open_connection", "asyncio.Event"]
signals: ["乌托邦·王的实验室 24 2024", "TOCTOU", "asyncio", "asyncio.open_connection", "asyncio.Event", "并发竞态", "补贴接口", "抢购", "logic", "TCP", "flag", "api", "user", "catalog"]
difficulty: medium
source: "https://www.ctfiot.com/299471.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 乌托邦·王的实验室24——拼少少商城 Writeup

> 赛事：乌托邦·王的实验室 24 2024 | 方向：web | 难度：medium

## 一句话总结

asyncio 300 个 TCP 并发触发补贴接口 TOCTOU 漏洞刷钱买 10000 特供商品拿 flag。

## 攻击链

1. 靶机提供 /api/user /api/catalog /api/subsidy /api/order /api/dialogue 接口
2. /api/subsidy 限领一次，但服务端检查 TOCTOU 漏洞
3. 同一 session 用 300 个 TCP 连接预建立
4. asyncio.open_connection 预热 + asyncio.Event 同步触发
5. event.set() 同时发送 300 个 POST /api/subsidy
6. 余额达 10000 后 POST /api/order 买 p_1004
7. 响应中含 flag

## 关键 payload

```
asyncio.open_connection + asyncio.Event + race_subsidy(cookie, n=300)
```

## 经验教训

TOCTOU 漏洞在状态机类业务接口（限领/限购/限次）中常出现；asyncio 预建连接 + Event 同步触发是高并发竞态标准姿势；asyncio.wait_for(reader.read) 必须加 timeout 否则协程卡死。

## 标签

TOCTOU、asyncio、asyncio.open_connection、asyncio.Event、并发竞态、补贴接口、抢购

## 参考来源

- https://www.ctfiot.com/299471.html
- 原文件：乌托邦·王的实验室24——拼少少商城_Writeup.full.md
