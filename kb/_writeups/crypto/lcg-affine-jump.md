---
title: "LCG：步数已知就倍增，步数未知先看固定点"
category: "crypto"
kind: "writeup"
tags: ["LCG", "仿射迭代", "固定点"]
signals: ["重复执行 a*x+b", "同样步数再走一次", "next_prime"]
source: "https://www.ctfplus.cn/problem-detail/2056307878381228032/description"
origin_id: "r67-lcg-affine-jump"
relates_to: ["crypto/lcg-predict.md", "_writeups/crypto/lcg-low-byte.md"]
verification: "本机用附件公开数据回验"
---

# LCG：步数已知就倍增，步数未知先看固定点

## 先看这一步

参数已知时，先问缺的是步数还是状态。步数已知就合并多轮递推；步数未知但看到了第一次的终点，可借固定点算第二次的终点。

**适用时**：同一个递推在相同模数下重复；固定点做法需要相应逆元。

**留意**：只泄漏状态低位时，不能直接拿它代替完整终点。

## 步数已知：把两轮合成一轮

把 `f(x)=a*x+b` 记成一对数 `(a,b)`。连续做两次，就得到 `(a²,(a+1)b)`，两项都对模数取余。不断把步长翻倍，再按步数的二进制位选用。合数模数也能这样算，因为只用到加法和乘法。汇编里的 LCG 只有 10 步，直接循环也行；倍增在步数很大时才有优势。

## 步数未知：第一次的终点已经够用

DlcgH_r 给出 `A=f^k(s)`，还要算 `f^k(A)`。若模数 `p` 为素数且 `a≠1`，固定点 `t=b/(1−a)` 满足 `f(t)=t`。把 `t` 当成原点，走 `k` 步只剩乘 `a^k`。若 `s≠t`，用 `(A−t)/(s−t)` 得到倍率，再乘到 `A−t` 上，最后加回 `t`。若 `s=t`，以后始终停在 `t`；若 `a=1`，第二次终点直接是 `2A−s`。这些式子都在原模数下计算。

## 怎么回验

LCG 核对第 10 步的状态。DlcgH_r 按原规则取新终点之后的第一个素数，检查它整除公开模数。加密指数是 4，两个素数域分别开根再合并；4 个候选逐个用原密文核对。

## 配套代码

`kb/_code/r67/case_relations.py`。函数接收题目的公开数值；不会运行题目源码。

## 出处

- [LCG](https://www.ctfplus.cn/problem-detail/2056307878381228032/description)：汇编中的 `题目/ctfplus-2056307878381228032/WP.md`。
- DlcgH_r：汇编中的 `题目/zhejiang-DlcgH_r/WP.md`。
