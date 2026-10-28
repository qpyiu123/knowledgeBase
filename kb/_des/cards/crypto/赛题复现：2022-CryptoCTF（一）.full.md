---
title: "赛题复现:2022-CryptoCTF(一)"
category: crypto
tags: ["CryptoCTF 2022", "crypto", "congruence", "modular-arith", "AES-CBC", "known-plaintext"]
signals: ["CryptoCTF 2022 2022", "congruence", "modular-arith", "AES-CBC", "known-plaintext", "3DES-MITM", "rsa-multi-prime", "DLP", "RsaCtfTool", "misc_math", "CryptoCTF", "Congruence", "AES", "DES"]
difficulty: medium
source: "https://www.ctfiot.com/58892.html"
tools: ["Sage"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 赛题复现:2022-CryptoCTF(一)

> 赛事：CryptoCTF 2022 2022 | 方向：crypto | 难度：medium | 工具：Sage

## 一句话总结

2022 CryptoCTF复现第一部分,涵盖Congruence同余式+AES已知明文攻击+3DES meet-in-the-middle+RSA多素数等经典密码学考点。

## 攻击链

1. Klamkin (Congruence): 已知(ax+by)%q=0对任意(ar+bs)%q=0成立,求(x,y)满足y是12-bit
2. 设x或y为getPrime(n),另一个由inverse计算
3. 交互式脚本:循环G/S选项+逆元算x或y
4. flag: CCTF{f1nDin9_In7Eg3R_50Lut1Ons_iZ_in73rEStIn9!}
5. Baphomet: 已知明文攻击,AES密钥在文件中,plain.txt+cipher.txt+key恢复
6. 多题涵盖Congruence+逆向数学题+3DES meet-in-the-middle+RSA多素数攻击

## 关键 payload

```
CCTF{f1nDin9_In7Eg3R_50Lut1Ons_iZ_in73rEStIn9!}
```

## 经验教训

任何(a,b)满足(ar+bs)%q=0时(ax+by)%q=0都成立,说明(x,y)与(r,s)同余,可设x或y为getPrime(n)然后inverse算另一个;CCTF的题多覆盖经典数学密码学。

## 标签

congruence、modular-arith、AES-CBC、known-plaintext、3DES-MITM、rsa-multi-prime、DLP、RsaCtfTool、Winedemic、differential-cryptanalysis、Sage、sympy

## 参考来源

- https://www.ctfiot.com/58892.html
- 原文件：赛题复现：2022-CryptoCTF（一）.full.md
