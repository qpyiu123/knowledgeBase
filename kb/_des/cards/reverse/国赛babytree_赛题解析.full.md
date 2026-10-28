---
title: "国赛babytree 赛题解析"
category: reverse
tags: ["国赛 babytree (Swift)", "reverse", "Swift逆向", "swiftc -dump-ast", "var b/k/r0/r1/r2/r3", "key循环移位"]
signals: ["国赛 babytree (Swift) 2024", "Swift逆向", "swiftc -dump-ast", "var b/k/r0/r1/r2/r3", "key循环移位", "反向异或", "42字节目标", "[UInt8]", "reverse", "Swift", "babytree", "key", "swiftc", "dump-ast"]
difficulty: medium
source: "https://www.ctfiot.com/162996.html"
tools: ["Radare2"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 国赛babytree 赛题解析

> 赛事：国赛 babytree (Swift) 2024 | 方向：reverse | 难度：medium | 工具：Radare2

## 一句话总结

Swift babytree 逆向：key="345y" 4 字节循环移位 + r0/r1/r2/r3 异或 + 42 字节目标反推。

## 攻击链

1. Swift babytree 逆向 (swiftc -dump-ast hello.swift)
2. var key = "345y" (4 字节)
3. var data = CommandLine.arguments[1]
4. check(data, key) 函数
5. var b = [UInt8](data.utf8)
6. var k = [UInt8]("345y".utf8) = [51, 52, 53, 121]
7. for i in 0..b.count-4:
8. r0,r1,r2,r3 = b[i..i+3]
9. b[i+0] = r2 ^ ((k[0] + (r0>>4)) & 0xff)
10. b[i+1] = r3 ^ ((k[1] + (r1>>2)) & 0xff)
11. b[i+2] = r0 ^ k[2]
12. b[i+3] = r1 ^ k[3]
13. k = [k[1], k[2], k[3], k[0]]  # 循环左移
14. return b == [88,35,88,225,7,201,57,94,77,56,75,168,72,218,64,91,16,101,32,207,73,130,74,128,76,201,16,248,41,205,103,84,91,99,79,202,22,131,63,255,20,16]
15. 反向: 倒序循环 + k 循环右移 + r0/r1/r2/r3 恢复

## 关键 payload

```
[88,35,88,225,...] + key 循环移位反推
```

## 经验教训

Swift 编译产物可用 swiftc -dump-ast 看 AST 还原源码; 4 字节 key 循环移位加密是经典 pattern; 反向算法倒序循环 + k 循环右移。

## 标签

Swift逆向、swiftc -dump-ast、var b/k/r0/r1/r2/r3、key循环移位、反向异或、42字节目标、[UInt8]

## 参考来源

- https://www.ctfiot.com/162996.html
- 原文件：国赛babytree_赛题解析.full.md
