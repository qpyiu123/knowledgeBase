---
title: "【WP】NewStar CTF 2025 Week1&Week2 之 WEB 方向题解"
category: web
tags: ["NewStarCTF", "web", "token-calc", "expression-regex", "requests-Session", "cookie-maintain"]
signals: ["NewStarCTF 2025", "token-calc", "expression-regex", "requests-Session", "cookie-maintain", "/start_challenge", "/verify_token", "multiply-xor", "web_unknown", "NewStar", "CTF", "Week1", "Week2", "Web"]
difficulty: easy
source: "https://www.ctfiot.com/274196.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【WP】NewStar CTF 2025 Week1&Week2 之 WEB 方向题解

> 赛事：NewStarCTF 2025 | 方向：web | 难度：easy

## 一句话总结

NewStar CTF 2025 Week1&Week2 Web 入门题，token 计算 + Session 维持 + 正则表达式。

## 攻击链

1. POST /start_challenge 拿 expression token 表达式 + hint + multiplier + xor_value + 新 session/正则提取 num1*num2^0x... 计算 token/POST /verify_token 提交 token/保持 session cookie 跨请求

## 关键 payload

```
expression = "token = (1234 * 5678) ^ 0xDEADBEEF"  token = (1234*5678) ^ 0xDEADBEEF
```

## 经验教训

requests.Session() 自动维持 cookie；正则 re.search 提取表达式数字和异或值；token = (num1*num2) ^ xor_val 是基础算术 XOR；Web 入门题通常用 icook 维持 session。

## 标签

token-calc、expression-regex、requests-Session、cookie-maintain、/start_challenge、/verify_token、multiply-xor

## 参考来源

- https://www.ctfiot.com/274196.html
- 原文件：【WP】NewStar_CTF_2025_Week1&Week2_之WEB方向题解.full.md
