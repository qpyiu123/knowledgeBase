---
title: "PWN - 西湖论剑 2022 中国杭州网络安全技能大赛初赛官方 Write Up"
category: pwn
tags: ["西湖论剑 2022 中国杭州网络安全技能大赛 初赛", "pwn", "pwn", "z3-solver", "babycalc", "jit"]
signals: ["西湖论剑 2022 中国杭州网络安全技能大赛 初赛 2023", "pwn", "z3-solver", "babycalc", "jit", "message-board", "fmt-string", "栈迁移", "orw", "rop", "PWN", "Message", "Board", "seccomp"]
difficulty: hard
source: "https://www.ctfiot.com/97886.html"
tools: ["Z3"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# PWN - 西湖论剑 2022 中国杭州网络安全技能大赛初赛官方 Write Up

> 赛事：西湖论剑 2022 中国杭州网络安全技能大赛 初赛 2023 | 方向：pwn | 难度：hard | 工具：Z3

## 一句话总结

西湖论剑 2022 三道 PWN 官方 WP：babycalc 单字节溢出+栈迁移、jit 自研 IR 编译器整数溢出、Message Board seccomp 沙箱下 orw+栈迁移双跳。

## 攻击链

1. 一 babycalc：read 末尾置 0 单字节溢出覆盖 rbp LSB
2. 任意偏移写 1 字节改 retaddr 为 leave;ret 触发栈迁移
3. 栈迁移到可控数据区布置 ret*21 + pop_rdi+got+puts+start 泄 libc
4. 输入 16 字节 z3 方程答案 (0x13 0x24 0x35 ... 0x03)
5. 计算 one_gadget 0xf1247 二次栈迁移
6. 二 jit：自研 IR (mov/and/or/xor/call) → mmap 编译为机器码
7. var2idx 整数溢出：variba=32 时 -8*32=0 绕过 fatal 检查
8. 用 jop 链 + movabs rsi 写入 6 字节 shellcode (push /sh; pop rax; shl 32; push /bin; or; syscall 0x3b)
9. 利用 ASLR 改写 retaddr 后 12 位跳 shellcode
10. 三 Message Board：seccomp 禁 execve 59 号系统调用
11. fmt-string 泄 libc + 栈溢出 0x10 控 rbp+ret
12. 跳 mov [rbp] rsi gadget 任意地址写 0xC0 (orw rop)
13. 二次 leave;ret 栈迁移到 bss 区域执行 open+read+puts 链

## 关键 payload

```
jit sc="\x68/sh\x00" + "\x58\x48\xc1\xe0\x20" + "\x68/bin" + "\x5f\x48\x09\xf8" + "\x50\x48\x89\xe7" + "\x48\x31\xf6\x48\x31\xd2" + "\x6a\x3b\x58\x0f\x05
```

## 经验教训

read 末尾 NUL 字节可单字节溢出改 rbp；自研 JIT 必须审计 var2idx 等边界检查；seccomp 禁 execve 必走 open+read+puts orw；fmt-string 泄 libc 后栈迁移到 bss 是经典二段跳。

## 标签

pwn、z3-solver、babycalc、jit、message-board、fmt-string、栈迁移、orw

## 参考来源

- https://www.ctfiot.com/97886.html
- 原文件：PWN｜西湖论剑·2022中国杭州网络安全技能大赛初赛官方Write_Up.full.md
