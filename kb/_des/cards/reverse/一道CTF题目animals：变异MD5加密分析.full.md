---
title: "一道CTF题目 animals 变异 MD5 加密分析"
category: reverse
tags: ["看雪", "reverse", "变异MD5-init-constant", "OLLVM-control-flow", "anti-patch-NOP", "scanf-animal-shop"]
signals: ["看雪 2024", "变异MD5-init-constant", "OLLVM-control-flow", "anti-patch-NOP", "scanf-animal-shop", "strncat-v25", "dword_6080F4-limit", "dword_608138-counter", "F-xor-and-hack", "reverse", "animals", "CTF", "OLLVM", "NOP"]
difficulty: hard
source: "https://www.ctfiot.com/283268.html"
tools: ["OLLVM"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 一道CTF题目 animals 变异 MD5 加密分析

> 赛事：看雪 2024 | 方向：reverse | 难度：hard | 工具：OLLVM

## 一句话总结

animals CTF 逆向题，OLLVM 控制流平坦化 + NOP patch + 变异 MD5 加密 + 动物商店菜单选项。

## 攻击链

1. 1. OLLVM 控制流平坦化 + NOP patch 0x08750a74/0x13751574 3-7 字节/2. 6 个动物选项 (cat/dog/fox/panda/dragon/monkey) + dword_6080F4 < 10 + dword_608138 counter/3. strncat 到 v25 256 字节 + Win! 触发 md5(input) = flag/4. 变异 MD5: state[0]=0xEFCDAB89 改成 0x67452301 调换 init constant/5. F 函数 = (x & y) | (~x & z) 改为 (x & y) | (y & ~z) 即 F 改 G

## 关键 payload

```
patch 0x08750a74/0x13751574 为 NOP  变异 MD5 state 0xEFCDAB89  F 改 G
```

## 经验教训

OLLVM 控制流平坦化用 patch 0x08750a74 (mov/jz 反汇编码) 改 NOP 还原；MD5 变异 = 改 init state + F/G 函数替换；6 个动物选项 dword_6080F4 < 10 限制次数。

## 标签

变异MD5-init-constant、OLLVM-control-flow、anti-patch-NOP、scanf-animal-shop、strncat-v25、dword_6080F4-limit、dword_608138-counter、F-xor-and-hack、F-xor-patch

## 参考来源

- https://www.ctfiot.com/283268.html
- 原文件：一道CTF题目animals：变异MD5加密分析.full.md
