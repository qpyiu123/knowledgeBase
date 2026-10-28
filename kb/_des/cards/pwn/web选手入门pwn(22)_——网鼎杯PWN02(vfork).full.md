---
title: "web选手入门pwn(22) 网鼎杯PWN02 vfork"
category: pwn
tags: ["网鼎杯", "pwn", "vfork", "canary-leak", "syscall", "SROP-chain"]
signals: ["网鼎杯 2024", "vfork", "canary-leak", "syscall", "SROP-chain", "ROP-pop-rax", "rop", "PWN02", "sendlineafter", "canary", "read", "execve", "ROP", "leave"]
difficulty: medium
source: "https://www.ctfiot.com/214123.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# web选手入门pwn(22) 网鼎杯PWN02 vfork

> 赛事：网鼎杯 2024 | 方向：pwn | 难度：medium | 工具：ROP

## 一句话总结

网鼎杯 PWN02，vfork 子进程断点跟随 + 多次 sendlineafter 泄 canary + 自写 read/execve syscall ROP 链。

## 攻击链

1. leave your name填p64(1)*8让后续puts打印栈上数据→泄canary/Wanna return填B跳过return/once again填C*256把栈扩到 canary 区域/fourth sendline after once again再次256字节爆破触发可写/final ROP: read(0,bss,0x100)→execve(/bin/sh,0,0)

## 关键 payload

```
pop_rax=0x450277  pop_rdi=0x40213f  pop_rsi=0x40a1ae  pop_rdx_rbx=0x485feb  syscall=0x41ac26  bss=0x4CB800
```

## 经验教训

vfork 子进程独立地址空间但共用父进程页表；gdb follow-fork-mode child + detach-on-fork off 同时跟踪父子；pop rax+syscall 不需要 magic gadget，可直接构造 read(0,bss,N)→execve(/bin/sh,0,0) 两段 ROP。

## 标签

vfork、canary-leak、syscall、SROP-chain、ROP-pop-rax

## 参考来源

- https://www.ctfiot.com/214123.html
- 原文件：web选手入门pwn(22)_——网鼎杯PWN02(vfork).full.md
