---
title: "mqtt 协议 pwn 入门 (ciscn2025_final_mqtt)"
category: pwn
tags: ["CISCN", "pwn", "mqtt", "mosquitto", "iot", "command-injection"]
signals: ["CISCN 2025", "mqtt", "mosquitto", "iot", "command-injection", "vin-set", "sum2hex", "paho-mqtt", "amd64", "pwn_unknown", "ciscn", "final", "MQTT", "Pwn"]
difficulty: hard
source: "https://www.ctfiot.com/263183.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# mqtt 协议 pwn 入门 (ciscn2025_final_mqtt)

> 赛事：CISCN 2025 | 方向：pwn | 难度：hard

## 一句话总结

ciscn 2025 final MQTT Pwn 题：物联网车机诊断协议 + 命令注入。

## 攻击链

1. 安装 mosquitto MQTT broker
2. mosquitto_sub/pub 测试通信
3. 监听端口 9999 + allow_anonymous
4. 启动 pwn binary
5. paho.mqtt.client 连接
6. 订阅 vehicle_diag/diag/#/diag/resp
7. publish 构造 json: auth/cmd/arg
8. set_vin 触发命令执行
9. cat /flag 通过 RCE

## 关键 payload

```
MQTT set_vin 命令注入 + sum2hex 鉴权
```

## 经验教训

物联网协议 (MQTT/CoAP/Modbus) 是现代 CTF 新增长点。

## 标签

mqtt、mosquitto、iot、command-injection、vin-set、sum2hex、paho-mqtt、amd64

## 参考来源

- https://www.ctfiot.com/263183.html
- 原文件：mqtt_协议pwn入门（ciscn2025_final_mqtt）.full.md
