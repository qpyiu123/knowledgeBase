---
title: "UIUCTF 2024 Writeup - 狼组"
category: web
tags: ["UIUCTF", "web", "md5-injection", "sqlite-binary-where", "syscall-sandbox", "format-string-shellcode"]
signals: ["UIUCTF 2024", "md5-injection", "sqlite-binary-where", "syscall-sandbox", "format-string-shellcode", "osint", "simple-xor-cipher", "matrix-solver", "sqli", "UIUCTF", "MD5", "binary", "SQL", "syscall"]
difficulty: medium
source: "https://www.ctfiot.com/191124.html"
tools: ["Z3"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# UIUCTF 2024 Writeup - 狼组

> 赛事：UIUCTF 2024 | 方向：web | 难度：medium | 工具：Z3

## 一句话总结

UIUCTF 2024 狼组：MD5 binary SQL 注入 + syscall sandbox 盲注 + z3 矩阵 + OSINT 系列。

## 攻击链

1. Fare Evasion (Web): SQLite 注入 + MD5 binary 注入
2. todo: convert md5 to hex string instead of latin1" → 爆破 5/6 字符的 MD5
3. 让 MD5 字节序列 latin1 中包含 'or' 闭合 SQL
4. or 1; → '=0-- → 爆破 xdax82'or'1+xd7Vpx1bwxd7.xb6
5. Syscalls (Pwn): shellcode 限制 - 只能用 openat+mmap 不能 write
6. 侧信道爆破 flag 字符 - mov dl, [rdi+pos]; cmp cl, char; jz loop; mov al, 60 (exit)
7. 按位爆破 uiuctf{a53aaf9aaed1fa5906de364a1162e0833c57a0246ab9ffc}
8. OSINT 系列 (3 题): LISA 地铁局 + Instagram + Google Maps
9. Night: Massachusetts Ave Bridge, Boston → Arlington Street, Boston
10. New Dallas: 经纬度坐标铁路交叉点
11. Summarize (Reverse): 6 个 9 位数 z3 求解
12. Goose Chase: 200MB dump + WinDbg !analyze -v
13. X Marked the Spot: 7 字节 XOR 已知 uiuctf{ 解首尾
14. Without a Trace: 5 元 1 次方程 sympy.solve
15. Determined: 矩阵推理 (Artin 引用)

## 关键 payload

```
SQL: ''or 1; (MD5 bytes 形式)
```

## 经验教训

MD5 输出是 16 字节二进制而非 16 进制；用 latin1 转换可含 'or' SQL 注入字符。

## 标签

md5-injection、sqlite-binary-where、syscall-sandbox、format-string-shellcode、osint、simple-xor-cipher、matrix-solver

## 参考来源

- https://www.ctfiot.com/191124.html
- 原文件：UIUCTF_2024_Writeup.full.md
