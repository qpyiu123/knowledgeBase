---
title: "Cyber Apocalypse 2023 硬件 CTF 题解"
category: misc
tags: ["Cyber Apocalypse 2023", "misc", "hardware", "逻辑分析仪", "Gerber", "UART"]
signals: ["Cyber Apocalypse 2023 2023", "hardware", "逻辑分析仪", "Gerber", "UART", "Verilog", "hamming74", "数码管", "misc_unknown", "Hamming", "Timed", "flag", "Critical", "Flight"]
difficulty: medium
source: "https://www.ctfiot.com/222634.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Cyber Apocalypse 2023 硬件 CTF 题解

> 赛事：Cyber Apocalypse 2023 2023 | 方向：misc | 难度：medium

## 一句话总结

5道硬件题综合：波形图+Gerber+UART+Hamming+数码管逆向

## 攻击链

1. Timed: 逻辑分析仪波形识别文字flag
2. Critical Flight: Gerber PCB viewer找隐藏字符串
3. Debug: UART波特率分析解码flag
4. HM74: Verilog 74汉明码纠错码统计分析
5. Secret-Code: 逻辑分析仪+Gerber通道映射还原数码管字符
6. hamming(7,4)码: p0,p1,p2校验+data_in3-0=4bit

## 关键 payload

```
ham_out={p0,p1,data_in3,p2,data_in2,data_in1,data_in0}  # 7位
```

## 经验教训

硬件CTF结合Verilog/逻辑分析仪/PCB viewer多工具

## 标签

hardware、逻辑分析仪、Gerber、UART、Verilog、hamming74、数码管

## 参考来源

- https://www.ctfiot.com/222634.html
- 原文件：Cyber_Apocalypse_2023_硬件_CTF_题解.full.md
