---
title: "一道 SROP 漏洞利用的 Pwn 题"
category: pwn
tags: ["个人赛", "pwn", "SROP-Sigreturn-Oriented-Programming", "SigreturnFrame", "syscall-rax-15", "pwntools-frame"]
signals: ["个人赛 2022", "SROP-Sigreturn-Oriented-Programming", "SigreturnFrame", "syscall-rax-15", "pwntools-frame", "mprotect-RWX", "ret2csu", "Oakland-2014", "rop", "SROP", "Pwn", "sigreturn", "execve", "bin"]
difficulty: medium
source: "https://www.ctfiot.com/90491.html"
tools: ["pwntools"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 一道 SROP 漏洞利用的 Pwn 题

> 赛事：个人赛 2022 | 方向：pwn | 难度：medium | 工具：pwntools

## 一句话总结

SROP 入门 Pwn 题，通过 sigreturn 系统调用号 15 触发 SigreturnFrame 恢复寄存器 + execve("/bin/sh") 收 shell。

## 攻击链

1. 1. read+write 泄露 /bin/sh 地址 (recv 8 字节 - 280 偏移) /2. 构造 SigreturnFrame: rax=59 SYS_execve rdi=binsh_addr rsi=0 rdx=0 rip=0x400501 syscall /3. 触发 sigreturn: rax=15 (mov rax,15) + syscall pop 所有寄存器 /4. 双 SROP 链: 第一次 rax=0 read(0, 0x402500, 0x300) + 第二次 rax=59 execve("/bin/sh", 0, 0)

## 关键 payload

```
rax=15 sigreturn syscall  syscall 0x400501  binsh_addr u64 - 280
```

## 经验教训

SROP 2014 年 Vrije Universiteit Amsterdam Erik Bosman 提出；rax=15 sigreturn 触发内核恢复所有用户态寄存器；SigreturnFrame() pwntools 一行构造。

## 标签

SROP-Sigreturn-Oriented-Programming、SigreturnFrame、syscall-rax-15、pwntools-frame、mprotect-RWX、ret2csu、Oakland-2014

## 参考来源

- https://www.ctfiot.com/90491.html
- 原文件：一道SROP漏洞利用的Pwn题.full.md
