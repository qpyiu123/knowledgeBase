---
title: "ssti 挑战——wp"
category: web
tags: ["ssti-challenge", "web", "thymeleaf-ssti", "s2-061", "instance-manager", "spel"]
signals: ["ssti-challenge 2024", "thymeleaf-ssti", "s2-061", "instance-manager", "spel", "jackson-defaulttyping", "mlet", "classloader", "web_unknown", "Thymeleaf", "SSTI", "S2-061", "Jackson", "SpEL"]
difficulty: hard
source: "https://www.ctfiot.com/301690.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# ssti 挑战——wp

> 赛事：ssti-challenge 2024 | 方向：web | 难度：hard

## 一句话总结

Thymeleaf SSTI 3 层防护绕过，S2-061 + Jackson + SpEL 完整利用链。

## 攻击链

1. Thymeleaf 3 阻断 `$$` 和 `new
2. 借鉴 S2-061 拿 org.apache.tomcat.InstanceManager
3. @servletContext.getAttribute(''org.apache.tomcat.InstanceManager'')
4. newInstance('SpelExpressionParser') 创建 SpEL
5. Jackson ObjectMapper enableDefaultTyping
6. constructFromCanonical 创建 JavaType
7. MLet 远程加载恶意 class
8. SpEL 表达式 Runtime.exec

## 关键 payload

```
S2-061 InstanceManager + Jackson + SpEL + MLet
```

## 经验教训

当 SSTI 阻断 `$$` 和 `new` 时，可以借助 InstanceManager 实例化类。

## 标签

thymeleaf-ssti、s2-061、instance-manager、spel、jackson-defaulttyping、mlet、classloader

## 参考来源

- https://www.ctfiot.com/301690.html
- 原文件：ssti挑战——wp.full.md
