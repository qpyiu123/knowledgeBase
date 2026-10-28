---
title: "2023 年安询杯 ez_cpp 题解"
category: reverse
tags: ["安询杯 2023", "reverse", "数组硬编码", "ROT13", "XOR差分", "半字节交换"]
signals: ["安询杯 2023 2023", "数组硬编码", "ROT13", "XOR差分", "半字节交换", "爆破", "reverse", "XOR", "ADD", "Enc1", "ROT13-like", "Enc2", "Enc3", "arr"]
difficulty: medium
source: "https://www.ctfiot.com/119444.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2023 年安询杯 ez_cpp 题解

> 赛事：安询杯 2023 2023 | 方向：reverse | 难度：medium

## 一句话总结

32 字节 ROT13 + 查表 XOR/ADD + 半字节反转 三层加密逆向。

## 攻击链

1. Enc1: ROT13-like 字符偏移 (v3 > 90 时 +13 否则 -13，v3+13 > 122 时回 -13)
2. Enc2: 32 字节查 v6 表 ^=4/9/6 或 +=2/5
3. Enc3: arr[i] ^= 1; arr[i] = dec3(arr[i])
4. dec3(a1) 是 8-bit reverse 字节反转
5. 给定 arr 数组 32 个 uint（含 32-bit 负数）
6. 反向 Enc3 → Enc2 → Enc1 还原明文

## 关键 payload

```
arr[] = {0x22, 0x0FFFFFFA2, 0x72, 0x0FFFFFFE6, 0x52, 0x0FFFFFF8C, ...}
```

## 经验教训

半字节反转 dec3(v) = ((v>>0)&1)<<7 + ... 是经典 8-bit reverse；查表操作要反向回推。

## 标签

数组硬编码、ROT13、XOR差分、半字节交换、爆破

## 参考来源

- https://www.ctfiot.com/119444.html
- 原文件：2023_年安询杯_ez_cpp_题解.full.md
