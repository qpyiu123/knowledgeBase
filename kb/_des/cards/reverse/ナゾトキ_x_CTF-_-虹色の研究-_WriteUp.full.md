---
title: "ナゾトキ x CTF? - 虹色の研究 - WriteUp"
category: reverse
tags: ["ナゾトキ", "reverse", "虹色の研究", "MineNumber-7", "reversing", "decompile"]
signals: ["ナゾトキ 2023", "虹色の研究", "MineNumber-7", "reversing", "decompile", "ASCII-sum", "0x309", "7 color", "日语", "reverse", "CTF", "MineNumber", "flag", "Search"]
difficulty: easy
source: "https://www.ctfiot.com/117900.html"
tools: ["netcat"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# ナゾトキ x CTF? - 虹色の研究 - WriteUp

> 赛事：ナゾトキ 2023 | 方向：reverse | 难度：easy | 工具：netcat

## 一句话总结

ナゾトキ x CTF 虹色の研究（日语 CTF 入门题），MineNumber=777 触发 flag 字符串输出。

## 攻击链

1. 1. nc 12345 启动 MineNumber Search Engine /2. 输入名字生成 MineNumber /3. strings + grep flag/4. 反编译：local_58 字符串 ASCII 求和 /5. 输入名字 ASCII 和 = 0x309 (777) 触发 flag

## 关键 payload

```
local_64 == 0x309  name ASCII sum = 777  flag.txt
```

## 经验教训

日语 CTF 入场题；ASCII 字符求和触发 flag 是入门级；strings + grep 找 flag 字符串；反编译看比较常量 0x309。

## 标签

虹色の研究、MineNumber-7、reversing、decompile、ASCII-sum、0x309、7 color、日语

## 参考来源

- https://www.ctfiot.com/117900.html
- 原文件：ナゾトキ_x_CTF-_-虹色の研究-_WriteUp.full.md
