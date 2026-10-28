---
title: RSA 维纳攻击（d 过小 / e 过大）
category: crypto
tags: [rsa, wiener, 连分数, 低解密指数]
signals: [e 非常大, e 和 n 位数差不多, e 比 n 还大, d 很小, 私钥指数小, e 有十几位十六进制, n 很大 e 也很长, 连分数攻击, 维纳攻击]
difficulty: medium
source: "CTF-Wiki / 公开 writeup"
tools: [python, gmpy2]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- `e` 异常大，通常和 `n` 同数量级（2048/4096 bit 的 `n` 配一个 2048/4096 bit 的 `e`），甚至 `e > n`。
- 题面代码里 `d = getPrime(256)` 或 `d = randint(1, 2**256)`，而 `p`、`q` 是 1024 bit —— 典型的"小私钥"。
- 有时明文只给 `n, e, c`，一眼望去 `e` 长到离谱，几乎不用计算就能判定。
- 变体：`d` 不到位数但有多个小 `d` 的份额（→ 扩展维纳 "Boneh-Durfee"，需要格）。
- 变体：`dp` 小（`dp` 相关攻击，见 `rsa-dp-leak.md`）。

## 二、原理

RSA 有 `ed ≡ 1 (mod φ(n))`，即存在整数 `k` 使：

```
ed = 1 + k*φ(n)          →   e/φ(n) = k/d + 1/(d*φ(n))
```

维纳定理（Wiener, 1990）：若 `d < (1/3) * n^(1/4)`，则 `k/d` 是 `e/n` 的连分数展开中的一个收敛子（convergent）。因为 `φ(n) ≈ n`，误差项极小。

算法：
1. 对 `e/n` 连分数展开，得到所有收敛子 `k_i / d_i`。
2. 对每个 `d_i`，用 `e*d_i - 1 = k_i * φ(n)`，若 `k_i != 0`，令 `phi = (e*d_i - 1) / k_i`。
3. 解方程 `x^2 - (n - phi + 1)x + n = 0`，判别式为 `(p-q)^2`；若判别式是完全平方且求得整数 `p, q`，则 `d_i` 正确。
4. `m = pow(c, d, n)`。

## 三、解题步骤

1. 观察 `e` 位数 ≫ 65537，先跑维纳。
2. 若维纳失败但 `d` 稍大（如 `n^(1/4)` 到 `n^(0.292)` 之间），换 **扩展维纳（Boneh-Durfee）**，需要 SageMath + LLL。
3. 若 `n` 由多个素数组成（`n = p1*p2*...`），维纳公式仍可用但 `phi` 要换成对应欧拉函数，常见失败原因见坑点。
4. 成功后验证 `pow(pow(m, e, n), d, n) == m`。

## 四、可直接运行的脚本

```python
from Crypto.Util.number import long_to_bytes
import gmpy2

def continued_fraction(num, den):
    cf = []
    while den:
        cf.append(num // den)
        num, den = den, num % den
    return cf

def convergents(cf):
    n0, n1 = 0, 1
    d0, d1 = 1, 0
    for a in cf:
        n0, n1 = n1, a * n1 + n0
        d0, d1 = d1, a * d1 + d0
        yield n1, d1          # (k, d) 候选

def wiener_attack(e, n):
    for k, d in convergents(continued_fraction(e, n)):
        if k == 0:
            continue
        if (e * d - 1) % k:
            continue
        phi = (e * d - 1) // k
        s = n - phi + 1                        # p + q
        disc = s * s - 4 * n                   # (p - q)^2
        if disc < 0:
            continue
        t, exact = gmpy2.iroot(disc, 2)
        if not exact:
            continue
        if (s + t) % 2:
            continue
        return d
    return None

# --- 自测 ---
from Crypto.Util.number import getPrime, inverse
from random import getrandbits
p, q = getPrime(512), getPrime(512)
n = p * q
d = getrandbits(200) | 1
while gmpy2.gcd(d, (p-1)*(q-1)) != 1:
    d = getrandbits(200) | 1
e = inverse(d, (p-1)*(q-1))
print("d found:", wiener_attack(e, n) == d)
```

扩展维纳 / Boneh-Durfee（SageMath，`d < n^0.292`）：

```python
# sage
def boneh_durfee(e, n, delta=0.292, m=4):
    R.<x, y> = PolynomialRing(Zmod(e))
    A = Integer(2) * ((n + 1) // 2)       # ≈ p+q
    f = x * (A + y) + 1                   # 源自 ed - k*phi ≡ 0
    # 构造 Herrmann-May 格，LLL 后取小根（详见 CTF-Wiki 扩展维纳）
    ...  # 生产环境直接用 GitHub 上的 standard-lib attack
```

## 五、常见坑 / 变体

- **`d` 的界是硬门槛**：`d > n^(1/4)/3` 时维纳必失败，不要去调参，直接上格方法。
- `e/n` 的连分数里可能出现 `k == 0` 的收敛子（即 `1/0`），要 `continue`。
- 某些题 `n` 不是两个素数乘积而是 `p^r`，此时 `phi` 公式不同（`p^(r-1)(p-1)`），需要改判别式分支或直接因式分解小 `r`。
- 有的题把 `e` 写成"看起来大"但其实是 `e = d^-1 mod φ` 的正常值——先 `bit_length` 检查一下再动手。
- 求出的 `d` 可能对应"错误收敛子"但恰好通过判别式检验的概率极低，仍建议加密验证一次。
- 与 `rsa-dp-leak.md`、`lattice-lll.md` 联动：`d` 稍大时先用 `dp` 泄露，再考虑格。

## 六、参考来源

- [CTF-Wiki 私钥 d 相关攻击（维纳攻击）](https://ctf-wiki.org/crypto/asymmetric/rsa/d_attacks/rsa_d_attack/)
- [CTF-Wiki 扩展维纳攻击](https://ctf-wiki.org/crypto/asymmetric/rsa/d_attacks/rsa_extending_wiener/)
- [CTF-Wiki GitHub](https://github.com/ctf-wiki/ctf-wiki)
- [维纳攻击原始论文（Boneh 综述 / Wiener 1990）](https://en.wikipedia.org/wiki/Wiener%27s_attack)
