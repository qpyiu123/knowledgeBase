---
title: "BabyStream – 从 LFSR 到 LPN 的完整攻击复现"
category: crypto
tags: ["BabyStream", "crypto", "LFSR流密码", "feedforward非线性", "4次/16次/63次项", "线性化攻击"]
signals: ["BabyStream 2025", "LFSR流密码", "feedforward非线性", "4次/16次/63次项", "线性化攻击", "GF(2)矩阵", "6.25%噪声", "矛盾方程", "多次随机子集", "crypto_rsa", "BabyStream", "LFSR", "feedforward", "flag"]
difficulty: hard
source: "https://www.ctfiot.com/281936.html"
tools: []
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# BabyStream – 从 LFSR 到 LPN 的完整攻击复现

> 赛事：BabyStream 2025 | 方向：crypto | 难度：hard

## 一句话总结

BabyStream LFSR 流密码 — 128位状态 + feedforward 4/16/63次非线性 + 线性化攻击 (矩阵 A·y 加 6.25% 噪声) + 多次随机子集 2000 次 + O(n) 优化 16384 倍加速 + 93.854% 准确率还原 flag。

## 攻击链

1. 128 位 LFSR + feedforward 非线性
2. 线性部分: x[127] + Σ(x[i] ⊕ x[box[i]]) 覆盖 127 比特
3. 非线性: 4 次 (x[11]&x[22]&x[33]&x[53]) + 16 次 + 63 次项
4. 4 次项概率 1/16 = 6.25% → 93.75% 干净
5. 矩阵 A ∈ GF(2)^(m×n) 已知, y = A·s + noise
6. 传统 O(n·128²) ≈ 268M 次运算
7. 优化: O(n) ≈ 16K 次运算 (列左移 → 行右移 + 反馈位注入 mask)
8. 矛盾方程 (有噪声) → 多次随机子集
9. trials=2000, subset=128, 取准确率最高解
10. 实际达到 93.854% 准确率, 100% byte 匹配
11. Flag: flag{ce2980ad9763b8468882f292dbe9f365}

## 关键 payload

```
LFSR 128位 / feedforward 4次16次63次 / 线性化攻击 / 矛盾方程 / trials=2000 subset=128 / O(n) 优化 / 93.854%
```

## 经验教训

LFSR + 弱 feedforward = LPN 风格;线性化是 LPN 标准攻击;6.25% 噪声下需多次子集投票;O(n) 矩阵乘法比 O(n²) 快 16384 倍。

## 标签

LFSR流密码、feedforward非线性、4次/16次/63次项、线性化攻击、GF(2)矩阵、6.25%噪声、矛盾方程、多次随机子集、准确率筛选、16384倍加速、转移矩阵、flag{ce2980ad9763b8468882f292dbe9f365}、SHA-256 825c3637

## 参考来源

- https://www.ctfiot.com/281936.html
- 原文件：BabyStream_–_从LFSR到LPN的完整攻击复现.full.md
