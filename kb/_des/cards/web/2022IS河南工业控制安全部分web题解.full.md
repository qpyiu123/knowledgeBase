---
title: "2022 IS 河南工业控制安全部分 Web 题解"
category: web
tags: ["IS河南工控安全", "web", "SQL注入", "XXE", "JSON弱类型", "array_search"]
signals: ["IS河南工控安全 2022", "SQL注入", "XXE", "JSON弱类型", "array_search", "load_file", "二次注入", "信息泄露", "sqli", "Web", "JSON", "SQL", "select", "selselectect"]
difficulty: easy
source: "https://www.ctfiot.com/90304.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 IS 河南工业控制安全部分 Web 题解

> 赛事：IS河南工控安全 2022 | 方向：web | 难度：easy

## 一句话总结

4 道 Web：二次注入 + 经典 XXE + JSON array_search 弱类型 + load_file 非预期。

## 攻击链

1. 单引号闭合确认 SQL 注入
2. 绕过 select 过滤用 selselectect + unioN 大小写混写
3. order by 判断列数为 3
4. 联合查询 information_schema 拿 security 库所有表
5. load_file(/var/www/html/index.php) 读源码发现非预期
6. load_file(/flag) 直拿根目录 flag
7. 经典 XXE 协议流向 doLogin.php 读 /flag
8. JSON year=2022a 弱类型绕过 int 比较

## 关键 payload

```
union/**/seselectlect/**/1,load_file("/flag"),3
```

## 经验教训

SQL 注入过滤 select 可用 selselectect 大小写混写；JSON 弱类型是 array_search 经典坑。

## 标签

SQL注入、XXE、JSON弱类型、array_search、load_file、二次注入、信息泄露

## 参考来源

- https://www.ctfiot.com/90304.html
- 原文件：2022IS河南工业控制安全部分web题解.full.md
