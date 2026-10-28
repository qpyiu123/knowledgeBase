---
title: "SHCTF-2024-Week2 官方WP"
category: web
tags: ["SHCTF", "web", "shctf2024-week2", "jwt-cracker", "python-pickle", "mersenne-twister"]
signals: ["SHCTF 2024", "shctf2024-week2", "jwt-cracker", "python-pickle", "mersenne-twister", "hash-length-extension", "flask-session-forge", "web_unknown", "ctfiot", "Week2", "Crypto", "JWT", "Pickle", "Flask"]
difficulty: medium
source: "https://www.ctfiot.com/210419.html"
tools: ["Flask", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# SHCTF-2024-Week2 官方WP

> 赛事：SHCTF 2024 | 方向：web | 难度：medium | 工具：Flask、Python

## 一句话总结

看雪 ctfiot 招新 Week2 完整 WP，涵盖 Crypto/JWT/Pickle/Flask/Pwn/Reverse 多类基础题。

## 攻击链

1. 从两端向中间搜索 pxorq 重建 p/q 二进制
2. QRazyBox 修复受损二维码 + Reed-Solomon 解码
3. 自定义 base64 字母表 (ABCDjp0yIJKL...2345678Y+/) 解密
4. jwt-cracker 6 位弱口令爆破 HS256 密钥 222333
5. 改 jwt payload role: user → admin
6. pickle find_class() 黑名单绕过 posix.system
7. random.seed(1000000-9999999) 爆破 seed 预测 next
8. 自实现 MD5 长度扩展攻击 + SECRET_KEY=Th1s_is_5ecr3t_k3y 伪造 session
9. flask-session-cookie-manager 伪造 is_admin: 1
10. union select secretdata from ctf.flag SQL 注入
11. seccomp 59 号 + open/read/write 链式 sys_open
12. 0xBB / 0x97 字节溢出一字节改 ret_addr
13. picoGadget 工具链泄露 libc → ret2libc
14. 0x100 字节异或 shellcode

## 关键 payload

```
-1") union select 1,scretdata from ctf.flag
```

## 经验教训

当 pickle 显式 import 黑名单时，要想到 posix.system 这类「带前缀的等价模块」常被遗忘在黑名单。

## 标签

shctf2024-week2、jwt-cracker、python-pickle、mersenne-twister、hash-length-extension、flask-session-forge

## 参考来源

- https://www.ctfiot.com/210419.html
- 原文件：SHCTF-2024-Week2_官方WP.full.md
