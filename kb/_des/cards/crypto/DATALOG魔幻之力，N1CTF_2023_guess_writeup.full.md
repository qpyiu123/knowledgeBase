---
title: "DATALOG 魔幻之力，N1CTF 2023 guess writeup"
category: crypto
tags: ["N1CTF", "crypto", "souffle", "datalog", "symbol-table", "ordinal"]
signals: ["N1CTF 2023", "souffle", "datalog", "symbol-table", "ordinal", "静态分析", "推理规则", "misc_math", "N1CTF", "guess", "Souffl", "Datalog", "flag", "number"]
difficulty: hard
source: "https://www.ctfiot.com/141277.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# DATALOG 魔幻之力，N1CTF 2023 guess writeup

> 赛事：N1CTF 2023 | 方向：crypto | 难度：hard

## 一句话总结

N1CTF 2023 guess 题用 Soufflé 静态分析引擎 + Datalog 推理规则恢复 flag 序号。

## 攻击链

1. 阅读 Soufflé 文档了解符号表机制
2. 理解 ordinal number 表示法
3. 利用 ord(@GETFLAG()) 推理规则
4. HINT(_) 触发 FLAG 关系防止被优化
5. __LINE__ 计算 salt 个数推算 flag 序号
6. as(序号, symbol) 反查
7. 36 轮不重置规则

## 关键 payload

```
ord() 推 symbol table 序号 + __LINE__ 动态调整
```

## 经验教训

Soufflé 等静态分析引擎的 symbol table + 推理规则是新型 CTF 出题方向。

## 标签

souffle、datalog、symbol-table、ordinal、静态分析、推理规则

## 参考来源

- https://www.ctfiot.com/141277.html
- 原文件：DATALOG魔幻之力，N1CTF_2023_guess_writeup.full.md
