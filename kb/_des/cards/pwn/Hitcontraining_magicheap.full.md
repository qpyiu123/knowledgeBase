---
title: "Hitcontraining magicheap 完整三解"
category: pwn
tags: ["HITCON Training", "pwn", "fastbin", "tcache", "unlink", "unsorted bin"]
signals: ["HITCON Training 2018", "fastbin", "tcache", "unlink", "unsorted bin", "libc-2.23", "heap_exploit", "HITCON", "single-null"]
difficulty: medium
source: "https://www.ctfiot.com/293125.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Hitcontraining magicheap 完整三解

> 赛事：HITCON Training 2018 | 方向：pwn | 难度：medium

## 一句话总结

HITCON 训练场经典 single-null 指针堆菜单，三种姿势教 unlink 怎么用。

## 攻击链

1. |

## 关键 payload

```
|
```

## 经验教训

heaparray/magic 都是全局变量，fastbin attack 0x21 fake chunk 头、unlink 双向链表 fd/bk 自引用检查、unsorted bin unlink 三套模板都要会背。

## 标签

fastbin、tcache、unlink、unsorted bin、libc-2.23

## 参考来源

- https://www.ctfiot.com/293125.html
- 原文件：Hitcontraining_magicheap.full.md
