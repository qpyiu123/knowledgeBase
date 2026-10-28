---
title: "2025 年能源网络安全大赛 Writeup（ThinkPHP 3.2.2 写配置 + RSA 费马 + LWE BSGS）"
category: web
tags: ["2025 能源网络安全大赛", "web", "能源 2025", "ThinkPHP 3.2.2 报错泄露", "db[] 写配置 RCE", "is_numeric 289114abc 弱类型比较"]
signals: ["2025 能源网络安全大赛 2025", "能源 2025", "ThinkPHP 3.2.2 报错泄露", "db[] 写配置 RCE", "is_numeric 289114abc 弱类型比较", "php://filter 读 flaaaaaaag.php base64", "NumberTheory 费马 2^hint ≡ 1 mod p", "easy_lwe 30 组", "Quaternion 四元数 DLP", "rce", "lfi", "crypto_rsa", "lattice", "ThinkPHP"]
difficulty: medium
source: "https://www.ctfiot.com/242944.html"
tools: ["ThinkPHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2025 年能源网络安全大赛 Writeup（ThinkPHP 3.2.2 写配置 + RSA 费马 + LWE BSGS）

> 赛事：2025 能源网络安全大赛 2025 | 方向：web | 难度：medium | 工具：ThinkPHP

## 一句话总结

2025 能源网络安全：ThinkPHP 3.2.2 db[] 写配置 RCE + yunnuuu.php is_numeric 弱类型 + 费马小定理解 RSA + LWE Quaternion BSGS。

## 攻击链

1. Web easyInstall: ThinkPHP 3.2.2 db[]=mysqli&...&db[]=1''.phpinfo().@eval(...).''&... → 写配置 RCE
2. yunnuuu.php: tmp1=289114abc is_numeric 假阴性 ==289114 弱类型
3. tmp2=php://filter/.../flaaaaaaag.php base64 读源码
4. NumberTheory: hint+233k=233kp → 2^hint ≡ 1 mod p → p = gcd(2^hint-1, n)
5. easy_lwe: 30 组 (a, c) + p-1 大素因子 → Pohlig-Hellman
6. Quaternion DLP: Q=(123456789, 987654321, 135792468, 864297531) R=power(Q, secret) → BSGS secret < 2^50
7. jwtKey 2 位爆破 (charset a-zA-Z0-9 62 字符)

## 关键 payload

```
p = gcd(pow(2, hint, n) - 1, n)
```

## 经验教训

ThinkPHP 3.2.2 db[] 写配置 RCE 是历史漏洞；is_numeric 弱类型比较经典套（289114abc 不通过 is_numeric 但 == 289114）；费马小定理 2^hint ≡ 1 mod p → p = gcd(2^hint-1, n) 是常用套路。

## 标签

能源 2025、ThinkPHP 3.2.2 报错泄露、db[] 写配置 RCE、is_numeric 289114abc 弱类型比较、php://filter 读 flaaaaaaag.php base64、NumberTheory 费马 2^hint ≡ 1 mod p、easy_lwe 30 组、Quaternion 四元数 DLP、BSGS 优化 secret < 2^50、jwtKey 2 位爆破

## 参考来源

- https://www.ctfiot.com/242944.html
- 原文件：2025年能源网络安全大赛-Writeup.full.md
