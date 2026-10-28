---
title: "【ACTF2022】从 Fuzz 到 XCTF 赛题"
category: pwn
tags: ["ACTF", "pwn", "Fuzz", "randint-random-op", "demo-ptmalloc2", "fmt-string"]
signals: ["ACTF 2022", "Fuzz", "randint-random-op", "demo-ptmalloc2", "fmt-string", "key_free-arbitrary-free", "write_in-arbitrary-write", "2D-coord-tree", "heap_exploit", "ACTF", "Nameless_a", "demo", "XCTF", "treepwn"]
difficulty: medium
source: "https://www.ctfiot.com/62611.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 【ACTF2022】从 Fuzz 到 XCTF 赛题

> 赛事：ACTF 2022 | 方向：pwn | 难度：medium

## 一句话总结

ACTF 2022 Nameless_a 经验分享，从 Fuzz demo 入门到 XCTF treepwn 实战的二维坐标 UAF。

## 攻击链

1. 堆题 Fuzz demo（add/delet/edit/show/leak/key_free/write_in/exit 7 个功能）/Fuzz 脚本 0x1000 轮每 10 轮 add 每 2 轮 delet 每 3 轮 show 检查 x55/x56 指针前缀/XCTF 赛题 treepwn 2D 坐标二叉树 add/edit/delet/show/query/批量 delet(i,j) 9x9 触发后 add(66,66,'nameless') + delet(3,6) + edit(3,6,p64(free_hook)) + add(3,6,'/bin/sh\x00') + add(6,6,p64(system)) + delet(3,6) 收壳

## 关键 payload

```
9x9 批量 delet + add(66,66,'nameless') 触发 nameless 链表 → UAF → __free_hook=system
```

## 经验教训

Fuzz 是发现 heap 漏洞模式的有效手段；randint 随机操作 + 检查残留指针前缀可快速发现 UAF；2D 坐标二叉树用 (x,y) 双重索引，批量删除后存在悬挂指针触发 UAF。

## 标签

Fuzz、randint-random-op、demo-ptmalloc2、fmt-string、key_free-arbitrary-free、write_in-arbitrary-write、2D-coord-tree

## 参考来源

- https://www.ctfiot.com/62611.html
- 原文件：【ACTF2022】从Fuzz到XCTF赛题.full.md
