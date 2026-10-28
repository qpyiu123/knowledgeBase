---
title: "Solving SandboxAQ's Post-Quantum Crypto CTF"
category: crypto
tags: ["SandboxAQ", "crypto", "post-quantum", "lwe", "ring-lwe", "module-lwe"]
signals: ["SandboxAQ 2024", "post-quantum", "lwe", "ring-lwe", "module-lwe", "kyber-768", "x25519kyber768", "prng-brute", "lattice", "SandboxAQ", "CTF", "Module-LWE", "Kyber-1024", "PRNG"]
difficulty: hard
source: "https://www.ctfiot.com/169657.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Solving SandboxAQ's Post-Quantum Crypto CTF

> 赛事：SandboxAQ 2024 | 方向：crypto | 难度：hard

## 一句话总结

SandboxAQ 后量子密码 CTF：Module-LWE 攻击 + Kyber-1024 PRNG 爆破 + X25519+Kyber768 混合 TLS 解密。

## 攻击链

1. rotMatrix poly cyclotomic=True 构造 X^N+1 上的旋转矩阵
2. module(polys, 2, 2) 拼装 2x2 块矩阵
3. LWE 攻击：DBDD_predict 估计 δ=1.045280 β=2.00
4. NTL ZZ_pX + OpenMP 并行爆破 s1, s2 ∈ {0,1}^16
5. 找到 s1=RR([1,1,1,1,1,0,1,1,0,0,0,1,0,0,1,1]) s2=RR([1,0,0,0,1,0,1,1,1,0,0,1,0,1,1,1])
6. 解密 v - s*u^T 再 decompress 还原 16 bit
7. flag = [1,0,0,1,0,1,1,0,0,1,1,1,0,0,0,1]
8. Kyber NIST KAT: entropy_input 24 bit 暴力枚举
9. OQS_KEM_kyber_1024_keypair 对比 test_public_key
10. 找到 seed 后复现 ECDH
11. x25519 + Kyber768 混合 TLS 抓包解密
12. wireshark 抓 pcap → pcap_processing → 解出 HTTP 响应
13. /dir/.../server_secret.txt → My v0ice is my p@ssport.
14. 54318...d90 = 真正的 flag

## 关键 payload

```
OQS_randombytes_nist_kat_init_256bit(entropy_input, NULL)
```

## 经验教训

后量子密码实现若 PRNG 种子空间过小，仍可通过暴力枚举恢复 shared secret。

## 标签

post-quantum、lwe、ring-lwe、module-lwe、kyber-768、x25519kyber768、prng-brute

## 参考来源

- https://www.ctfiot.com/169657.html
- 原文件：Solving_SandboxAQ’s_Post-Quantum_Crypto_CTF.full.md
