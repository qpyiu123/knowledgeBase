---
title: "2025 第三届京麒 CTF 挑战赛 writeup by Mini-Venom"
category: web
tags: ["京麒 CTF", "web", "SSTI", "删disable", "FastJson1.2.80", "CVE-2022-25845"]
signals: ["京麒 CTF 2025", "SSTI", "删disable", "FastJson1.2.80", "CVE-2022-25845", "JsonGenerationException", "FilterFileOutputStream", "MarshalOutputStream", "InflaterOutputStream", "web_unknown", "CTF", "disable", "RCE", "FastJson"]
difficulty: medium
source: "https://www.ctfiot.com/249673.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2025 第三届京麒 CTF 挑战赛 writeup by Mini-Venom

> 赛事：京麒 CTF 2025 | 方向：web | 难度：medium

## 一句话总结

京麒 CTF 三题 — SSTI 绕 disable 直接 RCE + FastJson 1.2.80 CVE-2022-25845 写 /etc/crontab 反弹 + 安卓 XXTEA Frida hook 提取密钥。

## 攻击链

1. 计算器题: 删 disable 后 ''''.__class__.__mro__[1].__subclasses__()[80].__init__.__globals__[''__builtins__''][''eval''](''__import__("os").popen("env").read()'') 拿 flag
2. FastJ 题 step1: 双 @type 触发 JsonGenerationException 缓存 UTF8JsonGenerator
3. FastJ 题 step2: $ref 二次取 OutputStream 走 MarshalOutputStream+InflaterOutputStream+FilterFileOutputStream 写 /etc/crontab
4. DeflaterOutputStream 把反弹 shell 指令压缩 + base64 作为 array 字段
5. Crontab root 反弹 shell → RCE
6. 安卓题: Frida hook libre0.so+0x184C 的 XXTEA 加密函数观察入参出参

## 关键 payload

```
{{+__class__+__mro__+__subclasses__+__init__+__globals__+__builtins__+eval+popen(env).read()}} + FastJson1.2.80 CVE-2022-25845 双 @type 缓存链
```

## 经验教训

FastJson 1.2.80 黑名单禁了 FileOutputStream 但应用自定义 FilterFileOutputStream 时仍可借 sun.rmi.server.MarshalOutputStream 走 RCE；SSTI 沙箱 disable 删配置即可破。

## 标签

SSTI、删disable、FastJson1.2.80、CVE-2022-25845、JsonGenerationException、FilterFileOutputStream、MarshalOutputStream、InflaterOutputStream、/etc/crontab、Frida hook、XXTEA、libre0.so

## 参考来源

- https://www.ctfiot.com/249673.html
- 原文件：2025第三届京麒CTF挑战赛_writeup_by_Mini-Venom.full.md
