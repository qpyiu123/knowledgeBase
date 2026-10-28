---
title: "RCTF2022 MyCarsShowSpeed 题目分析"
category: pwn
tags: ["RCTF 2022", "pwn", "pwn", "ncurses-game", "winTimes-cnt", "fake-flag-purchase"]
signals: ["RCTF 2022 2023", "pwn", "ncurses-game", "winTimes-cnt", "fake-flag-purchase", "uaf", "car-shop", "double-free", "heap_exploit", "RCTF2022", "PWN", "ncurses", "winTimes", "cheat"]
difficulty: hard
source: "https://www.ctfiot.com/96073.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# RCTF2022 MyCarsShowSpeed 题目分析

> 赛事：RCTF 2022 2023 | 方向：pwn | 难度：hard

## 一句话总结

RCTF2022 赛车游戏 PWN：ncurses 菜单 + winTimes 计数器 + cheat 检测触发 free + 空名 fix/fetch 漏洞 + 6 字节 carName 泄 heap 指针。

## 攻击链

1. 赛车主题 PWN 游戏：菜单 start/show/visit/switch
2. visit 商店: buy/sell/fix/fetch 4 项 + 5 项商品 (NormalCar/SuperCar/LongCar/GhostCar/flag)
3. 关键：winTimes<1000 时 buy('flag') 触发 cheat 检测 → 全 free curCar
4. start() 触发 winTimes++/money+=10 (每次赢得比赛)
5. fetch('') 空名修复触发 fetchTime=0 漏洞
6. fix('') 同样空名触发
7. 泄 heap 通过 switch(4) 接收 CarName 6 字节 = heap 指针
8. heap = u64(name+'\0\0\0') - 0x5e0
9. fix(name) 多次触发 memory corruption
10. buy('NormalCar', p64(heap+0x330)[:6]) 二次购买注入指针
11. buy('NormalCar', 'ssss') 触发 fake chunk 利用
12. buy('flag') 最终触发 flag 字符串读取 (绕过 cheat 检测)

## 关键 payload

```
buy('NormalCar', p64(heap+0x330)[:6]) + buy('NormalCar', p64(heap+0x330)[:6]) + buy('NormalCar', 'ssss') + buy('flag')
```

## 经验教训

字符串结尾 \0\0\0 补齐 u64 解析是固定套路；fix/fetch 用空字符串触发漏洞是赛车游戏常见挖法；多次 buy 注入 fake heap pointer 是 car list 类题目常见利用。

## 标签

pwn、ncurses-game、winTimes-cnt、fake-flag-purchase、uaf、car-shop、double-free

## 参考来源

- https://www.ctfiot.com/96073.html
- 原文件：RCTF2022-MyCarsShowSpeed_题目分析.full.md
