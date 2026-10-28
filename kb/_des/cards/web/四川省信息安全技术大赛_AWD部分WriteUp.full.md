---
title: "四川省信息安全技术大赛 AWD部分WriteUp"
category: web
tags: ["四川省信息安全技术大赛 AWD", "web", "AWD", "PHP代码审计", "Python Flask SSTI", "webshell查杀"]
signals: ["四川省信息安全技术大赛 AWD 2022", "AWD", "PHP代码审计", "Python Flask SSTI", "webshell查杀", "seay", "D盾", "河马", "流量分析", "web_unknown", "PHP", "SQL", "Python", "Flask"]
difficulty: medium
source: "https://www.ctfiot.com/76769.html"
tools: ["Flask", "PHP", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 四川省信息安全技术大赛 AWD部分WriteUp

> 赛事：四川省信息安全技术大赛 AWD 2022 | 方向：web | 难度：medium | 工具：Flask、PHP、Python

## 一句话总结

四川省信安 AWD 复盘: PHP 命令执行/SQL/上传修复 + Python Flask SSTI 批量攻击每轮 4000+ 分。

## 攻击链

1. 初始 7w 分, 15 分钟一轮, 一轮 100 分, 最终 22w+ 分
2. PHP 题: 整站 tar 备份 + D盾/河马 webshell 查杀 + seay 代码审计
3. 命令执行: manage_comment_del.php + Manage_rce.php 删代码修复
4. 任意 SQL: manage_sql.php TRUE→FALSE 修复
5. 文件上传: user_upload.php 加白名单
6. Python 题: Flask blog + render_template_string SSTI
7. 加固: 花括号过滤
8. 攻击: 找 /auth/reset 路由 + render_template_string 漏洞
9. 回显 flag 在 HTML 注释里
10. 批量脚本每轮打 4000+ 分

## 关键 payload

```
PHP 命令执行/SQL/上传 + Python Flask SSTI render_template_string + 批量 flag 脚本
```

## 经验教训

AWD 修复策略: 1) 删漏洞代码/修 TRUE→FALSE/加白名单; 2) webshell 查杀; 3) 备份源代码; 4) 改弱口令; 5) 看日志找他人攻击 payload; 6) 批量攻击脚本。

## 标签

AWD、PHP代码审计、Python Flask SSTI、webshell查杀、seay、D盾、河马、流量分析、render_template_string、批量攻击

## 参考来源

- https://www.ctfiot.com/76769.html
- 原文件：四川省信息安全技术大赛_AWD部分WriteUp.full.md
