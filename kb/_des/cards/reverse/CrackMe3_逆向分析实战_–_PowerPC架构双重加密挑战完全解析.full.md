---
title: "CrackMe3 逆向分析实战 – PowerPC架构双重加密挑战完全解析"
category: reverse
tags: ["公众号文章", "reverse", "rev", "powerpc", "idea", "rc6"]
signals: ["公众号文章 2024", "rev", "powerpc", "idea", "rc6", "dual-cipher", "radare2", "abiv2", "stripped", "reverse", "PowerPC64", "CrackMe", "IDEA", "RC6"]
difficulty: medium
source: "https://www.ctfiot.com/282755.html"
tools: ["Radare2"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# CrackMe3 逆向分析实战 – PowerPC架构双重加密挑战完全解析

> 赛事：公众号文章 2024 | 方向：reverse | 难度：medium | 工具：Radare2

## 一句话总结

PowerPC64 CrackMe，IDEA+RC6双重加密逆向

## 攻击链

1. file命令识别ELF 64-bit LSB PowerPC abiv2
2. radare2 r2 -q -c 'aaa; iz'列字符串
3. Bingo!"在0x100024a8
4. fcn.10001740(2528字节)主要加密逻辑
5. fcn.10000c64(1196字节)辅助加密/密钥派生
6. 16字节(128-bit)IDEA标准Key
7. 24字节可能是加密输出
8. 双重加密：IDEA加密→RC6加密→与硬编码比较

## 关键 payload

```
r2 -q -c ''aaa; iz'' ./crackme3  # 找Bingo!和加密数据
```

## 经验教训

非x86架构二进制逆向需用file/readelf先确认，r2跨平台支持好

## 标签

rev、powerpc、idea、rc6、dual-cipher、radare2、abiv2、stripped

## 参考来源

- https://www.ctfiot.com/282755.html
- 原文件：CrackMe3_逆向分析实战_–_PowerPC架构双重加密挑战完全解析.full.md
