---
title: "SWPUCTF 2021 新生赛 - 老鼠走迷宫"
category: reverse
tags: ["SWPUCTF", "reverse", "pyinstxtractor", "pyc-decompile", "maze-dfs", "md5-of-path"]
signals: ["SWPUCTF 2021", "pyinstxtractor", "pyc-decompile", "maze-dfs", "md5-of-path", "reverse", "SWPUCTF", "EXE", "pyc", "DFS", "md5", "struct"]
difficulty: easy
source: "https://www.ctfiot.com/146558.html"
tools: ["Python"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# SWPUCTF 2021 新生赛 - 老鼠走迷宫

> 赛事：SWPUCTF 2021 | 方向：reverse | 难度：easy | 工具：Python

## 一句话总结

SWPUCTF 2021 新生赛 RE 题：pyinstxtractor 拆 EXE → pyc 补头 → 反编译 → DFS 迷宫 → md5 路径。

## 攻击链

1. 文件 MZ 头识别为 EXE
2. pyinstxtractor.py 反编译为 5.pyc (无后缀) + struct.pyc
3. 用 struct.pyc 前 16 字节补齐 5.pyc 头
4. tool.lu/pyc 反编译得 .py 文件
5. 删除 return None 死代码
6. 加 for row in maze: print(row) 打印 25x25 maze
7. DFS 走迷宫 (0 可走, 1 墙) 从 (0,1) 到 (24,23)
8. wasd 表示最短路径 sssssddssddssaaaassssddwwddddssssssaawwaassssddssaassddddwwddssddwwwwwwwwaawwddwwwwaaaawwddwwwwddssssddwwwwddddwwddddssaassaassddddssddssaassssssddsssssss
9. 最后追加 s (因为终点外还要走一格)
10. flag = md5("sssssddssddssaa...") = 69193150b15c87d39252d974bc323217

## 关键 payload

```
md5("sssssddssddssaa...ddsssssss")
```

## 经验教训

PyInstaller 打包 EXE 提取 pyc 只需补 16 字节头，常见反编译入口点。

## 标签

pyinstxtractor、pyc-decompile、maze-dfs、md5-of-path

## 参考来源

- https://www.ctfiot.com/146558.html
- 原文件：SWPUCTF_2021_新生赛-老鼠走迷宫.full.md
