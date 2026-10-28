---
title: "CTF逆向工程深度解析: engineTest – 逻辑门电路引擎的完整破解"
category: reverse
tags: ["公众号文章", "reverse", "reverse", "ELF", "Z3", "SAT"]
signals: ["公众号文章 2024", "reverse", "ELF", "Z3", "SAT", "逻辑门", "电路模拟", "符号执行", "flag", "ELF64", "stripped", "aaa", "main"]
difficulty: hard
source: "https://www.ctfiot.com/284044.html"
tools: ["Radare2", "Z3"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# CTF逆向工程深度解析: engineTest – 逻辑门电路引擎的完整破解

> 赛事：公众号文章 2024 | 方向：reverse | 难度：hard | 工具：Radare2、Z3

## 一句话总结

逻辑门电路模拟flag验证，Z3建模为SAT求解

## 攻击链

1. 静态分析ELF64 stripped二进制r2 aaa; s main; pdf
2. 解析cp/ip/op三个文件结构：电路配置+输入映射+输出映射
3. 提取门电路节点表+坐标编码
4. Z3建模为布尔可满足性问题求解flag
5. stdin输入36字符flag走完整电路验证

## 关键 payload

```
r2 -q -c 'aaa; s main; pdf' ./engineTest; Solver().add(...)
```

## 经验教训

复杂flag验证可降为SAT/Z3约束求解

## 标签

reverse、ELF、Z3、SAT、逻辑门、电路模拟、符号执行

## 参考来源

- https://www.ctfiot.com/284044.html
- 原文件：CTF逆向工程深度解析-_engineTest_–_逻辑门电路引擎的完整破解.full.md
