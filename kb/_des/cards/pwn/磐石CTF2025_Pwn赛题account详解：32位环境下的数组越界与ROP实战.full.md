---
title: "磐石CTF2025 Pwn赛题account详解：32位环境下的数组越界与ROP实战"
category: pwn
tags: ["磐石CTF2025", "pwn", "32位ROP", "数组越界", "栈溢出", "vuln()循环"]
signals: ["磐石CTF2025 2025", "32位ROP", "数组越界", "栈溢出", "vuln()循环", "v1[v2++]覆盖返回地址", "ret2libc", "puts泄漏libc", "CTF2025", "account", "ROP", "libc", "vuln", "overwrite"]
difficulty: easy
source: "https://www.ctfiot.com/265318.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 磐石CTF2025 Pwn赛题account详解：32位环境下的数组越界与ROP实战

> 赛事：磐石CTF2025 2025 | 方向：pwn | 难度：easy

## 一句话总结

磐石CTF2025 account：32位v1数组越界+循环10次+v2覆盖+两次ROP（泄libc+ret2libc）

## 攻击链

1. vuln()读4字节入v0→v1[v2++]=v0循环10次填满v1→overwrite v1[10]=13改idx→v1[14]=ret_addr→ROP1:puts(puts@got)→libc_base→ROP2:system(/bin/sh)

## 关键 payload

```
v1[v2++]=v0;v1[10]=v2 idx;v1[14]=ret_addr;main=0x8049264;pop_ebx_ret=0x08049022;puts@got泄libc_base=puts-0x6d1e0;system(/bin/sh)
```

## 经验教训

循环写入数组时v2 idx也可被覆盖，构造精确索引可写任意栈位置

## 标签

32位ROP、数组越界、栈溢出、vuln()循环、v1[v2++]覆盖返回地址、ret2libc、puts泄漏libc

## 参考来源

- https://www.ctfiot.com/265318.html
- 原文件：磐石CTF2025_Pwn赛题account详解：32位环境下的数组越界与ROP实战.full.md
