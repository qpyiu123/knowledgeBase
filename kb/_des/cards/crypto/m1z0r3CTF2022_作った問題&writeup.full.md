---
title: "m1z0r3CTF 2022 作った問題 & writeup"
category: crypto
tags: ["m1z0r3CTF", "crypto", "lcg", "rsa-chain", "multi-prime", "prime-256bit"]
signals: ["m1z0r3CTF 2022", "lcg", "rsa-chain", "multi-prime", "prime-256bit", "custom-encrypt", "secret-png", "16bit-prime", "crypto_rsa", "m1z0r3CTF", "LCG", "RSA", "bit", "prime"]
difficulty: medium
source: "https://www.ctfiot.com/84177.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# m1z0r3CTF 2022 作った問題 & writeup

> 赛事：m1z0r3CTF 2022 | 方向：crypto | 难度：medium

## 一句话总结

m1z0r3CTF 2022 三道密码学题：LCG 加密 + 链式 RSA + 16bit prime 拼接。

## 攻击链

1. chall1: 未知 a, b, r, x (LCG)
2. 加密 = byte XOR LCG 输出
3. 已知明文头部 (PNG 头 8 字节) 推导 LCG
4. chall2: prime + 链式素数 + 16bit prime
5. 链式 q 拼接 next_prime
6. 小明文 + 已知 gen_p 爆破
7. chall3: getPrime(256) + 16bit 偏移 e
8. 16bit 偏移 ex + 2 字节 e 爆破

## 关键 payload

```
LCG 已知明文恢复 + 链式 RSA + 16bit prime
```

## 经验教训

LCG 加密 + 已知明文攻击是经典题型；链式 prime RSA 的"prime 链"是近年新趋势。

## 标签

lcg、rsa-chain、multi-prime、prime-256bit、custom-encrypt、secret-png、16bit-prime

## 参考来源

- https://www.ctfiot.com/84177.html
- 原文件：m1z0r3CTF2022_作った問題&writeup.full.md
