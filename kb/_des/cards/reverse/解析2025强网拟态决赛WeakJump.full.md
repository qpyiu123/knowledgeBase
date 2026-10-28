---
title: "解析2025强网拟态决赛WeakJump"
category: reverse
tags: ["强网拟态 2025 决赛 WeakJump", "reverse", "statically-linked", "stripped", "ptrace-anti-debug", "control-flow-flatten"]
signals: ["强网拟态 2025 决赛 WeakJump 2025", "statically-linked", "stripped", "ptrace-anti-debug", "control-flow-flatten", "TEA", "feistel-cipher", "dispatcher-block", "dynamic-analysis", "reverse", "WeakJump", "ptrace", "GDB", "catch"]
difficulty: hard
source: "https://www.ctfiot.com/285718.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 解析2025强网拟态决赛WeakJump

> 赛事：强网拟态 2025 决赛 WeakJump 2025 | 方向：reverse | 难度：hard

## 一句话总结

强网拟态2025决赛WeakJump逆向,静态链接+stripped+ptrace反调试(用GDB catch syscall ptrace改$rax=0绕过)+控制流平坦化(将函数视为黑盒+动态分析)+TEA Feistel(8字节块+4组+8轮+delta=0x9E3779B9)。

## 攻击链

1. ELF 64位LSB+statically linked+stripped+BuildID
2. 工具链:radare2/binutils/gdb/strace
3. ptrace(PTRACE_TRACEME, 0, 0, 0)反调试
4. 绕反调试:GDB的`catch syscall ptrace` + `commands ... end` + `set $rax = 0` + continue
5. 关键字符串:Provide the flag for WeakJump / WeakJump clear / Nope, WeakJump resists you
6. 算法:TEA (Tiny Encryption Algorithm) Feistel结构
7. 数据块:8字节64位,左右各4字节32位,8轮,4组(共32字节)
8. delta=0x9E3779B9(黄金分割),sum初值=delta*32=0xC6EF3720
9. delta补码0x61C88647
10. 控制流平坦化:switch-case+dispatcher+大量跳转+看似无意义计算
11. 策略:不要深入分析混淆细节,将函数视为黑盒+动态分析
12. axt @0x401639 查找字符串引用

## 关键 payload

```
ptrace=$rax=0 + TEA Feistel
```

## 经验教训

ptrace反调试用GDB catch syscall+set $rax=0绕过;TEA特征常量0x9E3779B9+0xC6EF3720+0x61C88647是快速识别;控制流平坦化不要深入分析,黑盒动态分析更高效。

## 标签

statically-linked、stripped、ptrace-anti-debug、control-flow-flatten、TEA、feistel-cipher、dispatcher-block、dynamic-analysis、black-box、switch-case

## 参考来源

- https://www.ctfiot.com/285718.html
- 原文件：解析2025强网拟态决赛WeakJump.full.md
