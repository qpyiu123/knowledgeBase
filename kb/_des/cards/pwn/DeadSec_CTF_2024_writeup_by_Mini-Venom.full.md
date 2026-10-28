---
title: "DeadSec CTF 2024 writeup by Mini-Venom"
category: pwn
tags: ["DeadSec CTF 2024", "pwn", "pwn", "user-management", "fmt-string", "three-write"]
signals: ["DeadSec CTF 2024 2024", "pwn", "user-management", "fmt-string", "three-write", "libc-leak", "privilege", "fmt_string", "DeadSec", "CTF", "GOT", "root_login", "add_user", "login"]
difficulty: hard
source: "https://www.ctfiot.com/196213.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DeadSec CTF 2024 writeup by Mini-Venom

> 赛事：DeadSec CTF 2024 2024 | 方向：pwn | 难度：hard

## 一句话总结

DeadSec CTF 2024 user-management fmt-string三段写GOT表

## 攻击链

1. 菜单 1=root_login/2=add_user/3=login/4=logout/5=vuln
2. root_login: manage users\x00\x00\x00\x00 / MrAlphaQ / \x00\x00\x00\x00\x00\x00\x00\x00
3. add_user: name/passwd=''0rb1t''/desc
4. vuln: 触发格式化字符串
5. generate_fmt三段写入任意地址
6. %hn按2字节写3次→6字节全地址
7. 改GOT表为system触发getshell

## 关键 payload

```
payload = b''%c''*14 + b''%''+str(d1-14)+b''c%hn'' + ...  # 3段%hn
```

## 经验教训

%hn可按2字节写入，3次%hn覆盖6字节地址

## 标签

pwn、user-management、fmt-string、three-write、libc-leak、privilege

## 参考来源

- https://www.ctfiot.com/196213.html
- 原文件：DeadSec_CTF_2024_writeup_by_Mini-Venom.full.md
