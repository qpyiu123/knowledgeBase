---
title: "2024 春秋杯夏季赛 WP(web)"
category: web
tags: ["2024 春秋杯网络安全联赛夏季赛", "web", "Java Proxy 代理 6666→3306", "javaagent javassist hook", "mysql_native_password", "System cmd \"/tmp/log.txt\" base64 写日志"]
signals: ["2024 春秋杯网络安全联赛夏季赛 2024", "Java Proxy 代理 6666→3306", "javaagent javassist hook", "mysql_native_password", "System cmd \"/tmp/log.txt\" base64 写日志", "/evil 端点 code key 校验", "php://filter zlib.inflate 多层解压", "ENV/DIFF/FILE/FUN POP 链", "LD_PRELOAD putenv system", "rce", "deserialize", "ssti", "web_unknown", "web"]
difficulty: medium
source: "https://www.ctfiot.com/192122.html"
tools: ["Java", "PHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 春秋杯夏季赛 WP(web)

> 赛事：2024 春秋杯网络安全联赛夏季赛 2024 | 方向：web | 难度：medium | 工具：Java、PHP

## 一句话总结

春秋杯夏季赛 web 三题：Java 代理 javaagent hook MySQL 流量 + /evil 代码执行 + PHP 多层 php://filter 解压 data URI + ENV/DIFF/FILE/FUN 反序列化 LD_PRELOAD 绕 disable_functions。

## 攻击链

1. Java Proxy: 6666→127.0.0.1:3306 透明转发
2. javaagent javassist: hook Proxy.send()，data 含 "def" 时改 base64 解密 payload
3. payload: 反编译 ELF 触发 mysql_native_password auth 字符串
4. /evil 端点接受 {"code": payload, "key": md5(secret)}，key=bb889ebe2ca32f6b188f07240e2204b9
5. code 用 exec("__import__('os').popen('cat /flag').read()")
6. payload2: hook socket.send 改路径 ''./1.tar.gz
7. php://filter read=zlib.inflate|zlib.inflate|dechunk|convert.iconv.latin1.latin1+base64 解压 data:
8. ENV/DIFF/FILE/FUN 反序列化 POP 链
9. ENV.__toString → putenv + system("cat hints.txt")
10. DIFF.__isset → system("cat /flag") + callback->p 触发 FUN.__get
11. FILE.__call → file_put_contents 写文件 + rename
12. DIFF private $flag=true 需绕过

## 关键 payload

```
ENV.__toString: putenv("$key=$value"); system("cat hints.txt")
```

## 经验教训

Java Proxy 透明代理+javaagent hook 是 CTF 高级 web 套路：拿到 jar 注入 javassist 改 send 逻辑；ENV/DIFF/FILE/FUN 这套 POP 链核心是 ENV.__toString 调 putenv+system，FILE.__call 写文件配合 LD_PRELOAD 绕 disable_functions。

## 标签

Java Proxy 代理 6666→3306、javaagent javassist hook、mysql_native_password、System cmd "/tmp/log.txt" base64 写日志、/evil 端点 code key 校验、php://filter zlib.inflate 多层解压、ENV/DIFF/FILE/FUN POP 链、LD_PRELOAD putenv system、syscall bypass disable_functions

## 参考来源

- https://www.ctfiot.com/192122.html
- 原文件：2024春秋杯网络安全联赛夏季赛WP(web).full.md
