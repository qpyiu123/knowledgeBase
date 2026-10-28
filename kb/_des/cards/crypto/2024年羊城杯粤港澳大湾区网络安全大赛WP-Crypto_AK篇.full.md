---
title: "2024 羊城杯 Crypto AK 篇（DASCTF 套题）"
category: crypto
tags: ["2024 羊城杯粤港澳大湾区网络安全大赛", "crypto", "Hessian curve", "EllipticCurve_from_cubic", "discrete_log", "自定义曲线离散对数"]
signals: ["2024 羊城杯粤港澳大湾区网络安全大赛 2024", "Hessian curve", "EllipticCurve_from_cubic", "discrete_log", "自定义曲线离散对数", "AES-CBC SHA256", "RSA padding", "RSA Iroot", "bcactf rsa-is-broken", "lattice", "ecdsa", "crypto_rsa", "DASCTF", "Hessian"]
difficulty: medium
source: "https://www.ctfiot.com/203023.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 羊城杯 Crypto AK 篇（DASCTF 套题）

> 赛事：2024 羊城杯粤港澳大湾区网络安全大赛 2024 | 方向：crypto | 难度：medium

## 一句话总结

把 5 道 DASCTF 套题串成一篇——Hessian 曲线、自定义曲线离散对数、ECC log、AES 派生、bcactf 原题搬运、RSA sqrt+CRT，每题一段解题脚本。

## 攻击链

1. 识别 Hessian curve ax³+y³+1=dxy 公式还原 d
2. EllipticCurve_from_cubic 升维到 Weierstrass 再 discrete_log
3. 小阶曲线穷举 i ∈ [0,1000] 比对 P 还原乘数
4. 标准 ECC curve 离散对数 P.log(G)
5. k 已知 → SHA256(key)[:16] + AES-CBC(iv) 解密
6. 短密文 m=c^d mod n → 加 n*256 跳到 DASCTF{ 前缀
7. 大整数 n 用 iroot(n,2) 取整 + next_prime 试 p

## 关键 payload

```
PR.<d>=PolynomialRing(Zmod(p)); f=a*gx^3+gy^3+1-d*gx*gy; f.roots()
```

## 经验教训

Hessian curve 化简到 Weierstrass 是 SageMath 一行 EllipticCurve_from_cubic 的事；CTF Crypto 真题常把 bcactf / corCTF 等国外比赛原题直接搬来当套题，看 flag 样式就能秒判出处。

## 标签

Hessian curve、EllipticCurve_from_cubic、discrete_log、自定义曲线离散对数、AES-CBC SHA256、RSA padding、RSA Iroot、bcactf rsa-is-broken

## 参考来源

- https://www.ctfiot.com/203023.html
- 原文件：2024年羊城杯粤港澳大湾区网络安全大赛WP-Crypto_AK篇.full.md
