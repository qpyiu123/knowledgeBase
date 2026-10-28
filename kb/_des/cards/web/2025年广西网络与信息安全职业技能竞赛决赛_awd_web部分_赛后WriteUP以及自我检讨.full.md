---
title: "2025 广西网络与信息安全职业技能竞赛决赛 AWD Web 复盘（断网惨痛教训+ThinkPHP+upload+jwt）"
category: web
tags: ["2025 广西网络与信息安全职业技能竞赛", "web", "广西 2025 决赛 AWD Web", "断网环境 复盘教训", "纸质密码信封 第二张纸", "过度紧张 基础薄弱"]
signals: ["2025 广西网络与信息安全职业技能竞赛 2025", "广西 2025 决赛 AWD Web", "断网环境 复盘教训", "纸质密码信封 第二张纸", "过度紧张 基础薄弱", "PHP likeadmin/admin 默认密码", "后台任意文件上传 UploadController file()", "123.php multipart/form-data", "未授权重置管理员密码 auth.admin/edit", "web_unknown", "sqli", "auth_bypass", "upload", "AWD"]
difficulty: medium
source: "https://www.ctfiot.com/283303.html"
tools: ["PHP", "ThinkPHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2025 广西网络与信息安全职业技能竞赛决赛 AWD Web 复盘（断网惨痛教训+ThinkPHP+upload+jwt）

> 赛事：2025 广西网络与信息安全职业技能竞赛 2025 | 方向：web | 难度：medium | 工具：PHP、ThinkPHP

## 一句话总结

2025 广西决赛 AWD Web 复盘：纸质密码信封错过 + PHP likeadmin 默认 + UploadController 上传 + 未授权改密 + ThinkPHP 鉴权绕过。断网教训。

## 攻击链

1. 默认密码 admin/likeadmin（很多人试不成功，可能密码重置）
2. 后台 UploadController.file() 任意文件上传
3. POST /adminapi/upload/file multipart form-data filename=123.php
4. 未授权：/adminapi/auth.admin/edit 改 id=1 账号密码
5. ThinkPHP 框架：删除管理员 token 仍可操作（鉴权绕过）
6. 断网教训：纸质密码信封 + SSH 密码独立纸片

## 关键 payload

```
POST /adminapi/upload/file Content-Type: multipart/form-data
```

## 经验教训

AWD 线下赛 = 断网 + 纸质密码信封多页 + 限时 20 分钟防御时间；赛前必备：本地代码审计脚本、漏洞扫描字典、上传 webshell 工具、ssh 弱密码字典；AWD 一题多漏洞，不要只审一个入口。

## 标签

广西 2025 决赛 AWD Web、断网环境 复盘教训、纸质密码信封 第二张纸、过度紧张 基础薄弱、PHP likeadmin/admin 默认密码、后台任意文件上传 UploadController file()、123.php multipart/form-data、未授权重置管理员密码 auth.admin/edit、用户操作未鉴权、ThinkPHP 鉴权漏洞、awd 一题多漏洞、离线资料包 应急

## 参考来源

- https://www.ctfiot.com/283303.html
- 原文件：2025年广西网络与信息安全职业技能竞赛决赛_awd_web部分_赛后WriteUP以及自我检讨.full.md
