---
title: "pem 类文件解析及 2022 蓝帽杯 crypto 详解"
category: crypto
tags: ["蓝帽杯", "crypto", "pem", "rsa", "openssl", "asn1"]
signals: ["蓝帽杯 2022", "pem", "rsa", "openssl", "asn1", "der", "public-key", "private-key", "pfx", "crypto_rsa", "PEM", "RSA", "base64", "construct"]
difficulty: medium
source: "https://www.ctfiot.com/49973.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# pem 类文件解析及 2022 蓝帽杯 crypto 详解

> 赛事：蓝帽杯 2022 | 方向：crypto | 难度：medium

## 一句话总结

2022 蓝帽杯 PEM 文件 RSA 密码学详解。

## 攻击链

1. PEM 文件 base64 + 头尾标记
2. 解析 n/e/d/p/q/u 6 个参数
3. RSA.construct 重建密钥
4. 已知 p, q 算 phi 求 d
5. 用公钥加密 + 私钥解密

## 关键 payload

```
PEM 解析 + RSA 参数构造
```

## 经验教训

PEM 文件本质是 base64 编码的 ASN.1 DER 序列，含 6 个 RSA 参数。

## 标签

pem、rsa、openssl、asn1、der、public-key、private-key、pfx

## 参考来源

- https://www.ctfiot.com/49973.html
- 原文件：pem类文件解析及2022蓝帽杯crypto详解.full.md
