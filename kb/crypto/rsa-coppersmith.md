---
title: RSA 已知高位攻击 / Coppersmith 小根
category: crypto
tags: [rsa, coppersmith, 格, 已知高位, 小根]
signals: [已知 p 的高位, 给了 p 的部分比特, 已知 m 的高位, 明文前几位已知, partial key exposure, 已知 d 的高位, 给了 factor 的高位, 位数泄漏]
difficulty: hard
source: "CTF-Wiki / Coppersmith (1996)"
tools: [SageMath, python, fpylll]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 题面给出 `p >> 200`（p 的高 312 位）并要求恢复 `n` 的因子。
- 明文形式已知：`m = b"flag{" + secret`，或 `c = (prefix * 2^k + x)^e`。
- 泄露 `d` 的高位（`d_high = d >> bits`）。
- 有"泄漏模块"：每次交互泄漏 `p` 的若干比特位，交互次数够多。
- 题目提示"我只知道 p 的一部分"、"你可能需要 Coppersmith"。
- 注意区分：给**低位**是更方便的情形（低比特成对立方可迭代恢复），给**高位**才需要 `small_roots`。

## 二、原理

> **Coppersmith 定理**：设 `f(x)` 是次数为 `δ` 的整系数首一多项式，`N` 为已知整数（通常 `N = n` 或 `N = p` 的高位近似）。若存在解 `|x0| < X` 使 `f(x0) ≡ 0 (mod b)`（`b` 是 `N` 的因子，`b ≥ N^β`），且 `X ≤ N^(β²/δ - ε)`，则可在多项式时间内找到 `x0`。

实现思路（Howgrave-Graham）：把 `f` 扩大成多项式集合 `g_{i,j}(x) = x^j * N^(m-i) * f(x)^i`，系数组成格；LLL 规约后取最短向量的系数为新的多项式，在新的整数域上求根。

SageMath 的 `small_roots` 就是这套构造：

```python
R.<x> = PolynomialRing(Zmod(N))
f = ...              # f(x0) = 0 mod p 或 mod n
f.small_roots(X=2^k, beta=0.5, epsilon=0.03)
```

- `beta`：`p` 在 `N` 中的比例。**只知道 `p` 的高位、不知道 `p`** 时 `beta = 0.5`；`N` 本身是模数且要整除 `N` 时 `beta = 1`。
- `X`：未知部分的界，**必须严格大于真实解**（留点余量），但不要大太多否则多项式得加次。

## 三、解题步骤

1. 把题目信息整理成 `f(x0) ≡ 0 (mod ?)` 的形式。已知 `p` 的高 `h` 位：
   ```
   p = p_high * 2^k + x,   |x| < 2^k
   f(x) = p_high * 2^k + x ≡ 0 (mod p),  f(0) ≡ 0 (mod p),  p | n
   ```
   → `beta = 0.5`，`X = 2^k`。
2. 已知明文高位：`c = (m_high * 2^k + x)^e mod n` → `f(x) = (m_high*2^k+x)^e - c`，`beta = 1`（`mod n`），`X = 2^k`。要求 `k < n.bit_length() * beta^2 / e`，`e=3` 时大约可恢复 `n` 位数 1/3 的位数。
3. 已知 `d` 高位：`f(x) = (d_high * 2^k + x)*e - 1 ≡ 0 (mod φ)` 附近，通常转为格构造 `Howgrave-Graham`，用 `Boneh-Durfee` 代码。
4. 运行 `small_roots`，对返回的每个根 `r` 验算 `pow(m_high*2^k + int(r), e, n) == c`。

## 四、可直接运行的脚本

已知 `p` 高 512 位（总长 1024），恢复 `q` 后解密（SageMath）：

```python
# ---- SageMath ----
n  = Integer(0x...)
e  = 65537
c  = Integer(0x...)
p_high = Integer(0x...)       # p 的高 512 位
kbits  = 512                  # 未知位数

R.<x> = PolynomialRing(Zmod(n))
f = p_high * 2^kbits + x      # f(x0) == 0 (mod p)
roots = f.small_roots(X=2^kbits, beta=0.5, epsilon=0.02)
for r in roots:
    p = Integer(p_high * 2^kbits + r)
    if n % p == 0:
        q = n // p
        d = inverse_mod(e, (p - 1) * (q - 1))
        m = power_mod(c, d, n)
        print(bytes.fromhex(hex(m)[2:]) if m else "fail")
```

已知明文高位（`e = 3`，明文前 8 字节已知）：

```python
# ---- SageMath ----
import binascii
n, e, c = Integer(n), 3, Integer(c)
prefix = b"flag{"
m_high = Integer(int.from_bytes(prefix + b"\x00" * 12, "big") >> (8 * 12))
kbits = 8 * (32 - len(prefix))        # 猜测 flag 总长约 32 字节
R.<x> = PolynomialRing(Zmod(n))
f = (m_high * 2^kbits + x) ** e - c
for r in f.small_roots(X=2^kbits, beta=1.0, epsilon=0.02):
    m = int(m_high * 2^kbits + r)
    print(binascii.unhexlify(hex(m)[2:]))
```

纯 Python 替代（用 `fpylll` 做 LLL，或直接 pip 安装 `coppersmith`）：SageMath 是最省事的，**强烈推荐**在 Docker `sagemath/sagemath` 里跑。

## 五、常见坑 / 变体

- **`beta` 设错是最常见的失败原因**：已知 `p` 高位时 `modulus = n`，`beta = 0.5`；如果把 `modulus` 设成 `p` 本身（不可能，因为不知道 p）就错了。
- **`X` 过小**：Coppersmith 要求 `X` 是真实解的上界，真实长度恰好等于 `2^kbits` 时要给 `2^(kbits+1)`。
- **`epsilon` 太小**：格维数暴涨，`small_roots` 里 `epsilon` 影响 `m, t` 参数，一般从 `0.02` 起调。
- **次数/位数超出上界**：`e=3` 时理论上限约为 `n^(1/3)` 的 1/3 位——即已知明文高位分别太少时**无解**，别硬跑。
- 已知 `p` 的**低位**不要用 Coppersmith，直接迭代恢复更快（`p & mask` 已知，逐 bit 枚举）。
- 变体：`n = p^r * q` 的 `beta` 要按 `p` 在 `n` 中的幂次调整。
- 变体：`dp` 高位泄露 → 用 `p = (e*dp-1)/k + 1` 的近似初值再 `small_roots`。

## 六、参考来源

- [CTF-Wiki Coppersmith 相关攻击](https://ctf-wiki.org/crypto/asymmetric/rsa/rsa_coppersmith_attack/)
- [CTF-Wiki 格基规约算法](https://ctf-wiki.org/crypto/asymmetric/lattice/lattice-reduction/)
- [CTF-Wiki GitHub](https://github.com/ctf-wiki/ctf-wiki)
- [Coppersmith, "Finding a Small Root of a Univariate Modular Equation"](https://link.springer.com/chapter/10.1007/3-540-68339-9_14)

## 七、实战检查清单（照做能省 1 小时）

1. `n.bit_length()` 与已知位数的差值 → 得到 `X` 的上界 `2^k`，**先算再写代码**。
2. 判断模数关系：`p | n` 时 `beta = 0.5`；直接 `mod n` 时 `beta = 1.0`。
3. 先跑 `epsilon=0.02`；失败再降到 `0.01`，维度涨得很快。
4. `small_roots` 返回空列表时，按顺序排查：`beta` 错 → `X` 太小 → 多项式非首一（先 `f.monic()`）。
5. 成功标准：`n % p == 0` 且 `p.bit_length()` 与预期一致。

```python
# 快速自检：把未知位数与理论上限做比较
n_bits = n.nbits()
print("n bits =", n_bits)
print("已知 p 的位数上限（beta=0.5, delta=1）:", n_bits * 0.5 * 0.5)
print("已知明文位数上限（e=3, beta=1）:", n_bits / 3)
```

> 经验值：1024 bit 的 `n`，已知 `p` 的高 256 位基本必成功；512 bit 的 `n` 上限约 128 位。
> 若题目给的位数正好卡在上限，优先调小 `epsilon` 而不是硬改 `X`。
