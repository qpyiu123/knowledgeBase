---
title: "HackTheBox Stocker WriteUp"
category: web
tags: ["HackTheBox Stocker", "web", "htb", "pentest", "nmap", "nginx"]
signals: ["HackTheBox Stocker 2023", "htb", "pentest", "nmap", "nginx", "ffuf", "vhost-fuzz", "subdomain", "dev", "web_unknown", "HTB", "Stocker", "vhost", "stocker"]
difficulty: medium
source: "https://www.ctfiot.com/122470.html"
tools: ["ffuf", "nmap"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# HackTheBox Stocker WriteUp

> 赛事：HackTheBox Stocker 2023 | 方向：web | 难度：medium | 工具：ffuf、nmap

## 一句话总结

HTB Stocker：ffuf vhost爆破dev.stocker.htb子域

## 攻击链

1. nmap: 22/80端口, nginx 1.18.0
2. ffuf 子域名爆破
3. 字典: /usr/share/wordlists/seclists/Discovery/DNS/namelist.txt
4. ffuf -w ... -H "Host: FUZZ.stocker.htb" -u http://10.10.11.196 -fs 178
5. 发现 dev.stocker.htb 子域
6. 访问 dev.stocker.htb 获取管理面板
7. SSH登录angoose
8. sudo -l 提权

## 关键 payload

```
dev.stocker.htb
```

## 经验教训

Vhost爆破是发现子域名隐藏功能的高效方法

## 标签

htb、pentest、nmap、nginx、ffuf、vhost-fuzz、subdomain、dev

## 参考来源

- https://www.ctfiot.com/122470.html
- 原文件：HackTheBox_Stocker_WriteUp.full.md
