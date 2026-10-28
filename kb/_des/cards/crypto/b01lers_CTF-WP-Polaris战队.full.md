---
title: "b01lers CTF WP - Polaris 战队"
category: crypto
tags: ["b01lersCTF", "crypto", "coppersmith", "certificate", "lop", "knapsack"]
signals: ["b01lersCTF 2024", "coppersmith", "certificate", "lop", "knapsack", "ntru", "lattice", "crypto_rsa", "b01lers", "CTF", "Polaris", "RSA", "Coppersmith"]
difficulty: medium
source: "https://www.ctfiot.com/105784.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# b01lers CTF WP - Polaris 战队

> 赛事：b01lersCTF 2024 | 方向：crypto | 难度：medium

## 一句话总结

b01lers CTF 多题 WP 合集，Polaris 战队对证书类 RSA 与格密码题给出系统化爆破思路。

## 攻击链

1. 解析 X.509 证书公钥
2. Coppersmith 小根
3. p=2,q=3 / p=3,q=2 爆破
4. 还原 RSA 私钥
5. 解密 flag

## 关键 payload

```
t0 证书爆破 + Coppersmith small_roots
```

## 经验教训

RSA 弱密钥(e 极小、p 邻近、证书 t0 已知)攻击面比单纯 e*d 完整攻击更多；CTF 出题常借 X.509 包装弱密钥。

## 标签

coppersmith、certificate、lop、knapsack、ntru、lattice

## 参考来源

- https://www.ctfiot.com/105784.html
- 原文件：b01lers_CTF-WP-Polaris战队.full.md
