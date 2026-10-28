---
title: "【NKCTF】babyHeap - Off by one & Tcache Attack"
category: pwn
tags: ["NKCTF", "pwn", "glibc", "off-by-one", "tcache-poisoning", "note-array"]
signals: ["NKCTF 2023", "glibc", "off-by-one", "tcache-poisoning", "note-array", "show", "UAF", "safe-linking", "strtol", "heap_exploit", "NKCTF", "babyHeap", "size", "tcache"]
difficulty: medium
source: "https://www.ctfiot.com/167429.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【NKCTF】babyHeap - Off by one & Tcache Attack

> 赛事：NKCTF 2023 | 方向：pwn | 难度：medium

## 一句话总结

NKCTF babyHeap 经典 off-by-one 堆题，覆盖 size+1 字节改 size 字段触发 tcache 攻击。

## 攻击链

1. 程序 16 个 nkctf notes 槽位 + add(size <=256) + delete + edit + show /off-by-one 编辑溢出 size+1 字节覆盖下一 chunk size 字段 /tcache 0x90 size 喷射 + delete 触发 tcache /edit 改 fd 指向 __free_hook

## 关键 payload

```
glibc 2.31 tcache poisoning + off-by-one 0x90 bin
```

## 经验教训

off-by-one 是 PWN 入门最常见堆漏洞；tcache 0x90 大小喷射配合 size 字段篡改可实现任意地址写。

## 标签

glibc、off-by-one、tcache-poisoning、note-array、show、UAF、safe-linking、strtol

## 参考来源

- https://www.ctfiot.com/167429.html
- 原文件：【NKCTF】babyHeap-Off_by_one&Tcache_Attack.full.md
