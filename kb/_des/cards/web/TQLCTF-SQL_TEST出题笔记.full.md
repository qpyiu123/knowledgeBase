---
title: "TQLCTF/SQL_TEST 出题笔记"
category: web
tags: ["TQLCTF", "web", "mysqli_options", "MYSQLI_INIT_COMMAND", "time-based blind", "secure_file_priv"]
signals: ["TQLCTF null", "mysqli_options", "MYSQLI_INIT_COMMAND", "time-based blind", "secure_file_priv", "INTO DUMPFILE", "Symfony", "Doctrine", "RedisProxy", "sqli", "phar", "deserialize", "rce", "INTO"]
difficulty: medium
source: "https://www.ctfiot.com/27107.html"
tools: ["PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# TQLCTF/SQL_TEST 出题笔记

> 赛事：TQLCTF null | 方向：web | 难度：medium | 工具：PHP

## 一句话总结

MYSQLI_INIT_COMMAND 注入 + secure_file_priv 盲注 + INTO DUMPFILE 写 phar + Doctrine 反序列化链 RCE

## 攻击链

1. 审 Symfony 控制器：/test 路由接受 key + value 两个 GET 参数
2. mysqli_options($con, $key, $value) 任意调用（key 是数字 option，value 是 string）
3. 关键 option: MYSQLI_INIT_COMMAND=3 → 发送 SQL 命令作为连接初始化
4. 强制禁用 LOCAL INFILE，再用 MYSQLI_OPT_LOCAL_INFILE=0
5. 但 MYSQLI_INIT_COMMAND 走的是 init_command 通道，不受 LOCAL INFILE 限制
6. 用 time-based blind 注 secure_file_priv 路径（select if((select substr(@@global.secure_file_priv, i, 1)='x'), sleep(2), 1)）
7. 得到 secure_file_priv 路径（如 /tmp/xxx/）
8. 用 INTO DUMPFILE 把 phar 写入该路径（select 0x<hex> into dumpfile '/tmp/xxx/random.phar'）
9. 用 phar://random.phar 触发 phar 反序列化
10. Symfony Doctrine 反序列化链：RedisProxy.__call → Dumper.__invoke → system()
11. 命令执行拿 flag

## 关键 payload

```
mysqli_options($con, MYSQLI_INIT_COMMAND, 'select 0x<phar_hex> into dumpfile "/tmp/xxx/random.phar"')
```

## 经验教训

PHP mysqli_options 接受任意 option 编号 + 任意 string value；MYSQLI_INIT_COMMAND 通道不受 LOCAL INFILE 禁用影响；Symfony Doctrine 反序列化链通过 RedisProxy.__call 触发

## 标签

mysqli_options、MYSQLI_INIT_COMMAND、time-based blind、secure_file_priv、INTO DUMPFILE、Symfony、Doctrine、RedisProxy、Dumper、phar 触发链

## 参考来源

- https://www.ctfiot.com/27107.html
- 原文件：TQLCTF-SQL_TEST出题笔记.full.md
