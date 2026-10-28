---
title: "Fuzz 在 CTF 中的基础利用"
category: pwn
tags: ["公众号文章", "pwn", "fuzz", "pwn", "tree", "mbr-structure"]
signals: ["公众号文章 2025", "fuzz", "pwn", "tree", "mbr-structure", "0-1000-random", "double-free", "crash-detect", "heap_exploit", "Fuzz", "CTF", "EOFError", "MBR", "obj1"]
difficulty: medium
source: "https://www.ctfiot.com/262435.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Fuzz 在 CTF 中的基础利用

> 赛事：公众号文章 2025 | 方向：pwn | 难度：medium

## 一句话总结

Fuzz在CTF基础利用：树形结构+随机操作+EOFError检测漏洞

## 攻击链

1. MBR A树形结构：MBR A1/MBR A2→obj1, obj2...
2. 树满TooManyElementsError重试
3. EOFError=找到漏洞
4. 0-1000轮循环
5. 每10次add，每2次delete
6. 随机a=0-8, b=0-8
7. delete记录+堆风水构造
8. 期望<20行有效命令触发double free
9. 重投机制

## 关键 payload

```
TooManyElementsError → retry; EOFError → success
```

## 经验教训

堆漏洞Fuzz可降低堆风水调试难度

## 标签

fuzz、pwn、tree、mbr-structure、0-1000-random、double-free、crash-detect

## 参考来源

- https://www.ctfiot.com/262435.html
- 原文件：Fuzz_在_CTF_中的基础利用.full.md
