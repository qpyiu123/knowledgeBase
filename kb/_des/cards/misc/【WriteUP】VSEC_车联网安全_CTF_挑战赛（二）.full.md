---
title: "【WriteUP】VSEC 车联网安全 CTF 挑战赛（二）"
category: misc
tags: ["VSEC", "misc", "ICSim-zombieCraig", "UDS-Service-0x27-Security-Access", "MAAATH-seed-1337", "UDS-Service-0x23-ReadMemory"]
signals: ["VSEC 2024", "ICSim-zombieCraig", "UDS-Service-0x27-Security-Access", "MAAATH-seed-1337", "UDS-Service-0x23-ReadMemory", "DTC-Pxxxx-xx", "cansend-vcan0", "BitFlip-XOR", "misc_unknown", "VSEC", "CTF", "ICSim", "UDS", "Service"]
difficulty: medium
source: "https://www.ctfiot.com/194326.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【WriteUP】VSEC 车联网安全 CTF 挑战赛（二）

> 赛事：VSEC 2024 | 方向：misc | 难度：medium

## 一句话总结

VSEC 车联网安全 CTF（二），ICSim 模拟 + UDS Service 0x27 SecurityAccess + MAAATH 取反 + ReadMemory 读 flag。

## 攻击链

1. 1. ICSim ./icsim vcan0 -s 10000 + ./controls vcan0 -s 10000/2. 统计 CAN ID 出现次数 找门锁/速度表 arbitration ID/3. cansend vcan0 7df#0322f190 读 VIN (UDS Service 0x22)/4. cansend vcan0 7E0#3000... 继续接收/5. 0x7DF 启动诊断 ASCII/6. DTC 读 Pxxxx-xx/7. UDS Service 0x23 ReadMemory 0xC3F80000 区域/8. UDS Service 0x27 SecurityAccess Level 3 + MAAATH seed 1337 → 0x1337 取反得 ecc8/9. Level 1 key = 9102870c c43b2d1b d64217a8 837bbdbf

## 关键 payload

```
ICSim seed 10000  MAAATH 0x1337 取反 = ecc8  Level 1 key 9102870c
```

## 经验教训

ICSim 是开源 CAN 仿真器 zombieCraig/ICSim；UDS Service 0x22 ReadDataByIdentifier 读 VIN；Service 0x23 ReadMemoryByAddress 读内存；Service 0x27 SecurityAccess 用 MAAATH 算 key；0x1337 按位取反 = 0xECC8。

## 标签

ICSim-zombieCraig、UDS-Service-0x27-Security-Access、MAAATH-seed-1337、UDS-Service-0x23-ReadMemory、DTC-Pxxxx-xx、cansend-vcan0、BitFlip-XOR

## 参考来源

- https://www.ctfiot.com/194326.html
- 原文件：【WriteUP】VSEC_车联网安全_CTF_挑战赛（二）.full.md
