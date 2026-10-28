---
title: "boomer_crypto-prime-guesser-1 and boomer_crypto-prime-guesser-2 in KITCTF 2022"
category: crypto
tags: ["KITCTF", "crypto", "rsa", "binary-search", "q-finding", "8-bit-prime"]
signals: ["KITCTF 2022", "rsa", "binary-search", "q-finding", "8-bit-prime", "q-recovery", "mitm", "16-bit-prime", "crypto_rsa", "KITCTF", "boomer", "prime-guesser", "bit", "RSA"]
difficulty: hard
source: "https://www.ctfiot.com/85512.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# boomer_crypto-prime-guesser-1 and boomer_crypto-prime-guesser-2 in KITCTF 2022

> 赛事：KITCTF 2022 | 方向：crypto | 难度：hard

## 一句话总结

KITCTF 2022 boomer prime-guesser 1/2 复盘，8/16-bit RSA 弱密钥枚举。

## 攻击链

1. 1: 8 bit q 暴力枚举
2. mod p 找 q
3. SCALED_PT 模式
4. 2: 16 bit q 暴力
5. FINDING Q 二分迭代
6. Q=2^i 模式（第一次 True 转 False 的位置）
7. SK 计算
8. 4 个 scaled_pt 恢复

## 关键 payload

```
FINDING Q 模式识别 + 二分搜索 q
```

## 经验教训

当 q < 2^k 时，q = 2^k + 1 转换点能定位 q 真实值。

## 标签

rsa、binary-search、q-finding、8-bit-prime、q-recovery、mitm、16-bit-prime

## 参考来源

- https://www.ctfiot.com/85512.html
- 原文件：boomer_crypto-prime-guesser-1_and_boomer_crypto-prime-guesser-2_in_KITCTF_2022.full.md
