---
title: "House of water + TFCCTF 2024 MCGUAVA"
category: pwn
tags: ["TFCCTF", "pwn", "House of Water", "tcache_perthread_struct", "UAF", "FSOP"]
signals: ["TFCCTF 2024", "House of Water", "tcache_perthread_struct", "UAF", "FSOP", "glibc 2.35", "heap_exploit", "unsorted", "bin", "fake", "chunk", "libc", "tcache", "entries"]
difficulty: hard
source: "https://www.ctfiot.com/205266.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# House of water + TFCCTF 2024 MCGUAVA

> 赛事：TFCCTF 2024 | 方向：pwn | 难度：hard

## 一句话总结

把 tcache_perthread_struct 变成 unsorted bin 的玩法，让 fake chunk 的 fd/bk 把 libc 指针反向注入到 tcache entries 数组。

## 攻击链

1. |

## 关键 payload

```
|
```

## 经验教训

任意大小 malloc + UAF 是 House of Water 的入场券；爆破 heapbase 第 4 位 1/16 成功率已经算很良心的现代 glibc 攻击。

## 标签

House of Water、tcache_perthread_struct、UAF、FSOP、glibc 2.35

## 参考来源

- https://www.ctfiot.com/205266.html
- 原文件：House_of_water_&_TFCCTF_2024_MCGUAVA.full.md
