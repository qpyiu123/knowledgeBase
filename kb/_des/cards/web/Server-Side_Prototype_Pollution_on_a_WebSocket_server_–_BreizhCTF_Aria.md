---
title: "Server-Side Prototype Pollution on a WebSocket server – BreizhCTF Ariane Chat"
category: web
tags: ["BreizhCTF", "web", "sspp", "socket-io", "nestjs", "prototype-pollution"]
signals: ["BreizhCTF 2023", "sspp", "socket-io", "nestjs", "prototype-pollution", "isadmin", "bot-client", "web_unknown", "BreizhCTF", "Ariane", "Chat", "NestJS", "socket", "SSPP"]
difficulty: medium
source: "https://www.ctfiot.com/102251.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Server-Side Prototype Pollution on a WebSocket server – BreizhCTF Ariane Chat

> 赛事：BreizhCTF 2023 | 方向：web | 难度：medium

## 一句话总结

BreizhCTF 2023 Ariane Chat：NestJS + socket.io 服务端原型污染 (SSPP) 提权为 admin。

## 攻击链

1. NestJS + socket.io 8888 WebSocket
2. loginAsHuman 创 Client 普通用户
3. loginAsAdmin 注释掉密码验证但有 client.isAdmin
4. 注释看 Admin 验证：if (client.isAdmin) socket.emit('onmessage', 'Welcome ...')
5. getCanceledPeople() 中 list[username][message] = reason 经典 SSPP
6. bot 客户端用 extraHeaders x-forwarded-for: 127.0.0.1
7. bot 调 reportClient(reason='isAdmin') 触发 client[reason] = 'suspicious
8. suspicious' 是字符串 → truthy → if (client.isAdmin) 走 if 分支
9. human 调 getBanList 触发 banClient → list[__proto__][isAdmin] = 'true
10. 全局 Object.prototype.isAdmin 污染
11. flagUser.emit('loginAsAdmin', {username, password}) → BZHCTF{...}

## 关键 payload

```
banClient({message: ''isAdmin'', reason: ''true''})
```

## 经验教训

当 admin 标志在字符串 truthy 检查且 Object 原型被污染时，所有 Client 实例都自动成为 admin。

## 标签

sspp、socket-io、nestjs、prototype-pollution、isadmin、bot-client

## 参考来源

- https://www.ctfiot.com/102251.html
- 原文件：Server-Side_Prototype_Pollution_on_a_WebSocket_server_–_BreizhCTF_Ariane_Chat.full.md
