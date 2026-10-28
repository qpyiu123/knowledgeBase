---
title: "CRYPTO｜西湖论剑 2022 中国杭州网络安全技能大赛初赛官方 Write Up"
category: crypto
tags: ["西湖论剑", "crypto", "MyCurveErrorLearn ECHNP", "MyErrorLearn MIHNP", "MyErrorLearnTwice LLL对角阵", "LockByLock Pollard kangaroo"]
signals: ["西湖论剑 2022", "MyCurveErrorLearn ECHNP", "MyErrorLearn MIHNP", "MyErrorLearnTwice LLL对角阵", "LockByLock Pollard kangaroo", "MyOracle MT19937 LSB", "椭圆曲线HNP", "模逆HNP", "Coppersmith", "crypto_rsa", "CRYPTO", "MyCurveErrorLearn", "ECHNP", "HNP"]
difficulty: hard
source: "https://www.ctfiot.com/97733.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# CRYPTO｜西湖论剑 2022 中国杭州网络安全技能大赛初赛官方 Write Up

> 赛事：西湖论剑 2022 | 方向：crypto | 难度：hard

## 一句话总结

西湖论剑 2022 CRYPTO 官方 WP — MyCurveErrorLearn ECHNP 椭圆 HNP + LockByLock Pollard kangaroo + MyErrorLearn MIHNP Coppersmith + MyErrorLearnTwice LLL 对角阵 + MyOracle MT19937 LSB state 恢复。

## 攻击链

1. MyCurveErrorLearn: ECHNP(DH) 椭圆曲线 Hidden Number Problem, 输入 0 得 t=0, t 与 oracle 输出多项式关系
2. LockByLock: secureProcedure 嵌套加密, A 加密 c1, B 加密 c1 得 c2, A 解 c2 得 c3
3. 两次输入得中间值, Pollard's kangaroo 在 e 范围内求解
4. MyErrorLearn: MIHNP 模逆 HNP, 二元 Coppersmith 解多项式
5. MyErrorLearnTwice: d 组输出, LLL 求对角阵 + 最短格向量恢复 e
6. MyOracle: 模是偶数时泄露 r LSB, 构造矩阵恢复 MT19937 全部 state

## 关键 payload

```
ECHNP(DH) / LockByLock kangaroo / MIHNP Coppersmith / MIHNP LLL 对角阵 / MT19937 LSB state 恢复
```

## 经验教训

HNP (Hidden Number Problem) 是密码学隐藏数问题模板;ECHNP/MIHNP/LWE 都基于 LLL;Pollard kangaroo 适合已知 e 范围;MT19937 LSB oracle 是 RNG 恢复经典。

## 标签

MyCurveErrorLearn ECHNP、MyErrorLearn MIHNP、MyErrorLearnTwice LLL对角阵、LockByLock Pollard kangaroo、MyOracle MT19937 LSB、椭圆曲线HNP、模逆HNP、Coppersmith、Pollard kangaroo e范围爆破、MT19937 state恢复

## 参考来源

- https://www.ctfiot.com/97733.html
- 原文件：CRYPTO｜西湖论剑·2022中国杭州网络安全技能大赛初赛官方Write_Up.full.md
