---
title: "web选手入门pwn(17) 2024春秋杯夏季赛pwn"
category: pwn
tags: ["春秋杯", "pwn", "ret2libc", "stack-overflow", "ret2vuln-loop", "整数溢出"]
signals: ["春秋杯 2024", "ret2libc", "stack-overflow", "ret2vuln-loop", "整数溢出", "prng爆破", "rop", "ROP", "ret2vuln", "gets", "extend", "printf", "libc"]
difficulty: easy
source: "https://www.ctfiot.com/198409.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# web选手入门pwn(17) 2024春秋杯夏季赛pwn

> 赛事：春秋杯 2024 | 方向：pwn | 难度：easy

## 一句话总结

春秋杯两题入门ROP，覆盖ret2vuln循环喷射+整数下溢gets覆盖的经典入门路径。

## 攻击链

1. 题目1循环ret2vuln+extend堆喷对齐栈帧触发printf泄libc+ret2libc / 题目2password=base64(this is password)登录+length=-1整数下溢触发gets→覆盖saved RBP+返回地址

## 关键 payload

```
题目2 length=-1 整数下溢 + payload A*104 + p64(pop_rdi_ret) + p64(binsh) + p64(system) 覆盖PRNG栈槽
```

## 经验教训

length字段使用int32比较但调用gets时无符号，length=-1溢出为最大正值绕过长度检查；ret2vuln+extend操作本质是栈空间对齐+控制字刷新printf参数。

## 标签

ret2libc、stack-overflow、ret2vuln-loop、整数溢出、prng爆破

## 参考来源

- https://www.ctfiot.com/198409.html
- 原文件：web选手入门pwn(17)_——2024年春秋杯夏季赛pwn.full.md
