---
title: "web选手入门pwn(31) 强网杯 bph (House of Apple 变种)"
category: pwn
tags: ["强网杯", "pwn", "glibc-2.39", "_IO_FILE", "_IO_wfile_jumps", "_wide_data"]
signals: ["强网杯 2024", "glibc-2.39", "_IO_FILE", "_IO_wfile_jumps", "_wide_data", "fake-stdout", "ORW", "setcontext", "pivote-gadget", "heap_exploit", "bph", "glibc", "House", "Apple-style"]
difficulty: hard
source: "https://www.ctfiot.com/288976.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# web选手入门pwn(31) 强网杯 bph (House of Apple 变种)

> 赛事：强网杯 2024 | 方向：pwn | 难度：hard | 工具：ROP

## 一句话总结

强网杯 bph，glibc 2.39 House of Apple-style 攻击，通过伪造 _IO_wide_data + chain(pivot) 触发 ORW 链。

## 攻击链

1. send A*0x28 触发 printf 残基泄 libc+token边界越界写stdin->_IO_buf_base零字节/伪造stdin->_IO_buf_base=stdout-0x48  _IO_buf_end=stdout+0x200 进入可写区/伪造 fake_stdout 套用 IO_FILE_plus_struct: vtable=jumps_mmap-0x20  _wide_data=stdout-0x48  chain=pivot_gadget(mov rsp, rdx) 触发 _io_wfile_underflow_mmap/stdout+0xe8 处放 ORW ROP

## 关键 payload

```
pivot_gadget = libc_base + 0x5ef5f  # mov rsp, rdx; ret  jumps_mmap = _IO_wfile_jumps + 0xb0
```

## 经验教训

glibc 2.39 移除了 __free_hook/__malloc_hook，但 IO_FILE vtable 攻击依然有效（_IO_wfile_jumps_mmap 不在检查表内）；mov rsp, rdx gadget 把栈迁到 ROP 区域，是 House of Apple 2/3 的核心 pivot 技巧。

## 标签

glibc-2.39、_IO_FILE、_IO_wfile_jumps、_wide_data、fake-stdout、ORW、setcontext、pivote-gadget

## 参考来源

- https://www.ctfiot.com/288976.html
- 原文件：web选手入门pwn(31)——强网杯bph.full.md
