---
title: CRT 同余方程组与 DH 小型子群攻击（Pohlig-Hellman）
category: crypto
tags: [crt, dh, pohlig-hellman, 小群攻击, 平滑阶]
signals: [给了多组不同的模数, 同一明文 mod 多个 n, 模数满足 a ≡ b mod 小素数, 给出了 p-1 的因子分解, p 减一有小因子, 公钥交换 g^a mod p, 只要求部分比特或部分余数, 每个模数都很小 几十位, 离散对数题目参数明显可分解, 给了 g^x mod p 和 g^y mod p]
difficulty: medium
source: "CTF-Wiki 离散对数 / Wikipedia Pohlig-Hellman"
tools: [python, gmpy2, SageMath]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 给了**多组** `(m mod n_i)`，`n_i` 互不相同，且「模数不大」或「部分模数共享因子」——CRT 场景。
- `p` 是 512~1024 位，但 `p-1` 恰好能被完整分解成若干小素数幂——Pohlig-Hellman 场景。
- DH 交换只给 `g^a mod p`、`g^b mod p`，要求 `g^(ab)`，但 `p-1` 有 ≤ 2^40 量级的因子。
- 题面提示「我们只相信 64 位安全」「为了速度我们用了 256 位素数」。
- 给了 `g^a mod p` 的**一部分比特**或多个不同模数下的余数（HNP / CRT 混合）。
- 参数里 `p = 2^k·q + 1`，或 `g` 的阶 `ord(g)` 不是大素数而是平滑数。
- 同一条明文分别用不同模数加密，密文可以两两相乘抵消（与广播攻击的区别：这里 `n` 互素且各 `n` 都很小）。

## 二、原理

1. **CRT（中国剩余定理）**：给定 `x ≡ r_i (mod n_i)`（`n_i` 两两互素），`x` 在 `mod N = Π n_i` 下唯一：
   `x = Σ r_i · M_i · (M_i^{-1} mod n_i) mod N`，其中 `M_i = N / n_i`。
   - 若 `x` 的真实值小于 `N`（没有取模溢出），CRT 直接得到 `x` 本身。
   - `n_i` **不互素**时，方程有解当且仅当 `r_i ≡ r_j (mod gcd(n_i, n_j))`，此时 CRT 仍可扩展求解（迭代法）。
2. **Pohlig-Hellman**：要求 `g^x = h (mod p)`，设 `n = ord(g) = Π q_i^{e_i}`，则
   - 对每个小素数幂 `q^e`，把问题**降维**到 `q^e` 阶子群：`h_i = h^(n/q^e)`、`g_i = g^(n/q^e)`，求出 `x mod q^e`（`q^e` 小时可枚举，稍大用 BSGS）。
   - 最后用 **CRT** 合并所有 `x mod q_i^{e_i}`，得到 `x mod n`。复杂度 `Σ O(sqrt(q_i^e))`，`q_i` 越小越快。
3. **DH 小群攻击**：把 `g^a` 升到 `n/q` 次幂落进 `q` 阶子群，能逐位泄露 `a` 的低位（类似进制泄露）。若 `p-1` 完全平滑，则 `a` 全可求，进而 `g^(ab)` 直接算。
4. **CRT + 多模数**：同一 `x` 在不同模数下给出不同余数时，先把每个模数**因式分解**，用 CRT 拼回大模数，再用「`x` 很小」判断是否可以直接读出。

## 三、解题步骤

1. 收集所有 `(r_i, n_i)`，先做 `gcd(n_i, n_j)` 检查，不完全互素就要用「扩展 CRT」（合并后再检查一致性）。
2. 用 CRT 合并成一个 `x mod N`；若 `N > x_real`，`x` 就是答案（常见于 `x` 是小 flag 编码）。
3. DH/离散对数题：先 `factor(p-1)`（`sympy.factorint` / Sage `factor` / yafu）。分解成功即可走 Pohlig-Hellman。
4. 每个小因子 `q`：`g_i = g^(n/q)`、`h_i = h^(n/q)`，求 `x_i = log_{g_i}(h_i)`（小 `q` 直接枚举）。
5. 用 CRT 把 `x_i` 合并得到 `x mod n`；若 `n` 就是 `p-1` 且 `x < p`，直接得到私钥。
6. 用 `pow(g, x, p) == h` 校验，再算共享密钥。

## 四、可直接运行的脚本

```python
# CRT + Pohlig-Hellman（离散对数）完整实现，纯 python，自带自测
import math
from functools import reduce

def egcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x, y = egcd(b, a % b)
    return g, y, x - (a // b) * y

def crt_two(r1, n1, r2, n2):
    """解 x ≡ r1 (mod n1), x ≡ r2 (mod n2)；不互素时也能处理。"""
    g, p, q = egcd(n1, n2)
    if (r2 - r1) % g != 0:
        raise ValueError("同余方程组无解")
    lcm = n1 // g * n2
    t = ((r2 - r1) // g * p) % (n2 // g)
    return (r1 + n1 * t) % lcm, lcm

def crt(pairs):
    """pairs: [(r, n)] -> (x mod N, N)"""
    x, mod = 0, 1
    for r, n in pairs:
        x, mod = crt_two(x, mod, r % n, n)
    return x, mod

def bsgs(g, h, p, order):
    """在阶为 order 的子群上求 g^x = h 的 x（0 <= x < order）。"""
    m = math.isqrt(order) + 1
    table = {}
    e = 1
    for j in range(m):
        table.setdefault(e, j)
        e = e * g % p
    factor = pow(g, p - 1 - m, p)     # g^(-m)
    gamma = h
    for i in range(m + 1):
        if gamma in table:
            return i * m + table[gamma]
        gamma = gamma * factor % p
    return None

def pohlig_hellman(g, h, p, factors):
    """factors: [(q, e)]，p-1 = Π q^e。返回 x（mod p-1），使 g^x ≡ h (mod p)。"""
    n = p - 1
    residues = []
    for q, e in factors:
        qe = q ** e
        gi = pow(g, n // qe, p)
        hi = pow(h, n // qe, p)
        xi = bsgs(gi, hi, p, qe)
        if xi is None:
            raise ValueError("子问题无解，检查因子是否完整")
        residues.append((xi, qe))
    x, mod = crt(residues)
    assert pow(g, x, p) == h % p
    return x % mod

if __name__ == "__main__":
    # ---------- CRT ----------
    pairs = [(2, 3), (3, 5), (2, 7)]      # x ≡ 2 mod 3, 3 mod 5, 2 mod 7 -> 23
    x, N = crt(pairs)
    assert x == 23 and N == 105
    print("CRT OK:", x)

    # 不互素的情形：x ≡ 3 mod 6, x ≡ 3 mod 9  -> x ≡ 3 mod 18
    x2, N2 = crt([(3, 6), (3, 9)])
    assert x2 % 18 == 3 and N2 == 18
    print("扩展 CRT（不互素）OK:", x2, N2)

    # 矛盾情形必须报错（1 mod 6 与 3 mod 9 相差 2，不是 gcd=3 的倍数）
    try:
        crt([(1, 6), (3, 9)])
        raise AssertionError("应当抛出无解")
    except ValueError:
        pass
    print("矛盾方程组正确报错 OK")

    # ---------- Pohlig-Hellman ----------
    # 构造 p-1 完全平滑的素数：p = 2*3*5*7*11*13*17*19*23*29*k + 1
    import sympy
    p = None
    for k in range(1, 3000):
        cand = 2 * 3 * 5 * 7 * 11 * 13 * 17 * 19 * 23 * 29 * k + 1
        if sympy.isprime(cand):
            p = cand
            break
    factors = list(sympy.factorint(p - 1).items())
    # 找原根：对所有 (p-1)/q 都满足 g^((p-1)/q) != 1
    g = 2
    while any(pow(g, (p - 1) // q, p) == 1 for q, _ in factors):
        g += 1
    secret = 123456789 % (p - 1)
    h = pow(g, secret, p)
    found = pohlig_hellman(g, h, p, factors)
    assert pow(g, found, p) == h
    print("Pohlig-Hellman OK, p 位数 =", p.bit_length(), "因子:", factors)
```

「参数平滑」的快速自检（在写求解器之前先跑）：

```python
import sympy

def smoothness_report(p):
    """返回 p-1 的最大素因子；< 2^40 基本可秒解。"""
    fac = sympy.factorint(p - 1)
    biggest = max(fac) if fac else 2
    return biggest, fac

if __name__ == "__main__":
    p = 2**256 + 12345
    biggest, fac = smoothness_report(p)
    print("最大素因子 bits =", biggest.bit_length(), "p-1 分解 =", dict(list(fac.items())[:5]))
```

## 五、常见坑 / 变体

- **`ord(g) ≠ p-1`**：`g` 可能是子群生成元，此时 `n = ord(g)` 才是模数；先算 `ord(g)`（对 `p-1` 的每个因子试除）。
- **CRT 无解**：`gcd(n1, n2)` 不整除 `r2 - r1` 时方程组矛盾，说明数据被污染或题目用了非标准构造。
- **`p-1` 分不动**：用 `sympy.factorint` / Sage `factor` / `yafu` / `msieve`，`cado-nfs` 处理 100+ 位；分不动就说明不是 Pohlig-Hellman 题。
- **BSGS 的 `order`**：求逆时用 `pow(g, p-1-m, p)` 等价于 `g^{-m}`，必须保证 `g` 与 `p` 互素；`m` 取 `isqrt(order)+1` 时表大小约 `√order`。
- **子群元素 `g_i` 可能为 1**：`n/q^e` 与 `ord(g)` 不互素时会退化，需换 `q` 或改用更强的原根。
- **DH 共享密钥**：求出 `a` 后直接 `pow(g^b, a, p)`；不要试图解 `b`，`a`、`b` 都求出更慢。
- **多模数不互素**：先把模数分解成素数幂，再在公共部分上验证一致性，最后 CRT。

## 六、参考来源

- [CTF-Wiki 离散对数](https://ctf-wiki.org/crypto/asymmetric/discrete-log/discrete-log/)
- [CTF-Wiki ECC / 离散对数题](https://ctf-wiki.org/crypto/asymmetric/discrete-log/ecc/)
- [Wikipedia: Pohlig–Hellman algorithm](https://en.wikipedia.org/wiki/Pohlig%E2%80%93Hellman_algorithm)
- [Wikipedia: Chinese remainder theorem](https://en.wikipedia.org/wiki/Chinese_remainder_theorem)
