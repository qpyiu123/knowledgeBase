---
title: "Hack-A-Sat 4 Qualifiers pwn部分题解"
category: pwn
tags: ["Hack-A-Sat 4 Qualifiers", "pwn", "pwn", "spacebus", "magic-bussin", "cfs"]
signals: ["Hack-A-Sat 4 Qualifiers 2023", "pwn", "spacebus", "magic-bussin", "cfs", "satellite", "oob-read", "hex-parser", "c", "heap_exploit", "Hack-A-Sat", "Magic", "Space", "Bussin"]
difficulty: hard
source: "https://www.ctfiot.com/113118.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Hack-A-Sat 4 Qualifiers pwn部分题解

> 赛事：Hack-A-Sat 4 Qualifiers 2023 | 方向：pwn | 难度：hard

## 一句话总结

Hack-A-Sat 4 Magic Space Bussin：奇数hex越界读

## 攻击链

1. Magic Space Bussin: 模拟消息队列
2. 两个管道+消息节点
3. 十六进制解析：2字符=1字节
4. 奇数长度：CalcPayloadLen保存原长度
5. 读取信息时根据保存长度输出 → 越界读
6. SB_Pipe::ParsePayload 解析漏洞
7. 越界泄露内存

## 关键 payload

```
奇数长度hex → oob read
```

## 经验教训

解析函数中奇偶处理不一致是经典OOB漏洞

## 标签

pwn、spacebus、magic-bussin、cfs、satellite、oob-read、hex-parser、c

## 参考来源

- https://www.ctfiot.com/113118.html
- 原文件：Hack-A-Sat_4_Qualifiers_pwn部分题解.full.md
