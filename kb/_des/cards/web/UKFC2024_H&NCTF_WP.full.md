---
title: "UKFC2024 H&NCTF WP"
category: web
tags: ["H&NCTF", "web", "aes-cbc-bitflip", "rc4-vbscript", "format-string-canary", "canary-overflow"]
signals: ["H&NCTF 2024", "aes-cbc-bitflip", "rc4-vbscript", "format-string-canary", "canary-overflow", "ret2libc", "i386-pwn", "uxntal-bagua", "unicode-stego", "crypto_symmetric", "NCTF", "flipped", "AES-CBC", "ELF"]
difficulty: medium
source: "https://www.ctfiot.com/181342.html"
tools: ["Python", "Z3"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# UKFC2024 H&NCTF WP

> 赛事：H&NCTF 2024 | 方向：web | 难度：medium | 工具：Python、Z3

## 一句话总结

H&NCTF 2024：flipped AES-CBC 翻转 + ELF 自修改还原 + VBScript RC4 + 32-bit ret2libc + 八卦符转义。

## 攻击链

1. flipped (Web): AES-CBC session 翻转 admin: 0 → 1
2. 0' index ^= 1 → 改 cookie session
3. /read?filename=/proc/1/cpuset LFI
4. subprocess.getoutput('env') 弹命令
5. tamuctf2024: ELF 自修改 0x8d35/0x0c34 标识 + 0x35 段 + XOR 还原
6. 远程交互 127 次解出所有字节
7. VBScript RC4 Initialize + Myfunc (certutil -hashfile MD5) 还原 key (6 字符)
8. EnCrypt 密文 0x35f7d3... → flag 44 字符
9. Caesar 偏移 K=10, K=5 解
10. idea (Pwn): %7$p 泄 canary + puts_plt 泄 libc → ret2libc
11. 32-bit i386 + 0x20 padding + canary + 3 aaa + system + /bin/sh
12. what (Pwn): 0x420 chunk + 16 个 0xfff + free 触发 unsorted bin 残余
13. __free_hook - 0x23 - 0x10 leak
14. __free_hook = system
15. ez_pwn: 43 字节栈溢出 + 1 字节 canary bypass
16. z3 RSA: x*y=n, x+y=n-phi+1 → 求 x, y
17. 八卦符 (乾坤兑离震巽坎艮) → 0-7 数字 → 3 位一组八进制 → chr
18. 字符串隐写: 0x200B 0xFEFF Unicode 隐藏字符
19. Python subprocess + sh 弹命令

## 关键 payload

```
c[default_session.index("0")] ^= 1  # 翻转 admin 字节
```

## 经验教训

32-bit PWN 32-bit canary 通过一个负数 -32 长度 leak 后爆破是经典手法。

## 标签

aes-cbc-bitflip、rc4-vbscript、format-string-canary、canary-overflow、ret2libc、i386-pwn、uxntal-bagua、unicode-stego

## 参考来源

- https://www.ctfiot.com/181342.html
- 原文件：UKFC2024_H&NCTF_WP.full.md
