---
title: RSA Fermat 分解（p、q 相近）
category: crypto
tags: [rsa, fermat, 因式分解, p q 相近]
signals: [p 和 q 很接近, p q 差值很小, 两个素数相邻, nextprime, 同一个素数生成 p 和 q, n 用相近素数生成, 分解 n]
difficulty: easy
source: "CTF-Wiki / 公开 writeup"
tools: [python, gmpy2]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 题面代码：`p = getPrime(512); q = nextprime(p)` 或 `q = getPrime(512)` 但只差几十 bit 位。
- `n` 的因子距离很小：`|p - q|` 远小于 `√n`。
- 题目提示"我用了两个非常接近的质数"、"p 和 q 只差一点点"。
- `n` 的十进制位数刚好是 `2*bitlen(p)` 甚至更短（因为乘积接近平方数）。
- 变体：`p = next_prime(q * 2**k + r)` 之类，需要先做近似估计。
- 变体：给了 `n` 且 `isqrt(n)^2 - n` 是完全平方 —— 一眼 Fermat。

## 二、原理

Fermat 分解基于恒等式：

```
n = p*q = a^2 - b^2 = (a+b)(a-b),  其中 a = (p+q)/2, b = (p-q)/2
```

从 `a = ceil(sqrt(n))` 开始，检查 `a^2 - n` 是否为完全平方：

```
a = ceil(sqrt(n))
while True:
    b2 = a*a - n
    if is_square(b2):
        return (a - isqrt(b2), a + isqrt(b2))
    a += 1
```

迭代次数约为 `(p+q)/2 - sqrt(n) ≈ (p-q)^2 / (8*sqrt(n))`。当 `|p-q| < 2*n^(1/4)` 时，几十次内收敛；`p`、`q` 完全随机时则需要天文数字次迭代，不可用。

## 三、解题步骤

1. 先求 `a = isqrt(n) + 1`。
2. 循环 `a += 1`，判断 `a*a - n` 是否完全平方数（`gmpy2.iroot(x, 2)`）。
3. 得到 `p = a - b, q = a + b`，验算 `p*q == n`。
4. 计算 `d = invert(e, (p-1)*(q-1))`，解密。
5. 若迭代超过阈值（例如 `10^7`）仍未命中，说明 `p, q` 差距太大，改用 yafu / Pollard / 其他方法。

## 四、可直接运行的脚本

```python
from Crypto.Util.number import long_to_bytes, inverse
from gmpy2 import isqrt, iroot

def fermat(n, max_iter=10_000_000):
    a = isqrt(n)
    if a * a == n:
        return a, a
    a += 1
    for _ in range(max_iter):
        b2 = a * a - n
        b, exact = iroot(int(b2), 2)
        if exact:
            return int(a - b), int(a + b)
        a += 1
    raise ValueError("迭代超限，p/q 差距过大")

def solve(n, e, c):
    p, q = fermat(n)
    assert p * q == n
    d = inverse(e, (p - 1) * (q - 1))
    return long_to_bytes(pow(c, d, n))

# --- 自测 ---
from Crypto.Util.number import getPrime
p = getPrime(512)
q = p + 1234567          # 差距极小，几秒内收敛
n, e = p * q, 65537
m = int.from_bytes(b"flag{f3rm4t_1s_f4st}", "big")
c = pow(m, e, n)
print(solve(n, e, c))
```

快速判定"是否值得跑 Fermat"：

```python
from gmpy2 import isqrt
n = 0x...  # 题面 n
a = isqrt(n) + 1
print("首次迭代差值 a^2-n =", a*a - n)   # 越小越接近正方形，Fermat 越快
print("经验界 sqrt(n)^(1/2) =", isqrt(isqrt(n)))
```

## 五、一页速查：常见攻击的输入与输出

```python
# 所有函数接收 (n, ...) 并返回明文 bytes；直接复制即可套题
def rsa_dispatch(n, e, c, extra=None):
    """按题面特征自动分流到对应攻击"""
    from Crypto.Util.number import long_to_bytes
    extra = extra or {}
    if "e1" in extra and "c2" in extra:                 # 共模
        from gmpy2 import gcdext, invert
        e1, c1, e2, c2 = extra["e1"], c, extra["e2"], extra["c2"]
        g, a, b = gcdext(e1, e2)
        if a < 0: a, c1 = -a, invert(c1, n)
        if b < 0: b, c2 = -b, invert(c2, n)
        return long_to_bytes(int((pow(c1, int(a), n) * pow(c2, int(b), n)) % n))
    if "dp" in extra:                                   # dp 泄露
        dp = extra["dp"]
        for k in range(1, e):
            if (e * dp - 1) % k: continue
            p = (e * dp - 1) // k + 1
            if p > 1 and n % p == 0:
                q = n // p
                from Crypto.Util.number import inverse
                d = inverse(e, (p - 1) * (q - 1))
                return long_to_bytes(pow(c, d, n))
    if e and e > 2 ** 128:                              # e 过大 -> 维纳
        from math import isqrt
        from gmpy2 import iroot
        def cf(a, b):
            while b:
                yield a // b
                a, b = b, a % b
        h1, h2, d1, d2 = 0, 1, 1, 0
        for x in cf(e, n):
            h1, h2 = h2, x * h2 + h1
            d1, d2 = d2, x * d2 + d1
            if h2 == 0 or d2 == 0: continue
            if (e * d2 - 1) % h2: continue
            phi = (e * d2 - 1) // h2
            s = n - phi + 1
            disc = s * s - 4 * n
            if disc < 0: continue
            t, ok = iroot(disc, 2)
            if not ok: continue
            return long_to_bytes(pow(c, d2, n))
    if e == 3:                                          # 小 e
        from gmpy2 import iroot
        r, ok = iroot(c, 3)
        if ok: return long_to_bytes(int(r))
        for k in range(1 << 20):
            r, ok = iroot(int(c + k * n), 3)
            if ok: return long_to_bytes(int(r))
    raise ValueError("未匹配到攻击类型，补参数")
```

> 用法：先把题面的 `(n, e, c)` 填好，再把额外参数（`e1/e2/c2`、`dp`）塞进 `extra`，
> 一次跑完四类常见攻击，命中就打印明文。

## 六、常见坑 / 变体

- **`p, q` 都是偶数位长且随机**：Fermat 迭代次数是天文数字，别硬跑，先换 Pollard rho / yafu / `fragment`。
- `p, q` 相距较远但 `p+q` 已知（例如题面泄漏 `p+q`）：直接解二次方程 `x^2 - (p+q)x + n = 0`。
- 变体：`n = p^2`（`isqrt` 直接是整数）→ 直接 `iroot(n, 2)`。
- 变体：`p = next_prime(q // 2)` 等有比例关系时，可以用 `n / ratio` 开方估计再 Fermat。
- 变体：多素数 `n = p*q*r` 且三数相近 → 双边分解（Dixon / Fermat 推广），通常转 Sage 的 `factor()`。
- 大整数运算用 `gmpy2.iroot` 比 `math.isqrt` 判定"是否完全平方"更快，但 `math.isqrt` 在 Python 3.8+ 已足够。
- 别在解密前忘记验证 `p*q == n`，否则会得到乱码而浪费时间。


## 七、参考来源

- [CTF-Wiki 模数相关攻击](https://ctf-wiki.org/crypto/asymmetric/rsa/rsa_module_attack/)
- [CTF-Wiki RSA 复杂题目](https://ctf-wiki.org/crypto/asymmetric/rsa/rsa_complex/)
- [Fermat's factorization method（维基百科）](https://en.wikipedia.org/wiki/Fermat%27s_factorization_method)
- [CTF-Wiki GitHub](https://github.com/ctf-wiki/ctf-wiki)
