---
title: "网鼎杯玄武组——PWN2"
category: pwn
tags: ["网鼎杯玄武组", "pwn", "canary-leak", "multithread-pwn", "fork-process", "sys_exit_group"]
signals: ["网鼎杯玄武组 2024", "canary-leak", "multithread-pwn", "fork-process", "sys_exit_group", "sys_exit", "halt-instruction", "rop-chain", "syscall-execve", "pwn_unknown", "PWN2", "fork", "gift", "canary"]
difficulty: hard
source: "https://www.ctfiot.com/217930.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 网鼎杯玄武组——PWN2

> 赛事：网鼎杯玄武组 2024 | 方向：pwn | 难度：hard | 工具：ROP

## 一句话总结

网鼎杯玄武组PWN2多线程题,主进程fork子进程+''gift: %p''泄canary+两次input(0x40/0x100)+两段syscall(读bss+execve /bin/sh)。

## 攻击链

1. main调用tip2()+main_main():fork子进程
2. 父进程:sub_44ED00 wait+onput_2('Wanna return?')+input(0,v2,1uLL)+exit_ma(0)
3. 子进程:onput_2('leave your name')+input(0,v4,0x40LL)+exit_ma(0)
4. leak:''gift: %p''打印canary/fs:0x28栈地址
5. 多线程:tip()循环fork,input(0,v1,0x100uLL)+sub_401A55(v1)
6. syscall gadget:rax=0x450277,rdi=0x40213f,rsi=0x40a1ae,rdx_rbx=0x485feb,syscall=0x41ac26
7. 第一次syscall:read(0,bss,0x100) 写入"/bin/sh
8. 第二次syscall:execve("/bin/sh",0,0)
9. 利用:gdb多线程切换info threads/thread ID
10. 子进程崩溃:子进程exit_group退出不影响主进程

## 关键 payload

```
canary + ROP(read→bss,execve→/bin/sh)
```

## 经验教训

fork子进程模式下canary独立,父进程泄漏canary+子进程ROP链崩溃不影响主进程;gdb多线程切换( info threads/thread ID)是必备技能;两段syscall(读+execve)稳定避开seccomp对open的限制。

## 标签

canary-leak、multithread-pwn、fork-process、sys_exit_group、sys_exit、halt-instruction、rop-chain、syscall-execve、syscall-read、syscall-write、multithread-debug

## 参考来源

- https://www.ctfiot.com/217930.html
- 原文件：网鼎杯玄武组——PWN2.full.md
