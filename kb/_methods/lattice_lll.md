---
title: 方法卡 · LLL 格基规约与低密度子集和（背包）恢复
category: crypto
tags: [方法卡, 格, lll, 背包, 子集和, 短向量, 格基规约, 载体构造]
signals: [格 lattice LLL 算法, 背包子集和, 求最小向量, 方程数不足以解方程, 未知量都很小, 低密度背包, hidden number problem]
difficulty: hard
source: kb/crypto/lattice-lll.md
tools: [python, 内置脚本]
updated: 2026-11-03
---

# 方法卡 · LLL 格基规约与低密度子集和

## 适用场景

题面给了一组**带小约束的线性关系**，直接解方程解不出来，但"未知量都很短"：

- 低密度背包 / 子集和：给 `weights` 与目标和 `s`，求 0/1 向量使 `Σ x_i·w_i = s`；
- 未知量都带界（`|x_i| < X`）、或者多个方程里只有部分比特正交；
- 看到提示词 `lattice / LLL / BKZ / basis / 短向量 / SVP / CVP`；
- 同一套载体还通向 Coppersmith（见 coppersmith 卡）与 HNP（见 ECDSA nonce 卡）。

## 前置条件

- 能写出格的**整数基**（每一行是一个基向量），并且知道"哪个量在答案里是短的"。
- 各列量级要可比：系数差 10⁶ 以上时 LLL 会被大项主导，必须按 `X^k` 或 `2^bits` 缩放列。
- 纯 Python 精确有理 LLL 适合维度 ≤ 20 左右；超过 40 维请换 Sage 的 `B.LLL()` 或 fpylll。
- 背包的密度要低（`n / log2(max w)` 大约 < 0.94），否则 LLL 找不到短向量，得用更重的格或 MITM。

## 步骤

1. 用 Sage 或本脚本先跑一次 LLL，确认规约后的基里出现"候选短向量"。
2. 对每个短向量按题目约束读回整数解（背包：按符号取 0/1；小根：取系数多项式求根）。
3. **每次读回都要回代原式验算**（`Σ w_i x_i == s`、`pow(m,e,n) == c`），不验算就是假绿。
4. 不命中时按顺序调：`delta` 从 3/4 调到 99/100、加大缩放、加维（加多项式次数 / 加同余行）、换 BKZ。
5. 结果拿不到时，同构但更小的手算样例用来校准"提取公式与构造是否配套"——两者一旦错配，解出来的永远是噪声。

## 立即可用脚本

`kb/_methods/scripts/lattice_lll.py`（纯标准库，无 Sage、无网络）：

```bash
# 1) 低密度子集和
python kb/_methods/scripts/lattice_lll.py --weights 3,4,5,9,11,15 --target 29

# 2) 规约任意整数基（JSON：[[..],[..]]），输出规约后的基
python kb/_methods/scripts/lattice_lll.py --reduce-file basis.json --delta 0.99

# 3) 自检（6 组断言：LLL 短向量、行体积不变、背包恢复、非法输入、无解防假阳、固定 seed）
python kb/_methods/scripts/lattice_lll.py --selftest
```

脚本提供 `lll_reduce(B, delta)`（精确 Fraction 的 Gram-Schmidt + 尺寸规约 + Lovász 交换，带 `max_steps` 和维度上限）
与 `solve_subset_sum(weights, target)`（Lagarias-Odlyzko 背包格 + meet-in-the-middle 兜底，两条路径都回代复验）。
退出码：`0` 成功；`2` 参数非法；`1` 未找到解。

## 失效场景

1. **密度不够低 / 维数太大**：LLL 只能给出"近似最短"，真正的 0/1 解可能没进前几行；本脚本的兜底是 MITM（≤24 个重量），再大就必须上 Sage + BKZ 或者问题本身的低密度更弱。
2. **行列式被破坏**：任何"约化"都必须是整数基变换，否则格已经变了。自检里用模素数行列式比对钉住这一条——早期版本在 `delta=0.99` 下出现过规约后体积变化的 bug，靠这个断言才发现。
3. **列没有缩放**：背包里若不把 `weights` 乘上 `scale`，最后一行会被前 n 列的 1 淹没，读出来全是垃圾。
4. **读回规则错**：背包短向量是 `x_i - 1/2` 的形状，取 `>0` 为 1；换一种构造（把 `n/B` 放到别的列）时读回规则随之改变，直接用旧公式会得到全 0。
5. **不验算**：`sum(w*x) == target` 这条断言不能省；LLL 的"短"不等于"对"。
6. **浮点 Gram-Schmidt**：系数到 100 位以上时会因有效位不足退化成恒等变换（永不交换），表现为"跑完了但一个短向量都没有"——本脚本全程用 `Fraction`。
