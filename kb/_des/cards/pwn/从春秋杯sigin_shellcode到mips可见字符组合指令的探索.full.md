---
title: "从春秋杯 sigin_shellcode 到 mips 可见字符组合指令的探索"
category: pwn
tags: ["春秋杯", "pwn", "MIPS-shellcode", "printable-ASCII", "R-type-I-type-J-type", "opcode-fuzz"]
signals: ["春秋杯 2023", "MIPS-shellcode", "printable-ASCII", "R-type-I-type-J-type", "opcode-fuzz", "syscall-restriction", "heterogeneous-PWN", "sigin", "pwn_unknown", "sigin_shellcode", "MIPS", "opcode", "jalx", "syscall"]
difficulty: hard
source: "https://www.ctfiot.com/119807.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 从春秋杯 sigin_shellcode 到 mips 可见字符组合指令的探索

> 赛事：春秋杯 2023 | 方向：pwn | 难度：hard

## 一句话总结

春秋杯 sigin_shellcode：探索 MIPS 可见字符组合指令，R 型 opcode=0 不可用 + J 型只有 jalx + 没有 syscall。

## 攻击链

1. MIPS 32 寄存器 ($0-$31) + HI/LO 特殊寄存器
2. 指令 32 位: R 型 (opcode=0) + I 型 (opcode+rs+rt+imm16) + J 型 (opcode+imm26)
3. 可见字符范围 [0x21, 0x7e]
4. R 型 opcode 必须是 0 → 不可见字符 → 不可用
5. J 型 fuzz 只剩 jalx (但需 microMIPS/MIPS16e 支持)
6. I 型可用: beqzl/beqz/bnezl/bnel/blezl/bgtzl/andi/slti
7. 没有 syscall 指令可用
8. 通用 MIPS 可见字符 shellcode 几乎不可能
9. sigin_shellcode 是异构 pwn 题, 让选手探索可见字符 MIPS shellcode

## 关键 payload

```
mips 可见字符 shellcode 不存在 (无 syscall) + R/I/J 型指令 fuzz
```

## 经验教训

通用 MIPS 可见字符 shellcode 几乎不可能（无 syscall 指令），异构 pwn 题设计思路。

## 标签

MIPS-shellcode、printable-ASCII、R-type-I-type-J-type、opcode-fuzz、syscall-restriction、heterogeneous-PWN、sigin

## 参考来源

- https://www.ctfiot.com/119807.html
- 原文件：从春秋杯sigin_shellcode到mips可见字符组合指令的探索.full.md
