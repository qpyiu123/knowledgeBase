---
title: "2024 鹏程杯 writeup by Mini-Venom（cool_book 沙箱 ORW）"
category: pwn
tags: ["2024 鹏程杯", "pwn", "cool_book 50 块后越界", "v6 溢出覆盖返回地址", "seccomp 沙箱手写 ORW", "shellcraft.open+read+write pwntools"]
signals: ["2024 鹏程杯 2024", "cool_book 50 块后越界", "v6 溢出覆盖返回地址", "seccomp 沙箱手写 ORW", "shellcraft.open+read+write pwntools", "mov rdi", "0; mov rsi", "rbp; pop rax; pop rcx; pop rdx; syscall", "heap_base 0x910-0x9a0 写 shellcode", "rop", "srop", "shellcode", "cool_book", "ORW"]
difficulty: hard
source: "https://www.ctfiot.com/214840.html"
tools: ["ROP", "pwntools"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 鹏程杯 writeup by Mini-Venom（cool_book 沙箱 ORW）

> 赛事：2024 鹏程杯 2024 | 方向：pwn | 难度：hard | 工具：ROP、pwntools

## 一句话总结

cool_book 50 块后 v6 越界覆盖返回地址到堆地址 + 堆上写 ORW shellcode，seccomp 禁 execve → 走手写 open/read/write。

## 攻击链

1. 50 个堆块 add 后越界覆盖 v6
2. v6 是返回地址 → 覆盖为堆地址
3. 堆地址处写 shellcode（手写 ORW）
4. 开了 seccomp → 不能 execve，只能 ORW
5. add 50 次后 add(49, asm('mov rdi,0;mov rsi,rbp;pop rax;pop rcx;pop rdx;syscall'))
6. 触发 ROP → 跳到 shellcode

## 关键 payload

```
asm('mov rdi,0;mov rsi,rbp;pop rax;pop rcx;pop rdx;syscall')
```

## 经验教训

开了 seccomp 的 pwn 题，syscall 只留 read/write/open 等几条 → 必须在堆上写 ORW shellcode，pwntools `shellcraft.open/read/write` 是最简方案；add 50 次后 v6 越界是经典菜单题 off-by-N 套路。

## 标签

cool_book 50 块后越界、v6 溢出覆盖返回地址、seccomp 沙箱手写 ORW、shellcraft.open+read+write pwntools、mov rdi、0; mov rsi、rbp; pop rax; pop rcx; pop rdx; syscall、heap_base 0x910-0x9a0 写 shellcode

## 参考来源

- https://www.ctfiot.com/214840.html
- 原文件：2024鹏程杯_writeup_by_Mini-Venom.full.md
