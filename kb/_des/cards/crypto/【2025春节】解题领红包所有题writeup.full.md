---
title: "2025 春节 解题领红包所有题 writeup"
category: crypto
tags: ["春节活动", "crypto", "XXTEA", "SPN", "AES-OFB", "custom-VM"]
signals: ["春节活动 2025", "XXTEA", "SPN", "AES-OFB", "custom-VM", "phoenixAES", "XTEA", "TEA", "md5-bruteforce", "crypto_symmetric", "writeup", "AES", "OFB", "delta"]
difficulty: medium
source: "https://www.ctfiot.com/227568.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2025 春节 解题领红包所有题 writeup

> 赛事：春节活动 2025 | 方向：crypto | 难度：medium

## 一句话总结

2025 春节解题领红包全题 writeup，覆盖 XXTEA + 自定义 SPN + AES OFB + 魔改 XTEA + 自定义 VM 5 大密码学/逆向方向。

## 攻击链

1. XXTEA 6+52/n 轮 + delta=0x9E3779B9 解密 SPN 密码 24 字节 S-box 拆位 (32 字节 16 字节) 查表/pheonixAES.crack_file AES OFB 已知 key=7E13141528AED2A6ABF7158809CF4F3C iv=0/AES mode=OFB/魔改 XTEA 12 轮 + delta=0xB979379E 加密 timestamp+uid+hash/VM 自定义指令 17 种操作 xor/neg/pop/or/nop/ret/cmpnz/swap/and/shl/div/add 栈机/flag 拼接 md5(uid) + "{}

## 关键 payload

```
AES key=7E13141528AED2A6ABF7158809CF4F3C  魔改 XTEA delta=0xB979379E  12 轮  XXTEA key="my-xxtea-secret\x00
```

## 经验教训

phoenixAES 用于 AES DPA 侧信道攻击或已知末轮密钥恢复；魔改 XTEA 把 delta 改成 0xB979379E 是非标准变种；XXTEA 的 6+52/n 轮数随 n 变化；自定义 VM 栈机 op>>3 区分操作 op&7 取立即数 7 表示后续字节为 16 位立即数。

## 标签

XXTEA、SPN、AES-OFB、custom-VM、phoenixAES、XTEA、TEA、md5-bruteforce

## 参考来源

- https://www.ctfiot.com/227568.html
- 原文件：【2025春节】解题领红包所有题writeup.full.md
