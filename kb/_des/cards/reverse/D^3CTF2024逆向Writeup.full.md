---
title: "D^3CTF 2024 逆向 Writeup"
category: reverse
tags: ["D3CTF", "reverse", "xtea-variant", "ida-python", "recur-func", "rand-graph"]
signals: ["D3CTF 2024", "xtea-variant", "ida-python", "recur-func", "rand-graph", "dfa-attack", "reverse", "CTF", "XTEA", "IDA", "Python", "delta", "xE8017300", "fakeflag"]
difficulty: hard
source: "https://www.ctfiot.com/176701.html"
tools: ["IDA", "Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# D^3CTF 2024 逆向 Writeup

> 赛事：D3CTF 2024 | 方向：reverse | 难度：hard | 工具：IDA、Python

## 一句话总结

D^3CTF 2024 逆向 2 道：XTEA 变体解密 + IDA Python 递归函数图。

## 攻击链

1. XTEA 变体 delta=0xE8017300
2. 32 轮减法 + 32 轮加法
3. 暴力逆向还原 fakeflag
4. 32 轮右移 1 位 + 0x84A6972F 异或
5. IDA Python recur 找函数关系
6. 提取 xor 推导下一函数
7. rand 关系图遍历

## 关键 payload

```
XTEA 变体 + IDA 递归脚本
```

## 经验教训

XTEA 变体只需调整 delta 和轮数；IDA Python recur() 适合还原复杂调用图。

## 标签

xtea-variant、ida-python、recur-func、rand-graph、dfa-attack

## 参考来源

- https://www.ctfiot.com/176701.html
- 原文件：D^3CTF2024逆向Writeup.full.md
