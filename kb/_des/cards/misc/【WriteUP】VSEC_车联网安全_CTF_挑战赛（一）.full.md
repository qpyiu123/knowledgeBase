---
title: "【WriteUP】VSEC 车联网安全 CTF 挑战赛（一）"
category: misc
tags: ["VSEC", "misc", "Block-Harbor", "VSEC-HarborBay", "Mach-E-UDS-simulation", "CAN-interface"]
signals: ["VSEC 2024", "Block-Harbor", "VSEC-HarborBay", "Mach-E-UDS-simulation", "CAN-interface", "Arbitration-ID", "license-plate-VIN", "MAC-address-geolocation", "OSINT", "misc_unknown", "VSEC", "CTF", "Mach-E", "UDS"]
difficulty: easy
source: "https://www.ctfiot.com/192410.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【WriteUP】VSEC 车联网安全 CTF 挑战赛（一）

> 赛事：VSEC 2024 | 方向：misc | 难度：easy

## 一句话总结

VSEC 车联网安全 CTF 挑战赛（一），Mach-E UDS 模拟器 + Block Harbor 背景 + 车牌 + MAC 地理定位。

## 攻击链

1. 1. VSEC 平台 → HarborBay → Mach-E UDS Challenge Simulation/2. CAN 接口名/3. 周期 CAN 帧 Arbitration ID/4. CAN 帧 data 字段字节数 + 值/5. 帧发送频率 Hz/6. Block Harbor 成立时间 2014 年/7. 车牌 DCR 660 密歇根州查 VIN + 品牌型号 + 制造地 + 进口时间/8. MAC 2A:38:5C:91:E5:27 查 2022-12-08 位置

## 关键 payload

```
Mach-E UDS Challenge  CAN 接口名  帧格式  车牌 DCR 660  MAC 2A:38:5C:91:E5:27
```

## 经验教训

Block Harbor 是汽车网络安全公司，VSEC 是其平台；Mach-E 是福特野马电动车；CAN 仲裁 ID + data 字段是基础协议；车牌反查 VIN 是 OSINT 经典题。

## 标签

Block-Harbor、VSEC-HarborBay、Mach-E-UDS-simulation、CAN-interface、Arbitration-ID、license-plate-VIN、MAC-address-geolocation、OSINT

## 参考来源

- https://www.ctfiot.com/192410.html
- 原文件：【WriteUP】VSEC_车联网安全_CTF_挑战赛（一）.full.md
