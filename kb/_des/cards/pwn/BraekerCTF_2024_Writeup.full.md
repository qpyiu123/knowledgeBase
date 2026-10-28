---
title: "BraekerCTF 2024 Writeup"
category: pwn
tags: ["BraekerCTF", "pwn", "32位 Linux", "sys_read shellcode", "add al [eax]", "add eax [eax]"]
signals: ["BraekerCTF 2024", "32位 Linux", "sys_read shellcode", "add al [eax]", "add eax [eax]", "add [eax] eax", "pop ecx", "jmp ecx", "execve /bin/sh", "pwn_unknown", "BraekerCTF", "Linux", "shellcode", "sys_read"]
difficulty: medium
source: "https://www.ctfiot.com/164132.html"
tools: ["pwntools"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# BraekerCTF 2024 Writeup

> 赛事：BraekerCTF 2024 | 方向：pwn | 难度：medium | 工具：pwntools

## 一句话总结

BraekerCTF 2024 — 32位 Linux shellcode: sys_read 0x18 字节 + add al,[eax] 链 + nop+write+int 0x80+jmp ecx + nop×7+sys_read 0x7f + execve /bin/sh + binary_shrink 自修改 XOR 0x42。

## 攻击链

1. vlun: sys_read(0, ecx, 0x18) + add al,[eax] + add eax,[eax] + add [eax],eax
2. _start: call vlun + xor al, 0
3. 利用: nop nop nop nop + mov eax,4 + mov ebx,1 + int 0x80 + jmp ecx
4. 高级: nop×7 + mov al,0x3 + add ecx,0x12 + mov dl,0x7f + int 0x80 + jmp ecx
5. 注入 shellcode: execve /bin///sh via pwntools shellcraft
6. binary_shrink: pop rdx + mov rax,rdx + jmp second + add rdx,0x91 + sub rax,0xe
7. mov rsi,rax + mov cl,0x56 + loop: xor [rdx],sil + xor [rdx],0x42 + inc rdx + inc rax + loop
8. 自修改代码 + XOR 0x42 还原

## 关键 payload

```
sys_read 0x18 字节 / add al [eax] / jmp ecx / nop×4 + write(1, ecx) / nop×7 + sys_read 0x7f / execve /bin/sh / binary_shrink XOR 0x42 loop 0x56
```

## 经验教训

极简 shellcode 注入常需要多次拼接;jmp ecx 是最简 shellcode 入口;自修改代码 + XOR 是 anti-disassemble 经典。

## 标签

32位 Linux、sys_read shellcode、add al [eax]、add eax [eax]、add [eax] eax、pop ecx、jmp ecx、execve /bin/sh、download.elf、vlun _start、binary_shrink XOR 0x42、self-modifying

## 参考来源

- https://www.ctfiot.com/164132.html
- 原文件：BraekerCTF_2024_Writeup.full.md
