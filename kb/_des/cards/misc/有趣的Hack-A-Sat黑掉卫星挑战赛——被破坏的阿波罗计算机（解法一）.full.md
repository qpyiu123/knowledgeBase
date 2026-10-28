---
title: "Hack-A-Sat 阿波罗导航计算机被破坏的 PI 值"
category: misc
tags: ["Hack-A-Sat", "misc", "Apollo", "AGC", "DSKY", "VirtualAGC"]
signals: ["Hack-A-Sat 2020", "Apollo", "AGC", "DSKY", "VirtualAGC", "Commanche055", "PI", "octal", "DP-float", "iot", "ROM", "rope-memory", "o27", "Bank"]
difficulty: hard
source: "https://www.ctfiot.com/97721.html"
tools: ["netcat"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Hack-A-Sat 阿波罗导航计算机被破坏的 PI 值

> 赛事：Hack-A-Sat 2020 | 方向：misc | 难度：hard | 工具：netcat

## 一句话总结

VirtualAGC 复现 Apollo AGC 的 DSKY 命令，从 ROM rope-memory 中挖出被篡改的 PI/16 DP 值。

## 攻击链

1. 用 VirtualAGC 模拟器定位 Commanche055 固件中 PI/16 存储的 0o27 Bank 0o3355 address
2. netcat 连 172.17.0.1:19008 与 yaDSKY 交互
3. DSKY 协议发送 V27N02E 进入"读取 ROM"模式
4. 输入 0o57355（Bank×0o2000+addr-0o2000）按 ENTR 循环读 ROM
5. 在 PI/16 邻位找到 0o37777 标记反向读出两个 DP 字
6. 拼接 0o6413 0o11416 按 AGC DP 浮点格式解出 3.26103293895721435546875

## 关键 payload

```
0o6413 0o11416 → PI = 3.26103293895721435546875
```

## 经验教训

历史向 CTF 考察领域知识（AGC 八进制 + Bank 寻址 + DP 浮点 + V/N 命令），解题关键是搞清 V27N02E 查表语义。

## 标签

Apollo、AGC、DSKY、VirtualAGC、Commanche055、PI、octal、DP-float、rope-memory、history

## 参考来源

- https://www.ctfiot.com/97721.html
- 原文件：有趣的Hack-A-Sat黑掉卫星挑战赛——被破坏的阿波罗计算机（解法一）.full.md
