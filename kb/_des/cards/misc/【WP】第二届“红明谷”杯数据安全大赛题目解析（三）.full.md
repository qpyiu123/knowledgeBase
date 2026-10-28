---
title: "【WP】第二届\"红明谷\"杯数据安全大赛题目解析（三）"
category: misc
tags: ["红明谷", "misc", "RTPS-protocol", "RSA-AES-pcap", "on-off-board-key", "pycryptor"]
signals: ["红明谷 2022", "RTPS-protocol", "RSA-AES-pcap", "on-off-board-key", "pycryptor", "USB-keystroke", "ROS-traffic", "blind-stack-overflow", "USB-hid-table", "crypto_rsa", "RTPS", "RSA", "AES", "USB"]
difficulty: hard
source: "https://www.ctfiot.com/33384.html"
tools: ["Wireshark", "tshark"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【WP】第二届"红明谷"杯数据安全大赛题目解析（三）

> 赛事：红明谷 2022 | 方向：misc | 难度：hard | 工具：Wireshark、tshark

## 一句话总结

第二届红明谷杯题解（三），RTPS 协议 RSA/AES 流量分析 + USB 键盘流量盲打还原。

## 攻击链

1. 1. 神秘电波：Wireshark 过滤 RTPS 协议 + onboard/offboard key 切换 RSA 加密三元素 (n, e, c) + AES 解密 /2. 重要系统：tshark 提取 USB capdata + normalKeys/shiftKeys 字典映射 + <DEL> 处理还原 player:guest

## 关键 payload

```
USB HID normalKeys/shiftKeys 0x04-0x1d 字典  RTPS onboard/offboard 切换
```

## 经验教训

RTPS 协议是 ROS/DDS 中间件的实时通信协议；USB 键盘流量通过 HID Usage ID 0x04-0x1d 映射到字母；正常/Shift 键切换大小写和符号。

## 标签

RTPS-protocol、RSA-AES-pcap、on-off-board-key、pycryptor、USB-keystroke、ROS-traffic、blind-stack-overflow、USB-hid-table

## 参考来源

- https://www.ctfiot.com/33384.html
- 原文件：【WP】第二届“红明谷”杯数据安全大赛题目解析（三）.full.md
