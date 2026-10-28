---
title: "pwn 题 ZJCTF 2019 login 的分析"
category: pwn
tags: ["ZJCTF", "pwn", "cpp-vtable", "virtual-function", "function-pointer", "two-level-pointer"]
signals: ["ZJCTF 2019", "cpp-vtable", "virtual-function", "function-pointer", "two-level-pointer", "asn-stack-overflow", "password-backdoor", "gdb-trace", "pwn_unknown", "ZJCTF", "login", "PWN", "User", "Admin"]
difficulty: hard
source: "https://www.ctfiot.com/89970.html"
tools: ["C"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# pwn 题 ZJCTF 2019 login 的分析

> 赛事：ZJCTF 2019 | 方向：pwn | 难度：hard | 工具：C

## 一句话总结

ZJCTF 2019 login PWN 复盘，C++ 虚函数表 + 二级指针调用 + 栈子函数复用覆盖。

## 攻击链

1. C++ User/Admin 结构体
2. 虚函数表 + 虚函数指针
3. main 函数 user->read_name 0x49 字节
4. 覆盖 password_checker 二级指针
5. 写后门函数 0x400e88 地址
6. 触发 password 验证流程
7. 二级指针调用跳到后门

## 关键 payload

```
C++ 二级虚函数指针 + 栈平移覆盖
```

## 经验教训

父子函数栈平移时，子函数栈空间的指针变量可能被父函数新调用破坏。

## 标签

cpp-vtable、virtual-function、function-pointer、two-level-pointer、asn-stack-overflow、password-backdoor、gdb-trace

## 参考来源

- https://www.ctfiot.com/89970.html
- 原文件：pwn题ZJCTF2019_login的分析.full.md
