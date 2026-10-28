---
title: "春秋杯WP｜2023春秋杯春季赛之pwn、web、misc篇"
category: pwn
tags: ["春秋杯2023春季赛", "pwn", "栈溢出", "partial write绕PIE", "格式化字符串泄露elfbase", "off-by-null"]
signals: ["春秋杯2023春季赛 2023", "栈溢出", "partial write绕PIE", "格式化字符串泄露elfbase", "off-by-null", "setcontext+orw", "lua字节码", "rop", "pwn", "web", "misc", "p2048", "partial", "write"]
difficulty: medium
source: "https://www.ctfiot.com/120359.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 春秋杯WP｜2023春秋杯春季赛之pwn、web、misc篇

> 赛事：春秋杯2023春季赛 2023 | 方向：pwn | 难度：medium

## 一句话总结

春秋杯2023春季赛pwn/web/misc三方向：p2048栈溢出+partial write+FTP fmtstr+got覆写+lua堆

## 攻击链

1. p2048栈溢出+partial write 4bit爆破→LzhiFTP格式化字符串泄elfbase+idx负数越界写got→lua字节码修复+off-by-null堆overleap+setcontext+orw劫持free_hook

## 关键 payload

```
p2048:sl(b'a'*(1048+4)+b'\x60'+b'\x5e'+b'\xff');LzhiFTP:'No%6$p'泄elfbase+idx=-16负数越界;setcontext+orw;lua字节码修复文件头
```

## 经验教训

partial write爆破4bit+fmtstr %p泄elfbase+idx未检查负数是常见pwn套路

## 标签

栈溢出、partial write绕PIE、格式化字符串泄露elfbase、off-by-null、setcontext+orw、lua字节码

## 参考来源

- https://www.ctfiot.com/120359.html
- 原文件：春秋杯WP｜2023春秋杯春季赛之pwn、web、misc篇.full.md
