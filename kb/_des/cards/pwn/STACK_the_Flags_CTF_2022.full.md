---
title: "STACK the Flags CTF 2022 - cursed_grimoires"
category: pwn
tags: ["STACK the Flags", "pwn", "house-of-botcake", "stdout-leak", "fsop", "mmap-then-edit"]
signals: ["STACK the Flags 2022", "house-of-botcake", "stdout-leak", "fsop", "mmap-then-edit", "glibc-2.35", "pwn_unknown", "STACK", "Flags", "cursed_grimoires", "mmap", "edit", "stdout", "Create"]
difficulty: medium
source: "https://www.ctfiot.com/84747.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# STACK the Flags CTF 2022 - cursed_grimoires

> 赛事：STACK the Flags 2022 | 方向：pwn | 难度：medium

## 一句话总结

STACK the Flags 2022 cursed_grimoires：菜单 1/2/3 二进制 + 1MB 大块跨 mmap 边界 + 单字节 edit 改 stdout。

## 攻击链

1. 选 Create Grimoire 一次，edit 单字节写
2. menu() 调 puts 触发 stdout write 路径
3. malloc 1MB 大块跨过 mmap threshold
4. mmap 区域位于 libc_base-0xf7ff0 处
5. edit 改 stdout->_flags = 0x1800 (NO_WRITES 清除 + APPEND/CURRENTLY)
6. edit 改 stdout->_IO_write_ptr 末字节为 0x50
7. 调 menu 触发 puts，泄 _IO_stdfile_1_lock 算 libc_base
8. chunk_addr = libc_base - 0xf7ff0 即 mmap 区域
9. 改 stdout->vtable 至 _IO_wfile_jumps
10. 改 _wide_data->_wide_vtable 伪造 _IO_wfile_overflow
11. ret2libc / 调 system 弹 shell
12. Full RELRO + Canary + NX + PIE 全开下利用 FSOP

## 关键 payload

```
edit(stdout_offset+0x28, 0x50)  # _IO_write_ptr LSB
```

## 经验教训

Full RELRO + Canary + NX + PIE 全开下，FSOP via _IO_wfile_jumps 仍可作为终极利用面。

## 标签

house-of-botcake、stdout-leak、fsop、mmap-then-edit、glibc-2.35

## 参考来源

- https://www.ctfiot.com/84747.html
- 原文件：STACK_the_Flags_CTF_2022.full.md
