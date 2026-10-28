---
title: "第三届黄河流域公安院校网络空间安全技能挑战赛官方Writeup"
category: web
tags: ["第三届黄河流域公安院校网络空间安全技能挑战赛", "web", "黄河流域公安", ".user.ini包含", "log注入UA头", "CSP绕过 max_input_vars=1000"]
signals: ["第三届黄河流域公安院校网络空间安全技能挑战赛 2024", "黄河流域公安", ".user.ini包含", "log注入UA头", "CSP绕过 max_input_vars=1000", "JSP welcome泄露", "路径穿越/WEB-INF", "帆软FineReport反序列化", "xss", "user", "ini", "CSP", "XSS", "JSP"]
difficulty: hard
source: "https://www.ctfiot.com/249193.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第三届黄河流域公安院校网络空间安全技能挑战赛官方Writeup

> 赛事：第三届黄河流域公安院校网络空间安全技能挑战赛 2024 | 方向：web | 难度：hard

## 一句话总结

第三届黄河流域公安院校挑战赛官方WP：.user.ini包含+CSP绕过XSS+JSP文件包含+路径穿越

## 攻击链

1. 1.奶龙:未过滤.user.ini→auto_prepend_file=/var/log/nginx/access.log→UA头写马→2.外国山海经:CSP绕过用1000+参数触发Warning+header失败→XSS→3.Message Board:welcome.jsp泄露isValidUser逻辑→m1xian_a注册改m1xian密码→/fileload+路径穿越/WEB-INF

## 关键 payload

```
auto_prepend_file=/var/log/nginx/access.log;UA头写马;max_input_vars=1000;CSP bypass;isValidUser('username_password.txt');username=m1xian_a 改密码;/fileload文件上传
```

## 经验教训

.user.ini可作为LFI目标；max_input_vars=1000触发Warning致header失败可绕过CSP

## 标签

黄河流域公安、.user.ini包含、log注入UA头、CSP绕过 max_input_vars=1000、JSP welcome泄露、路径穿越/WEB-INF、帆软FineReport反序列化

## 参考来源

- https://www.ctfiot.com/249193.html
- 原文件：第三届黄河流域公安院校网络空间安全技能挑战赛官方Writeup.full.md
