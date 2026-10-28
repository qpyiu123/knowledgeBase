---
title: "CakeCTF 2023 作問感想"
category: crypto
tags: ["CakeCTF 2023 (出题人感想)", "crypto", "crypto", "pwn", "签名前置", "RSA-CRT"]
signals: ["CakeCTF 2023 (出题人感想) 2023", "crypto", "pwn", "签名前置", "RSA-CRT", "矩阵幂", "出题人感想", "双语", "crypto_rsa", "CakeCTF", "DLP", "simple", "signature", "Cake"]
difficulty: hard
source: "https://www.ctfiot.com/145742.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# CakeCTF 2023 作問感想

> 赛事：CakeCTF 2023 (出题人感想) 2023 | 方向：crypto | 难度：hard

## 一句话总结

CakeCTF 2023出题人感想，5题涵盖签名+15拼图+矩阵DLP+RSA-CRT

## 攻击链

1. simple signature: x/u仅在公钥中，私钥无关联任意设值解
2. Cake Puzzle: 15-puzzle简单reversing+solver
3. janken vs yoshiking 2: GL5(Fp)矩阵幂+det() Pohlig-Hellman DLP
4. decryptyou: RSA-CRT Garner算法u=p mod q可pwn破坏但m≤p时不响
5. Iron Door: 高难度crypto

## 关键 payload

```
det(M^r) = det(M)^r 在Fp上做Pohlig-Hellman
```

## 经验教训

矩阵离散对数可用det()降到Fp上DLP；RSA-CRT Garner中临时变量u可被pwn

## 标签

crypto、pwn、签名前置、RSA-CRT、矩阵幂、出题人感想、双语

## 参考来源

- https://www.ctfiot.com/145742.html
- 原文件：CakeCTF_2023_作問感想.full.md
