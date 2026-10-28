---
title: ElGamal / Paillier / Rabin 同态性质与攻击面
category: crypto
tags: [elgamal, paillier, rabin, 同态加密, 选择密文]
signals: [加密结果可以相乘后解密, 题目给了 (c1 c2) 两元组, 提到了加法同态, paillier 的 g 等于 n+1, 反复对同一密文做乘法再解密, 密文是 (u v) 形式, 模数是两个素数的乘积 n=pq, rabin 加密 e 等于 2, 解密给出四个根, 给了 oracle 能解密任意密文]
difficulty: medium
source: "CTF-Wiki ElGamal / RSA 选择明密文 / Wikipedia Paillier"
tools: [python, gmpy2, SageMath]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 密文是 **二元组** `(c1, c2)` 或 `(u, v)`；源码里 `c1 = g^k mod p`、`c2 = m * h^k mod p`。
- 题面出现 `g = n+1`、`n^2` 取模、`L(x) = (x-1)//n`——这是 Paillier。
- 加密指数固定为 `e = 2`，解密时给的是「四个根之一」——这是 Rabin。
- 题目提供 oracle：能解任意密文，或能对密文做「乘一个常数后再解密」。同态性质被当作武器。
- `p-1` 光滑（`p = 2^k·q + 1`），或 `g` 的阶很小（`g^q ≡ 1`）。
- 同一个随机数 `r` 被用在两条 ElGamal / Paillier 密文里（nonce 复用）。
- 要求恢复「最后一个随机数」「群里的某个离散对数」或「明文之间的差值」。

## 二、原理

1. **ElGamal（乘法同态）**
   `Enc(m) = (g^r, m·h^r)`，`Dec(c1,c2) = c2·(c1^x)^(-1)`。
   - 同态：`Enc(m1)·Enc(m2) = Enc(m1·m2)`（逐元素相乘）。
   - **nonce 复用**：两条密文共用 `r`，则 `c1` 相同，直接 `m1/m2 = c2_1/c2_2`；配合已知明文或明文小空间即可解出。
   - **乘性选择密文**：给 oracle 送 `(c1, c2·t)`，它解密得到 `m·t`，于是能控制明文、做乘性差分。
   - **小子群攻击**：`g` 的阶只有小因子 `q` 时，把密文升到 `(p-1)/q` 次，离散对数落进 `q` 阶子群，可直接枚举。
2. **Paillier（加法同态）**
   `Enc(m) = g^m·r^n mod n^2`，`g = n+1` 时 `Enc(m1)·Enc(m2) = Enc(m1+m2)`，`Enc(m)^k = Enc(k·m)`。
   - **`r` 复用**：两条密文用同一 `r`，则 `c1/c2 = g^(m1-m2)`，枚举小差值即可读数。
   - **小明文**：`(1+n)^m ≡ 1 + mn (mod n^2)`，`c` 的 n 进制低位里直接含着 `m`。
   - **选择密文**：让 oracle 解 `Enc(m)·Enc(δ)` 得 `m+δ`，按 `m+δ` 是否越过 `n` 做二分。
3. **Rabin（平方，四解）**
   `c = m^2 mod n`，`n = pq`，解密有 **4 个根**。明文有冗余（flag 格式、固定前缀）才能挑出真根。
   - 求根：`p ≡ q ≡ 3 (mod 4)` 时 `m_p = c^((p+1)/4) mod p`，`m_q = c^((q+1)/4) mod q`，CRT 组合出 4 根。
   - **选择密文可分解 n**：让 oracle 解 `c·k^2` 得到 `m'`，若 `m' ≠ ±m·k (mod n)`，则 `gcd(m' - mk, n)` 直接给出 `p` 或 `q`。

## 三、解题步骤

1. 判断方案：二元组 + `g,h,p` → ElGamal；`n^2` + `g=n+1` → Paillier；`e=2` + 四解 → Rabin。
2. ElGamal：先看 `c1` 是否重复（nonce 复用），再看 `p-1` 是否光滑（Pohlig-Hellman），最后考虑选择密文。
3. Paillier：先测 `r` 复用，再看 `m` 是否小到可枚举，都不行就走加法同态 + oracle 二分。
4. Rabin：拿任一非平凡根做 `gcd` 分解 `n`，四根全枚举，按明文格式筛选。
5. 全程记住：**同态性质 = 免费的明文运算器**，题里只要给了 oracle，先想同态。

## 四、可直接运行的脚本

```python
# ElGamal / Paillier / Rabin 的同态演示与三类攻击（纯 python，自带自测）
import math, random

def is_probable_prime(x):
    if x < 2:
        return False
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]:
        if x % p == 0:
            return x == p
    d, s = x - 1, 0
    while d % 2 == 0:
        d //= 2; s += 1
    for a in [2, 3, 5, 7, 11, 13, 17]:
        v = pow(a, d, x)
        if v in (1, x - 1):
            continue
        for _ in range(s - 1):
            v = v * v % x
            if v == x - 1:
                break
        else:
            return False
    return True

def gen_prime(bits, cond=lambda p: True):
    while True:
        p = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_probable_prime(p) and cond(p):
            return p

# ---- ElGamal：加密 / 解密 / nonce 复用 ----
def elgamal_enc(m, p, g, h, r=None):
    r = r or random.randrange(2, p - 1)
    return pow(g, r, p), m * pow(h, r, p) % p

def elgamal_dec(c, x, p):
    c1, c2 = c
    return c2 * pow(pow(c1, x, p), -1, p) % p

def elgamal_reuse(c_a, c_b, p):
    """共用 r：c1 相同 -> m_a/m_b = c2_a/c2_b。"""
    (c1a, c2a), (c1b, c2b) = c_a, c_b
    assert c1a == c1b, "c1 不同，不是 nonce 复用"
    return c2a * pow(c2b, -1, p) % p

# ---- Rabin：四解 + 由 oracle 根分解 n ----
def rabin_decrypt_all(c, p, q):
    n = p * q
    rp, rq = pow(c, (p + 1) // 4, p), pow(c, (q + 1) // 4, q)
    inv_p, inv_q = pow(p, -1, q), pow(q, -1, p)
    roots = set()
    for a in (rp, p - rp):
        for b in (rq, q - rq):
            roots.add((a * q * inv_q + b * p * inv_p) % n)
    return sorted(roots)

def rabin_factor_from_oracle(m_oracle, m_expected, n):
    """oracle 返回 m^2 的一个根 m'；m' 与 ±m 不同则 gcd 直接分解 n。"""
    g = math.gcd(m_oracle - m_expected, n)
    return g if 1 < g < n else None

if __name__ == "__main__":
    p = gen_prime(64); g = random.randrange(2, p - 1)
    x = random.randrange(2, p - 1); h = pow(g, x, p)
    ca, cb = elgamal_enc(1234, p, g, h), elgamal_enc(9999, p, g, h)
    assert elgamal_dec(ca, x, p) == 1234 and elgamal_dec(cb, x, p) == 9999
    r_fixed = random.randrange(2, p - 1)
    c1, c2 = elgamal_enc(1234, p, g, h, r_fixed), elgamal_enc(9999, p, g, h, r_fixed)
    assert elgamal_reuse(c1, c2, p) == 1234 * pow(9999, -1, p) % p
    print("ElGamal 加解密 + nonce 复用 OK")

    p2 = gen_prime(64, lambda v: v % 4 == 3); q2 = gen_prime(64, lambda v: v % 4 == 3)
    nn = p2 * q2; m0 = random.randrange(2, nn)
    roots = rabin_decrypt_all(pow(m0, 2, nn), p2, q2)
    assert len(roots) == 4 and m0 in roots
    print("Rabin 四解 OK:", len(roots))
```

Paillier 的 keygen、加解密与两种经典攻击：

```python
def lcm(a, b):
    return a // math.gcd(a, b) * b

def paillier_keygen(p, q):
    n = p * q
    lam = lcm(p - 1, q - 1)
    g = n + 1
    mu = pow(lam, -1, n)
    return (n, g), (lam, mu)

def paillier_enc(m, pub, r=None):
    n, g = pub
    r = r or random.randrange(2, n)
    return pow(g, m, n * n) * pow(r, n, n * n) % (n * n)

def paillier_dec(c, pub, priv):
    n, _ = pub
    lam, mu = priv
    return ((pow(c, lam, n * n) - 1) // n) * mu % n

def paillier_reuse(c1, c2, n):
    """两条密文用同一个 r：c1/c2 = g^(m1-m2)，枚举小差值即可。"""
    g = n + 1
    ratio = c1 * pow(c2, -1, n * n) % (n * n)
    for d in range(0, 1 << 16):
        if pow(g, d, n * n) == ratio:
            return d
        if pow(g, n - d, n * n) == ratio:
            return -d
    return None

def paillier_small_msg(c, n):
    """m 很小时 (1+n)^m ≡ 1 + m*n (mod n^2)；对 c 做 n 进制展开读低位即可。"""
    low = c % (n * n)
    # c = (1+mn) * r^n -> 先去掉 r^n 的贡献：这里用「两次密文相除」消除 r
    return None if low == 0 else (low - 1) // n
```

## 五、常见坑 / 变体

- **ElGamal 的 `h` 与私钥**：`h = g^x`；若题给 `x` 就不是攻击题，直接解密。
- **`p-1` 光滑**：ElGamal 的离散对数用 Pohlig-Hellman，先分解 `p-1`，再对小因子分别解 DL、最后 CRT。
- **Paillier 的 `r` 必须与 `n` 互素**：若 `r` 由 `randint(0, n)` 生成，可能取到 0 或与 `n` 共享因子，直接泄 `n` 的分解。
- **`lambda` vs `phi`**：解密用 `lam = lcm(p-1,q-1)`；用 `phi(n)` 也能解，但 `mu` 必须按同样的模数重算，混用必错。
- **Rabin 四解歧义**：没有明文冗余时 4 个根都「合法」，靠后续加密/格式筛选；先 `gcd` 分解反而更快。
- **Rabin 的 `p,q ≡ 3 mod 4`**：不是这个形式时 `(p+1)/4` 不是整数，需 Tonelli-Shanks 或改选素数。
- **同态当 oracle**：凡是给了「解密任意密文 / 允许密文相乘」的题，先当同态题试探，通常比硬解离散对数快得多。

## 六、参考来源

- [CTF-Wiki ElGamal](https://ctf-wiki.org/crypto/asymmetric/discrete-log/elgamal/)
- [CTF-Wiki ElGamal 签名](https://ctf-wiki.org/crypto/signature/elgamal/)
- [Wikipedia: Paillier cryptosystem](https://en.wikipedia.org/wiki/Paillier_cryptosystem)
- [Wikipedia: Rabin cryptosystem](https://en.wikipedia.org/wiki/Rabin_cryptosystem)
- [CTF-Wiki RSA 选择明密文攻击](https://ctf-wiki.org/crypto/asymmetric/rsa/rsa_chosen_plain_cipher/)
