---
title: "2024 中国工业互联网安全大赛智能家电行业赛道选拔赛决赛"
category: misc
tags: ["智能家电行业赛道", "misc", "BLE link key 提取", "RSA gcdext", "vigor_router 命令注入", "shiro 反序列化"]
signals: ["智能家电行业赛道 2024", "BLE link key 提取", "RSA gcdext", "vigor_router 命令注入", "shiro 反序列化", "modbus 35152 PNG 拼接", "FINS 协议响应", "IEC104 ioa", "libc.so XOR 0x17", "stego_traffic", "crypto_rsa", "web_unknown", "auth_bypass", "Ble"]
difficulty: medium
source: "https://www.ctfiot.com/197061.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 中国工业互联网安全大赛智能家电行业赛道选拔赛决赛

> 赛事：智能家电行业赛道 2024 | 方向：misc | 难度：medium

## 一句话总结

工控赛事综合：Ble+路由器+shiro+Modbus+FINS+IEC104+智能家居 IoT。

## 攻击链

1. BLE 提取 link key → 解压 / RSA 同模攻击 gcdext / vigor_router keyPath 注入 / shiro 反序列化梭 / modbus 35152 拼接 PNG / FINS 响应构造 / IEC104 ioa 提取 / 安卓 md5+flag+str 掐头去尾 / libc.so XOR 0x17 / 智能家居 scrcpy 远控 / flipper zero 红外遥控 / vim SUID 提权

## 关键 payload

```
BLE link_key / gcdext(3, 17) 同模攻击 / keyPath=%27%0A/bin/ 注入 / shiro 一键梭 / modbus regval_uint16 / 35152 是 PNG 起点 / FINS 响应头 46494e53 / iec60870_asdu.ioa / md5+flag+str / test[i] ^ 0x17
```

## 经验教训

工控流量 modbus 寄存器值 35152 是 PNG \x89P magic；FINS 协议头 46494e53。

## 标签

BLE link key 提取、RSA gcdext、vigor_router 命令注入、shiro 反序列化、modbus 35152 PNG 拼接、FINS 协议响应、IEC104 ioa、libc.so XOR 0x17、智能家居遥控、vim SUID 提权

## 参考来源

- https://www.ctfiot.com/197061.html
- 原文件：2024中国工业互联网安全大赛智能家电行业赛道选拔赛决赛WriteUp.full.md
