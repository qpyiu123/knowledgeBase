---
title: "2024 CISCN x 长城杯 初赛逆向 0 解题 - VT 解题全流程"
category: reverse
tags: ["CISCN x 长城杯", "reverse", "CRC32爆破", "短密钥", "XOR轮密钥", "IDA条件断点"]
signals: ["CISCN x 长城杯 2024", "CRC32爆破", "短密钥", "XOR轮密钥", "IDA条件断点", "KeyList提取", "reverse", "misc_math", "CRC32", "KeyList", "XOR", "IDA", "CRC32-style", "xEDB88320"]
difficulty: medium
source: "https://www.ctfiot.com/232235.html"
tools: ["IDA"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2024 CISCN x 长城杯 初赛逆向 0 解题 - VT 解题全流程

> 赛事：CISCN x 长城杯 2024 | 方向：reverse | 难度：medium | 工具：IDA

## 一句话总结

2 字节密钥爆破 + CRC32 反推 + KeyList XOR。

## 攻击链

1. IDA 找主函数 + 子函数 → 看到 CRC32-style 函数（0xEDB88320 多项式）→ 找到 48 字节密文 KeyList → 2 字节密钥 Param1（0~0xFFFF 爆破）→ 48 字节密文 = KeyList[i] ^ pParam1[i%2] → 喂 calc 函数算 CRC32 → 比对 0xF703DF16 → 找到 Param1 = 0xXXXX → 拼 flag

## 关键 payload

```
uint8_t KeyList[] = {82,225,68,226,57,225,94,155,81,220,25,152,80,146,57,193,80,158,82,130,39,130,38,231,83,128,36,128,66,220,57,158,2,148,39,129,69,131,81,147,2,128,68,129,68,129,68,129} ; if (calc_value == 0xF703DF16) printf("Cracked:%02X%02X", pParam1[0], pParam1[1])
```

## 经验教训

短密钥 + 标准 CRC32 函数 + 已知 48 字节密文是爆破黄金组合。

## 标签

CRC32爆破、短密钥、XOR轮密钥、IDA条件断点、KeyList提取

## 参考来源

- https://www.ctfiot.com/232235.html
- 原文件：2024_CISCN_x_长城杯_初赛逆向0解题-VT_解题全流程.full.md
