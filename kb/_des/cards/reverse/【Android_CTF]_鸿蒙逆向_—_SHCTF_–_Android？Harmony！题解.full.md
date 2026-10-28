---
title: "【Android CTF】鸿蒙逆向 - SHCTF - Android？Harmony！题解"
category: reverse
tags: ["SHCTF", "reverse", "HarmonyOS", "ArkTS", "ETS-bytecode", "encode-114514"]
signals: ["SHCTF 2024", "HarmonyOS", "ArkTS", "ETS-bytecode", "encode-114514", "mod-95", "ASCII-shift", "maze-create", "promptAction", "reverse", "SHCTF", "secretKey", "encode", "ETS"]
difficulty: medium
source: "https://www.ctfiot.com/213606.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【Android CTF】鸿蒙逆向 - SHCTF - Android？Harmony！题解

> 赛事：SHCTF 2024 | 方向：reverse | 难度：medium

## 一句话总结

SHCTF 2024 鸿蒙 ArkTS 逆向，secretKey + encode 字符编码 (114514*x + 1919810) % 95 + 32 还原 + 迷宫生成。

## 攻击链

1. 鸿蒙 ArkTS/ETS 字节码反编译 Index 构造函数初始化 secretKey + __userInput/validateAndCreateMaze 用 encode(arg0) 与 secretKey 比较 + 调 maze.CreateMaze 生成迷宫写 /What 文件/encode 函数 (114514 * (ord - 32) + 1919810) % 95 + 32 字符编码/逆运算 ((y - 32) * 95^(-1) - 1919810) / 114514 + 32 还原

## 关键 payload

```
secretKey = "[f#fLw)??Pz?#9w)Du[ks[q[#w4D?4P4UJf,kU[f.rDkfwrDtq...)?J.#rP4[qrPDJkkJ|.9J|qffU?k|D4P4P[wkk.)k?JUJ[k#9kww[r??wUfw|PkrPUf.P#f.P#.PwJ4f4q.PU4UPDr9.[9fJ#PqP)cDDffJPDrJ.J4qPP[r[.JfJ4f|?U9#
```

## 经验教训

鸿蒙 ArkTS 编译为 ETS 字节码，可用 HarmonyOS 反编译工具还原；简单模运算 (a*x + b) % m + offset 可通过 mod 逆元还原输入；迷宫生成函数 CreateMaze(arg0) 把 flag 转迷宫。

## 标签

HarmonyOS、ArkTS、ETS-bytecode、encode-114514、mod-95、ASCII-shift、maze-create、promptAction

## 参考来源

- https://www.ctfiot.com/213606.html
- 原文件：【Android_CTF]_鸿蒙逆向_—_SHCTF_–_Android？Harmony！题解.full.md
