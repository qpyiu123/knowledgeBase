---
title: "2024 第四届\"网鼎杯\"玄武组 pwn02 writeup（fork + ret2syscall 栈迁移）"
category: pwn
tags: ["2024 第四届网鼎杯", "pwn", "玄武 pwn02", "x11x11x11... 绕过检测", "fork 后栈溢出", "pwndbg 不能跟 fork"]
signals: ["2024 第四届网鼎杯 2024", "玄武 pwn02", "x11x11x11... 绕过检测", "fork 后栈溢出", "pwndbg 不能跟 fork", "通用 gadget 链 rax/rdi/rsi/rdx/rbp/leave_ret", "AE64 shellcode 编码", "libc-2.35 SROP 栈迁移", "read 写 bss 0x4C72A0+0x100", "srop", "ret2libc", "rop", "shellcode", "pwn02"]
difficulty: hard
source: "https://www.ctfiot.com/214152.html"
tools: ["GDB", "ROP", "pwntools"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 第四届"网鼎杯"玄武组 pwn02 writeup（fork + ret2syscall 栈迁移）

> 赛事：2024 第四届网鼎杯 2024 | 方向：pwn | 难度：hard | 工具：GDB、ROP、pwntools

## 一句话总结

玄武 pwn02：fork 后栈溢出 + 通用 gadget 链 SROP + read 写 bss + AE64 shellcode 编码 — 大程序最常用 ROP 套路。

## 攻击链

1. x11x11x11... 绕过前段检测
2. 进 fork 子进程，栈溢出
3. pwndbg 不能跟 fork → 直接打 ret2syscall
4. 通用 gadget: rax=0x450277, rdi=0x40213f, rsi=0x40a1ae, rdx=0x485feb, rbp=0x401771, syscall=0x41ac26, leave_ret=0x40192F
5. 第一次 read 写 bss 0x4C72A0+0x100 拿到 execve 链子
6. 第二次 execve("/bin/sh", 0, 0)

## 关键 payload

```
rax=0x450277; rdi=0x40213f; rsi=0x40a1ae; rdx=0x485feb; rbp=0x401771; syscall=0x41ac26; leave_ret=0x40192F
```

## 经验教训

pwndbg 不能跟 fork 是 GDB 调试盲点，要么用 `set follow-fork-mode parent/child` 切换，要么干脆单步 payload 直出；AE64 库用来编码 shellcode 绕过字符过滤（pwntools `asm(shellcraft.sh())` 经常含坏字符）。

## 标签

玄武 pwn02、x11x11x11... 绕过检测、fork 后栈溢出、pwndbg 不能跟 fork、通用 gadget 链 rax/rdi/rsi/rdx/rbp/leave_ret、AE64 shellcode 编码、libc-2.35 SROP 栈迁移、read 写 bss 0x4C72A0+0x100、execve /bin/sh

## 参考来源

- https://www.ctfiot.com/214152.html
- 原文件：2024第四届“网鼎杯”玄武组_writeup.full.md
