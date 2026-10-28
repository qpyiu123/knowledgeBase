---
title: "DASCTF 2022 十月赛 Web 部分 Writeup"
category: web
tags: ["DASCTF", "web", "php", "pop-chain", "fine-show-sorry", "file-read"]
signals: ["DASCTF 2022", "php", "pop-chain", "fine-show-sorry", "file-read", "suid-date", "bash-reverse", "deserialize", "DASCTF", "Web", "PHP", "POP", "file", "SUID"]
difficulty: easy
source: "https://www.ctfiot.com/67573.html"
tools: ["PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DASCTF 2022 十月赛 Web 部分 Writeup

> 赛事：DASCTF 2022 | 方向：web | 难度：easy | 工具：PHP

## 一句话总结

DASCTF 2022 十月赛 Web 入门题集，5 层 PHP 反序列化 POP + file.php 源码泄露 + SUID 提权。

## 攻击链

1. 构造 sorry → show → secret_code → sorry → fine POP 链
2. fine.cmd = system
3. fine.content = 'cat /flag
4. serialize 后 base64 POST pop
5. /file.php?m=show&filename=file.php 读源
6. bash -i 反弹 shell
7. find / -perm -u=s -type f
8. date -f /hereisflag/flllll111aaagg

## 关键 payload

```
5 层 POP 链 + system 触发
```

## 经验教训

PHP 反序列化 POP 链构造的关键是"找到包含可调用方法的对象作为下一个对象的属性"。

## 标签

php、pop-chain、fine-show-sorry、file-read、suid-date、bash-reverse

## 参考来源

- https://www.ctfiot.com/67573.html
- 原文件：DASCTF2022_——十月赛_Web_部分Writeup.full.md
