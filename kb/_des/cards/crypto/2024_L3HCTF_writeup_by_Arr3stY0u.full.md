---
title: "2024 L3HCTF writeup by Arr3stY0u"
category: crypto
tags: ["L3HCTF", "crypto", "格基规约", "DSA nonce 复用", "SPN 自定义分组密码", "32位XTEA 变种 delta=0x114514"]
signals: ["L3HCTF 2024", "格基规约", "DSA nonce 复用", "SPN 自定义分组密码", "32位XTEA 变种 delta=0x114514", "Cyclotomic Polynomial 攻击", "python bytecode 提取", "AES-128-CBC", "lattice", "ecdsa", "reverse", "crypto_rsa", "LLL", "DSA"]
difficulty: hard
source: "https://www.ctfiot.com/161429.html"
tools: ["IDA", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 L3HCTF writeup by Arr3stY0u

> 赛事：L3HCTF 2024 | 方向：crypto | 难度：hard | 工具：IDA、Python

## 一句话总结

LLL DSA LCG 还原 + SPN 密钥爆破 + XTEA 变种 + Cyclotomic LLL + bytecode LCS。

## 攻击链

1. 1. 格攻击 DSA LCG PRNG nonce：构造 15x15 矩阵 LLL 还原 sk / 2. 4 轮 SPN 自定义分组密码爆破密钥：2^24 候选 + sha256 比对 / 3. 32 位 XTEA 变种 delta=0x114514 还原 8 个 uint32 / 4. Cyclotomic Polynomial LLL 攻击 1024 阶多项式还原低 64 字节 / 5. Python bytecode regex 提取 LOAD_CONST 序列调用 solution 求 LCS / 6. AES-128-CBC 'secret' XOR + base64 解 / 7. H3C ppp chap cipher $c$3$ 解 IV/CT 拿密码 / 8. SHA512 顺序混编算 HASH / 9. IDA Python sub+stk2 弹栈指令 hook

## 关键 payload

```
M = Matrix(RR,15,15) ; t = abs(LLL[0][:5]) ; 32-bit TEA delta=0x114514 ; Cyclotomic 1024 阶多项式 b=... s=... ; solution(['a', 'ba', 'ab', 'bc', 'cb', 'bda', 'bdca', 'bacd', 'bbbb', 'acdb', ...])
```

## 经验教训

L3HCTF 风格偏论文题：DSA PRNG LLL / Cyclotomic 格基 / 自定义 SPN 都要懂。

## 标签

格基规约、DSA nonce 复用、SPN 自定义分组密码、32位XTEA 变种 delta=0x114514、Cyclotomic Polynomial 攻击、python bytecode 提取、AES-128-CBC

## 参考来源

- https://www.ctfiot.com/161429.html
- 原文件：2024_L3HCTF_writeup_by_Arr3stY0u.full.md
