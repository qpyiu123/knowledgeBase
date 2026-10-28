---
title: "2024 羊城杯 PWN AK 篇（4 题：pstack / Travel / C++String catch / bigbin HoA2）"
category: pwn
tags: ["2024 羊城杯粤港澳大湾区网络安全大赛", "pwn", "pstack 控制 rbp", "ret2libc", "House of Apple 2", "setcontext ORW"]
signals: ["2024 羊城杯粤港澳大湾区网络安全大赛 2024", "pstack 控制 rbp", "ret2libc", "House of Apple 2", "setcontext ORW", "_IO_wfile_jumps", "largebin attack", "C++ String catch", "system command", "rop", "heap_exploit", "srop", "rbp", "House"]
difficulty: hard
source: "https://www.ctfiot.com/203007.html"
tools: ["C", "ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 羊城杯 PWN AK 篇（4 题：pstack / Travel / C++String catch / bigbin HoA2）

> 赛事：2024 羊城杯粤港澳大湾区网络安全大赛 2024 | 方向：pwn | 难度：hard | 工具：C、ROP

## 一句话总结

4 道堆栈综合：rbp 控 ret2libc、城市菜单 House of Apple 2 ORW、C++ String catch system、largebin 复用 HoA2——一题一 House of Apple 工业流水线。

## 攻击链

1. pstack: 0x10 字节溢出覆盖 rbp、leave;ret 二次跳到 bss 写 ROP
2. pstack: puts_plt(puts_got) 泄 libc → system("/bin/sh")
3. Travel: 增删改查菜单城市 + 大小堆 + 0x510 触发 largebin
4. Travel: 泄露 heap+libc → House of Apple 2 + setcontext 53 ROP
5. Travel: _IO_wfile_jumps -0x40 偏 0xc8 + orw pop_rdi/pop_rsi/pop_rdx 弹
6. C++: try/catch String 异常 → system(command) 直读 command 寄存器
7. bigbin: tcache+largebin overlap → UAF → House of Apple 2

## 关键 payload

```
payload = p64(bss)+p64(pop_rdi)+p64(bin_sh)+p64(ret)+p64(system)
```

## 经验教训

pstack 0x10 字节溢出看上去不够拿 shell，但 leave;ret + 二次 leave 就能把栈劫到 bss 上 ROP；House of Apple 2 + setcontext 53 是 libc ≥ 2.34 失 _IO_str_overflow 后唯一通用 ORW 出口。

## 标签

pstack 控制 rbp、ret2libc、House of Apple 2、setcontext ORW、_IO_wfile_jumps、largebin attack、C++ String catch、system command

## 参考来源

- https://www.ctfiot.com/203007.html
- 原文件：2024年羊城杯粤港澳大湾区网络安全大赛WP-PWN_AK篇.full.md
