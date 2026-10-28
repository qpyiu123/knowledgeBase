---
title: "第三届数字中国虎符网络安全赛道线上赛 官方Writeup"
category: web
tags: ["第三届数字中国虎符网络安全赛道线上赛", "web", "数字中国虎符", "LD_PRELOAD", "evil.so动态库", "/proc/pid/fd/fd"]
signals: ["第三届数字中国虎符网络安全赛道线上赛 2021", "数字中国虎符", "LD_PRELOAD", "evil.so动态库", "/proc/pid/fd/fd", "RCE", "多线程爆破", "official_writeup", "rce", "evil", "proc", "pid", "HTTP"]
difficulty: hard
source: "https://www.ctfiot.com/32430.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 第三届数字中国虎符网络安全赛道线上赛 官方Writeup

> 赛事：第三届数字中国虎符网络安全赛道线上赛 2021 | 方向：web | 难度：hard

## 一句话总结

数字中国虎符线上赛官方WP：LD_PRELOAD+evil.so+/proc/pid/fd/fd多线程爆破RCE

## 攻击链

1. 上传evil.so→HTTP请求触发LD_PRELOAD=/proc/pid/fd/fd→多线程for pid/fd爆破→RCE

## 关键 payload

```
LD_PRELOAD=/proc/pid/fd/fd;Thread for pid 12-40 fd 1-40;evil.so动态库;HTTP/1.1 packet构造
```

## 经验教训

上传.so文件通过LD_PRELOAD环境变量RCE；/proc/pid/fd/枚举打开文件描述符

## 标签

数字中国虎符、LD_PRELOAD、evil.so动态库、/proc/pid/fd/fd、RCE、多线程爆破、official_writeup

## 参考来源

- https://www.ctfiot.com/32430.html
- 原文件：第三届数字中国虎符网络安全赛道线上赛_官方Writeup.full.md
