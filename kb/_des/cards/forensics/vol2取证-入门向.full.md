---
title: "vol2 取证 - 入门向"
category: forensics
tags: ["vol2-share", "forensics", "volatility", "vmware-vmdk", "vmem", "forensics-plugin-list"]
signals: ["vol2-share 2024", "volatility", "vmware-vmdk", "vmem", "forensics-plugin-list", "amcache", "hashdump", "mimikatz", "forensic_disk", "Volatility", "VMware", "vmdk", "plugins", "apihooks"]
difficulty: easy
source: "https://www.ctfiot.com/190333.html"
tools: ["Volatility"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# vol2 取证 - 入门向

> 赛事：vol2-share 2024 | 方向：forensics | 难度：easy | 工具：Volatility

## 一句话总结

Volatility 2 取证入门，VMware 文件格式 + 全部插件功能列表。

## 攻击链

1. 解析 .vmdk 虚拟机磁盘
2. 解析 .vmem 内存页面
3. volatility plugins: amcache/apihooks/atoms/auditpol/bigpools/bioskd
4. cachedump 提域账号密码哈希
5. cmdline 显示进程命令行
6. dlllist/hivelist/lsadump/malfind/mftparser

## 关键 payload

```
volatility 2.x 插件列表
```

## 经验教训

内存取证 = 解析 .vmem + 跑 volatility 插件。

## 标签

volatility、vmware-vmdk、vmem、forensics-plugin-list、amcache、hashdump、mimikatz

## 参考来源

- https://www.ctfiot.com/190333.html
- 原文件：vol2取证-入门向.full.md
