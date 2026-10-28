---
title: "山东省技能兴鲁职业技能大赛—铸网 2025 工业和互联网 CTF WriteUp"
category: misc
tags: ["技能兴鲁", "misc", "ICS", "force-control-PCZ", "modbus-TCP-flow", "CAN-bus-speed"]
signals: ["技能兴鲁 2025", "ICS", "force-control-PCZ", "modbus-TCP-flow", "CAN-bus-speed", "OTA-AES-CBC", "PKCS7-padding", "UUID-validation", "Industrial-CTF", "misc_unknown", "PCZ", "flag", "TCP", "CAN"]
difficulty: medium
source: "https://www.ctfiot.com/269821.html"
tools: ["Wireshark"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 山东省技能兴鲁职业技能大赛—铸网 2025 工业和互联网 CTF WriteUp

> 赛事：技能兴鲁 2025 | 方向：misc | 难度：medium | 工具：Wireshark

## 一句话总结

山东省铸网 2025 工控 4 题：PCZ 解压找 flag + TCP 流拼字符 + CAN 速度积分算距离 + OTA AES-CBC UUID 爆破。

## 攻击链

1. ICS 失窃的工艺: test.PCZ 改后缀 .zip 解压 → 搜 flag 文本
2. ICS 工控协议分析: Wireshark 追踪 TCP 流 → flag 逐字符藏在流量中
3. Misc 总线流量分析: CAN ID 0x0000280 1 字节速度 (0x50≈80km/h)
4. 速度列表: [0x46, 0x48, 0x50, 0x50, 0x55, 0x58, 0x52, 0x5A, 0x58, 0x58, ...] (30 个)
5. 36 秒间隔，距离 = sum(v * 36 / 3600) * 1000 = 24470 米
6. Misc OTA 流量分析: device 发起 /api/v1/vehicle/handshake → server 返回 session_key (hex)
7. 后续用 session_key AES-CBC 解密固件包 (PKCS7 padding 校验)
8. k1 段: 三次 AES-CBC 解密 + PKCS7 校验 → 找到正确 k1
9. k0 段: 一次 AES-CBC + UUID 格式校验 → flag UUID

## 关键 payload

```
PCZ→.zip 解压 + CAN 0x0000280 速度 36s 间隔 24470m + session_key AES-CBC PKCS7 UUID
```

## 经验教训

工控 OT/IT 融合题考察 OT 协议 (modbus/TCP/CAN) + 流量分析 + 加密协议 (AES-CBC) 综合能力。

## 标签

ICS、force-control-PCZ、modbus-TCP-flow、CAN-bus-speed、OTA-AES-CBC、PKCS7-padding、UUID-validation、Industrial-CTF

## 参考来源

- https://www.ctfiot.com/269821.html
- 原文件：山东省“技能兴鲁”职业技能大赛—“铸网2025”山东省工业和互联网CTF竞赛WriteUp.full.md
