---
title: "ez_xor：用 AND、XOR 和乘积恢复一对 RSA 因子"
category: "crypto"
kind: "writeup"
tags: ["按位与", "按位异或", "二次方程", "RSA 子模数"]
signals: ["N/n 已知", "s&r", "s^r"]
source: "https://www.ctfplus.cn/problem-detail/1996418936001794048/description"
origin_id: "r67-rsa-and-xor-projection"
relates_to: ["_writeups/crypto/rabin-eight.md", "crypto/rsa-fermat-factorization.md"]
verification: "本机用附件公开数据回验"
---

# ez_xor：用 AND、XOR 和乘积恢复一对 RSA 因子

## 先看这一步

已知同一对整数的按位与、异或及乘积，就能先求它们的和，再用二次方程拆出两数。

**适用时**：提示对应同一对非负整数；读取子模数代表元前，检查原文长度范围。

**留意**：重加密能核对这个候选，剩下的模数因子仍是未知量。

## 先求两数之和

每一位上，只有一方为 1 的位置由 XOR（异或）计一次，两方都是 1 的位置由 AND（按位与）计两次。所以 `s+r=(s XOR r)+2(s AND r)`。本题还给 `N=pqsr` 和 `n=pq`，先算 `sr=N/n`，再解 `X²−(s+r)X+sr=0`。判别式须是整数平方，两根都要通过原始 AND、XOR 和乘积检查。

## 用可用的分量解密

把密文对 `sr` 取余。若指数在这个子模数的周期下可逆，就可以解出代表元。原文整数小于 `sr` 时可直接读；没有长度范围时，一个余数可能对应许多整数。

## 怎么回验

这次算到一个子模数候选，用完整 `N` 重算 65537 次幂也与原密文相符。剩下的 `n` 没有分解，原题另外给的 `p XOR q` 也没用到。

## 配套代码

`kb/_code/r67/case_relations.py`。函数接收题目的公开数值；不会运行题目源码。

## 出处

- [ez_xor](https://www.ctfplus.cn/problem-detail/1996418936001794048/description)：汇编中的 `题目/ctfplus-1996418936001794048/WP.md`。
