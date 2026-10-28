---
title: "【传智杯WP】\"传智杯\"大学生IT技能大赛（程序设计挑战赛）省赛第二场C组WP"
category: misc
tags: ["传智杯", "misc", "算法竞赛", "数论整除", "位运算OR", "平方数判定"]
signals: ["传智杯 2026", "算法竞赛", "数论整除", "位运算OR", "平方数判定", "DP-ovo", "二分查找", "LCA", "树上差分", "misc_unknown", "mask", "ovo"]
difficulty: easy
source: "https://www.ctfiot.com/307077.html"
tools: ["C"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【传智杯WP】"传智杯"大学生IT技能大赛（程序设计挑战赛）省赛第二场C组WP

> 赛事：传智杯 2026 | 方向：misc | 难度：easy | 工具：C

## 一句话总结

传智杯 6 道算法题程序设计挑战赛 WP，整除判断 + 位运算 OR + 平方数 + DP + 二分 + LCA。

## 攻击链

1. 6 道算法题：A 整除判断 (l+2)/3 <= r/3 / B n*m 矩阵 OR 找 mask / C 偶数 + 奇数平方数 前缀和 / D 字符串"ovo" DP / E 二分 + 前缀和 k+m / F LCA + 树上差分

## 关键 payload

```
mask = (1<<30) - 1  math.isqrt(x) % 2 == 1  up[k][v] 二分 LCA
```

## 经验教训

程序设计挑战赛考察算法实现能力；(l+2)//3 <= r//3 整除判断；mask = (1<<30)-1 位运算 OR；math.isqrt(x) 平方数判定；树上差分是 LCA 类题标准解法。

## 标签

算法竞赛、数论整除、位运算OR、平方数判定、DP-ovo、二分查找、LCA、树上差分

## 参考来源

- https://www.ctfiot.com/307077.html
- 原文件：【传智杯WP】“传智杯”大学生IT技能大赛（程序设计挑战赛）省赛第二场C组WP.full.md
