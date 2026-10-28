---
title: "Intigriti CTF 2023 Writeup [WEB]"
category: web
tags: ["Intigriti CTF 2023", "web", "WebSocket_SQL盲注", "JWT密钥爆破", "Nodejs原型链污染", "puppeteer_path注入"]
signals: ["Intigriti CTF 2023 2023", "WebSocket_SQL盲注", "JWT密钥爆破", "Nodejs原型链污染", "puppeteer_path注入", "isAdmin权限绕过", "web_unknown", "Intigriti", "CTF", "WebSocket", "JWT", "puppeteer", "path", "and"]
difficulty: hard
source: "https://www.ctfiot.com/146540.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Intigriti CTF 2023 Writeup [WEB]

> 赛事：Intigriti CTF 2023 2023 | 方向：web | 难度：hard

## 一句话总结

Intigriti CTF 2023：WebSocket 盲注+JWT 爆破+原型链污染+puppeteer path 注入。

## 攻击链

1. WebSocket 注入：{"id":"11 and (SELECT substr(description,1,1)='A')"}
2. websockets sync client 爆破 flag 字符
3. JWT 爆破：jwt2john + rockyou
4. Nodejs 原型链污染：污染 userData 写 isAdmin: true
5. puppeteer path 注入：userOptions.path=/app/data/test.json 写恶意 JSON
6. 写 {username, firstName, lastName, spotifyTrackCode, isAdmin: true} 覆盖 isAdmin
7. 访问 /admin 路由拿 flag

## 关键 payload

```
isAdmin: true 写 userData
```

## 经验教训

puppeteer page.pdf() 的 path 选项可控可写文件；JSON 写入可污染 isAdmin 字段。

## 标签

WebSocket_SQL盲注、JWT密钥爆破、Nodejs原型链污染、puppeteer_path注入、isAdmin权限绕过

## 参考来源

- https://www.ctfiot.com/146540.html
- 原文件：Intigriti_CTF_2023_Writeup_[WEB].full.md
