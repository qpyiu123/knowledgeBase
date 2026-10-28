---
title: "从某新生赛入门PWN"
category: pwn
tags: ["某新生赛 PWN 入门", "pwn", "encrypto还原", "ezr0p", "ezrop64", "格式化字符串"]
signals: ["某新生赛 PWN 入门 2022", "encrypto还原", "ezr0p", "ezrop64", "格式化字符串", "shellcoder字符限制", "mprotect", "整数溢出", "seccomp+orw", "pwn_unknown", "bad_c0de", "PWN", "encrypto", "ROP"]
difficulty: medium
source: "https://www.ctfiot.com/80255.html"
tools: ["GDB", "ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 从某新生赛入门PWN

> 赛事：某新生赛 PWN 入门 2022 | 方向：pwn | 难度：medium | 工具：GDB、ROP

## 一句话总结

bad_c0de 某新生赛 9 题 PWN：encrypto 还原 + 32/64 位 ROP + fmtstr + 字符 shellcode + seccomp+orw。

## 攻击链

1. 题 1 ezcmp: 自实现 enccrypt (rand+buff+bua+buffff XOR), srand(v0=1) 固定种子, GDB 0x4014b4 断点读 buff
2. 题 2 ezr0p: 32 位栈溢出 0x20+call_system(0x08048562)+0x0804A080 bss 写 /bin/sh
3. 题 3 ezrop64: pop_rdi+binsh+ret+system
4. 题 4 ezfmt: 6 个 %p 找到 name 偏移, %7$s....+p64(0x4040a0) 读 name
5. 题 5 shellcoder: 字符限制 ''0''~''z'' 内构造 xor 自解码 syscall read
6. xor dword ptr[rsi+0x33],ecx 改写 rip + asm(shellcraft.sh()) 拼接
7. 题 6 shellcode: mprotect RWX + 0x108 溢出 + ret=0x4040a0
8. 题 7 int 溢出: gets 覆盖 number!=0 触发 cat flag
9. 题 8 arrayRE: 24 数字 0-9 爆破 decode(a1,a2)=(35*(a1-48)+18*(a2-48)+2)%10
10. 题 9 intorw: seccomp 限制 open/read/write, vuln int 整数溢出
11. puts_got 泄 libc + 二次溢出 orw(open 'flag', 3, bss, 0x100, read+puts)
12. pop_rsi=libc+0x2be51, pop_rdx_r12=libc+0x11f497

## 关键 payload

```
9 题 PWN: encrypto+rop32+rop64+fmtstr+字符shellcode+orw+seccomp
```

## 经验教训

encrypto 自实现加密直接 GDB 断点读密文 (srand(1) 固定种子)；字符限制 shellcode 用 xor [rsi+0x33], ecx 自解码 syscall；intorw seccomp 用 libc pop_rsi/pop_rdx_r12 gadget。

## 标签

encrypto还原、ezr0p、ezrop64、格式化字符串、shellcoder字符限制、mprotect、整数溢出、seccomp+orw、intorw

## 参考来源

- https://www.ctfiot.com/80255.html
- 原文件：从某新生赛入门PWN.full.md
