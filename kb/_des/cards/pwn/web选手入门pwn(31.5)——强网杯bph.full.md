---
title: "web选手入门pwn(31.5) 强网杯bph stack-leak 变种"
category: pwn
tags: ["强网杯", "pwn", "glibc-2.39", "_IO_FILE", "_IO_write_base-leak", "environ"]
signals: ["强网杯 2024", "glibc-2.39", "_IO_FILE", "_IO_write_base-leak", "environ", "stack-read", "House-of-Apple", "heap_exploit", "bph", "IO_write_base", "IO_write_ptr", "IO_buf_base", "send", "x28"]
difficulty: hard
source: "https://www.ctfiot.com/289285.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# web选手入门pwn(31.5) 强网杯bph stack-leak 变种

> 赛事：强网杯 2024 | 方向：pwn | 难度：hard | 工具：ROP

## 一句话总结

强网杯 bph 变种，通过 _IO_write_base/_IO_write_ptr 范围读 environ 泄栈，再用 _IO_buf_base 改写栈。

## 攻击链

1. send A*0x28 泄 libc/choice=1 写一字节 0x00 到 stdin->_IO_buf_base 切断输入/伪造 stdin buf 指向 stdout+0x200 区可任意写 fake_stdout/伪造 fake_read_file: _IO_write_base=environ, _IO_write_ptr=environ+8, vtable=_IO_file_jumps 触发 puts 打印 environ → 泄 stack_N/再次伪造 fake_write_file: _IO_buf_base=stack_N, vtable=_IO_wfile_jumps 触发 gets 写栈上/栈上布置 ROP

## 关键 payload

```
fake_file_write = flat({0x00: 0x800|0x1000, 0x20: environ, 0x28: environ+8, 0x70: 1, 0x68: stdin, 0xd8: _IO_file_jumps}, filler=b"\x00")
```

## 经验教训

伪造 _IO_FILE 的 `_IO_write_base/_IO_write_ptr` 范围可触发 `puts` 读任意地址；`environ` 符号永远指向 __libc_start_main 栈帧，是稳定的栈地址锚点；同一 fake_file 多次重用，每次根据 vtable 切换触发不同 IO 操作。

## 标签

glibc-2.39、_IO_FILE、_IO_write_base-leak、environ、stack-read、House-of-Apple

## 参考来源

- https://www.ctfiot.com/289285.html
- 原文件：web选手入门pwn(31.5)——强网杯bph.full.md
