---
title: "TamuCTF 2024 Writeup - 狼组安全社区"
category: web
tags: ["TamuCTF", "web", "php-unserialize", "sql-injection", "cbc-bitflip", "fmt-string"]
signals: ["TamuCTF 2024", "php-unserialize", "sql-injection", "cbc-bitflip", "fmt-string", "blind-shellcode", "mmap-xchg-syscall", "deserialize", "TamuCTF", "Web", "SQL", "CBC", "Pwn", "fmt"]
difficulty: medium
source: "https://www.ctfiot.com/172434.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# TamuCTF 2024 Writeup - 狼组安全社区

> 赛事：TamuCTF 2024 | 方向：web | 难度：medium

## 一句话总结

TamuCTF 2024 狼组：Web 反序列化+SQL注入+CBC翻转 + Pwn fmt+canary+sandbox 盲注 + Reverse AES 动调。

## 攻击链

1. Cereal (Web): guest 登录 → profile.php 反序列化 → User.__wakeup refresh() 二次注入
2. id 字段拼 union select sql from sqlite_master → 触发 SQL 注入
3. 4 字段 base64 序列化 Tzo0OiJVc2VyIjo0OntzOjg6InVzZXJuYW1lIjtzOjU6Imd1ZXN0IjtzOjI6ImlkIjtzOjU3OiI5OTkndW5pb24gc2VsZWN0IChzZWxlY3Qgc3FsIGZyb20gc3FsaXRlX21hc3RlciksMiwzLDQtLSAiOw==
4. admin 密码用 group_concat(password) from users 拿
5. Flipped (Web): AES-CBC 翻转字节 iv[0] = 1 ^ 0 → admin: 1
6. newiv[i] = (plain[i] ^ iv[i] ^ decode_plain[i])
7. Admin Panel (Pwn): 密码处溢出覆盖 format，%15$p 泄 canary, %17$p 泄 libc
8. 0x48 padding + canary + rbp + rdi + /bin/sh + system
9. Rift (Pwn): fmt 写 6 次改 rbp 链 → rdi_ret + /bin/sh + system
10. Confinement (Pwn): sandbox 沙箱 + shellcode 盲注 flag
11. mov rdx, {j}; xor dl, [r8-0x1290+{i}]; mov rax, 231 (exit_group); syscall → 退码不同
12. 50 字节内 for j in 32..128 爆破
13. Five (Pwn): 5 字节 read shellcode：xchg rsi,rdx; syscall 写入 mmap 区域
14. Resistant (Reverse): 加密函数动调让 AES/CBC 自动解密
15. key/iv 异或后提取数据

## 关键 payload

```
newiv[i] = plain[i] ^ iv[i] ^ decode_plain[i]
```

## 经验教训

AES-CBC IV 翻转是经典 admin 0→1 trick；sandbox 沙箱 + shellcode 时用 exit_group 退码盲注 flag 字符。

## 标签

php-unserialize、sql-injection、cbc-bitflip、fmt-string、blind-shellcode、mmap-xchg-syscall

## 参考来源

- https://www.ctfiot.com/172434.html
- 原文件：TamuCTF_2024_Writeup.full.md
