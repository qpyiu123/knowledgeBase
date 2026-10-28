---
title: "【WP】春秋杯秋季赛 \"PWN 梦空间\" 设计思路与解析"
category: pwn
tags: ["春秋杯", "pwn", "盗梦空间-剧情", "6层梦境", "city-linux-cmd", "hotel-ret2text"]
signals: ["春秋杯 2022", "盗梦空间-剧情", "6层梦境", "city-linux-cmd", "hotel-ret2text", "snow-fmt-text-RWX", "home-UAF", "world-house-of-force", "final-hidden-file", "rce", "PWN", "ret2text", "UAF", "house"]
difficulty: hard
source: "https://www.ctfiot.com/23827.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【WP】春秋杯秋季赛 "PWN 梦空间" 设计思路与解析

> 赛事：春秋杯 2022 | 方向：pwn | 难度：hard

## 一句话总结

春秋杯秋季赛 PWN 梦空间 6 层梦境关卡设计稿，盗梦空间 + 神秘博士剧情融合，覆盖 ret2text/格式化字符串/UAF/house of force 多种 PWN 技巧。

## 攻击链

1. 6 层梦境 city→hotel→snow→home→world→final/city linux 命令 + hotel 0x38 padding + p64(0x4006B6) 跳 backdoor + snow 一次 fmt 写 .text RWX + home UAF + world 改 top chunk -1 + house of force 把 top chunk 迁到 got 区 + free.got=puts-ret gadget 泄 libc + 改 free=system

## 关键 payload

```
hotel_backdoor = 0x4006B6  snow %1515c%43$n  world house of force got 区域
```

## 经验教训

6 层关卡设计覆盖栈溢出 / fmt 写 .text 段 / UAF / House of Force 全 PWN 攻击面；.text 段 RWX 是绕过 NX 的方法；House of Force 把 top chunk 迁到 got 区是经典劫持路线。

## 标签

盗梦空间-剧情、6层梦境、city-linux-cmd、hotel-ret2text、snow-fmt-text-RWX、home-UAF、world-house-of-force、final-hidden-file

## 参考来源

- https://www.ctfiot.com/23827.html
- 原文件：【WP】春秋杯秋季赛“PWN梦空间”-设计思路与解析.full.md
