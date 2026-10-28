---
title: "春秋杯 2022/sql_debug"
category: web
tags: ["春秋杯", "web", "Nette", "PHP", "PDO", "pgsqlCopyFromFile"]
signals: ["春秋杯 2022", "Nette", "PHP", "PDO", "pgsqlCopyFromFile", "phar", "dsn_from_uri", "deserialize", "rce", "shell", "install", "php", "pdo"]
difficulty: medium
source: "https://www.ctfiot.com/39732.html"
tools: ["PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 春秋杯 2022/sql_debug

> 赛事：春秋杯 2022 | 方向：web | 难度：medium | 工具：PHP

## 一句话总结

PDO dsn_from_uri 触发 phar 反序列化拿 shell

## 攻击链

1. Nette 框架 install.php 可改数据库配置
2. 数据库用 PDO 连接，找 PDO 内部 phar 触发点
3. 发现 pdo pgsqlCopyFromFile 函数可触发 phar
4. 搜 PHP 源码找 phar 反序列化入口函数 dsn_from_uri
5. 构造 PDO dsn="uri:phar://phar.phar/..." 触发 phar 反序列化
6. 挖 Nette POP 链子写入 install.lock
7. 打 Phar 拿 shell

## 关键 payload

```
new PDO("uri:phar://phar.phar/mysql:host=localhost;dbname=test", $user, $pass)
```

## 经验教训

PHP PDO 的 pgsqlCopyFromFile、dsn_from_uri 等内部函数可作为 phar 反序列化触发点

## 标签

Nette、PHP、PDO、pgsqlCopyFromFile、phar、dsn_from_uri

## 参考来源

- https://www.ctfiot.com/39732.html
- 原文件：2022春秋杯联赛_传说殿堂赛道_sql_debug题目解析.full.md
