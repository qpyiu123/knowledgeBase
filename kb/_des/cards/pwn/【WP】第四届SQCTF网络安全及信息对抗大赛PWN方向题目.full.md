---
title: "【WP】第四届 SQCTF 网络安全及信息对抗大赛 PWN 方向题目"
category: pwn
tags: ["SQCTF", "pwn", "ret2backdoor", "shellcode-injection", "SROP-SigreturnFrame", "fmt-leak-canary"]
signals: ["SQCTF 2025", "ret2backdoor", "shellcode-injection", "SROP-SigreturnFrame", "fmt-leak-canary", "stack-pivot-leave-ret", "syscall-rax-rdi-rsi-rdx", "asm-pwntools", "fmt_string", "SQCTF", "PWN", "shellcode", "SROP", "fmt"]
difficulty: medium
source: "https://www.ctfiot.com/243289.html"
tools: ["pwntools"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【WP】第四届 SQCTF 网络安全及信息对抗大赛 PWN 方向题目

> 赛事：SQCTF 2025 | 方向：pwn | 难度：medium | 工具：pwntools

## 一句话总结

第四届 SQCTF PWN 方向 9 题合集，覆盖 ret2backdoor + shellcode + SROP + fmt 泄 canary + stack pivot + syscall 全套入门。

## 攻击链

1. 1. cat ret2backdoor 0x40121B / 2. shellcode push /bin/sh + rax=0x3b syscall / 3. SROP frame rdi=/bin/sh rip=syscall 触发 sigreturn / 4. gift ret2backdoor / 5. pwn02 base64 编码 + ret2backdoor / 6. 自写 pop rdx/rsi/rdi/rax syscall 调用 / 7. fmt %11$p %15$p %17$p 泄 canary+proc+stack 后 leave-ret 跳板 / 8. key 直接传 FTCUNQS 字符串 / 9. shellcode.ljust(0x48) + 0x4040A0

## 关键 payload

```
9 个 PWN 题涵盖 ret2backdoor/shellcode/SROP/fmt-leak/stack-pivot/syscall/asm  全套 PWN 基础
```

## 经验教训

PWN 入门九大题型：ret2backdoor / shellcode / SROP / fmt-leak / stack-pivot / syscall-rax / key-string / base64-wrap；asm() + shellcraft.sh() 是 pwntools 内置 shellcode 工具。

## 标签

ret2backdoor、shellcode-injection、SROP-SigreturnFrame、fmt-leak-canary、stack-pivot-leave-ret、syscall-rax-rdi-rsi-rdx、asm-pwntools

## 参考来源

- https://www.ctfiot.com/243289.html
- 原文件：【WP】第四届SQCTF网络安全及信息对抗大赛PWN方向题目.full.md
