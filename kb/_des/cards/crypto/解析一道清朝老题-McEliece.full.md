---
title: "解析一道清朝老题 - McEliece"
category: crypto
tags: ["Hack.lu CTF 2017 / 后量子 crypto", "crypto", "McEliece", "GRS", "Reed-Solomon", "范德蒙德"]
signals: ["Hack.lu CTF 2017 / 后量子 crypto 2025 (现代解析)", "McEliece", "GRS", "Reed-Solomon", "范德蒙德", "Sidelnikov-Shestakov", "Berlekamp-Welch", "GF(2^8)", "后量子", "crypto_rsa", "lattice", "ratio", "publickey", "sobj"]
difficulty: hard
source: "https://www.ctfiot.com/282175.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 解析一道清朝老题 - McEliece

> 赛事：Hack.lu CTF 2017 / 后量子 crypto 2025 (现代解析) | 方向：crypto | 难度：hard

## 一句话总结

Sidelnikov-Shestakov 攻击 McEliece GRS 码 255 ratio 枚举

## 攻击链

1. 公开 publickey.sobj 64×128 矩阵 over GF(2^8)
2. 公开 ciphertext.sobj 128 维向量
3. 识别 GRS 码（生成矩阵每列是范德蒙向量）
4. Sidelnikov-Shestakov 攻击：枚举 255 个 ratio 恢复支撑向量 α
5. 用 GRS 对偶码也是 GRS 性质恢复列乘子 v
6. Berlekamp-Welch 解码器解出 m·S
7. 左乘 S^-1 还原明文 m
8. flag: flag{ReedSolomonCodesAreNoGoodIdeaForMcElieceIfYouWantTopCrypto}

## 关键 payload

```
G[i,j] = v_j * α_j^i  (i=0..k-1, j=0..n-1) — 范德蒙德结构
```

## 经验教训

McEliece 安全只对二元 Goppa 码；GRS / Reed-Solomon 实现的 McEliece 是 1992 年就被破的；后量子选码要慎重

## 标签

McEliece、GRS、Reed-Solomon、范德蒙德、Sidelnikov-Shestakov、Berlekamp-Welch、GF(2^8)、后量子、编码密码

## 参考来源

- https://www.ctfiot.com/282175.html
- 原文件：解析一道清朝老题-McEliece.full.md
