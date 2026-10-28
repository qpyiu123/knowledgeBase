---
title: "香港網安奪旗賽HKCERT CTF 2025 資格賽WEB方向Writeup"
category: web
tags: ["HKCERT CTF 2025 資格賽", "web", "nextjs-rce", "cve-2025-55182", "prototype-pollution", "JSON5"]
signals: ["HKCERT CTF 2025 資格賽 2025", "nextjs-rce", "cve-2025-55182", "prototype-pollution", "JSON5", "ssti", "lua-sandbox", "gopher-lua", "thinkphp", "rce", "HKCERT", "WEB", "Next", "CVE"]
difficulty: medium
source: "https://www.ctfiot.com/288028.html"
tools: ["ThinkPHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 香港網安奪旗賽HKCERT CTF 2025 資格賽WEB方向Writeup

> 赛事：HKCERT CTF 2025 資格賽 2025 | 方向：web | 难度：medium | 工具：ThinkPHP

## 一句话总结

HKCERT 2025资格赛WEB方向5题,涵盖Next.js最新CVE RCE+原型链污染+JSON5 SSTI+lua沙箱逃逸+ThinkPHP模板注入+PHP反序列化+Apache ap_expr读文件。

## 攻击链

1. react: CVE-2025-55182 Next.js RCE直打Next-Action header + multipart form-data
2. ezjs: __proto__ admin=true原型链污染绕认证+JSON5.parse SSTI触发process.mainModule.constructor._load("child_process")
3. easy-lua: gopher-lua pairs(_G)枚举发现S3cr3t0sEx3cFunc内置RCE函数
4. renderme: ThinkPHP {args|func}模板注入+SetHandler application/x-httpd-php;.htaccess绕检测
5. r: PHP反序列化RequestHandler匿名类+DateTime::__construct+__wakeup null绕过+RCE
6. Apache ap_expr ErrorDocument 404 %{file:/flag}直接读flag

## 关键 payload

```
POST /apps multipart __proto__ then prototype pollution chain
```

## 经验教训

2025最新Web攻击面包括Next.js Server Actions的__proto__污染+JS对象字面量构造;ap_expr的file函数是Apache的隐藏文件读取向量;ThinkPHP的{args|func}写法能绕过很多函数名过滤。

## 标签

nextjs-rce、cve-2025-55182、prototype-pollution、JSON5、ssti、lua-sandbox、gopher-lua、thinkphp、tpl-injection、php-deserialize、callback

## 参考来源

- https://www.ctfiot.com/288028.html
- 原文件：香港網安奪旗賽HKCERT_CTF_2025_資格賽WEB方向Writeup.full.md
