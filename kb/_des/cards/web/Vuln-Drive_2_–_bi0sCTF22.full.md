---
title: "Vuln-Drive 2 – bi0sCTF22"
category: web
tags: ["bi0sCTF 2022", "web", "smuggling_path", "http_request_split", "waf_bypass", "sqlite_sqli"]
signals: ["bi0sCTF 2022 2022", "smuggling_path", "http_request_split", "waf_bypass", "sqlite_sqli", "ssrf_internal", "flag_header_xprohacker", "file_get_contents", "custom_http_in_post", "sqli", "bi0sCTF", "Vuln-Drive", "WAF", "HTTP"]
difficulty: medium
source: "https://www.ctfiot.com/94174.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Vuln-Drive 2 – bi0sCTF22

> 赛事：bi0sCTF 2022 2022 | 方向：web | 难度：medium

## 一句话总结

bi0sCTF 2022 Vuln-Drive 2 WAF 绕过，HTTP smuggling 把含 SQL 注入的 HTTP 请求塞进 multipart 上传，绕过 waf 直达内网 app。

## 攻击链

1. docker-compose 三层架构 frontend/waf/app → view.php?file=chdir 后 file_get_contents 读文件 (txt 后缀限制) → upload path= 路径穿越 + file content 是构造的 HTTP 请求 (含 X-pro-hacker: Pro-hacker + flag: gimme + Token header) → 通过 smuggling 绕过 waf 直达 app → SQLite SQL 注入 user=a'',substr((select*from flag),{},1));-- → 盲注爆破 flag

## 关键 payload

```
X-pro-hacker: Pro-hacker + flag: gimme + Content-Type: application/x-www-form-urlencoded + user=a'',substr((select*from flag),{},1));-- + Token: 16 字符
```

## 经验教训

经典 "HTTP smuggling via POST body"：上传文件内容实际是合法 HTTP 请求，被后端 view.php 转发到内网 app，绕开 WAF 检查。

## 标签

smuggling_path、http_request_split、waf_bypass、sqlite_sqli、ssrf_internal、flag_header_xprohacker、file_get_contents、custom_http_in_post

## 参考来源

- https://www.ctfiot.com/94174.html
- 原文件：Vuln-Drive_2_–_bi0sCTF22.full.md
