---
title: "【拟态挑战WP】2021 春秋杯秋季赛 mimic-ssrf"
category: web
tags: ["春秋杯", "web", "拟态防御-mimic-defense", "邬江兴-紫金山实验室", "SSRF", "file-protocol"]
signals: ["春秋杯 2021", "拟态防御-mimic-defense", "邬江兴-紫金山实验室", "SSRF", "file-protocol", "/proc/PID/cmdline", "XDebug-PHP", "python-debugpy", "Java-JDWP", "ssrf", "mimic-ssrf", "XDebug", "debugpy", "JDWP"]
difficulty: hard
source: "https://www.ctfiot.com/22547.html"
tools: ["Java", "PHP", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【拟态挑战WP】2021 春秋杯秋季赛 mimic-ssrf

> 赛事：春秋杯 2021 | 方向：web | 难度：hard | 工具：Java、PHP、Python

## 一句话总结

2021 春秋杯秋季赛 mimic-ssrf 拟态防御 + SSRF + XDebug/debugpy/JDWP 三语言 RCE 链。

## 攻击链

1. 1. SSRF file:///etc/passwd 读文件 /2. /proc/PID/cmdline 遍历进程找 3 个语言服务 (PHP/Python/Java) /3. PHP XDebug client_port 13000 → 反弹代码执行 /4. Python debugpy + Java JDWP 类似利用 /5. 三种异构体需同时返回一致结果（拟态表决）

## 关键 payload

```
file:///etc/passwd  /proc/§1§/cmdline  client_port=13000  三个异构体同时执行
```

## 经验教训

拟态防御（mimic defense）= 邬江兴院士 + 紫金山实验室；三语言异构体需一致响应通过表决；SSRF + XDebug 13000 端口是 PHP RCE 经典；debugpy/JDWP 是 Python/Java 对应端口。

## 标签

拟态防御-mimic-defense、邬江兴-紫金山实验室、SSRF、file-protocol、/proc/PID/cmdline、XDebug-PHP、python-debugpy、Java-JDWP、多异构体表决

## 参考来源

- https://www.ctfiot.com/22547.html
- 原文件：【拟态挑战WP】2021年春秋杯秋季赛mimic-ssrf.full.md
