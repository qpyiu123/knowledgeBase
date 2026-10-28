---
title: "miniL 2025 mmapheap 题解"
category: pwn
tags: ["miniL", "pwn", "custom-mmap-heap", "doubly-linked-list", "tcache-style", "glibc-2.35"]
signals: ["miniL 2025", "custom-mmap-heap", "doubly-linked-list", "tcache-style", "glibc-2.35", "large-chunk", "chunk-overlap", "heap_exploit", "miniL", "mmapheap", "mmap", "chunk", "heap", "node_header"]
difficulty: hard
source: "https://www.ctfiot.com/253195.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# miniL 2025 mmapheap 题解

> 赛事：miniL 2025 | 方向：pwn | 难度：hard

## 一句话总结

miniL 2025 mmapheap 题解，自定义 mmap 分配器 + 双向链表 chunk 攻击。

## 攻击链

1. 自定义 mmap heap 分配器
2. node_header: chunk_start/num/base/end/prev/next
3. Add paper/Edit/Delete/Show/Load
4. 65536 字节触发 mmap
5. 65184 字节切分 chunk
6. 改 chunk size (overflow 0x300-0x20-0xd0)
7. 跨 mmap 段覆盖

## 关键 payload

```
mmap 段切分 + 双向链表 + chunk overlap
```

## 经验教训

自定义分配器逆向关键是看 chunk_header 结构和链表操作。

## 标签

custom-mmap-heap、doubly-linked-list、tcache-style、glibc-2.35、large-chunk、chunk-overlap

## 参考来源

- https://www.ctfiot.com/253195.html
- 原文件：miniL2025_mmapheap_题解.full.md
