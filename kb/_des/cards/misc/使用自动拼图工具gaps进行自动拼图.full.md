---
title: "使用自动拼图工具 gaps 进行自动拼图"
category: misc
tags: ["CTF练习", "misc", "gaps", "puzzle-solver", "genetic-algorithm", "montage"]
signals: ["CTF练习 2024", "gaps", "puzzle-solver", "genetic-algorithm", "montage", "ImageMagick", "600-pieces", "automatic-puzzle", "MISC", "misc_unknown", "generations", "population", "PNG", "Step"]
difficulty: easy
source: "https://www.ctfiot.com/162924.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 使用自动拼图工具 gaps 进行自动拼图

> 赛事：CTF练习 2024 | 方向：misc | 难度：easy

## 一句话总结

MISC 拼图题 600 张 40×40：montage 拼接 + gaps 遗传算法自动拼图，--generations=400 --population=400 增加迭代。

## 攻击链

1. 600 张 40×40 PNG 图片，无规律命名
2. Step 1: 安装 ImageMagick + GraphicsMagick + montage 拼接
3. montage ./files/*.png -tile 20X30 -geometry +0+0 flag.png
4. 或尝试 30X20 排列
5. Step 2: 安装 poetry + tk + gaps (https://github.com/nemanja-m/gaps)
6. Step 3: gaps run ./flag.png resolve.png --size=40 --generations=20 --population=200
7. Step 4: 调整 tile 维度再跑一次
8. Step 5: 增加迭代: --generations=400 --population=400 --size=40
9. 输出 resolved puzzle image

## 关键 payload

```
gaps run puzzle.png solution.png --size=40 --generations=400 --population=400
```

## 经验教训

gaps 是 CTF MISC 拼图题必备工具，遗传算法自动求解；montage 用于快速拼接预览。

## 标签

gaps、puzzle-solver、genetic-algorithm、montage、ImageMagick、600-pieces、automatic-puzzle、MISC

## 参考来源

- https://www.ctfiot.com/162924.html
- 原文件：使用自动拼图工具gaps进行自动拼图.full.md
