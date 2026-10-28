---
title: "华为杯第一届中国研究生网络安全创新大赛初赛WriteUp"
category: web
tags: ["华为杯", "web", "JWT-HS256-forge", "URL-object-bypass", "nodemon-restart", "LCG-inverse"]
signals: ["华为杯 2022", "JWT-HS256-forge", "URL-object-bypass", "nodemon-restart", "LCG-inverse", "angr-symbolic-execution", "stack-pivot", "ssrf", "EDI", "Web", "HS256", "URL", "bypass", "Crypto"]
difficulty: medium
source: "https://www.ctfiot.com/75117.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 华为杯第一届中国研究生网络安全创新大赛初赛WriteUp

> 赛事：华为杯 2022 | 方向：web | 难度：medium

## 一句话总结

华为杯 2022 研究生国赛初赛 EDI 安全战队 WP，Web HS256 伪造 + URL 对象 bypass / Crypto 四层 LCG / Re angr / Pwn 栈迁移四方向。

## 攻击链

1. Web：用 public.pem 作 HS256 secret 伪造 admin JWT + URL 对象 href/origin/protocol/hostname/pathname 构造 file:// 协议 /app/ 路径避开关键字 + url 编码绕 %72%6f%75%74%65%73 关键字 + /api/upload 写新 index.js 含 execSync + nodemon 自动重启触发/Crypto：四层 LCG 挑战 solve1~4 分别 1/2/3/6 元逆元解 a/N/seed/Re：angr 符号执行 infantvm 找 good=Good job/avoid=Try again 路径/Pwn：栈迁移到 bss 0x6010A0 + leave_ret 跳板 + 泄 puts libc + one_gadget

## 关键 payload

```
HS256 伪造 JWT: payload={isAdmin:true, username:"admin", home:{href:"ank1e", origin:"ank1e", protocol:"file:", hostname:"", pathname:"/app/%72%6f%75%74%65%73/index.%6a%73"}}
```

## 经验教训

JWT 用 public.pem 作 HS256 secret 是经典算法混淆漏洞；URL 对象 pathname 可绕关键字正则；LCG 等差数列求 N 用 GCD 三个二阶差分；angr entry_state + simulation_manager 找 good/avoid 路径；栈迁移到 bss + leave_ret 是经典 pwn 入门。

## 标签

JWT-HS256-forge、URL-object-bypass、nodemon-restart、LCG-inverse、angr-symbolic-execution、stack-pivot

## 参考来源

- https://www.ctfiot.com/75117.html
- 原文件：“华为杯”第一届中国研究生网络安全创新大赛初赛WriteUp.full.md
