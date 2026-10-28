---
title: "津京冀网络攻防大赛线下决赛pwn–全场唯一解"
category: pwn
tags: ["津京冀网络攻防大赛决赛", "pwn", "堆溢出", "有符号比较绕过", "fopen NULL", "unsorted bin leak"]
signals: ["津京冀网络攻防大赛决赛 2025", "堆溢出", "有符号比较绕过", "fopen NULL", "unsorted bin leak", "fastbin attack", "libc2.23", "heap_exploit", "pwn1", "pwn2", "fopen", "NULL", "FILE", "fastbin"]
difficulty: medium
source: "https://www.ctfiot.com/282040.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 津京冀网络攻防大赛线下决赛pwn–全场唯一解

> 赛事：津京冀网络攻防大赛决赛 2025 | 方向：pwn | 难度：medium

## 一句话总结

津京冀决赛pwn1+pwn2全场唯一解：fopen(NULL) FILE结构泄漏+有符号比较堆溢出+fastbin attack stdout

## 攻击链

1. pwn1:fopen(NULL)获取FILE结构libc地址→add两次0x40堆→edit用极大值(0x7fffffff00000000+0x80)触发堆溢出覆盖chunk1 size位→show(1)泄main_arena+88→改chunk1函数指针为system+写/bin/sh→pwn2:UAF+fastbin attack→fake chunk在stdout(bss段)→show泄libc→改__malloc_hook为one_gadget

## 关键 payload

```
edit new_length=0x7fffffff00000000+0x80;libc=main_arena+88-0x3EC680;libc+0x4F440=system;pwn2:fake chunk at 0x60201d;__malloc_hook=one_gadget[0x4527a,0xf03a4,0xf1247]
```

## 经验教训

堆题中edit长度校验有符号比较用极大数绕过；fopen(NULL)FILE结构含libc指针可泄漏

## 标签

堆溢出、有符号比较绕过、fopen NULL、unsorted bin leak、fastbin attack、libc2.23

## 参考来源

- https://www.ctfiot.com/282040.html
- 原文件：津京冀网络攻防大赛线下决赛pwn–全场唯一解.full.md
