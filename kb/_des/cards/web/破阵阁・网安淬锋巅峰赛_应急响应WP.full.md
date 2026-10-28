---
title: "破阵阁・网安淬锋巅峰赛 应急响应WP"
category: web
tags: ["破阵阁网安淬锋巅峰赛", "web", "应急响应", "Tomcat后门", "/var/crash可疑tomcat", "/etc/profile后门"]
signals: ["破阵阁网安淬锋巅峰赛 2025", "应急响应", "Tomcat后门", "/var/crash可疑tomcat", "/etc/profile后门", "crontab持久化", "内存马/类加载器后门", "后门用户dev", "manager未授权", "web_unknown", "Tomcat", "ELF", "profile", "crontab"]
difficulty: medium
source: "https://www.ctfiot.com/297281.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 破阵阁・网安淬锋巅峰赛 应急响应WP

> 赛事：破阵阁网安淬锋巅峰赛 2025 | 方向：web | 难度：medium

## 一句话总结

破阵阁应急响应：Tomcat后门排查全流程（进程/ELF/profile/crontab/内存马/后门用户）

## 攻击链

1. netstat -anptu查java进程→发现/var/crash/tomcat后门ELF→rm -rf删除→检查/etc/profile后门命令→crontab -r清持久化→找webapps/a可疑目录→work/Catalina/localhost/a/类加载器字节码马→rm -rf清除→删除examples/login.jsp后门→修复manager context.xml限制IP→删除dev后门用户

## 关键 payload

```
netstat -anptu;/var/crash/tomcat ELF后门;/etc/profile;crontab -r;work/Catalina/localhost/a/ 类加载器字节码马;webapps/a;examples/login.jsp;manager/META-INF/context.xml ^.*$全IP;dev后门用户
```

## 经验教训

Tomcat应急响应必查项：crash目录ELF、profile、crontab、work/Catalina类加载器字节码、manager权限

## 标签

应急响应、Tomcat后门、/var/crash可疑tomcat、/etc/profile后门、crontab持久化、内存马/类加载器后门、后门用户dev、manager未授权

## 参考来源

- https://www.ctfiot.com/297281.html
- 原文件：破阵阁・网安淬锋巅峰赛_应急响应WP.full.md
