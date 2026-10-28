---
title: "Automotive CTF 2024 World Final Writeup"
category: misc
tags: ["Automotive CTF", "misc", "SWD协议", "SWCLK/SWDIO", "DEMCR 0xe000ed00", "RDBUFF"]
signals: ["Automotive CTF 2024", "SWD协议", "SWCLK/SWDIO", "DEMCR 0xe000ed00", "RDBUFF", "CPU ID 0x410fd212", "CTRL/STAT 0xf0000040", "0xe0042000", "CAN总线 778帧", "forensic_traffic", "Automotive", "CTF", "World", "Final"]
difficulty: hard
source: "https://www.ctfiot.com/210738.html"
tools: ["ARM", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Automotive CTF 2024 World Final Writeup

> 赛事：Automotive CTF 2024 | 方向：misc | 难度：hard | 工具：ARM、Python

## 一句话总结

Automotive CTF 2024 World Final — SWD 协议抓包 (DEMCR 0xe000ed00 + RDBUFF 0x410fd212 CPU ID) + I2C 0x63 0x00 0x00 0x01 + CAN 778 帧解 bh{INFAMOUS_REMAKE}。

## 攻击链

1. SWD 协议: SWCLK(1) SWDIO(2) 抓包
2. 0.594900000 起始时间戳
3. 写入 AP4: W AP4 OK
4. 读 APc: 0xe000ed00 (DEMCR 调试异常监控控制寄存器)
5. 读 RDBUFF: 0x410fd212 (CPU ID = ARM Cortex-M3)
6. 读 CTRL/STAT: 0xf0000040
7. 写 AP4 0xe0042000 读 ROM 表
8. 写 APc 0x00000000 + 状态机
9. Python rev(s) 4 字节反序: s[6:]+s[4:6]+s[2:4]+s[:2]
10. I2C: SCL=PB10, SDA=PB11, 0x63 0x00 0x00 0x01 命令
11. CAN0 778 帧: 62 68 7B 49 4E 46 41 4D 4F 55 53 5F 52 45 4D 41 4B 45 7D = "bh{INFAMOUS_REMAKE}

## 关键 payload

```
SWD 0xe000ed00 DEMCR / RDBUFF 0x410fd212 CPU ID / 0xf0000040 CTRL/STAT / 0xe0042000 ROM 表 / I2C 0x63 0x00 0x00 0x01 / CAN 778 帧 bh{INFAMOUS_REMAKE}
```

## 经验教训

SWD 协议是 ARM 调试标准,3-wire (SWDIO/SWCLK/SWO) + 状态机 (W AP4/R APc/RDBUFF);I2C 起始 + 地址 0x63 + 控制 0x00 0x00 0x01;CAN ID 778 是 vehicle bus 经典帧。

## 标签

SWD协议、SWCLK/SWDIO、DEMCR 0xe000ed00、RDBUFF、CPU ID 0x410fd212、CTRL/STAT 0xf0000040、0xe0042000、CAN总线 778帧、I2C 0x63 0x00 0x00 0x01、bh{INFAMOUS_REMAKE}、ARM CoreSight

## 参考来源

- https://www.ctfiot.com/210738.html
- 原文件：Automotive_CTF_2024_World_Final_Writeup.full.md
