---
title: "ångstromCTF Writeup by VP-Union"
category: crypto
tags: ["ångstromCTF", "crypto", "caesar-shift", "RSA-Leak-pmqm", "RSA-homomorphic", "fake_psi"]
signals: ["ångstromCTF 2023", "caesar-shift", "RSA-Leak-pmqm", "RSA-homomorphic", "fake_psi", "one_encoding", "zero_encoding", "fmt-string", "jinja2-SSTI", "crypto_rsa", "VP-Union", "ngstromCTF", "crypto", "RSA"]
difficulty: medium
source: "https://www.ctfiot.com/122441.html"
tools: ["Z3"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# ångstromCTF Writeup by VP-Union

> 赛事：ångstromCTF 2023 | 方向：crypto | 难度：medium | 工具：Z3

## 一句话总结

VP-Union ångstromCTF 2023 第二份 WP，crypto 比重更大，含 RSA 二方程解、homomorphic oracle、伪 set 交为空 trick。

## 攻击链

1. Caesar 26 shift 爆破/ RSA 给 (p-2)(q-1) 和 (p-1)(q-2) 两个方程 z3 解出 p q 算 (p-1)(q-1) phi/RSA homomorphic 给 5-bit X prime 选 X 让 Y = c*X^e mod n 通过解密 oracle 拿到 Y^d = m*X mod n 枚举 i 让 (n*i + m*X) / X 含 actf/fake_psi + one_encoding/zero_encoding: x=1<<64 + 1 即 65 位 1 / y=1<<64 即 64 位 1 满足 one_encoding(x) ∩ zero_encoding(y) = ∅

## 关键 payload

```
caesar: c = "rtkw{cf0bj_czbv_nv''cc_y4mv_kf_kip_re0kyvi_uivjj1ex_5vw89s3r44901831}" shift=12 → actf{lo0ks_like_we''ll_h4ve_to_try_an0ther_dress1ng_5ef89b3a44901831}
```

## 经验教训

RSA 二方程 (p-2)(q-1) + (p-1)(q-2) + n 可解 p q；homomorphic RSA 选 X prime 让 Y = c*X^e mod n 通过 oracle 拿到 m*X mod n；伪 set 交为空需要 one_encoding(x) 与 zero_encoding(y) 完全互斥。

## 标签

caesar-shift、RSA-Leak-pmqm、RSA-homomorphic、fake_psi、one_encoding、zero_encoding、fmt-string、jinja2-SSTI、BEAM-bytecode

## 参考来源

- https://www.ctfiot.com/122441.html
- 原文件：ångstromCTF_Writeup_by_VP-Union.full.md
