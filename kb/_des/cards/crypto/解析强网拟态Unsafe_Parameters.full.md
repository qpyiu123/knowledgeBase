---
title: "解析强网拟态 Unsafe Parameters - 共享私钥指数 RSA 攻击"
category: crypto
tags: ["强网拟态", "crypto", "RSA-shared-d", "LLL", "lattice-attack", "multi-prime-RSA"]
signals: ["强网拟态 2025", "RSA-shared-d", "LLL", "lattice-attack", "multi-prime-RSA", "AES-ECB", "SHA3-512", "Hidden-Number-Problem", "HNP", "crypto_rsa", "Unsafe", "Parameters", "RSA", "AES"]
difficulty: hard
source: "https://www.ctfiot.com/277005.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 解析强网拟态 Unsafe Parameters - 共享私钥指数 RSA 攻击

> 赛事：强网拟态 2025 | 方向：crypto | 难度：hard

## 一句话总结

强网拟态 2025 Unsafe Parameters：5 组 RSA 共享 d 触发 LLL 攻击，构造 6×6 矩阵恢复 d 分解模数解 AES。

## 攻击链

1. 5 组 RSA 共享一个 425 位素数 d 作为私钥
2. 每组 n = p*q*r (3 × 512-bit primes) + e_i = d^(-1) mod φ(n_i)
3. 关键: e_i × d ≈ k_i × n_i (近似关系)
4. 构造 6×6 格矩阵:
5. M = 2^1024 平衡常数
6. LLL 规约 → 短向量第一行 = (M*d, d*e_0-k_0*n_0, ...)
7. d = abs(Mat_LLL[3][0]) // M
8. 验证 d 比特长度 425 + isPrime(d)
9. 用 d 分解每个 n (g^t mod n 与 gcd 与 n 找因子)
10. 每组 p*q*r = n, 用 e*d-1 = k*φ(n) 找到 2^s*t
11. sum = Σ(p+q+r) over 5 组
12. AES-ECB key = sha3_512(str(sum).encode()).digest()[:16]
13. 解密 flag = flag{9b31dd3e-aa6a-4c4d-b796-bff4e4dfe0cc}

## 关键 payload

```
5 组共享 d + LLL 6×6 矩阵 + d 分解 n × 5 + SHA3-512[:16] AES-ECB
```

## 经验教训

多组 RSA 共享私钥是致命漏洞；e×d ≈ k×n 近似关系 + LLL 短向量是经典攻击。

## 标签

RSA-shared-d、LLL、lattice-attack、multi-prime-RSA、AES-ECB、SHA3-512、Hidden-Number-Problem、HNP、three-prime、425-bit-d

## 参考来源

- https://www.ctfiot.com/277005.html
- 原文件：解析强网拟态Unsafe_Parameters.full.md
