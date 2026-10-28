---
title: "【BuildCTF】Web 方向 AK 全解 WP"
category: web
tags: ["BuildCTF", "web", "ID-bruteforce", "robots.txt", "htaccess-upload", "HTTP-headers"]
signals: ["BuildCTF 2024", "ID-bruteforce", "robots.txt", "htaccess-upload", "HTTP-headers", "Flask-SSTI", "replace-length", "ffifdyop-MD5", "Character.toUpperCase-trick", "ssti", "BuildCTF", "Web", "htaccess", "headers"]
difficulty: medium
source: "https://www.ctfiot.com/212857.html"
tools: ["Flask", "Java"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【BuildCTF】Web 方向 AK 全解 WP

> 赛事：BuildCTF 2024 | 方向：web | 难度：medium | 工具：Flask、Java

## 一句话总结

BuildCTF 2024 Web 方向 AK 全解，13 道题覆盖 ID 爆破/htaccess/headers/SSTI/反序列化/JWT/字符 case-folding 漏洞。

## 攻击链

1. find-the-id 爆破数字 207/Tflock robots.txt + ctfer 登录态保持爆破 admin/Babyupload .htaccess 上传 + 木马 env 命令执行/ez!http 填 headers Date 点分隔格式/我写的网站被rce了 读文件命令执行/LovePopChain 反序列化链 post rce/RedFlag Flask ssti/Why_so_serials replace 长度变化构造反序列化 + joker 扩充/ez_md5 ffifdyop MD5 注入 → 爆破 3e41f780146b6c246cd49dd296a3da28 → 1145146803531 + 数组弱等于/eazyl0gin 字符ı→I ſ→S 登录绕 + 012346 md5/刮刮乐 cmd + Referer + 注释 /dev/null/sub admin + JWT_SECRET_KEY 伪造 token + 命令执行闭合/Cookie_Factory app.js 暴露 flag/ez_waf WAF 绕

## 关键 payload

```
admin token 伪造 + JWT_SECRET_KEY  + ffifdyop  MD5 注入 + ı/ſ 字符 case-folding
```

## 经验教训

Character.toUpperCase() 中 'ı'→'I' 'ſ'→'S' 是 Java 经典 Unicode case-folding 漏洞；ffifdyop 经 MD5 后得 'or' 触发 SQL 注入绕过；JWT_SECRET_KEY 泄漏直接伪造 token。

## 标签

ID-bruteforce、robots.txt、htaccess-upload、HTTP-headers、Flask-SSTI、replace-length、ffifdyop-MD5、Character.toUpperCase-trick、JWT-forge、app.js、JWT_SECRET_KEY、WAF-bypass

## 参考来源

- https://www.ctfiot.com/212857.html
- 原文件：【BuildCTF】Web方向AK全解WP.full.md
