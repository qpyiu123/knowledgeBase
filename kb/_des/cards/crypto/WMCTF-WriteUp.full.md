---
title: "WMCTF WriteUp (ChaMd5 Venom)"
category: crypto
tags: ["WMCTF", "crypto", "aes_cbc", "ocb_mode", "arbitrary_encrypt", "pmac_forgery"]
signals: ["WMCTF 2021", "aes_cbc", "ocb_mode", "arbitrary_encrypt", "pmac_forgery", "lattice_lll", "bkz_22", "sage_small_roots", "rabin_chain", "crypto_oracle", "WMCTF", "ChaMd5", "Venom", "AES-CBC"]
difficulty: hard
source: "https://www.ctfiot.com/1224.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# WMCTF WriteUp (ChaMd5 Venom)

> 赛事：WMCTF 2021 | 方向：crypto | 难度：hard

## 一句话总结

WMCTF 早期 ChaMd5 Venom 战队杂烩 WP，AES-CBC 密码爆破 + OCB 模式 oracle 标签伪造 + 32 元子集和 + Rabin 链解 e=4096 + LWE 格密码，多道密码学题经典攻击模板。

## 攻击链

1. v2x_misc.conf AES-CBC 16 字节密码 ljust\x00 → OCB 模式 Arbitrary_encrypt oracle 重放 + my_pmac 标签伪造 (xor_block(tag, pmac_admin)) → 32 元子集和问题 BKZ-22 求最短向量 → RSA p^5 Coppersmith small_roots X=2^369 → Rabin 链 c^(1/2^i) mod p 穷举 2^13 候选 → LWE q=2^24 格密码 to_mat 16 维 + Matrix(F).solve_left 求解向量

## 关键 payload

```
pmac_admin = my_pmac(bytearray(b'from admin')) / M = matrix(ZZ, m); v = M.BKZ(blocksize=22) / sympy.root(x, 2) 取整数
```

## 经验教训

OCB 模式 arbitrary_encrypt oracle 可直接伪造 PMAC 标签；子集和+super-increasing+前几位已知可用 BKZ-22 而非 LLL。

## 标签

aes_cbc、ocb_mode、arbitrary_encrypt、pmac_forgery、lattice_lll、bkz_22、sage_small_roots、rabin_chain、lwe_qary、knapsack_cvp、ocb_oracle

## 参考来源

- https://www.ctfiot.com/1224.html
- 原文件：WMCTF-WriteUp.full.md
