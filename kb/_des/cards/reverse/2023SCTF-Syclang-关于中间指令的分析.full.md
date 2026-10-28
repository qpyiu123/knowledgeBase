---
title: "2023 SCTF Syclang 关于中间指令的分析"
category: reverse
tags: ["SCTF 2023", "reverse", "Syclang IR", "自定义中间指令", "差分加密", "索引置乱"]
signals: ["SCTF 2023 2023", "Syclang IR", "自定义中间指令", "差分加密", "索引置乱", "数组加减", "看雪论坛", "reverse", "Syclang", "exp", "var22", "var23", "var24"]
difficulty: medium
source: "https://www.ctfiot.com/125684.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2023 SCTF Syclang 关于中间指令的分析

> 赛事：SCTF 2023 2023 | 方向：reverse | 难度：medium

## 一句话总结

Syclang 自定义 IR 逆向：4 轮差分/加减/累加/索引置乱混合加密。

## 攻击链

1. 解析 Syclang 自定义 IR 中间指令语法
2. 识别 4 个 exp 结构体 (var22/var23/var24/var25)
3. var22.L/R/X 8 组索引+偏移量硬编码
4. var23.key[0..23] 24 字节密文硬编码
5. 循环 1：exp.key[23-i] = input[i] 反序写入
6. 循环 2：差分 var22.key[i] -= var22.key[i-1]
7. 循环 3：8 组加减 var22.key[L[i]] += X[i] / var22.key[R[i]] -= X[i]
8. 循环 4：累加 var22.key[i] += var22.key[i-1]
9. 对 var23 做同样差分 + 减/加 var22.key[i*3] + 累加
10. 比较 var22 == var23

## 关键 payload

```
var23.key[0..23] = {252, 352, 484, 470, 496, 487, 539, 585, 447, 474, 577, 454, 466, 345, 344, 486, 501, 423, 490, 375, 257, 203, 265, 125}
```

## 经验教训

自定义 IR 逆向关键是识别循环结构 + 操作类型，差分加密逆向就是反向累加。

## 标签

Syclang IR、自定义中间指令、差分加密、索引置乱、数组加减、看雪论坛

## 参考来源

- https://www.ctfiot.com/125684.html
- 原文件：2023SCTF-Syclang-关于中间指令的分析.full.md
