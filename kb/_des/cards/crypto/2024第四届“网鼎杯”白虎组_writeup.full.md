---
title: "2024 第四届\"网鼎杯\"白虎组 writeup（GTP TEID + AES-ECB + SPN 仿射）"
category: crypto
tags: ["2024 第四届网鼎杯", "crypto", "白虎 misc01 GTP TEID 统计排序", "tshark gtp.teid", "tshark e GTP 流", "misc02 AES-ECB TEID 当 key"]
signals: ["2024 第四届网鼎杯 2024", "白虎 misc01 GTP TEID 统计排序", "tshark gtp.teid", "tshark e GTP 流", "misc02 AES-ECB TEID 当 key", "misc03 php filter 侧信道", "misc04 三个文件合并 zip 伪加密", "CRYPTO01 SPN P(x) 仿射变换", "S 看作 chips 线性变换", "block_cipher", "lattice", "ssrf", "crypto_rsa", "GTP"]
difficulty: hard
source: "https://www.ctfiot.com/213306.html"
tools: ["binwalk", "tshark"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 第四届"网鼎杯"白虎组 writeup（GTP TEID + AES-ECB + SPN 仿射）

> 赛事：2024 第四届网鼎杯 2024 | 方向：crypto | 难度：hard | 工具：binwalk、tshark

## 一句话总结

白虎组四题：GTP TEID 统计 + AES-ECB + php filter 侧信道 + zip 伪加密 + SPN 仿射 LLL 还原 keys。

## 攻击链

1. misc01: tshark -r UPF.cap -e "gtp.teid" 统计排序两处异常 TEID 拼接
2. misc02: TEID 作 AES-ECB key 解密加密流量
3. misc03: php filter convert.quoted-printable-encode 3000 次侧信道 (DownUnderCTF 2022 minimal-php 同款)
4. misc04: cat 1 2 3 > 1.zip binwalk 看 2.png 伪加密 + !@#QQQ0010flag**** 掩码爆破
5. CRYPTO01: P(x) = P*x, S(x) = A*x + b，T = P^{-1}AP, U = P^{-1}b
6. r = T^{14} x + (T^{13}+...+I) U + (T^{13}+...+I) P^{-1} k
7. flag 头 "wdflag{" 7 字符，爆破 1 字节解方程组，得 keys 列表
8. chips 只有 1 和 -1 → 对 S 求 LLL

## 关键 payload

```
S = chips 线性变换；S = LLL(chips) 还原 keys
```

## 经验教训

GTP 协议 TEID 是 5G 核心网隧道标识，tshark -e gtp.teid 提取；SPN 密码里 S 看作 chips 线性变换（chips ∈ {1,-1}）时，直接对 S 求 LLL 即可还原 key 比特。

## 标签

白虎 misc01 GTP TEID 统计排序、tshark gtp.teid、tshark e GTP 流、misc02 AES-ECB TEID 当 key、misc03 php filter 侧信道、misc04 三个文件合并 zip 伪加密、CRYPTO01 SPN P(x) 仿射变换、S 看作 chips 线性变换、对 S 求 LLL 还原 keys、flag 头 wdflag{ 爆破 1 字节

## 参考来源

- https://www.ctfiot.com/213306.html
- 原文件：2024第四届“网鼎杯”白虎组_writeup.full.md
