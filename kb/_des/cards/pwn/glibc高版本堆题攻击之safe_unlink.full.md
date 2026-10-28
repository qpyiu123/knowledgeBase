---
title: "glibc 高版本堆题攻击之 safe unlink"
category: pwn
tags: ["ctf-share", "pwn", "glibc-2.32", "glibc-2.33", "safe-linking", "tcache"]
signals: ["ctf-share 2022", "glibc-2.32", "glibc-2.33", "safe-linking", "tcache", "fastbin", "fd-xor", "uxor", "uaf", "pwn_unknown", "glibc", "pos", "ptr", "unsorted"]
difficulty: hard
source: "https://www.ctfiot.com/65732.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# glibc 高版本堆题攻击之 safe unlink

> 赛事：ctf-share 2022 | 方向：pwn | 难度：hard

## 一句话总结

glibc 2.32+ 堆利用：safe-linking 机制 + tcache fd 异或攻击。

## 攻击链

1. 识别 safe-linking 异或密钥 (pos >> 12) ^ ptr
2. 填满 tcache 触发 unsorted bin
3. 泄 libc + heap 地址
4. 计算密钥 key = heap >> 12
5. 改 tcache fd 为 (free_hook ^ key)
6. 申请覆盖 __free_hook = system
7. 触发 free("/bin/sh")

## 关键 payload

```
safe-linking 异或密钥 + tcache fd 攻击
```

## 经验教训

glibc 2.32+ 的 safe-linking 机制本质是 tcache/fastbin fd 的 12-bit ASLR 异或保护。

## 标签

glibc-2.32、glibc-2.33、safe-linking、tcache、fastbin、fd-xor、uxor、uaf

## 参考来源

- https://www.ctfiot.com/65732.html
- 原文件：glibc高版本堆题攻击之safe_unlink.full.md
