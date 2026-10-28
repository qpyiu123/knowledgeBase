---
title: "TAMUCTF 2025 WriteUp"
category: pwn
tags: ["TAMUCTF", "pwn", "ret2libc", "fmt-string-write", "go-binary", "seccomp-orw"]
signals: ["TAMUCTF 2025", "ret2libc", "fmt-string-write", "go-binary", "seccomp-orw", "7byte-shellcode", "math-z3", "rop", "TAMUCTF", "writeup", "Pwn", "Reverse", "Python", "SSRF"]
difficulty: medium
source: "https://www.ctfiot.com/234604.html"
tools: ["C", "Go", "Python", "ROP", "Z3"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# TAMUCTF 2025 WriteUp

> 赛事：TAMUCTF 2025 | 方向：pwn | 难度：medium | 工具：C、Go、Python、ROP、Z3

## 一句话总结

TAMUCTF 2025 狼组 writeup：7 题 Pwn + 4 题 Reverse，混合 Go/C++/Python + Go SSRF + 矩阵 Z3。

## 攻击链

1. Debug 1: 溢出 0x50 + p64(0x404100) + p64(0x4013A0) ret2libc
2. Sniper: fmt-string 改栈内容为 0x0a0a0000 + %s 读 flag
3. ROP Thirteen: Go 1.20.6 静态 elf + ret2syscall (read(0, bss, 0x100) + execve)
4. Seven: 7 字节 shellcode (push rsp; pop rsi; xor edi, edi; syscall; ret) + ret2csu + orw
5. Debug 2: 字符大小写反转函数绕过，PIE 1/16 爆破
6. Impossible: 童年游戏 (Pygame? - 文章未给细节)
7. Aggie Bookstore: 数组 nosql 注入
8. Deflated: ZipCrypto Deflate 已知明文攻击 (.git/HEAD)
9. Xorox: var_4020 ^ var_2060
10. Brainrot: Brain 类 + rot + think (矩阵乘法 + 移位) + z3 求解 4 块 10 字节
11. OTP: 核心转储 gdb 分析 key 还原

## 关键 payload

```
io.send(b"x54x5Ex31xFFx0Fx05xC3")  # 7-byte shellcode
```

## 经验教训

当 PIE 1/16 爆破可行时，覆盖 ret_addr 低 2 字节配合 read 重写栈是稳定技巧。

## 标签

ret2libc、fmt-string-write、go-binary、seccomp-orw、7byte-shellcode、math-z3

## 参考来源

- https://www.ctfiot.com/234604.html
- 原文件：TAMUCTF_·_2025_WriteUp.full.md
