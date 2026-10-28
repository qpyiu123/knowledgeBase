---
title: "【官方WP】第一届 solar 杯·应急响应挑战赛官方题解"
category: web
tags: ["solar杯", "web", "应急响应", "Solar-Cup", "GeoServer", "Tomcat-JSP"]
signals: ["solar杯 2024", "应急响应", "Solar-Cup", "GeoServer", "Tomcat-JSP", "webshell", "流量解密", "333.exe", "勒索病毒", "web_unknown", "Solar", "Tomcat", "JSP", "exe"]
difficulty: medium
source: "https://www.ctfiot.com/222532.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【官方WP】第一届 solar 杯·应急响应挑战赛官方题解

> 赛事：solar杯 2024 | 方向：web | 难度：medium

## 一句话总结

第一届 Solar 杯应急响应挑战赛官方 WP，GeoServer 入侵 + Tomcat JSP 动态类 + 流量解密 + 333.exe 工具。

## 攻击链

1. 1. 攻击者 IP 10.0.100.22 目录扫描 + b.jsp 上传/2. Tomcat work/Catalina/.../org/apache/jsp/ 找动态生成 class/3. xc 作为解密密钥解密流量/4. 删除无用部分另存为 pdf/5. 333.exe 工具使 10.0.11.6 与 10.0.11.10 TCP 连接

## 关键 payload

```
xc 解密密钥  GeoServer b.jsp  333.exe  flag{sA4hP_89dFh_x09tY_lL4SI4}
```

## 经验教训

应急响应三大模块：流量分析 + 文件排查 + webshell 还原；Tomcat work 目录是 JSP 动态类缓存；xc 作为密钥解密流量。

## 标签

应急响应、Solar-Cup、GeoServer、Tomcat-JSP、webshell、流量解密、333.exe、勒索病毒

## 参考来源

- https://www.ctfiot.com/222532.html
- 原文件：【官方WP】第一届solar杯·应急响应挑战赛官方题解.full.md
