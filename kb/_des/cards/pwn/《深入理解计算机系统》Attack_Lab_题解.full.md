---
title: "《深入理解计算机系统》Attack Lab 题解"
category: pwn
tags: ["CS:APP", "pwn", "CSAPP-Attack-Lab", "ret2func", "ret2arg", "ROP-gadget"]
signals: ["CS:APP 2024", "CSAPP-Attack-Lab", "ret2func", "ret2arg", "ROP-gadget", "x86-64", "hex2raw", "rop", "CSAPP", "Attack", "Lab", "ROP", "cookie", "Phase"]
difficulty: medium
source: "https://www.ctfiot.com/260639.html"
tools: ["ROP", "x86/x64"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 《深入理解计算机系统》Attack Lab 题解

> 赛事：CS:APP 2024 | 方向：pwn | 难度：medium | 工具：ROP、x86/x64

## 一句话总结

CSAPP 经典 Attack Lab 三阶段 ROP 题解：ret2func → ret2arg → 栈地址存 cookie 字符串后 ret2arg。

## 攻击链

1. Phase 1 (CI): getbuf 0x28 栈空间 + Gets 无界读 → 0x28 字节 padding + 0x4017c0 touch1 地址覆盖返回 → hex2raw < phase_1 | ./ctarget -q/Phase 2 (CII): touch2(unsigned val) 需要 val==cookie → 0x38 字节 padding + pop_rdi gadget + cookie 立即数 + touch2 地址/Phase 3 (CIII): touch3(char *s) 读 s 字符串 → 0x38 padding + pop_rdi + 栈地址（指向 cookie 字符串） + touch3

## 关键 payload

```
Phase 1: 0x28 bytes 0x00 + p64(0x4017c0)  Phase 2: 0x38 bytes + pop_rdi(0x59b997fa) + touch2  Phase 3: 0x38 bytes + pop_rdi(栈地址) + touch3
```

## 经验教训

Phase 1 直接覆盖返回地址；Phase 2 引入 pop_rdi gadget 传参；Phase 3 把 cookie 字符串放在栈上，用栈地址作为参数；hex2raw 工具把 ASCII hex 转为原始字节给 ctarget 喂。

## 标签

CSAPP-Attack-Lab、ret2func、ret2arg、ROP-gadget、x86-64、hex2raw

## 参考来源

- https://www.ctfiot.com/260639.html
- 原文件：《深入理解计算机系统》Attack_Lab_题解.full.md
