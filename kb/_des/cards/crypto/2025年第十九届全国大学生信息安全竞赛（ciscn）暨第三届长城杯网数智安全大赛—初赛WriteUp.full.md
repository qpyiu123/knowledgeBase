---
title: "2025 年第十九届全国大学生信息安全竞赛（CISCN）暨第三届长城杯网数智安全大赛—初赛 WriteUp"
category: crypto
tags: ["2025 CISCN / 第三届长城杯网数智", "crypto", "CISCN 2025 第十九届 长城杯 第三届 网数智", "ECDSA 私钥 sha512 Welcome to this challenge 模 n", "nonce k sha512 bias+i 已知 60 条", "双层 RSA 内外层 smooth_prime"]
signals: ["2025 CISCN / 第三届长城杯网数智 2025", "CISCN 2025 第十九届 长城杯 第三届 网数智", "ECDSA 私钥 sha512 Welcome to this challenge 模 n", "nonce k sha512 bias+i 已知 60 条", "双层 RSA 内外层 smooth_prime", "get_smooth_prime(1024", "20", "max_prime=p1)", "wasm2wat GDSC 版本 0x65", "ecdsa", "crypto_rsa", "block_cipher", "lattice", "CISCN"]
difficulty: hard
source: "https://www.ctfiot.com/290371.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2025 年第十九届全国大学生信息安全竞赛（CISCN）暨第三届长城杯网数智安全大赛—初赛 WriteUp

> 赛事：2025 CISCN / 第三届长城杯网数智 2025 | 方向：crypto | 难度：hard

## 一句话总结

2025 CISCN 第十九届+长城杯第三届初赛：ECDSA 已知私钥 + 双层 RSA smooth prime + wasm GDSC zstd + AES-128-GCM + 错误注入无列名二分。

## 攻击链

1. ECDSA: 私钥 d = sha512(Welcome...) % n, 60 条 nonce 已知 → d = (s*k - e) * pow(r, -1, n)
2. 双层 RSA: 内层 n1=p1*q1*r1*s1 (4 个 512-bit), 外层 n=p*q*r*s (1024-bit smooth 含 p1)
3. get_smooth_prime 把 p1 嵌入 p-1 因子 → Pollard rho 拆出 p1 → gcd(n, n1) 暴露共享 p1
4. wasm2wat release.wasm → 0x65 GDSC zstd 解压 → AES-ECB FanBglFanBglOoO!
5. ET3RNUMX 网络协议 AES-128-GCM KEY=xfqGcVjrOWp5tUGCPFQq448nPDjILTe7
6. exp(710) 错误注入：if((table)>('test'),exp(710),1) → 0.7s 延迟或错误判 1/0
7. blind 二分 32-126 ASCII 范围逐字符

## 关键 payload

```
d = (s*k - e) * pow(r, -1, n) % n
```

## 经验教训

CISCN 是国内最大 CTF 双赛（信安+长城杯网数智），初赛涉及密码学/逆向/Web/Pwn/AI 全栈；ECDSA 已知 nonce 直接拿 d；smooth prime Pollard rho 拆因子是 RSA 经典套路。

## 标签

CISCN 2025 第十九届 长城杯 第三届 网数智、ECDSA 私钥 sha512 Welcome to this challenge 模 n、nonce k sha512 bias+i 已知 60 条、双层 RSA 内外层 smooth_prime、get_smooth_prime(1024、20、max_prime=p1)、wasm2wat GDSC 版本 0x65、zstd 解压、AES-ECB FanBglFanBglOoO! wOW~youAregrEaT!、ET3RNUMX ET3 GCM AES-128、scapy rdpcap TCP Raw、SQL 无列名注入 where_is_my_flagggggg exp(710) error-based、if((table)>('test')、exp(710)、1)

## 参考来源

- https://www.ctfiot.com/290371.html
- 原文件：2025年第十九届全国大学生信息安全竞赛（ciscn）暨第三届长城杯网数智安全大赛—初赛WriteUp.full.md
