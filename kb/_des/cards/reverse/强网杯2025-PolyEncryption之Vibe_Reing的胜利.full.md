---
title: "强网杯2025 PolyEncryption - Vibe Reing的胜利 (看雪SleepAlone)"
category: reverse
tags: ["强网杯2025", "reverse", "PolyEncryption", "dotnet", "polyencrypt.dll", "saw.py"]
signals: ["强网杯2025 2025", "PolyEncryption", "dotnet", "polyencrypt.dll", "saw.py", "Hack.java", "AI辅助", "白盒AES", "S-box", "reverse", "saw", "Hack", "java", "patch"]
difficulty: hard
source: "https://www.ctfiot.com/287808.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 强网杯2025 PolyEncryption - Vibe Reing的胜利 (看雪SleepAlone)

> 赛事：强网杯2025 2025 | 方向：reverse | 难度：hard | 工具：Python

## 一句话总结

强网杯2025 PolyEncryption:AI辅助+dotnet反编译+saw.py Hack.java patch+22轮AES风格PolyEnc纯Python实现。

## 攻击链

1. 静态分析dotnet polyencrypt.dll → 找到saw.py/Hack.java关键模块 → AI推理数据流(明文abe74e3a9c375b3428bf31d1f8fa49c1→逆序处理→小端→AES风格加密) → Patch saw.py/Hack.java绕过混淆/反调试 → Debug docker日志敲定细节 → 纯Python实现PolyEnc 22轮(奇数轮SubBytes+MixColumns,偶数轮ShiftRows+AddRoundKey) → 加解密验证 → 解密flag.enc

## 关键 payload

```
22轮 PolyEnc(奇数SubBytes+MixColumns,偶数ShiftRows+AddRoundKey) + 密钥级联(A'=A^sbox(rol(D,8))^round_key) + 逆MixColumns[0x0E,0x0B,0x0D,0x09]
```

## 经验教训

AI辅助逆向+手动验证+patch关键模块;dotnet polyencrypt.dll分析策略:先看saw.py/Hack.java逻辑再Patch;PolyEnc 22轮用奇数轮SubBytes+MixColumns+偶数轮ShiftRows+AddRoundKey;密钥级联s[1]=A^sbox(rol(D,8))^round_key;逆MixColumns矩阵[0x0E,0x0B,0x0D,0x009];逆向流程:Round 22→Round 1(偶数→逆AddRoundKey+逆ShiftRows;奇数→逆MixColumns+逆SubBytes)。

## 标签

PolyEncryption、dotnet、polyencrypt.dll、saw.py、Hack.java、AI辅助、白盒AES、S-box、ShiftRows、MixColumns、AddRoundKey、22轮、Sbox+MixCols交错、dotnet反编译、AES密钥编排、SleepAlone

## 参考来源

- https://www.ctfiot.com/287808.html
- 原文件：强网杯2025-PolyEncryption之Vibe_Reing的胜利.full.md
