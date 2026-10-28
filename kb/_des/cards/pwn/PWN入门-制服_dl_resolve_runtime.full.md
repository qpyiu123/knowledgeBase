---
title: "PWN入门 - 制服 _dl_runtime_resolve"
category: pwn
tags: ["看雪论坛 ctfiot 系列", "pwn", "pwn", "教程", "glibc", "dynamic-linking"]
signals: ["看雪论坛 ctfiot 系列 2024", "pwn", "教程", "glibc", "dynamic-linking", "_dl_runtime_resolve", "_dl_fixup", "lazy-binding", "pwn_unknown", "dl_runtime_resolve_fxsave", "PLT", "dl_fixup", "ELF", "plt"]
difficulty: hard
source: "https://www.ctfiot.com/206959.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# PWN入门 - 制服 _dl_runtime_resolve

> 赛事：看雪论坛 ctfiot 系列 2024 | 方向：pwn | 难度：hard

## 一句话总结

深度逆向 glibc 动态链接器 _dl_runtime_resolve_fxsave 内部，从 PLT 跳转到 _dl_fixup 查找符号的完整调用链。

## 攻击链

1. 介绍 ELF 动态链接的两类时机：启动期 vs 调用期（延迟绑定）
2. 详解 .plt/.plt.sec/.got/.got.plt/.rela.plt/.dynsym/.dynstr 协同工作
3. PLT jmp *GOT_ENTRY 触发首次 push reloc_index + jmp _dl_runtime_resolve
4. _dl_runtime_resolve_fxsave 序言 push rbx / mov rsp,rbx / and 0x10 对齐 / sub 0x240
5. 保存 6 个参数寄存器 (rax/rcx/rdx/rsi/rdi/r8/r9) 到栈
6. fxsave 0x40(%rsp) 保存 FPU/MMX/SSE 上下文
7. 从 rbx 取 link_map+reloc_index 调 _dl_fixup
8. _dl_fixup 解析 link_map[0x70] 取 SYMTAB，l_info[] 检索
9. version check + strcmp 匹配 GLIBC_x.y
10. 返回值 r11，最后 jmp *r11 真正调到目标函数

## 关键 payload

```
A=arch JT=0x00 ... 0006: 0x15 0x00 0x0d 0xc000003e (BPF 过滤 read/write/open)
```

## 经验教训

GOT[plt] 首次未解析时跳 _dl_runtime_resolve 触发解析；解析完成后 GOT 写入真实函数地址；_dl_fixup 通过 link_map[0x70] 取 SYMTAB 再用 strcmp 验证 GLIBC 版本号。

## 标签

pwn、教程、glibc、dynamic-linking、_dl_runtime_resolve、_dl_fixup、lazy-binding

## 参考来源

- https://www.ctfiot.com/206959.html
- 原文件：PWN入门-制服_dl_resolve_runtime.full.md
