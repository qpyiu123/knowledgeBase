---
title: "解析LitCTF 2025 – Basic"
category: crypto
tags: ["LitCTF 2025", "crypto", "RSA", "prime-modulus", "Euler-totient", "phi-prime"]
signals: ["LitCTF 2025 2025", "RSA", "prime-modulus", "Euler-totient", "phi-prime", "modinv", "fatal-misimplementation", "RSA-break", "crypto_rsa", "LitCTF", "Basic", "getPrime", "phi", "n-1"]
difficulty: easy
source: "https://www.ctfiot.com/281399.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 解析LitCTF 2025 – Basic

> 赛事：LitCTF 2025 2025 | 方向：crypto | 难度：easy

## 一句话总结

LitCTF 2025 Basic方向RSA致命错误:n=getPrime(1024)用单个素数作模数,phi(n)=n-1,直接inverse(e,n-1)得d解密。

## 攻击链

1. 识别致命错误:n=getPrime(1024)直接用单个素数作模数,而非p*q
2. 标准RSA n=p*q,phi=(p-1)(q-1);此处n本身是质数,phi(n)=n-1
3. 直接计算phi=n-1
4. modinv d=inverse(e,phi)
5. m=pow(c,d,n)快速解密

## 关键 payload

```
LitCTF{...}
```

## 经验教训

任何RSA题目都应先验证n是合数(质数检测)再决定攻击策略;φ(p)=p-1对质数成立;实现失误让1024位"安全"在毫秒级崩塌。

## 标签

RSA、prime-modulus、Euler-totient、phi-prime、modinv、fatal-misimplementation、RSA-break

## 参考来源

- https://www.ctfiot.com/281399.html
- 原文件：解析LitCTF_2025_–_Basic.full.md
