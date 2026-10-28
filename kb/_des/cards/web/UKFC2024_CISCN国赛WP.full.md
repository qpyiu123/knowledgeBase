---
title: "UKFC2024 CISCN 国赛 WP (合并多个 WP)"
category: web
tags: ["UKFC2024 / CISCN 国赛", "web", "php-cms", "qrcode-ssrf", "frame-introspection", "gostack-ret2syscall"]
signals: ["UKFC2024 / CISCN 国赛 2024", "php-cms", "qrcode-ssrf", "frame-introspection", "gostack-ret2syscall", "tcache-dup", "house-of-apple", "lfsr-recursion", "vm-decompile", "rce", "UKFC2024", "CISCN", "PHP_CMS", "SSRF"]
difficulty: hard
source: "https://www.ctfiot.com/182308.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# UKFC2024 CISCN 国赛 WP (合并多个 WP)

> 赛事：UKFC2024 / CISCN 国赛 2024 | 方向：web | 难度：hard

## 一句话总结

UKFC2024 CISCN 国赛多 WP 合并：PHP_CMS 命令注入 + QR SSRF + frame 反射 + House of Apple + CryptoAPI + 魔改 TEA。

## 攻击链

1. PHP_CMS 命令注入: cmd=php+-r+system(hex2bin(...))
2. SELECT * FROM PHP_CMS.F1ag_Se3Re7 → flag
3. API qrcode thumb SSRF (requestrepo.com dnslog) → /readflag 外带
4. frame.f_back.f_back.f_back.f_globals['__builtins__'] 跨 frame 反射
5. gostack (Pwn): ret2libc 0x563720 bss + execve(/bin/sh) (6 寄存器 gadget 链)
6. orange_cat_diary: 0xfe1 错位 fake size → unsorted bin + __malloc_hook 改 one_gadget
7. EzHeap: 大块 overlap + largebin attack + setcontext SROP
8. gostack: pop rdi_5_ret 调 6 次 reg 链 execve
9. LFSR rec + CRT 多模数 + Pohlig-Hellman 解 RSA
10. VM 反编译: opcode 0x23-0x33 16 条指令表
11. Windows CryptoAPI CryptDecrypt 还原
12. 魔改 TEA delta=0x114514 还原
13. brotli 解压 dump + XOR secret 密钥
14. 字符串最长公共子序列 DP 求解
15. AES DES CBC 异或
16. rodata 嵌 shellcode 直接 VirtualAlloc + memcpy
17. QR code 字符串转 21x21 黑白图
18. numpy PCA trace 解 SCA side-channel
19. brotli + secret XOR + DP 还原 flag

## 关键 payload

```
SELECT * FROM PHP_CMS.F1ag_Se3Re7
```

## 经验教训

跨 frame 反射 (generator) 在沙箱逃逸中是强大攻击面；House of Apple 配合 setcontext+61 是 libc-2.35 主流打法。

## 标签

php-cms、qrcode-ssrf、frame-introspection、gostack-ret2syscall、tcache-dup、house-of-apple、lfsr-recursion、vm-decompile、des-cbc、aes-derive、brotli

## 参考来源

- https://www.ctfiot.com/182308.html
- 原文件：UKFC2024_CISCN国赛WP.full.md
