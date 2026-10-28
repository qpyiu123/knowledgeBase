---
title: "web选手入门pwn(20) 网鼎杯PWN01"
category: pwn
tags: ["网鼎杯", "pwn", "glibc-2.31", "unsorted-bin", "tcache", "__free_hook"]
signals: ["网鼎杯 2024", "glibc-2.31", "unsorted-bin", "tcache", "__free_hook", "leak-libc", "leak-heap", "heap_exploit", "PWN01", "glibc", "unsorted", "bin", "attack", "poison"]
difficulty: medium
source: "https://www.ctfiot.com/213214.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# web选手入门pwn(20) 网鼎杯PWN01

> 赛事：网鼎杯 2024 | 方向：pwn | 难度：medium

## 一句话总结

网鼎杯 PWN01，glibc 2.31 unsorted bin attack + tcache poison 覆盖 __free_hook=system 经典题。

## 攻击链

1. add(0x4f8)+add(0x98)交错布局让unsorted bin跨越两chunk/free(0)free(2)留下libc+heap指针在fd/bk/add(0x4f8)#c4+c5做show同时泄heap_N(main_arena_N)算libc_base/edit偏移0x50d修链表/add(0x4f8)fake chunk指向__free_hook-8/add(0x98)/bin/sh填充+system覆盖

## 关键 payload

```
free(8) 触发 system("/bin/sh")  其中 c8 chunk 内填 p64("/bin/sh\x00")
```

## 经验教训

0x4f8 落在 unsorted bin 范围，0x98 落在 tcache 范围；先用 0x4f8 大块 free 残留 main_arena 指针泄 libc，再用 0x98 链做 tcache 篡改；edit 用单字节 8 字节写改链表节点偏移实现 cross-bin 篡改。

## 标签

glibc-2.31、unsorted-bin、tcache、__free_hook、leak-libc、leak-heap

## 参考来源

- https://www.ctfiot.com/213214.html
- 原文件：web选手入门pwn(20)_——网鼎杯PWN01.full.md
