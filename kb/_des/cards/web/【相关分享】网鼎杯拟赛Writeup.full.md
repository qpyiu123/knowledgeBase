---
title: "【相关分享】网鼎杯拟赛 Writeup"
category: web
tags: ["网鼎杯", "web", "拟赛", "签到题", "upload.php", "一句话后门"]
signals: ["网鼎杯 2024", "拟赛", "签到题", "upload.php", "一句话后门", "Burp抓包改后缀", "文件上传", "隼目安全", "upload", "Writeup", "Web", "bypass", "php", "PHP"]
difficulty: easy
source: "https://www.ctfiot.com/211855.html"
tools: ["BurpSuite", "PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【相关分享】网鼎杯拟赛 Writeup

> 赛事：网鼎杯 2024 | 方向：web | 难度：easy | 工具：BurpSuite、PHP

## 一句话总结

网鼎杯拟赛 Writeup，签到题 + Web 文件上传改后缀 bypass。

## 攻击链

1. 1. 签到题：看群公告 /2. /upload.php 上传 PHP 一句话改 .png 后缀 /3. Burp 抓包改后缀 .php /4. 中国蚁剑 / 菜刀连接 webshell /5. 找 flag 文件

## 关键 payload

```
/upload.php  .png 改 .php  Content-Type: multipart/form-data
```

## 经验教训

文件上传经典 bypass：先传 .png 再 Burp 改后缀；Content-Type 检查可绕过；后门落地用中国蚁剑/菜刀。

## 标签

拟赛、签到题、upload.php、一句话后门、Burp抓包改后缀、文件上传、隼目安全

## 参考来源

- https://www.ctfiot.com/211855.html
- 原文件：【相关分享】网鼎杯拟赛Writeup.full.md
