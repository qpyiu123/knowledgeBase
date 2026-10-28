---
title: "2022 pwnhub 冬季赛 writeup by Arr3stY0u"
category: web
tags: ["2022 pwnhub 冬季赛", "web", "pwnhub", "git-objects", "zlib", "TCP-pcap"]
signals: ["2022 pwnhub 冬季赛 2022", "pwnhub", "git-objects", "zlib", "TCP-pcap", "base64-hexdump", "二分法", "CAN-bus", "飞驰人生", "lfi", "stego_traffic", "misc_math", "crypto_rsa", "TCP"]
difficulty: hard
source: "https://www.ctfiot.com/87197.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 pwnhub 冬季赛 writeup by Arr3stY0u

> 赛事：2022 pwnhub 冬季赛 2022 | 方向：web | 难度：hard

## 一句话总结

pwnhub 2022 冬季赛：git-objects + TCP hexdump + CAN-bus + RSA-gcd + LLL + 长度扩展

## 攻击链

1. Web Reset: 上传表单 ../.git/objects/5f/f1ef5c03448a1eb5571dd348cf717a7bad7402 + zlib 0x78 0x9C 头
2. PPC TCP_show: 解析 PCAP 包 16 字节/行 hexdump
3. MISC 飞驰人生: 二分法找超速报文 244#000000A60000 + 锁车报文 19B#00000F000000 → flag{244#000000A60000_19B#00000F000000}
4. MISC 坐井观天: 拼 chr() 字符串绕过字符限制 eval
5. Crypto ASR: gcd(RSA1, N) → s 大因子 → invert(65537, s-1) → flag
6. Crypto NN: LLL 短向量同时还原两个明文
7. Crypto POINT: 已知 e*d 范围 → randint g^((ed-1)/2^k) mod n → gcd(x-1, n) → p,q
8. Crypto: hlextend_bytes hash length extension attack

## 关键 payload

```
gcd(RSA1, N) = s → invert(e, s-1) → pow(c, d, s)
```

## 经验教训

PCAP 协议逆向 + git-objects 还原是 MISC 入门；gcd(RSA1,N) 是 RSA 经典；LLL 双明文恢复

## 标签

pwnhub、git-objects、zlib、TCP-pcap、base64-hexdump、二分法、CAN-bus、飞驰人生、chr-eval、RSAgcd、lattice-LLL、ECC-DLP、length-extension、hash-length-extension

## 参考来源

- https://www.ctfiot.com/87197.html
- 原文件：2022_pwnhub冬季赛_writeup_by_Arr3stY0u.full.md
