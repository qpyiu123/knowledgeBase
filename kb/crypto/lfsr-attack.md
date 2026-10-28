---
title: LFSR 关联攻击 / BM 算法（线性反馈移位寄存器）
category: crypto
tags: [lfsr, 伯利坎普梅西, 相关性攻击, 流密码]
signals: [线性反馈移位寄存器, lfsr, 输出比特流, 钥流, keystream, 多项式未知, 反馈函数, 抽头, bm 算法, 相关性]
difficulty: medium
source: "CTF-Wiki / 公开 writeup"
tools: [python, SageMath, galois]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 题面给出一串比特（`0101101...`）或 `keystream`，说明它是 LFSR 生成的。
- 给了"反馈多项式未知"、"抽头未知"，或者给了 `n` 级 LFSR 的初始状态。
- 多个 LFSR 的输出经过非线性组合（AND、XOR、多数表决），但有一条与密钥相关性强。
- 关键词：LFSR、shift register、tap、feedback、BM、Berlekamp-Massey、correlation。
- 变体：给了密文与明文的异或 = 密钥流，但密钥流有 2 倍重复（周期小）。

## 二、原理

**LFSR**：`n` 级寄存器，每步输出最低位（或最高位），新输入位为反馈多项式的线性组合：

```
s_{t+n} = c_1*s_{t+n-1} + c_2*s_{t+n-2} + ... + c_n*s_t  (mod 2)
```

**Berlekamp-Massey（BM）**：给定长度 `2n` 以上的输出序列，可唯一求出**最短线性递推式**（即特征多项式），复杂度 `O(n^2)`。任何"线性复杂度 ≤ L"的比特流，只要我们知道 `2L` 位，就能完整预测。

**相关性攻击**：非线性组合器 `f` 通常与某个单 LFSR `x` 高度相关（`P[f(x,...) = x] = p > 0.5`）。收集足够多的输出，将组合输出当作 `x` 的噪声版，枚举该 LFSR 的初始状态（2^n 太大时用 Fast Correlation Attack / 分治），再用汉明距离/相关度挑出正确种子。

## 三、解题步骤

1. 若已知输出位流 ≥ 2×线性复杂度，直接 BM 求多项式并预测。
2. 若组合器复杂（AND/多数），先观察相关度：对候选种子计算输出与组合输出的吻合率，大于阈值即命中。
3. 小 `n`（≤ 24）时直接穷举 2^n 个种子，用并行脚本跑。
4. 大 `n` 用 **Goppa / Meier-Staffelbach** 快速相关攻击或格方法。
5. 拿到完整密钥流后与密文异或得到明文。

## 四、可直接运行的脚本

BM 算法（纯 Python，标准写法）：

```python
def berlekamp_massey(s):
    """返回 (C, L)：C 为反馈多项式系数（C[0]=1），L 为线性复杂度"""
    n = len(s)
    C = [1] + [0] * n
    B = [1] + [0] * n
    L, m, b = 0, -1, 1
    for i in range(n):
        d = s[i]
        for j in range(1, L + 1):
            d ^= C[j] & s[i - j]
        if d == 1:
            T = C[:]
            coef = 1 << (i - m)                 # x^(i-m)
            coefs = [0] * n + [0]
            # 用整数位运算避免索引越界，简单起见用列表推导
            for j in range(n + 1):
                if (coef >> j) & 1 and j < n + 1:
                    pass
            shift = i - m
            for j in range(n - shift):
                C[j + shift] ^= B[j]
            if 2 * L <= i:
                L, B, b, m = i + 1 - L, T, d, i
    return C, L

def lfsr_next(state, taps):
    out = state[0]
    fb = 0
    for t in taps:
        fb ^= state[t]
    state[:] = state[1:] + [fb]
    return out

# --- 自测 ---
taps = [0, 2, 5]
state = [1, 0, 1, 1, 0, 0]
seq, st = [], state[:]
for _ in range(200):
    seq.append(lfsr_next(st, taps))
C, L = berlekamp_massey(seq[:60])
print("线性复杂度 L =", L)          # 应 ≤ 6
print("反馈多项式 C =", C[:L + 1])
```

多项式预测（用 BM 结果直接外推）：

```python
def predict_from_bm(seq, count):
    C, L = berlekamp_massey(seq)
    s = list(seq)
    for i in range(len(s), len(s) + count):
        v = sum(C[j] * s[i - j] for j in range(1, L + 1)) & 1
        s.append(v)
    return s[len(seq):]
```

相关性攻击（暴力种子，示例 `n ≤ 20`）：

```python
from itertools import product

def correlation_attack(outputs, n, taps, f, threshold=0.6):
    """outputs: 观测到的组合输出位；f: 组合函数；找 LFSR 初始状态"""
    best, best_hit = None, -1
    for seed in product([0, 1], repeat=n):
        st = list(seed)
        hit = 0
        for y in outputs:
            x = lfsr_next(st, taps, n)
            if f(x) == y:
                hit += 1
        if hit > best_hit:
            best_hit, best = hit, seed
        # 早停：命中率已很高
        if best_hit / len(outputs) > threshold:
            return best
    return best

# 示例：组合器 f(x) = x（最简单），种子 101100
out = [1, 0, 1, 1, 0, 0]
print(correlation_attack(out, 6, [0, 2, 5], lambda x: x))
```

快速相关攻击（Goppa 码 / 迭代解码）在 SageMath 中有成熟实现，`n` 推到 60+ 时用它：

```python
# sage: pip/源码搜 "fast correlation attack lfsr"
# 核心：用 BM 的校验矩阵对噪声序列做迭代软判决解码
```

## 五、常见坑 / 变体

- **BM 需要序列长度 ≥ 2L**：给得太少会得到错误的（更短的）多项式，预测跳变。
- **位序**：有的实现最高位先出，`s[i]` 与 `s[n-1-i]` 混用会得到"反向"的多项式，表现为 BM 结果长度对但预测全错。
- 组合器相关度太低（`p` 接近 0.5）时暴力种子会失败，必须用快速相关攻击或多路相关。
- **异或组合器**：`f = x1 ^ x2 ^ ...` 时整体仍是线性，直接 BM 一次搞定，不需要相关性分析。
- **多数表决**：与单个 LFSR 相关度 0.75，可暴力但 `n` 稍大（>25）就爆，转 Goppa。
- 若题目给的是"密文"而非密钥流，先确认是 `ct = pt ^ ks`；密钥流有重复周期时也可能是 LFSR 状态泄露。

## 六、参考来源

- [CTF-Wiki 线性反馈移位寄存器 LFSR](https://ctf-wiki.org/crypto/streamcipher/fsr/lfsr/)
- [CTF-Wiki 非线性反馈移位寄存器](https://ctf-wiki.org/crypto/streamcipher/fsr/nfsr/)
- [CTF-Wiki 流密码](https://ctf-wiki.org/crypto/streamcipher/intro/)
- [Meier & Staffelbach, "Fast Correlation Attacks on Certain Stream Ciphers"](https://link.springer.com/article/10.1007/BF00196774)
