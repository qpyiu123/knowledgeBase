---
title: "Hack.lu 2024 Getting into Shape 解析"
category: reverse
tags: ["Hack.lu 2024", "reverse", "rev", "wasm", "ttf", "rust"]
signals: ["Hack.lu 2024 2024", "rev", "wasm", "ttf", "rust", "regex-automata", "cipher", "expand-32-byte-k", "salsa20", "reverse", "Hack", "Getting", "into", "Shape"]
difficulty: hard
source: "https://www.ctfiot.com/216393.html"
tools: ["Rust"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# Hack.lu 2024 Getting into Shape 解析

> 赛事：Hack.lu 2024 2024 | 方向：reverse | 难度：hard | 工具：Rust

## 一句话总结

Hack.lu 2024 Getting into Shape：TTF嵌WASM+Rust cipher+Salsa20

## 攻击链

1. TTF文件包含WASM二进制
2. 提取 0x1eb9c 偏移 0x12841b 长度
3. d_Usersmsanftcargoregistrysrci 路径
4. Rust regex-automata 0.4.8 + cipher 0.4.4
5. StreamCipherError
6. 关键字 expand 32-byte k (Salsa20 constant)
7. flag{([^{}]*)} 正则
8. yasss!!" emoji 0xf09f988c 0xf09f9285
9. nahf09f9890f09f9890" 隐藏flag

## 关键 payload

```
expand 32-byte k (Salsa20 constant)
```

## 经验教训

Rust WASM二进制可藏在字体文件TTF中

## 标签

rev、wasm、ttf、rust、regex-automata、cipher、expand-32-byte-k、salsa20

## 参考来源

- https://www.ctfiot.com/216393.html
- 原文件：Hack.lu_2024_Getting_into_Shape_解析.full.md
