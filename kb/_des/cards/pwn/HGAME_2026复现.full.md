---
title: "HGAME 2026复现"
category: pwn
tags: ["HGAME 2026", "pwn", "pwn", "canary-bypass", "shellcode", "short-int"]
signals: ["HGAME 2026 2026", "pwn", "canary-bypass", "shellcode", "short-int", "v3-decrypt", "off-by-null", "libc-2.35", "stack_overflow", "HGAME", "short", "canary", "week1-adrift", "way"]
difficulty: medium
source: "https://www.ctfiot.com/301877.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# HGAME 2026复现

> 赛事：HGAME 2026 2026 | 方向：pwn | 难度：medium

## 一句话总结

HGAME 2026复现：short整数边界绕过+canary泄露+shellcode

## 攻击链

1. week1-adrift: 主循环菜单0=way/1=delete/2=show/3=change/4=exit
2. v6[0] 是 short int 16位
3. -32768 → 0x8000 取反+1 = 0xFFFB → 等价+5
4. case2 show(-32768) 打印canary值
5. case3 修改canary绕过case4检查
6. case0 0x410字节栈溢出写入shellcode
7. 0x3e8+2字节padding + shellcode + return_addr
8. shellcode: pop r11; mov rax 0x68732f6e69622f; push rax; push rsp; pop rdi; xor eax,59; xor rdx,rdx; syscall
9. week2 diary keeper: glibc 2.35 patchelf
10. PROTECT_PTR指针保护
11. off by null 合并ABC

## 关键 payload

```
-32768 = 0xFFFB = +5 绕过case v6
```

## 经验教训

short int -32768 (0x8000) 取反+1=0xFFFB 实际为+5

## 标签

pwn、canary-bypass、shellcode、short-int、v3-decrypt、off-by-null、libc-2.35

## 参考来源

- https://www.ctfiot.com/301877.html
- 原文件：HGAME_2026复现.full.md
