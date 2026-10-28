---
title: 格攻击入门（LLL / Coppersmith 载体构造）
category: crypto
tags: [格, lll, coppersmith, 最短向量, 载体构造]
signals: [格, lattice, lll 算法, 背包, 子集和, 小根, 已知部分比特, 求最小向量, 方程数不足以解方程, hidden number problem]
difficulty: hard
source: "CTF-Wiki / Coppersmith (1996) / Howgrave-Graham"
tools: [SageMath, fpylll, python]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 方程数量不够 / 未知量带"小"约束（每个未知量都比模数小很多）。
- 背包问题（子集和）、低密度子集和需要恢复 0/1 向量。
- RSA 已知高位（见 `rsa-coppersmith.md`）、近似公共除数攻击（ACD）。
- 提示词：LLL、lattice、BKZ、basis、格基规约、SVP/CVP。
- 变体：多个 RSA 模数共享一个大素数 `p`（近似公共模数）。
- 变体：DSA/ECDSA 的 nonce 部分比特已知（Hidden Number Problem）。

## 二、原理

**格**是 `R^n` 中所有整数系数线性组合构成的离散子空间。LLL（Lenstra-Lenstra-Lovász）在多项式时间内求出"近似最短"的短向量。

**构造反问题的标准套路**：
1. 把"未知量"变成格中的短向量分量（因为未知量小而短）。
2. 把"已知关系"变成格的基向量的线性组合。
3. LLL 后短向量就是答案。

**Coppersmith 载体**（Howgrave-Graham 构造）：给 `f(x) ≡ 0 (mod N)` 且 `|x0| < X`，构造 m 次移位多项式

```
g_{i,j}(x) = x^j * N^(m-i) * f(x)^i  , 0 ≤ i < m, 0 ≤ j < δ
```

把每个 `g` 的系数向量作为格基（系数乘 `X^j` 做缩放），LLL 后取最短向量的系数，得到一个在**整数域**上满足 `g(x0) = 0` 的多项式，求其根即得 `x0`。

**低密度背包（Lagarias-Odlyzko）**：`a_i` 是背包重量，目标和 `s`，想找子集 `x_i ∈ {0,1}` 使 `sum(x_i a_i) = s`。构造格

```
[ 1  0  ... 0   N*a_1 ]
[ 0  1  ... 0   N*a_2 ]
[ ...              ...]
[ 0  0  ... 1   N*a_n ]
[ 1/2 1/2 ... 1/2 N*s ]
```

短向量即 `(x_i - 1/2)` 的形式，LLL 后读出。

## 三、解题步骤

1. 用 SageMath（`sagemath/sagemath` Docker）—— 原生支持 `Matrix(ZZ, ...)`、`.LLL()`。
2. 明确"哪个量是短的"，把它放到格的最后一列/行，乘以缩放系数。
3. 构造后 `B.LLL()`，检查每个短向量是否符合约束（`0/1`、`|x| < X`）。
4. 若不命中，调 `delta`（LLL 的近似因子）、`BKZ` 的 `block_size`，或增加多项式次数。
5. 拿到短向量后回到原问题验算（`pow`、`sum`、`assert`）。

## 四、可直接运行的脚本

示例 A —— 低密度子集和（SageMath）：

```python
# sage
n = 32
weights = [random_prime(2^20) for _ in range(n)]     # 背包重量
sol = [random.randint(0, 1) for _ in range(n)]        # 真实解（0/1）
s = sum(w*x for w, x in zip(weights, sol))

# 构造格：前 n 列为单位阵，最后一列放权重*s
N_scale = 2^20
B = Matrix(ZZ, n + 1, n + 1)
for i in range(n):
    B[i, i] = 1
    B[i, n] = weights[i] * N_scale
for j in range(n):
    B[n, j] = 1/2 * N_scale
B[n, n] = s * N_scale

Bred = B.LLL()
for row in Bred.rows():
    # 正确行形如 (x_i - 1/2) * N_scale ...
    cand = [(r > 0) ^ True for r in row[:n]]
    if sum(w*c for w, c in zip(weights, cand)) == s:
        print("sol =", [int(c) for c in cand])
```

示例 B —— Coppersmith 单变量小根（SageMath 一行版）：

```python
# sage
N = Integer(0x...)
X = 2^128
R.<x> = PolynomialRing(Zmod(N))
f = x^3 + 0x... * x^2 + 0x... * x + 0x... - Integer(c)
roots = f.small_roots(X=X, beta=1.0, epsilon=0.03)
print([Integer(r) for r in roots])
```

示例 C —— 手写 Howgrave-Graham 构造（理解载体长什么样）：

```python
# sage
def howgrave_graham(f, N, X, m, t):
    """f(x) ≡ 0 mod N，|x0| < X。返回 LLL 后候选多项式"""
    R.<x> = PolynomialRing(Zmod(N))
    d = f.degree()
    polys = []
    for i in range(m):
        for j in range(d):
            polys.append(x^j * N^(m - i) * f(x)^i)
    for j in range(t):
        polys.append(x^j * f(x)^m)
    # 系数向量（按 X 缩放，让每一项大小可比）
    B = Matrix(ZZ, len(polys), max(p.degree() for p in polys) + 1)
    for i, p in enumerate(polys):
        for k, coef in enumerate(p.coefficients(sparse=False)):
            B[i, k] = Integer(coef) * X^k
    Bred = B.LLL()
    out = []
    for row in Bred.rows():
        poly = sum(Integer(row[k]) * x^k for k in range(row.length()))
        rr = poly.roots()
        out.append(rr)
    return out
```

示例 D —— 纯 Python LLL（不含 Sage 时用，可正确处理尺寸规约与 Lovász 条件）：

```python
from fractions import Fraction

def lll_reduce(B, delta=Fraction(3, 4)):
    """B: list[list[int]]，返回 LLL 规约后的基（Fraction 形式）。
       维度 > 30 时请用 SageMath 的 B.LLL()。"""
    B = [[Fraction(x) for x in row] for row in B]
    n, m = len(B), len(B[0])

    def gso():
        Bs, mu = [], [[Fraction(0)] * n for _ in range(n)]
        for i in range(n):
            v = B[i][:]
            for j in range(i):
                den = sum(x * x for x in Bs[j])
                if den:
                    mu[i][j] = sum(B[i][k] * Bs[j][k] for k in range(m)) / den
                v = [v[k] - mu[i][j] * Bs[j][k] for k in range(m)]
            Bs.append(v)
        return Bs, mu

    def norm(v): return sum(x * x for x in v)

    k = 1
    while k < n:
        Bs, mu = gso()
        for j in range(k - 1, -1, -1):          # 尺寸规约
            if abs(mu[k][j]) > Fraction(1, 2):
                q = round(mu[k][j])
                B[k] = [B[k][i] - q * B[j][i] for i in range(m)]
                Bs, mu = gso()
        # Lovász 条件
        if norm(Bs[k]) >= (delta - mu[k][k - 1] ** 2) * norm(Bs[k - 1]):
            k += 1
        else:
            B[k], B[k - 1] = B[k - 1], B[k]
            k = max(k - 1, 1)
    return B

# 自测：[[4,1,3],[4,2,1],[1,3,4]] 规约后第一条应为短向量 (0,1,-2)
print(lll_reduce([[4, 1, 3], [4, 2, 1], [1, 3, 4]]))
```

## 五、常见坑 / 变体

- **缩放系数**：系数大小差 10^6 以上时，LLL 会被大项主导；用 `X^k` 或 `2^bits` 缩放每一列，使格中各项量级一致。
- **`delta` 越接近 1 越慢**：Sage 的 `B.LLL(delta=0.99)` 在维度 > 100 时可能要几分钟。
- **维度上界**：手写构造一般维数 10~40 效果好，超过 80 建议 BF/BKZ。
- **Coppersmith 的 `beta`**：`modulus` 是合数时忘记设 `beta` 是头号失败原因。
- **CVP 转 SVP**：解"最近向量"问题时，在格最后加一列 `t`（目标）再 LLL，见 LLM `CVP` 章节。
- 变体：**隐数问题（HNP）**、**RSA 近似公因子（ACD）**、**NTRU 恢复** 都是同一套载体。
- 变体：**格维数不够时失败** → 增加多项式次数 `m` 或 `t`，也就是 CTF-Wiki 里的 `epsilon` 调参。

## 六、参考来源

- [CTF-Wiki 格概述](https://ctf-wiki.org/crypto/asymmetric/lattice/overview/)
- [CTF-Wiki 格基规约算法](https://ctf-wiki.org/crypto/asymmetric/lattice/lattice-reduction/)
- [CTF-Wiki CVP](https://ctf-wiki.org/crypto/asymmetric/lattice/cvp/)
- [CTF-Wiki Coppersmith 相关攻击](https://ctf-wiki.org/crypto/asymmetric/rsa/rsa_coppersmith_attack/)
- [Howgrave-Graham, "Finding Small Roots of Univariate Modular Equations Revisited"](https://link.springer.com/chapter/10.1007/BFb0024458)
