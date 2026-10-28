---
title: "Pwn - oneday 题目解析 - House of Apple × House of Emma 联动"
category: pwn
tags: ["看雪论坛 ctfiot 系列", "pwn", "pwn", "house-of-apple", "house-of-emma", "largebin-attack"]
signals: ["看雪论坛 ctfiot 系列 2024", "pwn", "house-of-apple", "house-of-emma", "largebin-attack", "pointer-guard", "pcop", "fake-io-file", "_IO_wstrn_jumps", "heap_exploit", "House", "Apple", "Emma", "pointer_guard"]
difficulty: hard
source: "https://www.ctfiot.com/164936.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Pwn - oneday 题目解析 - House of Apple × House of Emma 联动

> 赛事：看雪论坛 ctfiot 系列 2024 | 方向：pwn | 难度：hard | 工具：ROP

## 一句话总结

House of Apple + House of Emma 高级堆攻击联动：House of Apple 写 pointer_guard 解密 pcop，House of Emma 用 pcop 跳 ROP+mprotect+orw 读 flag。

## 攻击链

1. 菜单 add/delete/edit/show 4 项 + key=10
2. 多个 0x20-0x80 堆块 add/delete 触发 tcache 复用 + unsorted bin
3. show(3) 泄 libc_base (0x1f2cc0) + heap_base (0x17f0)
4. largebin attack：bk_nextsize 指向 _IO_list_all-0x20
5. House of Apple 攻击 pointer_guard：_IO_wstrn_overflow 通过 _wide_data 指针
6. 伪造 chunk3 size=0xab1 触发 _IO_flush_all_lockp 时进入 fake file 链
7. 第一个 fake file: _IO_read_ptr=0xa81 凑 size + chain=heap+0x1910 链向第二个 fake file
8. vtable=_IO_wstrn_jumps 触发 _IO_wstrn_overflow 改 pointer_guard
9. 第二个 fake file: vtable=_IO_cookie_jumps+0x58 触发 _IO_cookie_read
10. 覆盖 read 指针为 magic_gadget (pcop: mov rdx,[rdi+8]; mov [rsp],rax; call [rdx+0x20])
11. magic_gadget 用 rax=rol(magic_gadget^expected, 0x11) 解密 pcop
12. 跳 mov_rsp_rdx_ret → rsp 指向 ROP 链 → mprotect rwx 0x4000
13. ROP 后跳 chain+0x200 跑 shellcraft.open('./flag', 0) + read(3, heap, 0x100) + write(1, heap, 0x100)

## 关键 payload

```
f1.vtable=_IO_wstrn_jumps + f2.vtable=_IO_cookie_jumps+0x58 + magic_gadget=0x146020 (mov rdx,[rdi+8]; mov [rsp],rax; call [rdx+0x20])
```

## 经验教训

单一 largebin attack 只能一次任意地址写，但 House of Emma 需两次，可先用 House of Apple 改 pointer_guard 解锁加密指针，再用 House of Emma 跳 ROP；_IO_wstrn_jumps+_wide_data 是改 pointer_guard 经典入口。

## 标签

pwn、house-of-apple、house-of-emma、largebin-attack、pointer-guard、pcop、fake-io-file、_IO_wstrn_jumps、_IO_cookie_jumps、mprotect-orw

## 参考来源

- https://www.ctfiot.com/164936.html
- 原文件：Pwn-oneday题目解析.full.md
