---
title: "CSAW CTF 2023 Writeup"
category: pwn
tags: ["CSAW CTF", "pwn", "unlimited_subway 32位", "canary泄", "Partial RELRO", "No PIE"]
signals: ["CSAW CTF 2023", "unlimited_subway 32位", "canary泄", "Partial RELRO", "No PIE", "super_secure_heap 64位", "Full RelRO PIE", "endbr64", "整数边界", "pwn_unknown", "CSAW", "CTF", "unlimited_subway", "canary"]
difficulty: medium
source: "https://www.ctfiot.com/136187.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# CSAW CTF 2023 Writeup

> 赛事：CSAW CTF 2023 | 方向：pwn | 难度：medium

## 一句话总结

CSAW CTF 2023 — unlimited_subway 32位 canary按字节泄+super_secure_heap 64位 PIE+Full RELRO set/delete secure_stuff 漏洞链。

## 攻击链

1. unlimited_subway: 32 位 ELF, Canary/NX/Partial RELRO/No PIE
2. view_account 按字节读, index 128-131 读 4 字节 canary
3. payload: 44 ''A'' + ''AAAA''*5 + p32(canary) + p32(0x0804900e) + p32(0x8049304)
4. super_secure_heap: 64 位 ELF PIE + Full RELRO + Canary
5. set(): 读 int item 0-9, size 必须 < 已存 size, secure_stuff(key)
6. delete(): free + 条件清零 size 和指针
7. 整数边界 set 触发越界, secure_stuff 漏洞

## 关键 payload

```
view 按字节读 / canary 128-131 / 44+20+4+4+4 payload / endbr64 64位 PIE / set 整数边界 / secure_stuff 加密
```

## 经验教训

按字节 (printf %02x) 读 canary 是经典;32 位 Partial RELRO 可直接覆盖返回;64 位 PIE + Full RELRO 需 leak PIE base + 改 got (Full RELRO 不行只能 FSOP/IO_FILE)。

## 标签

unlimited_subway 32位、canary泄、Partial RELRO、No PIE、super_secure_heap 64位、Full RelRO PIE、endbr64、整数边界、set+delete+secure_stuff、F/D/V/E 命令

## 参考来源

- https://www.ctfiot.com/136187.html
- 原文件：CSAW_CTF_2023_Writeup.full.md
