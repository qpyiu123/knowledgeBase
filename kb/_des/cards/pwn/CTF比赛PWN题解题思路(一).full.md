---
title: "CTF比赛PWN题解题思路(一)"
category: pwn
tags: ["公众号文章（小话安全）", "pwn", "pwn", "栈溢出", "ret2shell", "IDA"]
signals: ["公众号文章（小话安全） 2024", "pwn", "栈溢出", "ret2shell", "IDA", "入门", "rop", "PWN", "ROP", "admin", "x405D36", "shell", "data", "xc0"]
difficulty: easy
source: "https://www.ctfiot.com/201125.html"
tools: ["IDA"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# CTF比赛PWN题解题思路(一)

> 赛事：公众号文章（小话安全） 2024 | 方向：pwn | 难度：easy | 工具：IDA

## 一句话总结

4道PWN入门题，栈溢出+返回地址覆盖+ROP思路

## 攻击链

1. 题1：栈溢出admin+51字符+0x405D36覆盖返回地址shell函数
2. 题2：data输入0xc0字节覆盖v7变量与v5比较触发shell
3. 题3：gets栈溢出+RDI指向/bin/sh+调用system
4. 题4：gets栈溢出+vmmap找可写地址注入/bin/sh再system

## 关键 payload

```
payload = b"a"*32+b"b"*8+rop()  # 含add rax,1;ret 循环
```

## 经验教训

栈溢出三要素：覆盖长度+目标地址+payload构造

## 标签

pwn、栈溢出、ret2shell、IDA、入门

## 参考来源

- https://www.ctfiot.com/201125.html
- 原文件：CTF比赛PWN题解题思路(一).full.md
