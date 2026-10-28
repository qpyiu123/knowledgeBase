---
title: "由SUCTF一血题SU_Harmony初探鸿蒙应用安全分析"
category: reverse
tags: ["SUCTF 2024", "reverse", "鸿蒙HAP", "ArkTS", "modules.abc", "abc-decompiler"]
signals: ["SUCTF 2024 2024", "鸿蒙HAP", "ArkTS", "modules.abc", "abc-decompiler", "libentry.so", "大整数运算", "z3求解", "reverse", "SUCTF", "SU_Harmony", "HAP", "unzip", "modules"]
difficulty: medium
source: "https://www.ctfiot.com/224542.html"
tools: ["Z3"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 由SUCTF一血题SU_Harmony初探鸿蒙应用安全分析

> 赛事：SUCTF 2024 2024 | 方向：reverse | 难度：medium | 工具：Z3

## 一句话总结

SUCTF 2024 SU_Harmony：鸿蒙HAP包逆向+abc-decompiler+大整数运算链+z3解

## 攻击链

1. HAP包unzip解压→abc-decompiler反编译modules.abc→找TextInput onSubmit事件→check函数入口→IDA分析libentry.so垃圾代码→sub_57B0大整数运算链sub_62F0/6D20/8270/9890/A8F0/C160→z3解(input^2+2*input-3)//2=array

## 关键 payload

```
abc-decompiler;modules.abc;libentry.so;sub_62F0/6D20/8270/9890/A8F0/C160大整数加/减/乘/除2;z3 ToInt;array=[b'999272289930604998',...,b'2213954953857181622']
```

## 经验教训

鸿蒙HAP = Zip结构，逆向modules.abc (ArkTS) + libentry.so (NAPI)；大整数反转+加减乘除2混合运算

## 标签

鸿蒙HAP、ArkTS、modules.abc、abc-decompiler、libentry.so、大整数运算、z3求解

## 参考来源

- https://www.ctfiot.com/224542.html
- 原文件：由SUCTF一血题SU_Harmony初探鸿蒙应用安全分析.full.md
