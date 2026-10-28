---
title: ECC 小阶 / 无效曲线攻击（Invalid Curve / Small Subgroup）
category: crypto
tags: [ecc, 无效曲线攻击, 小阶点, 离散对数, Pohlig-Hellman]
signals: [椭圆曲线, ecc, 只给了点坐标没有 a b, 点可以自由提交, 曲线参数未校验, 共享密钥验证, 小阶点, 群运算, 离散对数, ecdh]
difficulty: medium
source: "CTF-Wiki / 公开 writeup"
tools: [SageMath, python, sympy]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 题面给了 `p`、基点 `G`、公开点 `Q = k*G`，让求离散对数 `k`。
- 曲线参数 `a, b` **没有给**，只给点坐标；服务器接收任意点 `P` 并返回 `d*P`。
- 服务端**不检查点是否在曲线上**（或只固定 `b`、`a` 由你选）→ 无效曲线攻击。
- ECDH 场景：你把公钥发过去，对方用私钥乘完返回结果 —— 这是现成的标量乘 oracle。
- 题面提示"点可以随便选"、"参数可以自己定"、"阶可能不平滑"。
- ECDSA 场景：`k` 复用 / nonce 可预测（这属于 nonce 攻击，本页只提一句，见坑点）。

## 二、原理

**离散对数直接解**：`Q = kG`。若 `#E(Fp)` 平滑（小素因子乘积），用 **Pohlig-Hellman** 把大群分解成小素数阶子群，每个子群用 **BSGS** 解，最后 CRT 合并。

**无效曲线攻击（Invalid Curve）**：
服务端只校验 `P` 的坐标在 `Fp × Fp` 内，不校验 `P` 是否在指定曲线上。攻击者选**自己可控 `b'` 的弱曲线**（`y^2 = x^3 + a*x + b'`），其 `#E'` 含小素因子 `r`。取 `E'` 上阶为 `r` 的点 `P_r = (#E'/r) * R`，提交后服务端返回 `d*P_r`（落在 `E'` 上）。由 `d*P_r` 可解出 `d mod r`。对多个小 `r` 收集后 CRT 恢复 `d`（要求 `prod r_i > d`）。

**小阶点攻击**：如果曲线固定且无法换，直接在 `E` 上取 `P_r = (#E/r) * G` 得到阶 `r` 的点，同样能从 `d*P_r` 得到 `d mod r`。

## 三、解题步骤

1. 求曲线阶：`E.order()`；用 `factorize` 看是否平滑。
2. 平滑 → Pohlig-Hellman + BSGS + CRT，一步到位。
3. 不平滑且能提交任意点 → 对每个小素数 `r` 找 `E'` 阶含 `r` 的点，收集 `d mod r`。
4. `prod r_i` 超过 `d` 上界（通常 `d < #E`）后 CRT 恢复。
5. 解密 / 恢复 flag，注意 `k` 可能还需要 `% n` 取正确分支。

## 四、可直接运行的脚本

版本 A —— 纯 Python，Pohlig-Hellman + BSGS（阶平滑时最实用）：

```python
from math import isqrt, gcd
from sympy import factorint

class Curve:
    def __init__(self, p, a):
        self.p, self.a = p, a
    def inv(self, v): return pow(v % self.p, -1, self.p)
    def add(self, P, Q):
        p, a = self.p, self.a
        if P is None: return Q
        if Q is None: return P
        if P[0] == Q[0] and (P[1] + Q[1]) % p == 0: return None
        if P == Q: lam = (3 * P[0] ** 2 + a) * self.inv(2 * P[1]) % p
        else:      lam = (Q[1] - P[1]) * self.inv(Q[0] - P[0]) % p
        x = (lam * lam - P[0] - Q[0]) % p
        return (x, (lam * (P[0] - x) - P[1]) % p)
    def mul(self, k, P):
        R = None
        while k:
            if k & 1: R = self.add(R, P)
            P = self.add(P, P); k >>= 1
        return R

    def bsgs(self, G, H, order):
        m = isqrt(order) + 1
        table, P = {}, None
        for j in range(m):
            table.setdefault(P, j)
            P = self.add(P, G)
        mG = self.mul(m, G)
        neg_mG = (mG[0], (-mG[1]) % self.p) if mG else None
        Q = H
        for i in range(m):
            if Q in table:
                return (i * m + table[Q]) % order
            Q = self.add(Q, neg_mG)
        raise ValueError("BSGS 未命中")

    def dlog_pohlig_hellman(self, G, Q, n):
        residues, moduli = [], []
        for r, e in factorint(n).items():
            ri = r ** e
            Gi = self.mul(n // ri, G)              # 阶 r^e
            Qi = self.mul(n // ri, Q)
            x, gamma, rp = 0, Gi, 1
            for _ in range(e):
                # h = r^(e-1) * (Q - x*G) ，阶为 r
                h = self.mul(ri // (rp * r), self.add(Qi, self.mul(n - x % n, Gi)))
                g_r = self.mul(ri // r, Gi)        # 阶为 r 的基点
                d = self.bsgs(g_r, self.mul(ri // r, h), r)
                x += d * rp
                rp *= r
            residues.append(x % ri); moduli.append(ri)
        x, M = 0, 1
        for res, mod in zip(residues, moduli):
            while x % mod != res:
                x += M
            M = M * mod // gcd(M, mod)
        return x % M

# --- 自测：y^2 = x^3 + 497x + 1768 (mod 9739) ---
c = Curve(9739, 497)
G = (5323, 5438)
print("2G =", c.add(G, G))                # (1512, 8728)
```

版本 B —— 无效曲线攻击（SageMath，生产环境）：

```python
# sage
p  = 2**256 - 2**32 - 2**9 - 2**8 - 2**7 - 2**6 - 2**4 - 1     # 题目的素数域
a  = 0x...
E  = EllipticCurve(GF(p), [a, b])
n  = E.order()
print(factor(n))                       # 平滑就直接 dlog

# 不平滑：对每个小素数 r 构造 b' 使 #E' 含因子 r
small = [3, 5, 7, 11, 13, 17, 19, 23]
d_mods = {}
for r in small:
    for bb in range(1, 5000):
        E2 = EllipticCurve(GF(p), [a, bb])
        if E2.order() % r:
            continue
        P = (E2.order() // r) * E2.random_point()
        if r * P != E2(0):
            continue
        R = oracle(P)                  # 服务端返回 d*P
        # 遍历 0..r-1 找 d mod r
        for k in range(r):
            if k * P == R:
                d_mods[r] = k
                break
        break
print(d_mods)                          # 用 CRT 合并
```

## 五、常见坑 / 变体

- **无效曲线只作用于"`a` 可控"或"完全不校验"的实现**：若服务端把所有参数硬编码并校验点在曲线上，请改走 Pohlig-Hellman。
- 小阶点必须真的满足 `r*P = O`，否则解得 `d mod r` 是错的，务必 `assert`。
- **`p` 是合数**：先 `factor(p)`；`p-1` 平滑时离散对数同在乘法群里退化。
- **异常曲线**（`4a^3 + 27b^2 ≡ 0 mod p`）：同构于加法/乘法群，直接解。
- ECDSA 的 nonce 重用：`k1 == k2` 时 `d = (s1*k - z1)/r1`，与本页不是一类，但常同现。
- `d` 只恢复到 `prod r_i` 模下：确保乘积大于 `d` 上界，否则要加更多 `r`。

## 六、参考来源

- [CTF-Wiki ECC 介绍](https://ctf-wiki.org/crypto/asymmetric/discrete-log/ecc/)
- [CTF-Wiki 离散对数](https://ctf-wiki.org/crypto/asymmetric/discrete-log/discrete-log/)
- [Neves & Tibouchi, "Degenerate Curve Attacks"（无效曲线）](https://eprint.iacr.org/2015/1233)
- [CTF-Wiki GitHub](https://github.com/ctf-wiki/ctf-wiki)
