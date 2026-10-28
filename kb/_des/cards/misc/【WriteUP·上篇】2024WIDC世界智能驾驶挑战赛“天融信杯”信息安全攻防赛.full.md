---
title: "【WriteUP·上篇】2024WIDC 世界智能驾驶挑战赛\"天融信杯\"信息安全攻防赛"
category: misc
tags: ["WIDC", "misc", "车联网-ransomware", "Sepolia-Etherscan", "calldata-extract", "XOR-decrypt-3-9"]
signals: ["WIDC 2024", "车联网-ransomware", "Sepolia-Etherscan", "calldata-extract", "XOR-decrypt-3-9", "RSA-public-key-PEM", "encrypted-seed", "misc_unknown", "WIDC", "OEM", "Sepolia", "Etherscan", "calldata", "XOR"]
difficulty: medium
source: "https://www.ctfiot.com/185724.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【WriteUP·上篇】2024WIDC 世界智能驾驶挑战赛"天融信杯"信息安全攻防赛

> 赛事：WIDC 2024 | 方向：misc | 难度：medium | 工具：Python

## 一句话总结

2024 WIDC 世界智能驾驶挑战赛"天融信杯"信息安全攻防赛上篇，OEM 勒索病毒恢复数据 + Sepolia Etherscan 提取 calldata + XOR 解密。

## 攻击链

1. 1. 从 Sepolia Etherscan 提取 calldata 拿到加密字符串/2. Python decrypt: (ord(c) + 3) ^ 9 处理前 67 字符/3. Base64 解码得 PEM 公钥/4. 私钥 (n, d) 加密 seed 发给服务端过 27 服务

## 关键 payload

```
decrypt = (ord(c) + 3) ^ 9  RSA 私钥 627585038806247 / 119987789848673  base64 flag
```

## 经验教训

Sepolia 是 Ethereum 测试网；calldata 是 EVM 合约调用数据；(ord+3)^9 是经典 XOR 加偏移解密；RSA 短密钥 (n 短到能 627585038806247) 暗示 RSA-CRT 攻击。

## 标签

车联网-ransomware、Sepolia-Etherscan、calldata-extract、XOR-decrypt-3-9、RSA-public-key-PEM、encrypted-seed

## 参考来源

- https://www.ctfiot.com/185724.html
- 原文件：【WriteUP·上篇】2024WIDC世界智能驾驶挑战赛“天融信杯”信息安全攻防赛.full.md
