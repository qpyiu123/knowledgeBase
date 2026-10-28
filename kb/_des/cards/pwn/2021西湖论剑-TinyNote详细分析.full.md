---
title: "2021 西湖论剑 - TinyNote 详细分析"
category: pwn
tags: ["2021 西湖论剑", "pwn", "libc-2.33", "tcache", "UAF", "PROTECT_PTR"]
signals: ["2021 西湖论剑 2021", "libc-2.33", "tcache", "UAF", "PROTECT_PTR", "heap-base-leak", "ORW", "setcontext", "IO_FILE", "heap_exploit", "pwn_unknown", "libc-2", "IO_wfile_jumps", "add"]
difficulty: hard
source: "https://www.ctfiot.com/153753.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2021 西湖论剑 - TinyNote 详细分析

> 赛事：2021 西湖论剑 2021 | 方向：pwn | 难度：hard

## 一句话总结

libc-2.33 IO_FILE 利用 _IO_wfile_jumps + setcontext+61 + ORW

## 攻击链

1. add(0) add(1) delete(0) show(0) leak heap_base（残留 5 字节）
2. xor = heap_base >> 12 利用 PROTECT_PTR 绕过 tcache key 校验
3. edit(1, p64(xor^heap)) 写 fake tcache fd 链
4. add(1) add(0) edit(0, p64(0)+p64(0x421)) 制造 unsorted bin 大小
5. 33 次 add(0) 填满 tcache
6. delete(1) show(1) leak libcbase
7. tcache poisoning 把 free_hook 改成 setcontext+61
8. change 改 heap 0x30/0x40/0x50/0xc0/0xe0/0x1a0 构造 IO_FILE + vtable
9. start 改 p64(pcop)+p64(heap+0x700) 触发 _IO_wfile_overflow → call [rdx+0x20]
10. setcontext+61 控 rsp/rip → ORW (open/read/write flag)

## 关键 payload

```
mov rdx, [rdi+8]; mov [rsp], rax; call [rdx+0x20]  → setcontext+61 触发 gadget
```

## 经验教训

libc-2.33+ 没了 __free_hook 还能用，要走 IO_FILE 走 exit 时 _IO_wfile_overflow

## 标签

libc-2.33、tcache、UAF、PROTECT_PTR、heap-base-leak、ORW、setcontext、IO_FILE、exit_hook、free_hook

## 参考来源

- https://www.ctfiot.com/153753.html
- 原文件：2021西湖论剑-TinyNote详细分析.full.md
