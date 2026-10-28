---
title: "强网杯 S8 初赛 PWN 赛题解析"
category: pwn
tags: ["强网杯", "pwn", "menu-heap", "libc-got-overwrite", "write-what-where", "getenv"]
signals: ["强网杯 2024", "menu-heap", "libc-got-overwrite", "write-what-where", "getenv", "srand-1", "expect-number", "brute-force-sequence", "env", "pwn_unknown", "PWN", "libc", "got", "expect_number"]
difficulty: medium
source: "https://www.ctfiot.com/218976.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 强网杯 S8 初赛 PWN 赛题解析

> 赛事：强网杯 2024 | 方向：pwn | 难度：medium

## 一句话总结

强网杯 S8 PWN 双题：菜单 PWN 改 libc.got 触发 env(getenv) + expect_number srand(1) 序列预测 + 越界读 code base。

## 攻击链

1. 题目 1 (菜单 PWN): 6 个功能 add/free/edit/show/env/write
2. 漏洞: write(6) 任意地址写 + env(5) 调 getenv
3. 利用: 申请 4 个 0x500 chunk + free(1) + free(3) + show(3) 泄 libc
4. libc_addr = u64 - 0x21ace0
5. write(libc + 0x21a118, libc + puts) 改 libc .got
6. env(2) 触发 getenv 调用走篡改的 .got 跳 system
7. 题目 2 (expect_number): srand(1) 产生确定性序列 4 3 2 4 2 4 3 1 2 2 3 4 3 4 4 3...
8. 操作堆栈到 0x60 target + 越界读泄 code base
9. 4 = 累加 2, 3 = 输入 1, 2 = 输入 0
10. 后期: 4/2 = 输入 0, 1/3 = 输入 1
11. choice=2 退出后 recv until k 越界读 → addr = u64 - 0x4c60 (code base)
12. choice=4 触发 'Tell me your favorite number' 接收 payload
13. payload = b'\x00'*0x20 + p64(addr+0x5080) + p64(addr+0x251A) 改后门

## 关键 payload

```
libc.got overwrite + env getenv + srand(1) 序列预测 + choice=4 后门调用
```

## 经验教训

getenv() 内部调用 libc 函数可被 .got 劫持；srand(1) 固定序列爆破是简单 PWN 题常见套路。

## 标签

menu-heap、libc-got-overwrite、write-what-where、getenv、srand-1、expect-number、brute-force-sequence、env、PIE-low-entropy

## 参考来源

- https://www.ctfiot.com/218976.html
- 原文件：强网杯S8初赛_PWN_赛题解析.full.md
