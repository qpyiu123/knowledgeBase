---
title: "强网杯 S8 决赛 Reverse S1mpleVM"
category: reverse
tags: ["强网杯", "reverse", "custom-VM", "stack-VM", "LinkEntry", "opcode-16"]
signals: ["强网杯 2024", "custom-VM", "stack-VM", "LinkEntry", "opcode-16", "virtual-machine", "compiler", "vmrun", "pwn-reverse", "reverse", "S1mpleVM", "opcode", "struct", "signed"]
difficulty: hard
source: "https://www.ctfiot.com/220846.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 强网杯 S8 决赛 Reverse S1mpleVM

> 赛事：强网杯 2024 | 方向：reverse | 难度：hard

## 一句话总结

强网杯 S8 决赛 S1mpleVM：自定义 16 opcode 栈式 VM 编译器，逆向需要还原指令语义。

## 攻击链

1. S1mpleVM 自定义栈式 VM，16 个 opcode
2. 数据结构: struct LinkEntry { signed val; LinkEntry *next; } 链表栈
3. case 0u: pop+pop+v7%v8 push 模运算（0x80000000 标志空栈）
4. case 1u: push PC+1 单字节
5. case 2u: pop to v5 (load)
6. case 3u: sub (类似)
7. case 4u: add
8. case 5u: bitwise NOT
9. case 6u: XOR
10. case 7u: OR
11. case 8u: AND
12. case 9u: CMP (类似)
13. case 10u: JMP PC
14. case 11u: JE
15. case 12u: JNE
16. case 13u: read (input)
17. case 14u: write (output)
18. case 15u: end
19. vmrun 接受 input + vmcode 字节码
20. 指令格式: 1 字节 opcode (vmcode[0]-16), 部分带 1 字节操作数 (vmcode[1])

## 关键 payload

```
16 opcode stack VM + LinkEntry 链表 + input/vmcode 参数
```

## 经验教训

自定义 VM 逆向关键在数据结构（LinkEntry 链表栈）+ opcode 表 + 操作数格式（1 字节）。

## 标签

custom-VM、stack-VM、LinkEntry、opcode-16、virtual-machine、compiler、vmrun、pwn-reverse

## 参考来源

- https://www.ctfiot.com/220846.html
- 原文件：强网杯S8决赛Reverse.full.md
