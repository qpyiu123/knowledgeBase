---
title: "DASCTF 2025 上半年赛 Writeup by Mini-Venom"
category: crypto
tags: ["DASCTF", "crypto", "obex", "bluetooth", "lsb-stego", "openssl"]
signals: ["DASCTF 2025", "obex", "bluetooth", "lsb-stego", "openssl", "rsa-key-recover", "sm4", "sm2", "xianyu-fs", "misc_math", "DASCTF", "Mini-Venom", "OBEX", "RSA"]
difficulty: medium
source: "https://www.ctfiot.com/258051.html"
tools: ["hashcat", "tshark"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DASCTF 2025 上半年赛 Writeup by Mini-Venom

> 赛事：DASCTF 2025 | 方向：crypto | 难度：medium | 工具：hashcat、tshark

## 一句话总结

DASCTF 2025 上半年赛 Mini-Venom 战队 WP，OBEX/RSA 复私钥/ECDSA 复用/SM4 文件系统解密。

## 攻击链

1. BlueTrace: tshark 提 OBEX 图片
2. 像素 hex 拼接
3. Webshell Plus: 提 RSA p,q 复私钥
4. openssl_decrypt AES-128
5. TCP 流找 /etc/shadow
6. hashcat 爆破 root 密码
7. Excessive Security: ECDSA r 复用恢复 sk
8. 多项式 GCD 攻击
9. xianyu_decrypt: SM4 解密

## 关键 payload

```
OBEX 流量 + RSA 私钥恢复 + ECDSA nonce 复用
```

## 经验教训

蓝牙 OBEX 协议 tshark `-Y obex.header.value.byte_sequence` 抓图片；RSA 私钥只要 p,q 可直接 cryptography 重构。

## 标签

obex、bluetooth、lsb-stego、openssl、rsa-key-recover、sm4、sm2、xianyu-fs

## 参考来源

- https://www.ctfiot.com/258051.html
- 原文件：DASCTF_2025上半年赛_Writeup_by_Mini-Venom.full.md
