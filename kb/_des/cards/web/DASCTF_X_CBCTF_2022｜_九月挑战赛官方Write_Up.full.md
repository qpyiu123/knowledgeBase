---
title: "DASCTF X CBCTF 2022 九月挑战赛官方 Write Up"
category: web
tags: ["DASCTF+CBCTF", "web", "ssti-reverse", "prototype-pollution", "file-read-url", "cc11-injectortocontroller"]
signals: ["DASCTF+CBCTF 2022", "ssti-reverse", "prototype-pollution", "file-read-url", "cc11-injectortocontroller", "gopher", "post", "easykey", "crypto_hash", "DASCTF", "CBCTF", "SSTI", "Spring", "Sign_in"]
difficulty: medium
source: "https://www.ctfiot.com/57949.html"
tools: ["Jinja2", "Spring"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DASCTF X CBCTF 2022 九月挑战赛官方 Write Up

> 赛事：DASCTF+CBCTF 2022 | 方向：web | 难度：medium | 工具：Jinja2、Spring

## 一句话总结

DASCTF X CBCTF 2022 九月赛官方 WP，涵盖 SSTI/JS 原型污染/Spring 内存马。

## 攻击链

1. Sign_in: md5(score+salt) 时间戳爆破
2. Text Reverser: 字符串反转触发 Jinja2 反射
3. zzz_again: __proto__ 污染 Object.assign
4. a_proxy_server: URL.href 协议 file:///fl%61g
5. JavaMaster: file:// 读 /etc/hosts + Spring Boot 反序列化
6. InjectToController 内存马注册
7. gopher POST readObject
8. 写 cc11 字节码
9. TemplatesImpl + TiedMapEntry + LazyMap

## 关键 payload

```
SSTI 反转 + JS 原型污染 + Spring 内存马
```

## 经验教训

JavaMaster" 这类无出网 Spring 内存马是现代 CTF WEB 高频考点。

## 标签

ssti-reverse、prototype-pollution、file-read-url、cc11-injectortocontroller、gopher、post、easykey

## 参考来源

- https://www.ctfiot.com/57949.html
- 原文件：DASCTF_X_CBCTF_2022｜_九月挑战赛官方Write_Up.full.md
