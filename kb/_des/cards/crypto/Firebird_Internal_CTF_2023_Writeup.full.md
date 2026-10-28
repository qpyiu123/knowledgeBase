---
title: "Firebird Internal CTF 2023 Writeup"
category: crypto
tags: ["Firebird Internal CTF 2023", "crypto", "rsa", "partial-info", "padding-oracle", "rizo-duong"]
signals: ["Firebird Internal CTF 2023 2023", "rsa", "partial-info", "padding-oracle", "rizo-duong", "side-channel", "2048-bit", "crypto_rsa", "Firebird", "CTF", "RSA", "partial", "info", "recovery"]
difficulty: hard
source: "https://www.ctfiot.com/95037.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Firebird Internal CTF 2023 Writeup

> 赛事：Firebird Internal CTF 2023 2023 | 方向：crypto | 难度：hard

## 一句话总结

Firebird CTF 2023：RSA partial info recovery+padding oracle

## 攻击链

1. 引用 Gabrielle de Micheli, Nadia Heninger 2020 论文
2. Recovering cryptographic keys from partial information
3. Juliano Rizzo, Thai Duong 2010 "Practical Padding Oracle Attacks
4. RSA 2048位 + 固定 seed(1337)
5. t=[(key.p>>random.getrandbits(10))&1 ...]
6. 已知 p/q 一些 LSB 信息
7. 构造 _ps, _qs 候选位
8. guess(n, _ps, _qs) 还原 p
9. n%p==0, q=n//p, phi=(p-1)(q-1)
10. d=pow(e,-1,phi_n), m=pow(c,d,n)
11. Padding Oracle 攻击
12. Hacker.__oracle(token) → authenticate

## 关键 payload

```
random.seed(1337)  # 固定随机种子
```

## 经验教训

固定seed RSA可预测；partial info论文+padding oracle组合

## 标签

rsa、partial-info、padding-oracle、rizo-duong、side-channel、2048-bit

## 参考来源

- https://www.ctfiot.com/95037.html
- 原文件：Firebird_Internal_CTF_2023_Writeup.full.md
