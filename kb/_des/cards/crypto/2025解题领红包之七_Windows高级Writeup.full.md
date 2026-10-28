---
title: "2025 解题领红包之七 - Windows 高级 Writeup"
category: crypto
tags: ["解题领红包", "crypto", "ECC椭圆曲线", "point_add", "加密d-1轮", "解密d-1轮"]
signals: ["解题领红包 2025", "ECC椭圆曲线", "point_add", "加密d-1轮", "解密d-1轮", "108字符6字符组", "ParseInt", "时间戳异或", "abs64平方", "crypto_rsa", "Windows", "UID", "Str2", "Key"]
difficulty: hard
source: "https://www.ctfiot.com/227560.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2025 解题领红包之七 - Windows 高级 Writeup

> 赛事：解题领红包 2025 | 方向：crypto | 难度：hard

## 一句话总结

解题领红包 Windows 高级 — UID+时间戳异或得 Str2 + 108 字符 Key 转 18 数组 + ECC 加解密 d-1 轮 + 复杂字符算式比较。

## 攻击链

1. 入口 sub_1400017A0: 输入 UID (范围 1..0x5F5E0FE)
2. UID ^= 60 * (time(0)/60) / 10
3. Str2 = abs64(UID*UID) sprintf 16 字符
4. 输入 Key 长度必须 108
5. Key 每 6 字符一组, ParseInt 3 个 2 字符为 100*v9 + 10*v10 + v11
6. 共 18 个整数组成 IntArray[0..17]
7. 椭圆曲线加密: 用 (a, d, Gx, Gy, p) 跑 d-1 次 point_add 得 (x, y) = (v12, v13)
8. 从 IntArray 取 de_a = [16], de_p = [17] (用户提供 a, p)
9. 用 de_a, de_p 解密 d-1 次得 (x1, y1)
10. 循环 16 次: Str1[i] = (IntArray[i] - 10*y1 - v20) / x1 (mod? 步长 10202)
11. 比较 Str1 != Str2
12. 步长 10202 × 16 = 163232
13. Str2 由 abs64(UID^2) 决定, UID 又被时间戳影响

## 关键 payload

```
108字符→18 数组 / ECC 加密-解密 d-1 轮 / de_a, de_p 用户控制 / 步长 10202 16 次 / Str1 != Str2 校验
```

## 经验教训

比较 Str1 != Str2 即失败, 需让两边相等; UID^2 决定 Str2, 但 UID 也被 time(0) 量化异或, 所以爆破时间窗口 + 构造 Key 是双难。

## 标签

ECC椭圆曲线、point_add、加密d-1轮、解密d-1轮、108字符6字符组、ParseInt、时间戳异或、abs64平方、UID、比较Str1!=Str2、复杂条件、排行榜第五

## 参考来源

- https://www.ctfiot.com/227560.html
- 原文件：2025解题领红包之七_Windows高级Writeup.full.md
