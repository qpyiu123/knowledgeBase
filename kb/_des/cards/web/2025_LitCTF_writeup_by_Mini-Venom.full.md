---
title: "2025 LitCTF writeup by Mini-Venom（NestJS 爆破 + 多重宇宙日记原型链污染 + 星愿信箱 SSTI）"
category: web
tags: ["2025 LitCTF", "web", "LitCTF nest_js 爆破 admin:password", "星愿信箱 {{ 过滤 SSTI", "多重宇宙日记 settings update JSON 解析", "/api/profile/update POST 任意 settings 字段"]
signals: ["2025 LitCTF 2025", "LitCTF nest_js 爆破 admin:password", "星愿信箱 {{ 过滤 SSTI", "多重宇宙日记 settings update JSON 解析", "/api/profile/update POST 任意 settings 字段", "settingsPayload 构造原型链污染", "升级 isAdmin=true", "web_unknown", "ssti", "deserialize", "auth_bypass", "LitCTF", "Web", "NestJS"]
difficulty: medium
source: "https://www.ctfiot.com/250466.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2025 LitCTF writeup by Mini-Venom（NestJS 爆破 + 多重宇宙日记原型链污染 + 星愿信箱 SSTI）

> 赛事：2025 LitCTF 2025 | 方向：web | 难度：medium

## 一句话总结

2025 LitCTF Web 三题：NestJS admin 弱密码爆破 + SSTI 绕 {{ 过滤 + 多重宇宙日记 settings JSON 注入 isAdmin=true 提权。

## 攻击链

1. nest_js: admin/password 爆破登入即得 flag
2. 星愿信箱: 过滤 {{ 的 SSTI，需绕括号/下划线
3. 多重宇宙日记: 注册 a/a 登入 → 个人资料源代码 → /api/profile/update
4. 构造 JSON {"settings": {"theme": ..., "isAdmin": true, ...}} 注入管理员
5. 设置 isAdmin=true 后 page reload 看导航栏 admin 菜单 → 拿 flag

## 关键 payload

```
settingsPayload.isAdmin = true → setTimeout(reload, 1000) → page reload 拿 flag
```

## 经验教训

settings 类 JSON 接口常见原型链污染：把 admin 权限字段注入到 settings 后端会被 merge 到 user 对象 → 提权；SSTI 过滤 `{{` 时可考虑 `${ }` 或 `{% %}` 或 `#{ }`。

## 标签

LitCTF nest_js 爆破 admin:password、星愿信箱 {{ 过滤 SSTI、多重宇宙日记 settings update JSON 解析、/api/profile/update POST 任意 settings 字段、settingsPayload 构造原型链污染、升级 isAdmin=true

## 参考来源

- https://www.ctfiot.com/250466.html
- 原文件：2025_LitCTF_writeup_by_Mini-Venom.full.md
