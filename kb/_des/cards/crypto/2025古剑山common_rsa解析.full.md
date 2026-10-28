---
title: "2025 古剑山 common_rsa 解析（RSA 共模攻击+扩展欧几里得）"
category: crypto
tags: ["2025 古剑山", "crypto", "古剑山 2025 common_rsa 物不知数", "RSA 共模攻击 同一 m 不同 e", "c1=m^e1 mod N", "c2=m^e2 mod N"]
signals: ["2025 古剑山 2025", "古剑山 2025 common_rsa 物不知数", "RSA 共模攻击 同一 m 不同 e", "c1=m^e1 mod N", "c2=m^e2 mod N", "gcd(e1", "e2)=1", "扩展欧几里得 s*e1+t*e2=1", "m=c1^s * c2^t mod N", "crypto_rsa", "lattice", "common_rsa", "mod", "gcd"]
difficulty: medium
source: "https://www.ctfiot.com/284446.html"
tools: ["gmpy2"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2025 古剑山 common_rsa 解析（RSA 共模攻击+扩展欧几里得）

> 赛事：2025 古剑山 2025 | 方向：crypto | 难度：medium | 工具：gmpy2

## 一句话总结

2025 古剑山 common_rsa 物不知数：同 N 同 m 不同 e1=35422, e2=1033 共模攻击，扩展欧几里得求 s, t，c1^(-1)^334 * c2^11453 mod N 还原 m。

## 攻击链

1. 同 N 同 m 不同 e1, e2，e1=35422 e2=1033
2. 扩展欧几里得 gcd(e1, e2)=1, s=-334, t=11453
3. s*e1 + t*e2 = -334*35422 + 11453*1033 = 1
4. c1^s = c1^(-334) = (c1^(-1))^334
5. c1_inv = gmpy2.invert(c1, N)
6. m = (c1_inv)^|s| * c2^t mod N = (c1^(-1))^334 * c2^11453 mod N
7. flag = bytes.fromhex(hex(m)[2:])

## 关键 payload

```
m = (c1_inv)^|s| * c2^t mod N
```

## 经验教训

RSA 共模攻击 = 同 N 同 m 不同 e，扩展欧几里得求 s*e1 + t*e2 = 1，m = c1^s * c2^t mod N；s 为负数时取模逆元 invert(c1, N)。

## 标签

古剑山 2025 common_rsa 物不知数、RSA 共模攻击 同一 m 不同 e、c1=m^e1 mod N、c2=m^e2 mod N、gcd(e1、e2)=1、扩展欧几里得 s*e1+t*e2=1、m=c1^s * c2^t mod N、c1_inv=invert(c1、N) c1^(-1)^334、part1+part2 mod N、gmpy2.gcdext

## 参考来源

- https://www.ctfiot.com/284446.html
- 原文件：2025古剑山common_rsa解析.full.md
