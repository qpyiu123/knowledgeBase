---
title: "【WP】破阵阁・网安淬锋公开赛题目全解"
category: web
tags: ["破阵阁", "web", "intruder-bruteforce", "sqlmap-dump", "path-traversal", "JWT-alg-none"]
signals: ["破阵阁 2025", "intruder-bruteforce", "sqlmap-dump", "path-traversal", "JWT-alg-none", "nacos-command-injection", "crontab-crash-tomcat", "sqlmap-search-param", "Joomla-3.7-CVE-2017-8917", "sqli", "SQL", "JWT", "alg", "none"]
difficulty: easy
source: "https://www.ctfiot.com/295990.html"
tools: ["Wireshark", "sqlmap"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【WP】破阵阁・网安淬锋公开赛题目全解

> 赛事：破阵阁 2025 | 方向：web | 难度：easy | 工具：Wireshark、sqlmap

## 一句话总结

破阵阁・网安淬锋公开赛 10 道题全解 WP，涵盖 SQL 注入/路径穿越/JWT alg=none/命令注入/Webshell 还原/渗透。

## 攻击链

1. 1. 最简单签到 intruder id 遍历 47/2. 游戏营销 api.php 成绩提交接口/3. 最简单 Web id sql 注入 sqlmap dump/4. 安全牛 ERP 目录穿越 flag.html/5. 身份鉴权 JWT alg=none 绕签名/6. 诡异命令执行 第 250 个流 nacos 注入/7. webshell 被删除 grep -r "flag{" 整盘搜/8. 暗影迷踪 crontab -r 清空 + 删除 /var/crash/tomcat/9. 激进的开发者 search sql 注入 superadmin/1Qaz2Wsx + 文件上传/10. 小小的挑战 Joomla 3.7 CVE-2017-8917 SQL 注入

## 关键 payload

```
flag uuids  intruder id=47  sqlmap search  superadmin/1Qaz2Wsx
```

## 经验教训

JWT alg=none 是经典签名绕过；Joomla 3.7.0 CVE-2017-8917 SQL 注入；nacos 注入看 Wireshark 第 250 流；crontab -r + 删 crash 是应急响应清痕迹。

## 标签

intruder-bruteforce、sqlmap-dump、path-traversal、JWT-alg-none、nacos-command-injection、crontab-crash-tomcat、sqlmap-search-param、Joomla-3.7-CVE-2017-8917

## 参考来源

- https://www.ctfiot.com/295990.html
- 原文件：【WP】破阵阁・网安淬锋公开赛题目全解.full.md
