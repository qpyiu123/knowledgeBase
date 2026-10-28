---
title: "HackerGame 2022 出题记"
category: crypto
tags: ["HackerGame 2022 (出题记)", "crypto", "crypto", "aes-cbc", "chosen-ciphertext", "crc128"]
signals: ["HackerGame 2022 (出题记) 2022", "crypto", "aes-cbc", "chosen-ciphertext", "crc128", "affine-crc", "sagemath", "gf2", "writeup-design", "crypto_rsa", "HackerGame", "AES-CBC", "chosen", "ciphertext"]
difficulty: hard
source: "https://www.ctfiot.com/76391.html"
tools: ["C"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# HackerGame 2022 出题记

> 赛事：HackerGame 2022 (出题记) 2022 | 方向：crypto | 难度：hard | 工具：C

## 一句话总结

HackerGame 2022 出题记：AES-CBC chosen ciphertext+仿射CRC

## 攻击链

1. AES-CBC chosen ciphertext attack
2. AES_CBC_chosen_ciphertext: pos指定位置插入
3. crc128 = (1<<128) - 1 多项式
4. poly=0x883ddfe55bba9af41f47bd6e0b0d8f8f
5. 等价仿射CRC: crc(x) = M*x + C (GF(2))
6. Affine_Matrix = []
7. target_bits = 8 * target_bytes
8. v2n + n2v 转换 GF(2) vector
9. matrix(GF(2), Affine_Matrix).transpose()

## 关键 payload

```
crc(x) = M*x + C in GF(2)
```

## 经验教训

CRC可表示为GF(2)上仿射变换；AES-CBC chosen ciphertext可构造任意块

## 标签

crypto、aes-cbc、chosen-ciphertext、crc128、affine-crc、sagemath、gf2、writeup-design

## 参考来源

- https://www.ctfiot.com/76391.html
- 原文件：HackerGame_2022_出题记.full.md
