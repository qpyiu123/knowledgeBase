---
title: "ECC 尖点：把点的倍乘换成一次模除法"
category: "crypto"
kind: "writeup"
tags: ["奇异曲线", "尖点", "三重根", "离散对数"]
signals: ["配方后 y²=(x−r)^3", "判别式为零", "广义曲线有 y 项"]
source: "https://www.ctfplus.cn/problem-detail/2045446312698056704/description"
origin_id: "r67-ecc-cusp-additive"
relates_to: ["crypto/ecc-small-order.md", "_writeups/crypto/curve-parameters.md"]
verification: "本机用附件公开数据回验"
---

# ECC 尖点：把点的倍乘换成一次模除法

## 先看这一步

题目自己实现点加法时，先从公式核对曲线模型。配方后的三次式若恰好有一个三重根，可把曲线点换成加法群坐标。

**适用时**：p 是大于 3 的素数，配方后确实有三重根；点在曲线上且不是奇点。

**留意**：双重根需要另一套处理；恢复的标量以 p 为周期。

## 先检查是哪种退化

样本使用 `y²+a·x·y+c·y=x³+b·x²+d·x+e`。在奇素数域里置 `Y=y+(ax+c)/2`。右端三次式若能写成 `(x−r)^3`，就是这里的尖点。先用二次项系数算 `r`，再逐项核对一次项和常数项。仅有判别式为零还分不清尖点和其他退化情况。

## 把点换成加法坐标

对非奇点令 `t=(x−r)/Y`，无穷远点记作 0。把 `x−r=t⁻²、Y=t⁻³` 代入过两个点的非竖直直线，得到不含 `t²` 的三次式，三个交点的参数和为零。曲线加法要将第三点取反，所以参数直接相加。已知 `Q=kG`，算 `k=t(Q)/t(G) mod p` 即可。

## 怎么回验

先检查基点和目标点满足原方程。用 `k·t(G)` 反算目标的 `x,Y`，再还原 `y`，与附件的两个坐标比较。

## 配套代码

`kb/_code/r67/case_relations.py`。函数接收题目的公开数值；不会运行题目源码。

## 出处

- [ECC](https://www.ctfplus.cn/problem-detail/2045446312698056704/description)：汇编中的 `题目/ctfplus-2045446312698056704/WP.md`。
