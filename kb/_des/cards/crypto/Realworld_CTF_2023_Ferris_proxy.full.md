---
title: "Realworld CTF 2023 - Ferris_proxy 逆向分析"
category: crypto
tags: ["Realworld CTF 2023", "crypto", "rust", "reverse", "custom-protocol", "rc4-encrypt"]
signals: ["Realworld CTF 2023 2023", "rust", "reverse", "custom-protocol", "rc4-encrypt", "rsa-key-exchange", "aes-128-cbc", "sha256-hmac", "pcapng", "crypto_oracle", "Realworld", "CTF", "Ferris_proxy", "Rust"]
difficulty: hard
source: "https://www.ctfiot.com/106020.html"
tools: ["Python", "Rust"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Realworld CTF 2023 - Ferris_proxy 逆向分析

> 赛事：Realworld CTF 2023 2023 | 方向：crypto | 难度：hard | 工具：Python、Rust

## 一句话总结

Realworld CTF 2023 Ferris_proxy：Rust 协议逆向 (有符号) + pcapng 全流量 rc4 解密 + RSA 加密 AES 密钥交换 + AES-128-CBC IV 16 字节 + ZIP XOR 双方 key。

## 攻击链

1. Rust binary (有符号) server 监听 8888 + client 二进制
2. 协议: TCP 包头 12 字节 = length(4) + action(4) + streamid(4)
3. action 0=open / 1=transfer / 2=close
4. rc4 全流量加密 + 密钥 explorer
5. serde_yaml::from_str 读硬编码 RSA 密钥
6. RSA 公钥加密 AES 密钥 = key_exchange
7. rsa_encrypt 自己的随机数 + rsa_decrypt 对方随机数
8. AES 密钥 = 双方随机数 ZIP XOR (rust 同域匿名函数)
9. 每个 stream 都进行 key_exchange: 256 字节 RSA + 2 字节长度 (0100) + AES key sha256
10. aes_128_cbc IV 每次 16 字节新生成
11. 包头: 4 字节 length + 16 字节 IV
12. 完整解密: 拆 c2s/s2c 流 → 解析 streamid → RSA 解 AES key → 算 XOR 双方 key
13. SHA256 校验双方 AES key
14. 找到 HTTP/1.0 200 OK SimpleHTTP/0.6 Python/3.6.9 响应
15. flag.txt 内容: rwctf{l1fe_1s_sh0rt_DO0...}
16. 提示: rust 闭包 + zip + map lambda (a^b) 计算 AES key

## 关键 payload

```
d_lst[streamid] = concat(0x0100+RSA(rand_self)+RSA(rand_other)) + SHA256(aes_key) + AES_CBC(data, iv)
```

## 经验教训

Rust 协议逆向关键是找闭包 (a^b) = zip+map 模式；rc4 全流量加密是初阶 (key=explorer)；RSA+AES key_exchange 模式在 4 stream 中重复；SHA256(aes_key) 校验保证双方 key 一致。

## 标签

rust、reverse、custom-protocol、rc4-encrypt、rsa-key-exchange、aes-128-cbc、sha256-hmac、pcapng、serde-yaml

## 参考来源

- https://www.ctfiot.com/106020.html
- 原文件：Realworld_CTF_2023_Ferris_proxy.full.md
