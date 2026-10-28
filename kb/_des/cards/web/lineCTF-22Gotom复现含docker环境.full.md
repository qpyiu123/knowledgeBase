---
title: "lineCTF-22 Gotom 复现含 docker 环境"
category: web
tags: ["lineCTF", "web", "golang", "jwt", "text-template", "ssti"]
signals: ["lineCTF 2022", "golang", "jwt", "text-template", "ssti", "misconf", "admin-flag", "clear-account", "auth_bypass", "lineCTF", "Gotom", "JWT", "text", "template"]
difficulty: medium
source: "https://www.ctfiot.com/167267.html"
tools: ["Go"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# lineCTF-22 Gotom 复现含 docker 环境

> 赛事：lineCTF 2022 | 方向：web | 难度：medium | 工具：Go

## 一句话总结

lineCTF 2022 Gotom 题复现：Go JWT + text/template 注入。

## 攻击链

1. /auth 登录获取 JWT
2. /regist 注册新用户
3. /flag X-Token + is_admin=true 返回 flag
4. JWT 伪造需要 secret_key
5. SECRET_KEY 环境变量可读
6. text/template 渲染 acc.id 用户控制
7. template 注入 {{.}}
8. clear_account 重置 acc 切片

## 关键 payload

```
Go template SSTI + JWT secret 伪造
```

## 经验教训

Go text/template 也是 SSTI 攻击面，{{.}} 直接输出上下文对象。

## 标签

golang、jwt、text-template、ssti、misconf、admin-flag、clear-account

## 参考来源

- https://www.ctfiot.com/167267.html
- 原文件：lineCTF-22Gotom复现含docker环境.full.md
