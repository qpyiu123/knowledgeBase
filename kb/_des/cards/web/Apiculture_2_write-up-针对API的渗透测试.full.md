---
title: "Apiculture 2 - API 渗透测试 write-up"
category: web
tags: ["Apiculture (养蜂业 API 挑战)", "web", "API", "swagger.json", "/API/v2/", "OSINT"]
signals: ["Apiculture (养蜂业 API 挑战) 2023", "API", "swagger.json", "/API/v2/", "OSINT", "DOCX-metadata", "sitemap.xml", "captcha-math", "4-digit-PIN", "auth_bypass", "web_unknown", "DOCX", "PIN", "swagger"]
difficulty: medium
source: "https://www.ctfiot.com/107150.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Apiculture 2 - API 渗透测试 write-up

> 赛事：Apiculture (养蜂业 API 挑战) 2023 | 方向：web | 难度：medium

## 一句话总结

旧版 API + DOCX 元数据 OSINT + 4 位 PIN 爆破

## 攻击链

1. /API/v4/swagger.json 暴露 /users/reset 邮件密码重置
2. 降级到 /API/v2/swagger.json 旧版 API
3. v2 三阶段重置：/users/reset1 拿 aes256Payload + 算术验证码
4. v2 /users/reset2 提交答案 + payload 拿新 payload
5. v2 /users/reset3 提交 payload + 4 位 SMS PIN 暴力 10000 次
6. OSINT：sitemap.xml → marketing_legacy/giftcard.pdf → 父目录 DOCX/PPTX 元数据
7. DOCX 作者 'Winny BÄRENJUNGEN' → LinkedIn 找 CEO 邮箱
8. 重置 CEO 邮箱 winnybarenjungen@gmail.com 拿 flag

## 关键 payload

```
POST /API/v2/users/reset3 { aes256Payload, sms4digits: 0000-9999 }
```

## 经验教训

API 弃用版本不删是常见漏洞；DOCX/PPTX 元数据泄露作者；4 位 PIN 暴力无防是经典

## 标签

API、swagger.json、/API/v2/、OSINT、DOCX-metadata、sitemap.xml、captcha-math、4-digit-PIN、brute-force、deprecated-API

## 参考来源

- https://www.ctfiot.com/107150.html
- 原文件：Apiculture_2_write-up-针对API的渗透测试.full.md
