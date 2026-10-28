---
title: "bi0sCTF 2022 Writeup by r3kapig"
category: pwn
tags: ["bi0sCTF", "pwn", "r3kapig", "menu", "static-key", "encrypt-injection"]
signals: ["bi0sCTF 2022", "r3kapig", "menu", "static-key", "encrypt-injection", "rop", "cross-challenge", "reverse", "bi0sCTF", "PWN", "ROP", "add", "delete", "show"]
difficulty: hard
source: "https://www.ctfiot.com/93593.html"
tools: ["ROP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# bi0sCTF 2022 Writeup by r3kapig

> 赛事：bi0sCTF 2022 | 方向：pwn | 难度：hard | 工具：ROP

## 一句话总结

bi0sCTF 2022 r3kapig 战队多题 WP，菜单类 PWN 注入与跨题 ROP 链构造。

## 攻击链

1. 逆向菜单 1-5 选项 add/delete/show/edit/encrypt
2. 发现静态密钥 2111485077978050
3. encrypt(0, decrypt(payload)) 触发注入
4. 构造 ROP pop_rdi+pop_rax+syscall
5. execve /bin/sh

## 关键 payload

```
静态 AES key + encrypt-decrypt 注入链
```

## 经验教训

CTF 题目间可能存在 attack 复用：encrypt 题目拿到的 oracle 可注入其他题；RCE 链要从前置题"借"密钥。

## 标签

r3kapig、menu、static-key、encrypt-injection、rop、cross-challenge

## 参考来源

- https://www.ctfiot.com/93593.html
- 原文件：bi0sCTF2022_Writeup_by_r3kapig.full.md
