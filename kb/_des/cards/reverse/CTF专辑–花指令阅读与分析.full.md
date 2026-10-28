---
title: "CTF 专辑 – 花指令阅读与分析"
category: reverse
tags: ["CTF Reverse", "reverse", "花指令", "JunkCode", "等价替换", "抵消型"]
signals: ["CTF Reverse 2024", "花指令", "JunkCode", "等价替换", "抵消型", "jmp db型", "间接赋值", "IDA LinearSweep", "Recursive Traversal", "reverse", "push", "pop", "retn", "add-sub"]
difficulty: medium
source: "https://www.ctfiot.com/194547.html"
tools: ["IDA"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# CTF 专辑 – 花指令阅读与分析

> 赛事：CTF Reverse 2024 | 方向：reverse | 难度：medium | 工具：IDA

## 一句话总结

花指令阅读与分析 — JunkCode 算数拆分 + push/pop/retn 等价解释 + 抵消型 (add-sub/xor-xor) + jmp db 型 (EB 03 跳 55 E8 AA) + 间接赋值 + IDA LinearSweep vs Recursive Traversal 反汇编算法差异。

## 攻击链

1. JunkCode: mov eax,eax; jmp rva=0; xor eax,0
2. 算数拆分: add eax,5 → add eax,2; add eax,1; inc eax; inc eax
3. shl eax,5 → shl eax,3; shl eax,1; shl eax,1
4. 等价解释: push 0x11111 ≡ sub esp,4; mov [esp],0x11111
5. retn 0x5 ≡ mov eip,[esp]; add esp,4+5
6. enter 8,0 ≡ push ebp; mov ebp,esp; sub esp,8
7. 抵消型: push-pop / add-sub / inc-dec / xor-xor
8. jmp db 型: EB 03 55 E8 AA → EB 03 jmp 跳过 55 E8 AA 数据
9. 条件跳转 jmp db: jz label0; jnz label1; label0: db 0E8h
10. 间接赋值: b=a, c=b → c=a (用于构造花指令)
11. IDA Linear Sweep 逐行反汇编, Recursive Traversal 按代码顺序

## 关键 payload

```
JunkCode 算数拆分 / 等价解释 push pop retn / 抵消型 push-pop add-sub / jmp db EB 03 / 间接赋值 / IDA LinearSweep vs Recursive Traversal
```

## 经验教训

花指令分 4 类:① 垃圾代码 ② 等价替换 ③ 抵消型 ④ jmp db 型;IDA LinearSweep 逐行 vs Recursive Traversal 按执行顺序;call+5 拿 eip 是经典 trick。

## 标签

花指令、JunkCode、等价替换、抵消型、jmp db型、间接赋值、IDA LinearSweep、Recursive Traversal、OllyDbg、算数拆分、栈平衡、call+5取eip

## 参考来源

- https://www.ctfiot.com/194547.html
- 原文件：CTF专辑–花指令阅读与分析.full.md
