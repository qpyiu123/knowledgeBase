---
title: "PWN 赛题解析"
category: pwn
tags: ["看雪论坛 ctfiot 系列", "pwn", "pwn", "ret2libc", "shellcode", "seccomp"]
signals: ["看雪论坛 ctfiot 系列 2024", "pwn", "ret2libc", "shellcode", "seccomp", "sandbox-bypass", "fmt-string", "栈迁移", "orw", "rop", "PWN", "openat", "mmap", "writev"]
difficulty: medium
source: "https://www.ctfiot.com/196469.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# PWN 赛题解析

> 赛事：看雪论坛 ctfiot 系列 2024 | 方向：pwn | 难度：medium

## 一句话总结

4 道 PWN 题合集，涵盖 ret2libc 泄地址循环填充、seccomp 下 openat+mmap+writev orw、fmt-string 泄三件套栈迁移、自定义 VM 解释器 PC 劫持。

## 攻击链

1. 一 stdout 题：read 0x60 越界写覆盖 rbp/rip
2. 跳 vuln 函数循环 20 次填满 stdout 缓冲区
3. 泄 read@got 计算 libc 偏移
4. 构造 pop_rdi+rsi+rdx 调 execve
5. 二 Shuffled_Execution 题：seccomp 沙箱禁 execve 系
6. 写入 orw shellcode (openat+mmap+writev)
7. 三 SavethePrincess：rand 派生密钥 + 偏序密码爆破
8. 泄 canary/libc/stack 三件套
9. 栈迁移到 mprotect rwx 区域执行 shellcode
10. 四 spiiill：自定义 VM 字节码解释器
11. 越界 PC 控制跳 system 执行 sh

## 关键 payload

```
payload1='a'*0x58+p64(vuln); payload4=p64(0xa)+p64(0xc)+p64(0xfffffffffffffc02)+'sh\x00
```

## 经验教训

ASLR 开启时只能绕过 libc/stack/canary；seccomp 沙箱禁 execve 时必须用 openat+mmap+writev 替代；自定义 VM 程序 PC 越界即可劫持控制流。

## 标签

pwn、ret2libc、shellcode、seccomp、sandbox-bypass、fmt-string、栈迁移、orw

## 参考来源

- https://www.ctfiot.com/196469.html
- 原文件：PWN_赛题解析.full.md
