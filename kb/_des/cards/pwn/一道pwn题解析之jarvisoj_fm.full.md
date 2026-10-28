---
title: "一道 pwn 题解析之 jarvisoj_fm"
category: pwn
tags: ["jarvisoj", "pwn", "fmt-string-leak", "fmt-write-%n", "%hhn-byte-write", "AAAA-%p-%p-pivot"]
signals: ["jarvisoj 2022", "fmt-string-leak", "fmt-write-%n", "%hhn-byte-write", "AAAA-%p-%p-pivot", "format-string-offset-11", "GOT-overwrite", "fmt_string", "jarvisoj_fm", "AAAA-", "AAAA", "GOT", "addr"]
difficulty: easy
source: "https://www.ctfiot.com/94853.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 一道 pwn 题解析之 jarvisoj_fm

> 赛事：jarvisoj 2022 | 方向：pwn | 难度：easy

## 一句话总结

jarvisoj_fm 格式化字符串经典题，AAAA-%p 找偏移 11 + %4c%13$n 写 4 字节到任意地址。

## 攻击链

1. 1. 泄露栈偏移：AAAA-%p-%p-%p...%p-%p-%p 找 AAAA 出现位置（11）/2. 改写 GOT：%4c%13$n + addr=0x0804A02C 偏移处 /3. 4c 字符宽度 + %13$n 写到第 13 个参数（指向 addr）/4. 触发原 printf 调用走改写后的 GOT

## 关键 payload

```
addr=0x0804A02C  payload=b"%4c%13$n"  偏移 11 = 0xB
```

## 经验教训

格式化字符串 %n 系列可任意地址写；%hhn = 单字节写；AAAA-%p-%p... 找 AAAA 在栈上偏移；%Nc 控制写入字符数。

## 标签

fmt-string-leak、fmt-write-%n、%hhn-byte-write、AAAA-%p-%p-pivot、format-string-offset-11、GOT-overwrite

## 参考来源

- https://www.ctfiot.com/94853.html
- 原文件：一道pwn题解析之jarvisoj_fm.full.md
