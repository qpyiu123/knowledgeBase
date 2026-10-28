---
title: "0xGame 2025/Crypto WriteUp Week1"
category: crypto
tags: ["0xGame", "crypto", "新人向", "factordb", "Vigenère 标准", "Vigenère 魔改乘法"]
signals: ["0xGame 2025", "新人向", "factordb", "Vigenère 标准", "Vigenère 魔改乘法", "GB2312", "三进制 base", "iroot(7) 整数根", "POW 爆破", "crypto_rsa", "diffie_hellman", "block_cipher", "vigenere", "crypto"]
difficulty: easy
source: "https://www.ctfiot.com/273923.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 0xGame 2025/Crypto WriteUp Week1

> 赛事：0xGame 2025 | 方向：crypto | 难度：easy

## 一句话总结

7 个新人向 crypto 子题合集（DH s=1 / factordb / Vigenère 两种 / GB2312 三进制 iroot / POW + 2025 位 RSA）

## 攻击链

1. 子题 1 流量登录：扫 QR 码填 6 位验证码
2. 子题 2 DH 退化：设 Bob 公钥 B=1 → s=pow(1,a,p)=1 → 直接用 s=1 派生 AES key
3. 子题 3 RSA factordb：n 256-bit 太小，直接 factordb 分解 p,q
4. 子题 4 Vigenère 标准：已知 key "Welcome-2025-0xGame"，解密
5. 子题 5 Vigenère 魔改乘法：((char_index + bias) * char_index) mod len → 逐位解二次同余
6. 子题 6 flag 切 4 段：b64 + hex + 三进制 a/w/q + iroot(7) → 拼回 flag (gb2312)
7. 子题 7 POW + 2025 位 RSA：4 字符前缀爆破 + d=inverse(e, n-1)

## 经验教训

DH 协议 s 值退化时（公钥=1）直接 s=1；factordb 是小指数 RSA 标准武器；Vigenère 乘法变种需逐位解二次同余；多段编码拼接时按段确认长度和编码

## 标签

新人向、factordb、Vigenère 标准、Vigenère 魔改乘法、GB2312、三进制 base、iroot(7) 整数根、POW 爆破、DH s=1 退化

## 参考来源

- https://www.ctfiot.com/273923.html
- 原文件：0xGame_2025_Crypto_WriteUp_Week1.full.md
