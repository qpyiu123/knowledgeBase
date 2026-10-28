---
title: "【工控Writeup】2022 河南工业互联网安全大赛复赛"
category: misc
tags: ["河南工业互联网", "misc", "MMS-protocol", "modbus-ICS", "fileOpen-fileRead", "base64-image-flag"]
signals: ["河南工业互联网 2022", "MMS-protocol", "modbus-ICS", "fileOpen-fileRead", "base64-image-flag", "hex-shift", "function-code-17-109-65-1-3-67", "工业互联网", "misc_unknown", "MMS", "fileOpen", "hex", "modbus", "fileRead"]
difficulty: medium
source: "https://www.ctfiot.com/78419.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【工控Writeup】2022 河南工业互联网安全大赛复赛

> 赛事：河南工业互联网 2022 | 方向：misc | 难度：medium

## 一句话总结

2022 河南工业互联网安全大赛复赛 3 题 WP，MMS fileOpen 读图 + hex 移位爆破 + modbus 异常检测。

## 攻击链

1. 1. MMS 流量过滤 fileOpen 操作 4 次拿标识符 /2. 找 fileRead 操作提取 base64 图片 /3. 异或/移位 666i5250... + 61673255... 偏移 6 /4. modbus 流量 function_code 序列 17,109,65,1,1,3,3,67 /5. 提取发送方 frame_id + func_code 找异常

## 关键 payload

```
flag{ICS-mms104}  flag{RP2U5myhBI5m}  modbus function 17 109 65 1 1 3 3 67
```

## 经验教训

MMS (Manufacturing Message Specification) 是工业自动化协议；modbus function code 序列分析是工控异常检测；hex 移位爆破是常见编码。

## 标签

MMS-protocol、modbus-ICS、fileOpen-fileRead、base64-image-flag、hex-shift、function-code-17-109-65-1-3-67、工业互联网

## 参考来源

- https://www.ctfiot.com/78419.html
- 原文件：【工控Writeup】2022河南工业互联网安全大赛复赛.full.md
