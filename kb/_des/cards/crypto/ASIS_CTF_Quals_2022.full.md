---
title: "ASIS CTF Quals 2022"
category: crypto
tags: ["ASIS CTF", "crypto", "BinomialExpansion", "enc % pubkey^2 // pubkey", "LatticeHashCollision", "chaffymasking"]
signals: ["ASIS CTF 2022", "BinomialExpansion", "enc % pubkey^2 // pubkey", "LatticeHashCollision", "chaffymasking", "fixed_p DLP", "CRT Joye-Libert", "EC离散对数smallfactor", "EC Pohlig-Hellman+CRT", "crypto_rsa", "ASIS", "CTF", "Quals", "Crypto"]
difficulty: hard
source: "https://www.ctfiot.com/67889.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# ASIS CTF Quals 2022

> 赛事：ASIS CTF 2022 | 方向：crypto | 难度：hard

## 一句话总结

ASIS CTF Quals 2022 — 8 道 Crypto 集锦：Binomial 展开 + Lattice 哈希碰撞 + Fixed p DLP + Joye-Libert CRT 还原 + 嵌套 EC Pohlig-Hellman + nearby_rational 求 phi + LSB discard 收窄 + openssl pbkdf2。

## 攻击链

1. Binomial: enc % pubkey^2 // pubkey 得明文（(a+b)^2 拆解）
2. Lattice hash collision: chaffymasking 1024 bit salt 漏洞, masked_flag 直接 hex 解码
3. Fixed p DLP: p 已知, g 已知, send (1-p) 反推 x 满足 m*G = x*G
4. Joye-Libert CRT: 4 组 (n,s) + c, n>>268 拆 a+b, a*b, GF(2^134) 算 (F(c)^a / F(s)^a).log()
5. Nested EC DLP: y1=0, y2=i 控制曲线参数, Pohlig-Hellman small factor 走 CRT 拼 fullres
6. Nearby rational: (y-x)/n 取 2^64 逼近, 求 phi
7. LSB: 40 字符 8 个候选,逐位 discard 收窄到唯一解
8. Xor 256 爆破: wormrep.klr.enc1 字节 XOR
9. openssl aes-256-cbc -pbkdf2 -a -d -salt: U2FsdGVkX18 + 20字节 salt

## 关键 payload

```
enc % n^2 // n / chaffymasking / 1-p DLP / Joye-Libert CRT / Pohlig-Hellman small factor CRT / nearby_rational 2^64 / LSB discard / openssl pbkdf2
```

## 经验教训

ASIS 风格是全覆盖所有方向的高质量 Crypto;Joye-Libert 是教科书方案;Pohlig-Hellman 小因子+CRT 拼是 EC DLP 标准法;nearby_rational(max_denominator=2^64) 是连分数在 phi 恢复的应用。

## 标签

BinomialExpansion、enc % pubkey^2 // pubkey、LatticeHashCollision、chaffymasking、fixed_p DLP、CRT Joye-Libert、EC离散对数smallfactor、EC Pohlig-Hellman+CRT、ratio nearby_rational、LSB_attack、openssl_pbkdf2、Xor256爆破

## 参考来源

- https://www.ctfiot.com/67889.html
- 原文件：ASIS_CTF_Quals_2022.full.md
