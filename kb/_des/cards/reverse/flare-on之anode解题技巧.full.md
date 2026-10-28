---
title: "flare-on 之 anode 解题技巧"
category: reverse
tags: ["FLARE-ON", "reverse", "nodejs", "nexe", "js-extract", "switch-fsm"]
signals: ["FLARE-ON 2018", "nodejs", "nexe", "js-extract", "switch-fsm", "bigint-truthy", "state-machine", "reverse", "FLARE-ON", "anode", "NodeJS", "NEXE", "Enter", "flag"]
difficulty: medium
source: "https://www.ctfiot.com/80126.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# flare-on 之 anode 解题技巧

> 赛事：FLARE-ON 2018 | 方向：reverse | 难度：medium

## 一句话总结

FLARE-ON anode NodeJS NEXE 打包逆向，从十六进制编辑提取 JS 源码 + 状态机逆推。

## 攻击链

1. 识别 NEXE 打包的 NodeJS 可执行
2. 十六进制编辑搜 "Enter flag" 特征字符串
3. 提取 JS 源码
4. 解读 44 字节输入 → 16 个 long state 状态机
5. state = 1337; state ^= random(2^30)
6. switch(state) 跳转
7. 大数 1n / 93909087n 永真 → 走 if 分支
8. 逆推 b[i] 异或/加减
9. 对比 target 数组

## 关键 payload

```
NEXE 提 JS 源码 + 长 switch 状态机逆推
```

## 经验教训

NEXE 把 JS 源码直接打包进 EXE（无加密无压缩），十六进制编辑就能还原。

## 标签

nodejs、nexe、js-extract、switch-fsm、bigint-truthy、state-machine

## 参考来源

- https://www.ctfiot.com/80126.html
- 原文件：flare-on之anode解题技巧.full.md
