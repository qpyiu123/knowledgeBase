---
title: "小 E 的管理系统"
category: web
tags: [NewStar CTF 2025, wp prose]
signals: [小 E 的管理系统]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week2/web/e-admin-system.md"
tools: []
origin: imported
origin_id: official-7c3dc0ab23379b448a41f6
origin_sha256: 8072c2dd4675810c2583641346e91e74ae286544a339475108ae0715cb6facc5
origin_event: "NewStar CTF 2025"
origin_kind: wp_prose
license: "MIT"
updated: 2026-10-23
---
# NewStar CTF 2025 / 小 E 的管理系统

> 来源：NewStar CTF 2025  |  类型：wp_prose  |  https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week2/web/e-admin-system.md

import Container from '@/components/docs/Container.vue'

# 小 E 的管理系统


本题考查基本的 SQL 注入绕过。

SQL 注入<span data-desc>（SQL Injection）</span>是一种常见的网络攻击手段，攻击者通过在输入字段或请求中注入恶意的 SQL 语句，操控数据库执行意图之外的操作。

此处由于使用了 SQL 语句拼接，导致了可以被 SQL 注入。

## fuzz

由于题目没有给源码，不知道具体过滤方式，需要 fuzz（模糊测试） 一下

发现过滤了 `['#', '--', ';',' ',"'",'"','=','/']`

以及部分函数 `/(char|hex|ascii|substr|substring|mid)\s*\(/i`

## union

对空格的过滤可以用换行符绕过，URL 编码就是 `%0a`。等号可以用 LIKE 绕过

虽然过滤了 `#` 和 `--`，但是测试发现不需要注释掉末尾语句，猜测拼接在 sql 语句最后

过滤了 `'` 和 `"`，但是测试可以发现闭合语句不需要引号

过滤了 `;` 所以不能堆叠注入

最终考虑使用 UNION 联合注入<span data-desc>（通过 UNION 将攻击者构造的查询结果与合法查询结果合并，从而获取敏感数据）</span>

## 行数

UNION 联合注入要求 union 的语句输出的行数与原本语句输出的行数一致，正常情况需要用逗号测试出行数


但是这里过滤了逗号，需要用 JOIN 来绕过


将空格替换为 `%0a`，逐一测试，当正常返回代表行数正确，最终测试出行数为 5 行


## 表

测试出行数后，需要挑选一行替换为我们需要查询的语句

我们需要先查询有哪些表。正常 SQL 查看有哪些表可以用


编码后发送


但是返回 `{"error":"database error: Unable to prepare statement: 1, no such table: information_schema.tables"}`，可以推测是 sqlite 数据库。查询 SQLite 的系统表 `sqlite_master` 即可


成功返回


## 表结构

查看表结构


返回


可以看到 sys_config 中有 config_key 以及 config_value

## flag

查看 config_value


即可获取 flag
