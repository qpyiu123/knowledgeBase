---
title: "SECCON 2022 Writeup"
category: pwn
tags: ["SECCON 2022", "pwn", "pwn", "ret2libc", "libc-leak", "name-format"]
signals: ["SECCON 2022 2022", "pwn", "ret2libc", "libc-leak", "name-format", "babyfile", "io-file", "fsop", "_IO_read_base", "rop", "SECCON", "koncha", "scanf", "one_gadget"]
difficulty: hard
source: "https://www.ctfiot.com/74039.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# SECCON 2022 Writeup

> 赛事：SECCON 2022 2022 | 方向：pwn | 难度：hard

## 一句话总结

SECCON 2022 koncha (scanf 栈溢出 + one_gadget) + babyfile (FILE 结构 _IO_read_base/vtable 偏移 trick 任意改 → _IO_finish 触发 system(binsh))。

## 攻击链

1. 题目 1 koncha: scanf 栈溢出 + libc 地址泄露
2. name[0x30] + country[0x20] + scanf("%[^\n]s") 绕过 \n 截断
3. printf("Nice to meet you, %s!\n", name) 泄露栈地址
4. 攻击: 跳过 name → country cyclic(88) + p64(libc_base+one_gadget 0xe3b01)
5. 题目 2 babyfile: FILE 结构 + trick(offset, value) 改 fp->xx
6. menu: 1=Flush 2=Trick 0=Exit
7. _IO_FILE _flags + _IO_read_ptr/end/base + _IO_write_ptr + _chain
8. 改 _mode=0x1 + vtable=0xa8 触发 _IO_doallocbuf + 分配 buffer
9. 改 vtable=0x60 触发 _IO_underflow 设置 read_base
10. getheap 16 次爆破 heap/libc leak
11. 攻击: trick(_fileno, 0x04) + trick(vtable, 0x50) 触发 _IO_finish
12. finish → puts(fp->_IO_read_ptr) 调 system
13. free_space 写 system 8 字节 + binsh 8 字节
14. _IO_save_base 写 target (system 参数 "/bin/sh")
15. _IO_write_base FROM + _IO_buf_base/__free_hook TO 触发任意地址写
16. flush 触发 system(binsh) shell

## 关键 payload

```
trick(free_speace+i, system_byte) + trick(free_speace+8+i, binsh_byte) + trick(_IO_save_base+i, heap_arg)
```

## 经验教训

scanf("%[^\n]s") 格式串保留换行前内容；FILE 结构 vtable 偏移可触发任意 _IO_xxx 函数 (如 _IO_finish 调 puts)；trick(offset, value) 任意改 FILE 字段是 FILE 攻击经典模式。

## 标签

pwn、ret2libc、libc-leak、name-format、babyfile、io-file、fsop、_IO_read_base、vtable-overflow、free-hook

## 参考来源

- https://www.ctfiot.com/74039.html
- 原文件：SECCON_2022_Writeup.full.md
