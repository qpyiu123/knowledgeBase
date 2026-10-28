---
title: "【Hack The Box】Sandworm【Writeup】"
category: web
tags: ["HackTheBox", "web", "rustscan", "nmap", "dirsearch", "ffuf"]
signals: ["HackTheBox 2023", "rustscan", "nmap", "dirsearch", "ffuf", "Flask-login", "JWT-forge", "CVE-2023-25577", "radius-protocol", "auth_bypass", "Hack", "Box", "Sandworm", "Flask"]
difficulty: medium
source: "https://www.ctfiot.com/146323.html"
tools: ["Dirsearch", "Flask", "ffuf", "nmap"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【Hack The Box】Sandworm【Writeup】

> 赛事：HackTheBox 2023 | 方向：web | 难度：medium | 工具：Dirsearch、Flask、ffuf、nmap

## 一句话总结

Hack The Box Sandworm 中等题，Flask Web + JWT 伪造 + RADIUS 协议深度利用链。

## 攻击链

1. rustscan 22/80/443/dirsearch 找 /admin /login /guide/ffuf 子目录爆破/Flask 登录后端 JWT forge + CVE-2023-25577 长度扩展/send crafted RADIUS packet

## 关键 payload

```
ssa.htb  Flask  PyJWT  RADIUS protocol
```

## 经验教训

dirsearch 找 admin/login/logout 路由；ffuf 高并发子目录爆破；Flask + PyJWT 是 HTB 常见栈；CVE-2023-25577 是 PyJWT 长扩展漏洞；RADIUS 协议走 UDP 1812。

## 标签

rustscan、nmap、dirsearch、ffuf、Flask-login、JWT-forge、CVE-2023-25577、radius-protocol、PyJWT

## 参考来源

- https://www.ctfiot.com/146323.html
- 原文件：【Hack_The_Box】Sandworm【Writeup】.full.md
