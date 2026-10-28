---
title: "SigMachine CTF 逆向题深度解析"
category: reverse
tags: ["自制 CTF 教学题", "reverse", "ELF", "x86-64", "statically-linked", "stripped"]
signals: ["自制 CTF 教学题 2025", "ELF", "x86-64", "statically-linked", "stripped", "Linux-signal", "sigaction", "OLLVM", "signal-handler", "reverse", "misc_math", "signal", "handler", "file"]
difficulty: hard
source: "https://www.ctfiot.com/283400.html"
tools: ["IDA", "OLLVM", "x86/x64"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# SigMachine CTF 逆向题深度解析

> 赛事：自制 CTF 教学题 2025 | 方向：reverse | 难度：hard | 工具：IDA、OLLVM、x86/x64

## 一句话总结

ELF+signal handler+OLLVM 三合一逆向入门

## 攻击链

1. file 命令识别 ELF 64-bit LSB 静态链接 stripped
2. 字符串定位: 0x47c093 ''wrong!'' 0x47c09a ''right!'' 0x47c0a1 ''password:
3. 查 signal/sigaction 函数引用 → 注册信号处理器
4. signal handler 里藏 flag 校验逻辑（保护主函数不让单步）
5. 反反调试: 用 ptrace 接管 / 改 signal handler 跳过
6. 静态链接 + stripped → 手工定位关键函数（搜索 0x400a70 等候选）
7. OLLVM 混淆（控制流平坦化 + 虚假控制流）→ 用 D-810 反混淆插件
8. 还原加密函数: 输入 password → state machine → 比较 right! 决定输出

## 关键 payload

```
0x47c093 'wrong!' / 0x47c09a 'right!' / 0x47c0a1 'password:
```

## 经验教训

signal handler 是反调试常用手段；OLLVM 是工业级混淆；静态链接二进制要手动定位

## 标签

ELF、x86-64、statically-linked、stripped、Linux-signal、sigaction、OLLVM、signal-handler、反调试、SROP、自定义加密、IDA

## 参考来源

- https://www.ctfiot.com/283400.html
- 原文件：SigMachine_CTF逆向题深度解析-从零到一的完整解题之旅.full.md
