---
title: "AWD 离线 - Jar 文件冷补丁"
category: web
tags: ["AWD 入门", "web", "DocToolkit", "Spring Boot", "CFR反编译", "javac重编译"]
signals: ["AWD 入门 2024", "DocToolkit", "Spring Boot", "CFR反编译", "javac重编译", "jar -cvfM0重打包", "BOOT-INF/classes", "BOOT-INF/lib", "ShiroConfig", "web_unknown", "AWD", "Jar", "Spring", "Boot"]
difficulty: medium
source: "https://www.ctfiot.com/182663.html"
tools: ["C", "Java", "Spring"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# AWD 离线 - Jar 文件冷补丁

> 赛事：AWD 入门 2024 | 方向：web | 难度：medium | 工具：C、Java、Spring

## 一句话总结

AWD 离线 Jar 冷补丁 — Spring Boot DocToolkit + CFR 反编译 + javac 重编译 (ShiroConfig+UserRealm+AdminController) + jar -cvfM0 重打包 + 改密钥 QZIysgMYhG7/CzAlphabug 留后门。

## 攻击链

1. 准备 Oracle Java 8/11/17 + cfr-0.152.jar
2. unzip DocToolkit-0.0.1-SNAPSHOT.jar -d example
3. mkdir -p src/main/java + cp example/BOOT-INF/classes/* src/main/java/
4. 用 CFR 反编译所有 .class 为 .java
5. 改 ShiroConfig.java 中的密钥: QZIysgMYhG7/CzIJlVpR1g → QZIysgMYhG7/CzAlphabug
6. CLASS_LIB=$(find example/BOOT-INF/lib/ -name "*.jar" | tr '\n' ':') 拼 classpath
7. javac -cp ".:${CLASS_LIB%:}" 重编译 ShiroConfig.java + UserRealm.java + AdminController.java
8. cp 编译后的 .class 覆盖 example/BOOT-INF/classes/
9. jar -xvf 解包所有 lib/*.jar 到 lib_unpacked/
10. jar -cvfM0 重打包所有 lib
11. jar -cvfM0 ../example_repacked.jar -C . . 重打主 jar
12. java -jar example_repacked.jar 验证后门

## 关键 payload

```
CFR-0.152 + javac -cp BOOT-INF/lib + jar -cvfM0 / ShiroConfig 密钥改 / UserRealm 改 / AdminController 改
```

## 经验教训

Spring Boot jar 冷补丁关键在 BOOT-INF/classes/ + BOOT-INF/lib 双层结构;CFR-0.152 是 Java 8/11/17 通用反编译首选;jar -cvfM0 (无清单) 是快速重打方案。

## 标签

DocToolkit、Spring Boot、CFR反编译、javac重编译、jar -cvfM0重打包、BOOT-INF/classes、BOOT-INF/lib、ShiroConfig、UserRealm、AdminController、QZIysgMYhG7/CzIJlVpR1g改QZIysgMYhG7/CzAlphabug、留后门

## 参考来源

- https://www.ctfiot.com/182663.html
- 原文件：AWD离线-Jar文件冷补丁.full.md
