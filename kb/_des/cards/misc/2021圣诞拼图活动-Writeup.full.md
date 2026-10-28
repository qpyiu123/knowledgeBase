---
title: "2021 圣诞拼图活动 Writeup"
category: misc
tags: ["2021 圣诞活动", "misc", "拼图", "A-star", "数字华容道", "4x4"]
signals: ["2021 圣诞活动 2021", "拼图", "A-star", "数字华容道", "4x4", "16-puzzle", "自动求解", "启发式搜索", "MinBinHeapq", "misc_unknown", "stego_image", "puzzle"]
difficulty: easy
source: "https://www.ctfiot.com/19654.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2021 圣诞拼图活动 Writeup

> 赛事：2021 圣诞活动 2021 | 方向：misc | 难度：easy

## 一句话总结

16-puzzle 数字华容道 A* 自动求解

## 攻击链

1. 题目给 4x4 拼图（16 块），一块全黑，其余 15 块打乱
2. 随机滑动 64 步，理论上 ≤64 步可还原
3. 原图块对应序列: 5, 1, 6, 8, 2, 11, 7, 13, 15, 14, 3, 4, 10, 16, 12, 0
4. A* 算法 + MinBinHeapq 优先队列 + 曼哈顿距离启发
5. 求解 72 步（>64 步时重置）
6. 输出方向: RRDDRDLULURRULDLDLUURRRDLLDRULDDRULUURDRULLDRRDLLLDRURULLDDRULURRDLDRURU
7. 步数超出时多刷几张图重试

## 关键 payload

```
5, 1, 6, 8, 2, 11, 7, 13, 15, 14, 3, 4, 10, 16, 12, 0
```

## 经验教训

N-puzzle 是经典 AI 搜索问题；曼哈顿距离是 admissible heuristic

## 标签

拼图、A-star、数字华容道、4x4、16-puzzle、自动求解、启发式搜索、MinBinHeapq

## 参考来源

- https://www.ctfiot.com/19654.html
- 原文件：2021圣诞拼图活动-Writeup.full.md
