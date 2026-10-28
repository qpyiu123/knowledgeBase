---
title: "D3CTF 2023 REVERSE"
category: reverse
tags: ["D3CTF", "reverse", "nand-vm", "rc4", "pyd", "bindiff"]
signals: ["D3CTF 2023", "nand-vm", "rc4", "pyd", "bindiff", "syscall-hooking", "kernel-module", "fork-pipe", "z3", "reverse", "D3CTF", "NAND-VM", "Bindiff", "syscall"]
difficulty: hard
source: "https://www.ctfiot.com/133171.html"
tools: ["Ghidra", "IDA", "Z3"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# D3CTF 2023 REVERSE

> 赛事：D3CTF 2023 | 方向：reverse | 难度：hard | 工具：Ghidra、IDA、Z3

## 一句话总结

D3CTF 2023 四道逆向 WP 合集，NAND-VM / fork-pipe 套娃 / pyd Bindiff / syscall 劫持 VM。

## 攻击链

1. D3SKY: RC4 解密 opcode 还原 NAND VM
2. 条件断点提取 opcode 操作
3. 识别 XOR 比较模式
4. Z3 约束求解
5. D3RC4: 反编译 fork+pipe 子进程
6. 模拟递归 get_key
7. 还原 RC4 key
8. Z3 解密
9. D3RECOVER: Bindiff 合并 pyd 符号
10. XOR+add 还原
11. D3SYSCALL: 内核模块劫持 syscall_table
12. 翻译 rax 调度

## 关键 payload

```
RC4 加密 opcode + NAND VM + fork/pipe 子进程 + syscall hook
```

## 经验教训

当 IDA/Ghidra 看到 "mov byte 一坨"、自定义 syscall、fork/pipe 套娃时，要立刻反应过来这是 VM 套娃。

## 标签

nand-vm、rc4、pyd、bindiff、syscall-hooking、kernel-module、fork-pipe、z3

## 参考来源

- https://www.ctfiot.com/133171.html
- 原文件：D3CTF2023_REVERSE.full.md
