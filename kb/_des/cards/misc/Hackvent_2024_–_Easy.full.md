---
title: "Hackvent 2024 – Easy"
category: misc
tags: ["Hackvent 2024", "misc", "misc", "gifsicle", "change-color", "ean8"]
signals: ["Hackvent 2024 2024", "misc", "gifsicle", "change-color", "ean8", "barcode", "python-check-digit", "png-extract", "misc_unknown", "Hackvent", "Easy", "EAN-8", "ffffff", "help"]
difficulty: easy
source: "https://www.ctfiot.com/218690.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Hackvent 2024 – Easy

> 赛事：Hackvent 2024 2024 | 方向：misc | 难度：easy | 工具：Python

## 一句话总结

Hackvent 2024 Easy：gifsicle改色+EAN-8条形码校验位

## 攻击链

1. gifsicle --change-color 234 "#000000" --change-color 235 "#ffffff" 04ab...gif > mod.gif
2. 解压help.zip得到9个example*.png
3. 162x191 1-bit grayscale PNG
4. EAN-8 校验位计算:
5. odd_sum = sum(odd positions * 3)
6. even_sum = sum(even positions)
7. check_digit = (10 - (odd+even)%10) % 10
8. 拼接flag

## 关键 payload

```
gifsicle --change-color 234 "#000000" --change-color 235 "#ffffff
```

## 经验教训

gifsicle改透明色+EAN-8校验位算法

## 标签

misc、gifsicle、change-color、ean8、barcode、python-check-digit、png-extract

## 参考来源

- https://www.ctfiot.com/218690.html
- 原文件：Hackvent_2024_–_Easy.full.md
