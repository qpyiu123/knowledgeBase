---
title: "DASCTF 2022 5 月出题人挑战赛官方 Write"
category: web
tags: ["DASCTF", "web", "golang-upload", "cve-2021-42013", "golang-ssti", "ua-spoof"]
signals: ["DASCTF 2022", "golang-upload", "cve-2021-42013", "golang-ssti", "ua-spoof", "sys-auth-rc4", "docker-layer", "suid", "mt19937-symbolic", "web_unknown", "DASCTF", "Web", "Misc", "Crypto"]
difficulty: medium
source: "https://www.ctfiot.com/42240.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DASCTF 2022 5 月出题人挑战赛官方 Write

> 赛事：DASCTF 2022 | 方向：web | 难度：medium | 工具：Python

## 一句话总结

DASCTF 2022 5 月出题人挑战赛官方 WP，6 Web + 6 Misc + 3 Crypto + 2 Pwn。

## 攻击链

1. hackme: 上传 users.go 白名单绕过
2. getme: CVE-2021-42013 目录穿越读 access_log
3. fxxkgo: golang jwt {{.}} 模板注入
4. 魔法浏览器: UA 修改 + JS 反混淆
5. Power Cookie: cookie=admin 1
6. ezcms: Mc_Encryption_Key 解密 update.php
7. delflag: docker save + layer extract
8. Yusa MT19937 线性攻击
9. 山重水复: off-by-one 改 size 0x481
10. house of kiwi 劫持

## 关键 payload

```
Apache 2.4.50 目录穿越 + MT19937 符号执行
```

## 经验教训

golang web 框架的 SSTI 比 Python 难利用，但模板渲染时同样注入 . 用 {{.}} 即拿到 key。

## 标签

golang-upload、cve-2021-42013、golang-ssti、ua-spoof、sys-auth-rc4、docker-layer、suid、mt19937-symbolic

## 参考来源

- https://www.ctfiot.com/42240.html
- 原文件：DASCTF｜2022DASCTF_May出题人挑战赛官方Write.full.md
