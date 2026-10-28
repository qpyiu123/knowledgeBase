---
title: "CCB CISCN 半决赛 AWDP pwn 题解 (2 道)"
category: pwn
tags: ["CISCN 半决赛 (AWDP)", "pwn", "AWDP", "libc 2.35", "tcache dup", "stdout leak"]
signals: ["CISCN 半决赛 (AWDP) 2024", "AWDP", "libc 2.35", "tcache dup", "stdout leak", "__free_hook", "protobuf", "heap_exploit", "CCB", "CISCN", "pwn", "stdout", "partial", "overwrite"]
difficulty: medium
source: "https://www.ctfiot.com/243175.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# CCB CISCN 半决赛 AWDP pwn 题解 (2 道)

> 赛事：CISCN 半决赛 (AWDP) 2024 | 方向：pwn | 难度：medium

## 一句话总结

CCB CISCN 半决赛 AWDP 模式 pwn 双题 (传统菜单 + protobuf 协议)，都是 stdout partial overwrite + __free_hook/system。

## 攻击链

1. |

## 关键 payload

```
|
```

## 经验教训

AWDP 模式 (Attack With Defense Plus) 攻防兼备，2 道都用 stdout partial overwrite 12 位爆破；protobuf 协议要熟悉 `p32(len) + raw` 的包装。

## 标签

AWDP、libc 2.35、tcache dup、stdout leak、__free_hook、protobuf

## 参考来源

- https://www.ctfiot.com/243175.html
- 原文件：CCB_CISCN_半决赛-AWDP-pwn_题解.full.md
