---
title: "CakeCTF 2022 Writeup"
category: reverse
tags: ["CakeCTF 2022", "reverse", "rev", "nim", "luau", "lua-bytecode"]
signals: ["CakeCTF 2022 2022", "rev", "nim", "luau", "lua-bytecode", "forensics", "welcome", "eqStrings", "reverse", "CakeCTF", "writeup", "nimrev", "zundamon", "survey"]
difficulty: easy
source: "https://www.ctfiot.com/49056.html"
tools: ["GDB"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# CakeCTF 2022 Writeup

> 赛事：CakeCTF 2022 2022 | 方向：reverse | 难度：easy | 工具：GDB

## 一句话总结

CakeCTF 2022 5题writeup：welcome+nimrev+luau+zundamon+survey

## 攻击链

1. welcome: 直接从Discord拿flag
2. nimrev: gdb-peda断eqStrings看参数x/24c
3. luau: viruscamp/luadec构建反编译Lua 5.3字节码
4. zundamon: 日语语音合成软件+隐写
5. 典型: 直接调用eqStrings比较flag

## 关键 payload

```
gdb-peda$ x/24c 0x7ffff7d0f0e0 → CakeCTF{s0m3t1m3s_n0t_C}
```

## 经验教训

NimMainModule中找eqStrings直接拿flag；Lua字节码用luadec反编译

## 标签

rev、nim、luau、lua-bytecode、forensics、welcome、eqStrings

## 参考来源

- https://www.ctfiot.com/49056.html
- 原文件：CakeCTF_2022_Writeup.full.md
