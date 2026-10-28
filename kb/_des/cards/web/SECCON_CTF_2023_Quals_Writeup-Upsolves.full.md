---
title: "SECCON CTF 2023 Quals/Upsolves"
category: web
tags: ["SECCON CTF", "web", "JWT alg 注入", "constructor prototype", "弱 secret", "notevil eval"]
signals: ["SECCON CTF 2023", "JWT alg 注入", "constructor prototype", "弱 secret", "notevil eval", "CSP 绕过", "XSS 拿 cookie", "简单计算器 XSS", "jwt", "xss", "rce", "JWT", "alg", "prototype"]
difficulty: medium
source: "https://www.ctfiot.com/136184.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# SECCON CTF 2023 Quals/Upsolves

> 赛事：SECCON CTF 2023 | 方向：web | 难度：medium

## 一句话总结

JWT alg 注入 prototype pollution + CSP Host 头污染 XSS 拿 flag

## 攻击链

1. bad-jwt 题目：JWT 验证函数 createSignature 用 algorithms[header.alg.toLowerCase()]()
2. 攻击：把 alg 改成 "constructor" → algorithms.constructor 是 Object constructor → 拼出恒等签名
3. 伪签名："eyJhbGciOiJjb25zdHJ1Y3RvciJ9eyJpc0FkbWluIjp0cnVlfQ=="（拼接 header+payload 不加点）
4. 验证：calculated_signature == expected_signature 恒等 → 通过
5. 设 session 携带伪造 JWT 拿到 admin
6. simplecalc 题目：CSP `default-src ${js_url} 'unsafe-eval'`，url 来自 req.hostname
7. 攻击：控制 Host 头让 js_url 指向攻击者服务器，返回恶意 JS
8. eval(params.get('expr')) 可执行任意 JS
9. 用 XSS 拿管理员 cookie 访问 /flag
10. 上报链接触发 admin 访问 → 收集 flag

## 关键 payload

```
header = {"alg": "constructor", "typ": "JWT"}; payload = {"isAdmin": true}; token = base64(header) + ''.'' + base64(payload) + ''.'' + base64(header+payload)
```

## 经验教训

JWT 库用字典查算法时 alg 字段可被注入到 Object 原型链；CSP 中 default-src 接受 Host 头参数可被污染

## 标签

JWT alg 注入、constructor prototype、弱 secret、notevil eval、CSP 绕过、XSS 拿 cookie、简单计算器 XSS

## 参考来源

- https://www.ctfiot.com/136184.html
- 原文件：SECCON_CTF_2023_Quals_Writeup-Upsolves.full.md
