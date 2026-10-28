---
title: "Coppersmith's Attack"
category: crypto
tags: ["公众号文章", "crypto", "crypto", "rsa", "coppersmith", "small-e"]
signals: ["公众号文章 2020", "crypto", "rsa", "coppersmith", "small-e", "部分p泄露", "sagemath", "sha256前缀", "crypto_rsa", "Coppersmith", "SHA256", "gmpy2", "iroot", "PolynomialRing"]
difficulty: medium
source: "https://www.ctfiot.com/42969.html"
tools: ["gmpy2"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Coppersmith's Attack

> 赛事：公众号文章 2020 | 方向：crypto | 难度：medium | 工具：gmpy2

## 一句话总结

Coppersmith攻击小e+部分p泄露+SHA256前缀爆破综合

## 攻击链

1. 第1题: e=3, c<m^3 直接 gmpy2.iroot(c,3) 开立方
2. 第2题: e=65537, p高128位已知 用Coppersmith f=x+p4
3. PR.<x>=PolynomialRing(Zmod(n)) f=x+p4
4. x0=f.small_roots(X=2^kbits, beta=0.4)[0]求小根
5. 第0题: SHA256前缀爆破找 skr

## 关键 payload

```
f.small_roots(X=2^kbits, beta=0.4)[0]  # sagemath
```

## 经验教训

已知p高位时用Coppersmith在Zmod(n)上多项式小根求低位

## 标签

crypto、rsa、coppersmith、small-e、部分p泄露、sagemath、sha256前缀

## 参考来源

- https://www.ctfiot.com/42969.html
- 原文件：Coppersmith’s_Attack.full.md
