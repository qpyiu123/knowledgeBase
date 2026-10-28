---
title: "【WriteUP】VSEC 车联网安全 CTF 挑战赛（三）"
category: misc
tags: ["VSEC", "misc", "UDS-ReadDataByIdentifier-Service-0x22", "RoutineControl-Service-0x31", "SecurityAccess-Service-0x27-XOR", "single-byte-XOR-brute"]
signals: ["VSEC 2024", "UDS-ReadDataByIdentifier-Service-0x22", "RoutineControl-Service-0x31", "SecurityAccess-Service-0x27-XOR", "single-byte-XOR-brute", "0xc0ffe000", "0x7E0-TesterPresent", "misc_unknown", "VSEC", "CTF", "UDS", "Service", "x22", "x31"]
difficulty: medium
source: "https://www.ctfiot.com/197222.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【WriteUP】VSEC 车联网安全 CTF 挑战赛（三）

> 赛事：VSEC 2024 | 方向：misc | 难度：medium

## 一句话总结

VSEC 车联网安全 CTF（三），UDS Service 0x22/0x31/0x27 全套诊断 + 单字节 XOR 爆破 SecurityAccess。

## 攻击链

1. 1. Service 0x22 读数据 identifier 遍历 (0x03 0x22 i j)/2. Service 0x31 RoutineControl 遍历 (0x04 0x31 0x01 i j) 过滤 037f3131/3. Service 0x27 SecurityAccess 单字节 XOR 爆破 (0x02 0x11 0x01 reset + 0x02 0x27 0x01 seed) + (0x06 0x27 0x02 key1 key2 key3 key4)/4. 0x20 成功 seed ^ 0x20 = key/5. ReadMemory 0xc0ffe000 看 flag

## 关键 payload

```
Service 0x22 i,j 遍历  Service 0x31 i,j RoutineControl  Service 0x27 单字节 XOR 爆破 0x20
```

## 经验教训

UDS Service 0x22 ReadDataByIdentifier 遍历 (DID, i, j) 找有效数据；0x31 RoutineControl 爆破 (routine_id, sub_func)；0x27 SecurityAccess 单字节 XOR 可 0x00-0xFF 爆破；0xc0ffe000 是典型蜜罐地址。

## 标签

UDS-ReadDataByIdentifier-Service-0x22、RoutineControl-Service-0x31、SecurityAccess-Service-0x27-XOR、single-byte-XOR-brute、0xc0ffe000、0x7E0-TesterPresent

## 参考来源

- https://www.ctfiot.com/197222.html
- 原文件：【WriteUP】VSEC_车联网安全_CTF_挑战赛（三）.full.md
