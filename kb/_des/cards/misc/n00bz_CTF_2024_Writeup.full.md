---
title: "n00bz CTF 2024 Writeup"
category: misc
tags: ["n00bzCTF", "misc", "powershell-xor-3", "brainfuck-c-translation", "qbasic", "vm-qbasic"]
signals: ["n00bzCTF 2024", "powershell-xor-3", "brainfuck-c-translation", "qbasic", "vm-qbasic", "write-only", "misc_unknown", "n00bz", "CTF", "Writeup", "PowerShell", "XOR", "brainfuck", "cat"]
difficulty: medium
source: "https://www.ctfiot.com/197699.html"
tools: ["C", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# n00bz CTF 2024 Writeup

> 赛事：n00bzCTF 2024 | 方向：misc | 难度：medium | 工具：C、Python

## 一句话总结

n00bz CTF 2024 Writeup：PowerShell XOR 加密 + brainfuck → C 翻译。

## 攻击链

1. PowerShell: cat flag.txt | ForEach { $_ -bxor 3 }
2. 输出 `m33ayxeqln\sbqjp\twk\{lq~` 加密
3. brainfuck → C 翻译 (bftoc.py by Paul Kaefer)
4. 模拟 tape[1000] 跑 BF VM
5. 输出 32 字符明文

## 关键 payload

```
PowerShell XOR 3 + brainfuck C 翻译
```

## 经验教训

写多语言题目（PowerShell/BF/QBasic）是 n00bz 系列特色。

## 标签

powershell-xor-3、brainfuck-c-translation、qbasic、vm-qbasic、write-only

## 参考来源

- https://www.ctfiot.com/197699.html
- 原文件：n00bz_CTF_2024_Writeup.full.md
