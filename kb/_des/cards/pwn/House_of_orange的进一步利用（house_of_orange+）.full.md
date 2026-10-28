---
title: "House of orange的进一步利用（house of orange+）"
category: pwn
tags: ["公众号文章（看雪论坛）", "pwn", "pwn", "house-of-orange", "no-free", "topchunk"]
signals: ["公众号文章（看雪论坛） 2024", "pwn", "house-of-orange", "no-free", "topchunk", "sysmalloc", "malloc_hook", "wkctf-2024", "heap_exploit", "House", "orange", "free", "top", "chunk"]
difficulty: hard
source: "https://www.ctfiot.com/194805.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# House of orange的进一步利用（house of orange+）

> 赛事：公众号文章（看雪论坛） 2024 | 方向：pwn | 难度：hard

## 一句话总结

House of orange+：无free时通过堆溢出+top chunk sysmalloc伪造释放

## 攻击链

1. 条件: 无free但有堆溢出
2. House of Orange: 覆盖topchunk size触发sysmalloc
3. sysmalloc 释放old top → 进入unsorted bin
4. use_top 切割 victim (top chunk)
5. 例题: WKCTF2024 easy_heap
6. add(0xbf0) + add(0x78) + edit堆溢出0x381
7. add(0x3f0) + add(0x208) show leak libc (0x3c4e0a)
8. add(0x7f0) + add(0x360) edit 0x91
9. 改 __malloc_hook-0x23 → 0x68 chunk
10. 写入ogg (one_gadget) 0xf1247
11. add(0x68)*0x13 + p64(ogg) 覆盖__malloc_hook
12. cmd(1)触发 getshell

## 关键 payload

```
__malloc_hook-0x23 + p64(ogg)  # one_gadget
```

## 经验教训

堆溢出不free时可改top chunk size触发sysmalloc+_int_free

## 标签

pwn、house-of-orange、no-free、topchunk、sysmalloc、malloc_hook、wkctf-2024

## 参考来源

- https://www.ctfiot.com/194805.html
- 原文件：House_of_orange的进一步利用（house_of_orange+）.full.md
