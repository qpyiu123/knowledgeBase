---
title: "一道关于逆向的实战CTF题目分析"
category: reverse
tags: ["实战逆向 CTF", "reverse", "left函数", "xor函数", "32轮调度", "dword数组"]
signals: ["实战逆向 CTF 2024", "left函数", "xor函数", "32轮调度", "dword数组", "简单C还原", "reverse", "left", "xor", "dword", "flag", "IDA", "printf", "xors"]
difficulty: easy
source: "https://www.ctfiot.com/193276.html"
tools: ["C", "IDA"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 一道关于逆向的实战CTF题目分析

> 赛事：实战逆向 CTF 2024 | 方向：reverse | 难度：easy | 工具：C、IDA

## 一句话总结

自实现 left/xor 双函数 + 32 轮调度 + dword 数组还原 flag。

## 攻击链

1. IDA 反编译 left(a1,a2): printf("%c", ((a1 ^ a2) >> 8))
2. xors(a1,a2): printf("%c", (((a1 + a2) >> 8) ^ a2))
3. dword_402120[32] 已知 32 个 16 位数
4. temp[32]={1,0,0,1,0,1,1,0,...} 决定每轮调用 left/xor
5. temp[i]=1 调 left(dword[i], 8)
6. temp[i]=0 调 xors(dword[i], 40)
7. 32 轮逐字节打印还原 flag

## 关键 payload

```
flag{(a1^a2)>>8 | ((a1+a2)>>8)^a2}
```

## 经验教训

IDA 反编译时遇到 `((a2 ^ a1) << 8) - a2` 这种结构要还原原始算术语义；32 轮调度类 VM 用 C 复写比反汇编快 10 倍。

## 标签

left函数、xor函数、32轮调度、dword数组、简单C还原

## 参考来源

- https://www.ctfiot.com/193276.html
- 原文件：一道关于逆向的实战CTF题目分析.full.md
