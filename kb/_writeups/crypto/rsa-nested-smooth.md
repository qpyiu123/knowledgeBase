---
title: "RSA_NestingDoll：外层素数减一里藏着内层素因子"
category: "crypto"
kind: "writeup"
tags: ["嵌套 RSA", "Pollard p−1", "光滑阶"]
signals: ["inner RSA modulus", "outer RSA modulus", "get_smooth_prime"]
source: "密码学题解汇编 / RSA_NestingDoll：内外层欧拉函数"
origin_id: "r67-rsa-nested-smooth"
relates_to: ["_methods/rsa_d_modulus.md", "crypto/rsa-fermat-factorization.md"]
verification: "本机用附件公开数据回验"
---

# RSA_NestingDoll：外层素数减一里藏着内层素因子

## 先看这一步

密文实际对内层模数加密。外层每个素数减一含一个内素数；先分外层，再从最大公约数取回内层因子。

**适用时**：剩下的小素数幂要被试探指数覆盖，而且中途检查点要能分出因子。

**留意**：底数或平滑界不合适时，最大公约数可能一直是 1，或一下变成整个模数。

## 先看密文用哪个模数

原附件实际输出 `pow(m,e,n_inner)`。外层的每个素数 `P` 用某个内素数 `u` 生成：`P−1=u·S`，`S` 由较小的素因子构成。已知 `n_inner` 是四个 `u` 的乘积，可把它当成试探指数的一部分，不用先分解它。

## 在指数增长途中分因子

从 `a^n_inner` 起，逐步乘进小素数幂。若累积指数覆盖了某个 `P−1`，该幂在模 `P` 下等于 1。对幂值减一与剩下的外层模数求最大公约数。若一批之后出现因子，回到批起点逐项检查。如果不同因子一起命中，就要换检查点或底数。

## 怎么回验

每找到一个外层因子 `P`，用 `gcd(P−1,n_inner)` 找对应内因子。确认两边各自乘回公开模数，再用内层四个素因子求逆指数。重加密也在内层做，外层从头到尾用于找因子。

## 配套代码

`kb/_code/r67/nested_pm1.py`。函数接收题目的公开数值；不会运行题目源码。

## 出处

- RSA_NestingDoll：内外层欧拉函数：汇编中的 `题目/upload-rsa_nestingdoll/WP.md`。
