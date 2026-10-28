---
title: "【pwn61.0】Oath to Order - Ricerca CTF 2023"
category: pwn
tags: ["RicercaCTF", "pwn", "aligned_alloc", "size-0-bug", "getstr-overflow", "fastbin-free"]
signals: ["RicercaCTF 2023", "aligned_alloc", "size-0-bug", "getstr-overflow", "fastbin-free", "libc-leak", "malloc-algorithm", "fuzzer-find-vuln", "heap_exploit", "Ricerca", "CTF", "Oath", "Order", "size"]
difficulty: hard
source: "https://www.ctfiot.com/111898.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【pwn61.0】Oath to Order - Ricerca CTF 2023

> 赛事：RicercaCTF 2023 | 方向：pwn | 难度：hard

## 一句话总结

Ricerca CTF 2023 Oath to Order 高级堆题，aligned_alloc size=0 整数零化触发任意长输入 + fastbin 残留 libc 指针泄地址。

## 攻击链

1. 1. NOTE_LEN=10 NOTE_SIZE=300 不可 free/edit/create(idx, align, size, data) 多次写同 index 重新 alloc/2. aligned_alloc(align, size) + size=0 时 getstr(buf, 0) while(--size) 不进入循环任意长输入 → 堆溢出/3. align=0xF0 + size=0x20 aligned_alloc split 3 块 1+3 释放 + 残留 main_arena libc 指针/4. Fuzz 找 size=0 漏洞

## 关键 payload

```
aligned_alloc(0xF0, 0) + getstr size=0 任意长输入  fastbin 残留 libc 指针 0x7f1773219ce0
```

## 经验教训

aligned_alloc(align, size) 内部走 __int_memalign → __int_malloc(size + align) split 3 块机制；size=0 时 getstr while(--size) 直接退出，可写任意长数据；fastbin 残留指针是经典 libc 泄方法。

## 标签

aligned_alloc、size-0-bug、getstr-overflow、fastbin-free、libc-leak、malloc-algorithm、fuzzer-find-vuln

## 参考来源

- https://www.ctfiot.com/111898.html
- 原文件：【pwn61.0】Oath_to_Order_–_Ricerca_CTF_2023.full.md
