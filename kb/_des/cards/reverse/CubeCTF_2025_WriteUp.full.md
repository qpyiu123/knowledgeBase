---
title: "CubeCTF 2025 WriteUp"
category: reverse
tags: ["CubeCTF 2025", "reverse", "forensics", "reverse", "pcap", "流量分析"]
signals: ["CubeCTF 2025 2025", "forensics", "reverse", "pcap", "流量分析", "ELF", "后门逆向", "加密通信", "CubeCTF", "Operator", "tcp", "flags", "x0018", "lvp"]
difficulty: medium
source: "https://www.ctfiot.com/262340.html"
tools: ["netcat"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# CubeCTF 2025 WriteUp

> 赛事：CubeCTF 2025 2025 | 方向：reverse | 难度：medium | 工具：netcat

## 一句话总结

CubeCTF 2025 Operator取证题，pcap提取ELF后门逆向解密

## 攻击链

1. pcap筛选tcp.flags==0x0018 [PSH,ACK]
2. 发现攻击者执行id, nc -lvp 2025 > /tmp/xcat传输ELF
3. 三段TCP重组为ELF文件/tmp/xcat
4. /tmp/xcat -l 2025加密传输密文到/tmp/supersecret
5. 逆向xcat解密sub_15D0(sub_16A0(s1))双重函数
6. 还原6段密文得到明文

## 关键 payload

```
tcp.flags == 0x0018; nc -lvp 2025 > /tmp/xcat
```

## 经验教训

多段TCP重组需按顺序拼接；自写加密工具逆向需识别sub_15D0/sub_16A0

## 标签

forensics、reverse、pcap、流量分析、ELF、后门逆向、加密通信

## 参考来源

- https://www.ctfiot.com/262340.html
- 原文件：CubeCTF_2025_WriteUp.full.md
