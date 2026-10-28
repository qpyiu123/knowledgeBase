---
title: "vctf apples leak libc 操作复现（高版本 libc overlapping）"
category: pwn
tags: ["VCTF", "pwn", "glibc-2.35", "off-by-one", "unsortedbin-overlap", "chunk-merge"]
signals: ["VCTF 2023", "glibc-2.35", "off-by-one", "unsortedbin-overlap", "chunk-merge", "off-by-null", "low-byte-00", "fake-chunk", "heap_exploit", "VCTF", "apples", "leak", "libc", "glibc"]
difficulty: hard
source: "https://www.ctfiot.com/174987.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# vctf apples leak libc 操作复现（高版本 libc overlapping）

> 赛事：VCTF 2023 | 方向：pwn | 难度：hard

## 一句话总结

VCTF apples leak libc 操作复现，高版本 glibc 堆合并 + overlapping。

## 攻击链

1. add 8 个 chunk 排布
2. free(0/3/6) 触发 0x860 合并
3. 分割 0x860 + 控制 fd/bk
4. add 0x450 设 chunk3 为 allocated
5. 改 chunk0 fd
6. free 序列触发 overlapping
7. 假 chunk 头 + 低地址 0x00 (便于 off-by-null)
8. free 触发 unlink 检查
9. 泄 libc + 改 __free_hook

## 关键 payload

```
unsortedbin 合并 + overlapping + off-by-null
```

## 经验教训

高版本 glibc 2.35 堆合并时 off-by-one 可以构造精确的 overlapping + 假 chunk。

## 标签

glibc-2.35、off-by-one、unsortedbin-overlap、chunk-merge、off-by-null、low-byte-00、fake-chunk

## 参考来源

- https://www.ctfiot.com/174987.html
- 原文件：vctf_apples_leak_libc操作复现(高版本libc_overlapping).full.md
