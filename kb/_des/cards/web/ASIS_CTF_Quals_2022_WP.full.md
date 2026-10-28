---
title: "ASIS CTF Quals 2022 WP (狼组版)"
category: web
tags: ["ASIS CTF", "web", "Python eval", "f.name泄漏", "/duck?what=f.name", "pop rdi; ret"]
signals: ["ASIS CTF 2022", "Python eval", "f.name泄漏", "/duck?what=f.name", "pop rdi; ret", "libc-puts", "/bin/sh", "0x48 padding", "mod n^3后3项", "web_unknown", "ASIS", "Quals", "eval", "name"]
difficulty: medium
source: "https://www.ctfiot.com/63407.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# ASIS CTF Quals 2022 WP (狼组版)

> 赛事：ASIS CTF 2022 | 方向：web | 难度：medium | 工具：Python

## 一句话总结

ASIS 2022 Quals 狼组复盘 — eval f.name 拿 flag + ret2libc 二次 payload + (a+1)^n mod n^3 还原 + Chaffymasking LTC 矩阵 salt 漏洞。

## 攻击链

1. Beginner ducks: /duck?what=f.name eval 触发 f.name 拿到 /flag.txt
2. Baby scan I: size=0 + data=0x48 字节 padding + pop rdi;ret + puts.got + puts.plt + main 链拿 libc
3. 二次 payload pop rdi;ret+1 跳过 ret + /bin/sh + system
4. Binned: (a+1)^n mod pubkey^3 只剩 3 项, 解出 m
5. h = (enc-1) - pubkey, c = h // pubkey // pubkey, c*2 = 中间系数
6. Chaffymasking: 选 salt 128 bit + half1 XOR half2 != 0 跳过 os.urandom 注入
7. out_1, out_2 = LTC·vec1 mod n^2, XOR 还原 flag

## 关键 payload

```
eval(f.name) / pop rdi;ret + puts.got + puts.plt / (a+1)^n mod n^3 / LTC·vec mod n^2 XOR / salt XOR half1 != 0
```

## 经验教训

Python eval 配合文件描述符 f.name 泄露路径;mod n^3 后 (a+1)^n 剩 3 项 (m + m(m-1)/2 * pubkey + m(m-1)(m-2)/6 * pubkey^2);Chaffymasking 的 XOR half1!=0 漏洞可绕 os.urandom。

## 标签

Python eval、f.name泄漏、/duck?what=f.name、pop rdi; ret、libc-puts、/bin/sh、0x48 padding、mod n^3后3项、Binned a^1 a^2 a^3、Chaffymasking LTC矩阵、half1 XOR half2 salt 128bit

## 参考来源

- https://www.ctfiot.com/63407.html
- 原文件：ASIS_CTF_Quals_2022_WP.full.md
