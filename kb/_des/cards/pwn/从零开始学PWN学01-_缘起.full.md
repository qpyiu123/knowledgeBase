---
title: "从零开始学 PWN 01 - 缘起（栈对齐）"
category: pwn
tags: ["自学系列 (来源 ctfiot)", "pwn", "x86_64", "stack-alignment", "movaps", "gets"]
signals: ["自学系列 (来源 ctfiot) 2025", "x86_64", "stack-alignment", "movaps", "gets", "BUUOJ", "cyclic", "pwntools", "prologue", "ret2libc", "pwn_unknown", "pwn", "gdb", "offset"]
difficulty: easy
source: "https://www.ctfiot.com/250955.html"
tools: ["pwntools"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 从零开始学 PWN 01 - 缘起（栈对齐）

> 赛事：自学系列 (来源 ctfiot) 2025 | 方向：pwn | 难度：easy | 工具：pwntools

## 一句话总结

经典 pwn 入坑文 — x86_64 16 字节栈对齐 movaps 崩溃

## 攻击链

1. cyclic 100 生成模式串
2. gdb 在 gets 断点看栈帧布局确认 offset=23
3. payload = A*23 + p64(func_addr)
4. system("/bin/sh") 调用触发 movaps 段错误
5. 跳过 push rbp 把 ret 改到 func+1 修复 16 字节对齐

## 关键 payload

```
p64(0x00401186+1) 即跳到 push rbp 之后
```

## 经验教训

x86_64 SystemV ABI 要求调用时 rsp % 16 == 0；劫持 ret 跳到 push rbp 之后可省一次 push 让栈对齐

## 标签

x86_64、stack-alignment、movaps、gets、BUUOJ、cyclic、pwntools、prologue、ret-sled

## 参考来源

- https://www.ctfiot.com/250955.html
- 原文件：从零开始学PWN学01-_缘起.full.md
