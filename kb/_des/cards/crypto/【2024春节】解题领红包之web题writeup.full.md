---
title: "2024 春节 解题领红包之 web 题 writeup"
category: crypto
tags: ["2024 春节活动 (52pojie)", "crypto", "52pojie", "春节活动", "ASCII-art", "banner"]
signals: ["2024 春节活动 (52pojie) 2024", "52pojie", "春节活动", "ASCII-art", "banner", "banner-grab", "slider", "CSS-variable", "LCG", "misc_math", "web_unknown", "web", "ASCII", "art"]
difficulty: easy
source: "https://www.ctfiot.com/165808.html"
tools: ["netcat"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 春节 解题领红包之 web 题 writeup

> 赛事：2024 春节活动 (52pojie) 2024 | 方向：crypto | 难度：easy | 工具：netcat

## 一句话总结

2024 春节 web：ASCII art 读字 + CSS slider + LCG 模逆 + 大数因子

## 攻击链

1. Q1: netcat 124.232.185.97 2024challenge.52pojie.cn → 抓 ASCII 艺术
2. 从 ASCII 字符形状读出 flag: flag{5P3rF1ag3}
3. Q2: 网页有 slider1/slider2 → 改 --var1=71 --var2=20
4. 读 num = 1213159497, while 循环 num & 0xff 转字符 → flag12{...}
5. Q3: LCG 模逆 1103515245 模 2^32 → modinv = pow(1103515245, -1, 2**32)
6. Q4: 18464037713 × 999063388 验证 2^65 范围爆破

## 关键 payload

```
flag{5P3rF1ag3} / flag12{...}
```

## 经验教训

netcat 抓 banner 读字；CSS 变量 + slider 是 web 入门；LCG 模逆是密码学入门

## 标签

52pojie、春节活动、ASCII-art、banner、banner-grab、slider、CSS-variable、LCG、mod-inverse、egcd、JavaScript-decode

## 参考来源

- https://www.ctfiot.com/165808.html
- 原文件：【2024春节】解题领红包之web题writeup.full.md
