---
title: "b3typer - bi0sCTF 2022"
category: pwn
tags: ["bi0sCTF 2022", "pwn", "WebKit", "JSC", "JavaScriptCore", "B3"]
signals: ["bi0sCTF 2022 2022", "WebKit", "JSC", "JavaScriptCore", "B3", "JIT", "range-analysis", "integer-underflow", "OOB-write", "pwn_unknown", "reverse", "rangeForMask", "debug"]
difficulty: hard
source: "https://www.ctfiot.com/92870.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# b3typer - bi0sCTF 2022

> 赛事：bi0sCTF 2022 2022 | 方向：pwn | 难度：hard

## 一句话总结

WebKit B3 rangeForMask 偏差 + 整数下溢消除边界检查

## 攻击链

1. 编译 debug 模式 WebKit JSC
2. 分析 rangeForMask 偏差 [0,2] vs [1,2]
3. 触发 c & 2 = 0 → 整数下溢到 -1
4. 编译器假定 idx ≥ 0 跳过减法范围检查
5. 覆盖 butterfly 后续数组 length=0x1337 OOB 读写
6. 暴露 structureID bits → 类型混淆 + 任意 r/w

## 关键 payload

```
let c = b & 2; let idx = c - 1; if (idx < 1) { idx += -0x80000000; }
```

## 经验教训

JIT range analysis 若起点假定偏移，实际 0 也可触发下溢消除上界检查；patch Reflect.strid 暴露 structureID 即可类型混淆

## 标签

WebKit、JSC、JavaScriptCore、B3、JIT、range-analysis、integer-underflow、OOB-write、butterfly、structID

## 参考来源

- https://www.ctfiot.com/92870.html
- 原文件：b3typer_–_bi0sCTF_2022.full.md
