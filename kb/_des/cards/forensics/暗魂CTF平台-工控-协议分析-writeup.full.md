---
title: "暗魂CTF平台-工控-协议分析-writeup"
category: forensics
tags: ["暗魂CTF", "forensics", "工控CTF", "Modbus协议", "S7comm协议", "OMRON协议"]
signals: ["暗魂CTF 2024", "工控CTF", "Modbus协议", "S7comm协议", "OMRON协议", "Wireshark", "TCP流", "字节交换", "forensic_traffic", "CTF", "modbus", "s7comm", "omron", "http"]
difficulty: easy
source: "https://www.ctfiot.com/198479.html"
tools: ["Wireshark"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 暗魂CTF平台-工控-协议分析-writeup

> 赛事：暗魂CTF 2024 | 方向：forensics | 难度：easy | 工具：Wireshark

## 一句话总结

暗魂CTF工控协议分析三题：modbus+s7comm异常过滤+omron字节交换解码

## 攻击链

1. modbus协议过滤追踪第一条http流→flag1=We1c0meToZXB2023→tcp流追踪16进制拼接→flag2=EnergyRevolution→s7comm.header.errcod !== 0x00过滤异常→OMRON omron.command==0x0102→每两字节swap_bytes交换位置解码flag3

## 关键 payload

```
wireshark filter modbus;s7comm.header.errcod !== 0x00;omron.command==0x0102;swap_bytes(每两字节交换)
```

## 经验教训

工控CTF核心Wireshark过滤器：modbus/s7comm/omron；OMRON密文常需每两字节swap

## 标签

工控CTF、Modbus协议、S7comm协议、OMRON协议、Wireshark、TCP流、字节交换

## 参考来源

- https://www.ctfiot.com/198479.html
- 原文件：暗魂CTF平台-工控-协议分析-writeup.full.md
