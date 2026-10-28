---
title: "祥云杯2022-leak Writeup"
category: pwn
tags: ["祥云杯2022", "pwn", "glibc 2.27-1.6", "UAF", "IO结构体伪造", "_IO_write_base泄露"]
signals: ["祥云杯2022 2022", "glibc 2.27-1.6", "UAF", "IO结构体伪造", "_IO_write_base泄露", "fastbin reverse into tcache", "tcache双链表", "堆地址泄露", "0xfbad1800", "heap_exploit", "leak", "glibc", "fastbin", "reverse"]
difficulty: hard
source: "https://www.ctfiot.com/80771.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 祥云杯2022-leak Writeup

> 赛事：祥云杯2022 2022 | 方向：pwn | 难度：hard

## 一句话总结

祥云杯2022 leak：glibc 2.27堆题+IO结构体泄露+fastbin reverse into tcache

## 攻击链

1. 入口读flag到堆→add/delete/edit有UAF无show→fastbin reverse into tcache写堆地址到IO结构体→修改stdout._flags=0xfbad1800 + _IO_write_base=堆地址→exit时泄露堆内容→堆地址已知→改stdout写指针到libc→获取system

## 关键 payload

```
stdout._flags=0xfbad1800;_IO_write_base=heap_addr;fastbin->bk=&tcache[size];tcache双链表fd/bk;glibc 2.27-1.6;flag在堆上
```

## 经验教训

无show的2.27堆题：IO结构体伪造 + fastbin reverse into tcache利用堆地址

## 标签

glibc 2.27-1.6、UAF、IO结构体伪造、_IO_write_base泄露、fastbin reverse into tcache、tcache双链表、堆地址泄露、0xfbad1800

## 参考来源

- https://www.ctfiot.com/80771.html
- 原文件：祥云杯2022-leak_Writeup.full.md
