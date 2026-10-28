---
title: "DEFCON Quals 2023 Writeup と CTF のリハビリ"
category: pwn
tags: ["DEFCON", "pwn", "glibc-2.37", "glibc-2.35", "tcache-double-free", "cyclic-0x208"]
signals: ["DEFCON 2023", "glibc-2.37", "glibc-2.35", "tcache-double-free", "cyclic-0x208", "house-of", "pwn_unknown", "DEFCON", "Quals", "open-house", "PWN", "cyclic", "x208", "create"]
difficulty: medium
source: "https://www.ctfiot.com/117899.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DEFCON Quals 2023 Writeup と CTF のリハビリ

> 赛事：DEFCON 2023 | 方向：pwn | 难度：medium

## 一句话总结

DEFCON 2023 Quals open-house PWN 题复盘，日文 WP。

## 攻击链

1. cyclic(0x208) 输入 create
2. 11 次 delete(1) 触发 unsorted bin
3. create("") 切割 unsorted bin
4. 多次 create 触发 tcache
5. libc 2.37 mmap_threshold 调整
6. tcache double free 攻击

## 关键 payload

```
cyclic 0x208 + 11 次 delete 触发 unsorted bin
```

## 经验教训

11 次 delete(1) 同一个 index 触发 tcache 重复 + unsorted bin 残留。

## 标签

glibc-2.37、glibc-2.35、tcache-double-free、cyclic-0x208、house-of

## 参考来源

- https://www.ctfiot.com/117899.html
- 原文件：DEFCON_Quals_2023_WriteupとCTFのリハビリ.full.md
