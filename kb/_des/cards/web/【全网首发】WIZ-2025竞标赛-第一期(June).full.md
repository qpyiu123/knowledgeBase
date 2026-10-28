---
title: "【全网首发】WIZ-2025 竞标赛 第一期(June) Perimeter Leak"
category: web
tags: ["WIZ", "web", "WIZ-CTF", "cloud-security", "AWS-S3", "Spring-Boot-Actuator"]
signals: ["WIZ 2025", "WIZ-CTF", "cloud-security", "AWS-S3", "Spring-Boot-Actuator", "IMDSv1", "IMDSv2", "data-perimeter", "cloud-CTF", "heap_exploit", "WIZ-2025", "Perimeter", "Leak", "Spring"]
difficulty: medium
source: "https://www.ctfiot.com/259761.html"
tools: ["Spring"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【全网首发】WIZ-2025 竞标赛 第一期(June) Perimeter Leak

> 赛事：WIZ 2025 | 方向：web | 难度：medium | 工具：Spring

## 一句话总结

WIZ-2025 竞标赛第一期 Perimeter Leak，Spring Boot Actuator + IMDS 攻击 + AWS S3 数据外泄。

## 攻击链

1. 1. Spring Boot Actuator /actuator/env /actuator/heapdump 暴露敏感信息/2. IMDSv1 169.254.169.254/latest/meta-data/ 直接访问/3. AWS S3 存储桶 flag 提取/4. data perimeter 限制 + 凭证提权

## 关键 payload

```
/actuator/heapdump  IMDSv1 169.254.169.254  AWS S3
```

## 经验教训

Spring Boot Actuator 暴露 heapdump 含密钥；IMDSv1 无认证可访问，IMDSv2 需 token；AWS data perimeter 是 S3 访问控制机制；cloud CTF 三大攻击面。

## 标签

WIZ-CTF、cloud-security、AWS-S3、Spring-Boot-Actuator、IMDSv1、IMDSv2、data-perimeter、cloud-CTF

## 参考来源

- https://www.ctfiot.com/259761.html
- 原文件：【全网首发】WIZ-2025竞标赛-第一期(June).full.md
