---
title: "2025 LitCTF ez_math - 2×2 矩阵幂 Cayley-Hamilton 攻击"
category: crypto
tags: ["LitCTF", "crypto", "matrix-power", "Cayley-Hamilton", "finite-field", "quadratic-extension"]
signals: ["LitCTF 2025", "matrix-power", "Cayley-Hamilton", "finite-field", "quadratic-extension", "GF-p2", "quotient-ring", "RSA-matrix", "modular-inverse", "crypto_rsa", "LitCTF", "ez_math", "mod", "flag"]
difficulty: hard
source: "https://www.ctfiot.com/278432.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2025 LitCTF ez_math - 2×2 矩阵幂 Cayley-Hamilton 攻击

> 赛事：LitCTF 2025 | 方向：crypto | 难度：hard

## 一句话总结

LitCTF 2025 ez_math：2×2 矩阵 A^e mod p 的 Cayley-Hamilton 攻击，把高次幂降维到商环多项式求逆。

## 攻击链

1. 加密: A = [[flag, getPrime], [getPrime, getPrime]]; B = A^e mod p (e=65537, p 512-bit 素数)
2. 关键: flag 在 A[0][0]
3. Cayley-Hamilton: M² - (tr M)·M + (det M)·I = 0 → M^n = p_n·M - (det M)·p_{n-1}·I
4. 特征多项式: χ_A(x) = x² - (tr A)x + det A
5. 特征值: B 的特征值 = A 特征值的 e 次方
6. 在 GF(p²)* 中, gcd(e, p²-1) = 1 → 映射 x → x^e 是双射
7. 计算私钥: d = inverse_mod(e, p²-1)
8. 商环: R = F_p[X]/(X² - s1·X + s2), X 模拟 B 的特征值
9. 计算 X^d = β + α·X (商环中快速幂)
10. 恢复 A: A = α·B + β·I
11. flag = A[0][0] = LitCTF{13dd217e-9a67-4093-8a1b-d2592c45ba82}

## 关键 payload

```
A = α·B + β·I + 商环 mul + pow_poly + d = inverse_mod(e, p²-1)
```

## 经验教训

Cayley-Hamilton 定理 + 二次扩域是矩阵密码的通用解法；商环运算避开了复杂特征值计算。

## 标签

matrix-power、Cayley-Hamilton、finite-field、quadratic-extension、GF-p2、quotient-ring、RSA-matrix、modular-inverse、characteristic-polynomial

## 参考来源

- https://www.ctfiot.com/278432.html
- 原文件：解析2025LitCTF_ez_math.full.md
