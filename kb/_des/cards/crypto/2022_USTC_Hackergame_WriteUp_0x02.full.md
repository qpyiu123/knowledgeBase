---
title: "2022 USTC Hackergame WriteUp 0x02"
category: crypto
tags: ["2022 USTC Hackergame (中科大)", "crypto", "Hackergame", "15-puzzle", "A-star", "数字华容道"]
signals: ["2022 USTC Hackergame (中科大) 2022", "Hackergame", "15-puzzle", "A-star", "数字华容道", "量子计算", "旅行商", "RSA-教学", "Z3", "misc_math", "reverse", "web_unknown", "crypto_unknown", "USTC"]
difficulty: medium
source: "https://www.ctfiot.com/71319.html"
tools: ["IDA", "Z3"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# 2022 USTC Hackergame WriteUp 0x02

> 赛事：2022 USTC Hackergame (中科大) 2022 | 方向：crypto | 难度：medium | 工具：IDA、Z3

## 一句话总结

USTC Hackergame 0x02 量子计算 + 拼图 + RSA + 旅行商 + LaTeX 渲染

## 攻击链

1. 15-puzzle: 数字华容道 + A* 求解 80 步内还原
2. 量子计算 1+1=?: 提示板扰动 → 反推
3. 旅行商 NP-hard: 小规模穷举 / 启发式
4. RSA 教学: 课本 p,q,e → d = inverse(e, (p-1)*(q-1))
5. IDA 静态分析: 找 main 函数 main_loop 状态机还原
6. angr 符号执行: 找路径条件解迷宫 / 表达式
7. Z3 SMT 求解: 线性方程组 / 不等式组
8. LaTeX 渲染: 注入 RCE / 读取文件

## 关键 payload

```
flag{it_works_like_magic_e2a53e77e7}
```

## 经验教训

USTC 信安赛题目趣味性强 + 知识面广；量子计算 / 旅行商 / LaTeX 都是冷门考点

## 标签

Hackergame、15-puzzle、A-star、数字华容道、量子计算、旅行商、RSA-教学、Z3、angr、IDA、LaTeX、APlayer

## 参考来源

- https://www.ctfiot.com/71319.html
- 原文件：2022_USTC_Hackergame_WriteUp_0x02.full.md
