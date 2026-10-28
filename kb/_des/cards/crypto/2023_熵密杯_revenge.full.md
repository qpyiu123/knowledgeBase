---
title: "2023 熵密杯 revenge"
category: crypto
tags: ["熵密杯 2023", "crypto", "openssl补丁", "drbg_lib硬编码随机数", "TLS预主密钥恢复", "Wireshark解密"]
signals: ["熵密杯 2023 2023", "openssl补丁", "drbg_lib硬编码随机数", "TLS预主密钥恢复", "Wireshark解密", "SM2临时密钥派生", "SHA256(seed)", "临时密钥恢复私钥", "crypto_oracle", "Gitea", "openssl", "TLS", "SM2", "crypto"]
difficulty: hard
source: "https://www.ctfiot.com/133267.html"
tools: ["Wireshark"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2023 熵密杯 revenge

> 赛事：熵密杯 2023 2023 | 方向：crypto | 难度：hard | 工具：Wireshark

## 一句话总结

Gitea 检测 openssl 硬编码随机数 → TLS 解密 → SM2 临时密钥派生 → 恢复私钥。

## 攻击链

1. Gitea 检材发现 openssl crypto/rand/drbg_lib.c 修改
2. 原本 32 字节随机数被写死成 32 字节常量数组
3. rand0_32 = {0x67, 0xc6, 0x69, ..., 0x9a} 用于服务端私钥生成
4. 用 X25519PrivateKey.from_private_bytes(rand0_32) 拿服务端私钥
5. X25519 客户端公钥 + 服务端私钥 → shared_key
6. Wireshark 导入 PMS_CLIENT_RANDOM + 共享密钥解密 TLS 流量
7. 找到 SM2 数字签名系统账号密码 + 验签源码
8. 分析 Sign 函数发现 time_parse + derive_from_time
9. derive_from_time(seed) = SHA256(seed) || SHA256(seed+1) || ... 输出 32 字节
10. 计算 msg1 时间戳对应的临时密钥 k
11. 签名 r,s 经 FlipEndian 处理，逆序还原数值
12. sk = (k - s) * inverse(s + r, n) % n 恢复私钥
13. 用私钥给 msg2 签名，伪造合法签名

## 关键 payload

```
rand0_32 = {0x67, 0xc6, 0x69, 0x73, 0x51, 0xff, 0x4a, 0xec, ...}
```

## 经验教训

openssl 改 drbg_lib.c 是经典后门；derive_from_time 用 SHA256(seed) 派生临时密钥可逆；SM2 签名 r,s 有字节序处理。

## 标签

openssl补丁、drbg_lib硬编码随机数、TLS预主密钥恢复、Wireshark解密、SM2临时密钥派生、SHA256(seed)、临时密钥恢复私钥

## 参考来源

- https://www.ctfiot.com/133267.html
- 原文件：2023_熵密杯_revenge.full.md
