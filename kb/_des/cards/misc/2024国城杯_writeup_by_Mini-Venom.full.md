---
title: "2024 国城杯 writeup by Mini-Venom"
category: misc
tags: ["国城杯", "misc", ".264 视频隐写", "np.random seed 爆破", "DataMatrix 二维码", "PGP wordlist 编码"]
signals: ["国城杯 2024", ".264 视频隐写", "np.random seed 爆破", "DataMatrix 二维码", "PGP wordlist 编码", "shiro 反序列化", "AES-ECB", "AES key=oursecret", "stego_image", "stego_traffic", "crypto_unknown", "misc_unknown", "UDP", "seed"]
difficulty: medium
source: "https://www.ctfiot.com/219184.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 国城杯 writeup by Mini-Venom

> 赛事：国城杯 2024 | 方向：misc | 难度：medium

## 一句话总结

UDP .264 视频 + seed 爆破乱序图 + PGP 词表 + AES-ECB。

## 攻击链

1. 1. Tr4ffIc_w1th_Ste90: password.pacpng → 追踪 UDP 流 → hex 还原 → 改后缀 .264 → VLC 拿压缩包密码 → 解压 → 乱序图片 (np.random.shuffle 行列) → 爆破 seed → DataMatrix 二维码 → 在线扫码 → PGP wordlist 解密 / 2. Just_F0r3n51Cs: 流量包导图 → 拼接还原 → base64 → oursecret is D0g3xGC → AES-ECB 解密

## 关键 payload

```
np.random.seed(seed) ; np.random.shuffle(row_indices) ; np.argsort 还原 ; PGP wordlist 'crumpled' = '44' ; AES-ECB key='oursecret is D0g3xGC' ; shiro 默认 key
```

## 经验教训

PGP 词表每个 2 字母/词对应 0x00-0xFF 字节；np.random.shuffle 行列只需 argsort 还原。

## 标签

.264 视频隐写、np.random seed 爆破、DataMatrix 二维码、PGP wordlist 编码、shiro 反序列化、AES-ECB、AES key=oursecret

## 参考来源

- https://www.ctfiot.com/219184.html
- 原文件：2024国城杯_writeup_by_Mini-Venom.full.md
