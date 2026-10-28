---
title: "Primes：乘积编码与连分数"
category: crypto
tags: [wp prose translation]
signals: [Primes：乘积编码与连分数]
difficulty: medium
source: "https://github.com/google/google-ctf/blob/f683ff991cac26f7673d2f2de5ac9d226b95b847/2023/quals/crypto-primes/solution/README.md"
tools: []
origin: imported
origin_id: gctf-2023-crypto-primes
origin_sha256: 0315efa6874630fba49cf2f750ba589a1b6c4583426d1b3634b9ab7151cd7a98
origin_event: ""
origin_kind: wp_prose_translation
license: "Apache-2.0"
updated: 2026-10-23
---
# Primes：乘积编码与连分数

> 来源：https://github.com/google/google-ctf/blob/f683ff991cac26f7673d2f2de5ac9d226b95b847/2023/quals/crypto-primes/solution/README.md

# Google CTF 2023 — Crypto：Primes 题解

题目给出一段包含 flag 的字符串的编码结果，以及该字符串的一个打乱版本；打乱版本中的 flag 已被随机字符替换。

对于长度为 n 的位串 $b\in\{0,1\}^n$，编码的计算方式是：

$$x=\prod_{i=0}^n p_i^{b_i}\pmod q$$

其中 $p_i$ 是第 i 个素数，q 是固定的素数模数。

给定打乱后的位串，可以用同样方法算出编码 y，再计算误差乘积：

$$e=xy^{-1}\pmod q=\prod_{i=0}^n p_i^{e_i}\pmod q$$

其中差异指数 $e_i\in\{-1,0,1\}$。将乘积写成 $e=nd^{-1}\pmod q$，也就是：

$$ed=n+sq$$

这里 n 与 d 都只含那组 $p_i$ 的正整数次幂，且存在某个未知整数 $s\in\mathbb Z$。

整理上式可得：

$$\left|\frac eq-\frac sd\right|=\frac n{qd}$$

若 $nd<q/2$，那么 s/d 就是 e/q 的一个连分数渐近分数。因为此时：

$$\left|\frac eq-\frac sd\right|<\frac1{2d^2}$$

由丢番图逼近的结论，s/d 是 e/q 的一个最佳逼近。原文补充参考：[丢番图逼近](https://en.wikipedia.org/wiki/Diophantine_approximation)。

题目选择 q 的大小时，已让打乱字符串满足 $nd<q/2$。因此策略是：计算 e/q 的连分数渐近分数 $s_j/d_j$，尝试把 $d_j$ 及 $d_je\bmod q$ 分解为那组 $p_i$ 的乘积。找到合适的分解后，就可修正打乱位串中的错误，恢复 flag。

---

译注：原文同时用 n 表示位串长度和上述分子，且乘积下标照录原式；具体实现前应核对索引约定。这是记号提醒，不是本轮复现结果。
