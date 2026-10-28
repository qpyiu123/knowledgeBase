---
title: "ByteCTF 逆向解析 - babyapk"
category: reverse
tags: ["ByteCTF", "reverse", "Flutter babyapk", "blutter解析", "main.dart", "simple.dart"]
signals: ["ByteCTF 2024", "Flutter babyapk", "blutter解析", "main.dart", "simple.dart", "m3N4B5V6函数", "Rust FFI", "z3约束求解", "32e750c8fb214562af22973fb5176b9c", "reverse", "ByteCTF", "babyapk", "Flutter", "APK"]
difficulty: hard
source: "https://www.ctfiot.com/208437.html"
tools: ["IDA", "Rust", "Z3"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# ByteCTF 逆向解析 - babyapk

> 赛事：ByteCTF 2024 | 方向：reverse | 难度：hard | 工具：IDA、Rust、Z3

## 一句话总结

ByteCTF babyapk 逆向 — Flutter APK blutter 解析 + IDA 找 m3N4B5V6 + Frida hook app.so + z3 解 4 轮 8 变量非线性约束 + 32e750c8... + 4 个 - 位置穷举 + byte_18E46 表。

## 攻击链

1. Flutter APK, jadx 无法看, 用 blutter 解析 libapp.so
2. main.dart 调 m3N4B5V6() 函数
3. 找到 simple.dart 包含验证逻辑
4. IDA 搜 Simple/m3N4B5V6 找加密函数
5. Frida hook app.so 多个 native 函数 → 没反应, 怀疑长度检测
6. 改长度, HOOK 情况: 长度为 0x2d, {} 内为 36 位
7. 加密函数逆推, 4 轮 8 变量非线性约束
8. z3 解: 数组解都是可显字符 → 32e750c8fb214562af22973fb5176b9c
9. 长度 32 包含 4 个 -, 穷举 - 位置
10. byte_18E46 表查 byte → 验证 hyphen 位置

## 关键 payload

```
blutter main.dart simple.dart / IDA 搜 Simple m3N4B5V6 / Frida hook app.so / z3 4 轮 8 变量约束 / 32e750c8... 32 字符 / 4 个 - 位置穷举 / byte_18E46 表
```

## 经验教训

Flutter APK 逆向核心是 blutter 解析 libapp.so;Rust FFI 加密函数 IDA 找 cross-ref;z3 解非线性约束 + 穷举小集合是混合策略。

## 标签

Flutter babyapk、blutter解析、main.dart、simple.dart、m3N4B5V6函数、Rust FFI、z3约束求解、32e750c8fb214562af22973fb5176b9c、4个-位置、byte_18E46表、validate_hyphen_positions、app.so、Native Hook

## 参考来源

- https://www.ctfiot.com/208437.html
- 原文件：ByteCTF逆向解析.full.md
