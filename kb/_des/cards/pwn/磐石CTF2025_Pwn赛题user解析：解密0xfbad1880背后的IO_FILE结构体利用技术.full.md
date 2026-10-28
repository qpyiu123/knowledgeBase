---
title: "磐石CTF2025 Pwn赛题user解析：解密0xfbad1880背后的IO_FILE结构体利用技术"
category: pwn
tags: ["磐石CTF2025", "pwn", "IO_FILE结构体", "0xfbad1880", "_IO_2_1_stdout_", "_flags字段"]
signals: ["磐石CTF2025 2025", "IO_FILE结构体", "0xfbad1880", "_IO_2_1_stdout_", "_flags字段", "_IO_write_base/ptr", "glibc 2.31", "负数idx", "任意地址写", "heap_exploit", "CTF2025", "user", "glibc", "show"]
difficulty: medium
source: "https://www.ctfiot.com/265310.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 磐石CTF2025 Pwn赛题user解析：解密0xfbad1880背后的IO_FILE结构体利用技术

> 赛事：磐石CTF2025 2025 | 方向：pwn | 难度：medium

## 一句话总结

磐石CTF2025 user：glibc 2.31菜单题无show+IO_FILE结构体伪造+stdout泄露libc

## 攻击链

1. heap[-8] = _IO_2_1_stdout_→edit修改stdout结构体→_flags=0xfbad1880+_IO_write_base改低地址→泄露libc地址→其他漏洞(如tcache)任意地址写

## 关键 payload

```
heap[-8]=_IO_2_1_stdout_;_flags=0xfbad1880;_IO_write_base低地址;stdout距离heap 0x40字节;heap数组5个chunk 0x50/0x40;delete/edit负数idx
```

## 经验教训

堆bss数组距stdout固定0x40字节可用edit(-8)修改stdout；_flags=0xfbad1880触发写缓冲

## 标签

IO_FILE结构体、0xfbad1880、_IO_2_1_stdout_、_flags字段、_IO_write_base/ptr、glibc 2.31、负数idx、任意地址写

## 参考来源

- https://www.ctfiot.com/265310.html
- 原文件：磐石CTF2025_Pwn赛题user解析：解密0xfbad1880背后的IO_FILE结构体利用技术.full.md
