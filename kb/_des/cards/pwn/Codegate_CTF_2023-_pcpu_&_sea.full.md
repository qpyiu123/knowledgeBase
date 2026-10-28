---
title: "Codegate CTF 2023: pcpu & sea"
category: pwn
tags: ["Codegate CTF 2023", "pwn", "pwn", "register-uaf", "signed-cmp", "AES-CBC"]
signals: ["Codegate CTF 2023 2023", "pwn", "register-uaf", "signed-cmp", "AES-CBC", "rop", "libc-2.31", "splice", "heap_exploit", "Codegate", "pcpu", "UAF", "sea", "signed"]
difficulty: hard
source: "https://www.ctfiot.com/121257.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Codegate CTF 2023: pcpu & sea

> 赛事：Codegate CTF 2023 2023 | 方向：pwn | 难度：hard | 工具：ROP

## 一句话总结

Codegate 2023两道pwn：pcpu寄存器竞态UAF+sea signed混淆AES-CBC

## 攻击链

1. pcpu: reg_list sleep(1)竞态UAF + alloc_list(3)复用释放buffer
2. 0x10000 list OOB read_reg_idx泄露其他寄存器
3. sea: signed/unsigned类型混淆 char last_byte+memcpy扩展长度
4. dec()栈溢出leak canary/libc/pie
5. AES-CBC+ROP execve(/bin/sh)

## 关键 payload

```
prog=[alloc_list(0),alloc_list(1),copy_reg(0,1),write_reg0_idx(0,10),alloc_list(3),dump_regs()]
```

## 经验教训

sleep(1)竞态+register复用可OOB；signed/unsigned混淆可扩大memcpy长度

## 标签

pwn、register-uaf、signed-cmp、AES-CBC、rop、libc-2.31、splice

## 参考来源

- https://www.ctfiot.com/121257.html
- 原文件：Codegate_CTF_2023-_pcpu_&_sea.full.md
