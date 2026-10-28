---
title: "Apiculture 1 write-up - 针对 API 的渗透测试"
category: web
tags: ["Apiculture", "web", "API penetration", "vendorID leakage", "swagger.json", "/api/products"]
signals: ["Apiculture 2022", "API penetration", "vendorID leakage", "swagger.json", "/api/products", "/api/vendors/{id} IDOR", "/api/flags/ Basic Auth", "SHA1 弱密码", "57332 admin", "web_unknown", "Apiculture", "API", "api", "products"]
difficulty: easy
source: "https://www.ctfiot.com/107011.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Apiculture 1 write-up - 针对 API 的渗透测试

> 赛事：Apiculture 2022 | 方向：web | 难度：easy

## 一句话总结

Apiculture 1 API 渗透 — /api/products 泄露 vendorID + /api/swagger.json 找 /api/flags/ + /api/vendors/{id} IDOR 试 57332 admin + SHA1 弱密码 abeille 登录拿 flag。

## 攻击链

1. /api/products/ 端点泄露未使用 vendorID 字段
2. 看到所有产品 vendorID=57336
3. /api/swagger.json 发现 /api/flags/ (Basic Auth 保护)
4. /api/vendors/57336 拿到 SHA1 密码哈希
5. 谷歌 SHA1 哈希得弱密码
6. 但 57336 用户无法访问 /api/flags/
7. IDOR: /api/vendors/57332 试错发现 admin
8. 57332 同样是 SHA1 弱密码 (abeille)
9. 用 admin 身份 + abeille 登录 /api/flags/ 拿 flag

## 关键 payload

```
/api/products vendorID 57336 泄露 / /api/swagger.json 找 /api/flags/ / /api/vendors/57336 SHA1 弱密码 / IDOR 试错找 57332 admin / SHA1 弱密码 abeille / Basic Auth 登录
```

## 经验教训

API 渗透标准链: 端点泄露字段 → swagger.json 找受保护端点 → IDOR 试错 admin → 弱密码爆破;vendorID 是常见 IDOR 字段。

## 标签

API penetration、vendorID leakage、swagger.json、/api/products、/api/vendors/{id} IDOR、/api/flags/ Basic Auth、SHA1 弱密码、57332 admin、abeille密码

## 参考来源

- https://www.ctfiot.com/107011.html
- 原文件：Apiculture_1_write-up-针对API的渗透测试.full.md
