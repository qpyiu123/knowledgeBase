"""把本地赛题里的递推、消元和分组关系写成可回验的函数。

仿射、位运算、尖点与分组异或只用标准库。有限域多项式用 sympy。
函数收题面数值，不载入或运行题目脚本。
"""

from itertools import product
from math import gcd, isqrt, lcm


def affine_jump(seed, a, b, modulus, steps):
    """计算 f(x)=a*x+b 的第 steps 次迭代；允许合数模数。"""
    if steps < 0 or modulus < 2:
        raise ValueError("步数须非负，模数须大于 1。")
    mul, add = a % modulus, b % modulus
    seed %= modulus
    while steps:
        if steps & 1:
            seed = (mul * seed + add) % modulus
        mul, add = mul * mul % modulus, (mul + 1) * add % modulus
        steps >>= 1
    return seed


def affine_repeat(seed, observed, a, b, p):
    """已知 A=f^k(s)，求 f^k(A)。p 是素数，k 可以未知。"""
    a %= p
    if a == 1:
        return (2 * observed - seed) % p
    fixed = b * pow(1 - a, -1, p) % p
    if (seed - fixed) % p == 0:
        if (observed - fixed) % p:
            raise ValueError("固定点的观测值与原始递推不符。")
        return fixed
    ratio = (observed - fixed) * pow(seed - fixed, -1, p) % p
    return (fixed + ratio * (observed - fixed)) % p


def and_xor_pair(bit_and, bit_xor, product_value):
    """从非负整数的 AND、XOR 与乘积恢复无序二元组。"""
    if min(bit_and, bit_xor) < 0 or product_value <= 0 or bit_and & bit_xor:
        raise ValueError("按位提示与正整数乘积不相容。")
    total = 2 * bit_and + bit_xor
    disc = total * total - 4 * product_value
    root = isqrt(disc) if disc >= 0 else -1
    if root * root != disc or (total + root) % 2:
        raise ValueError("判别式不是与因子和同奇偶的整数平方。")
    a, b = (total - root) // 2, (total + root) // 2
    if a * b != product_value or a & b != bit_and or a ^ b != bit_xor:
        raise ValueError("候选未通过原始提示。")
    return a, b


def cusp_scalar(p, coefficients, base, target):
    """原曲线为 y²+a*x*y+c*y=x³+b*x²+d*x+e；p>3。"""
    a, b, c, d, e = coefficients
    inv2 = pow(2, -1, p)
    inv4 = inv2 * inv2 % p
    r = -(b + a * a * inv4) * pow(3, -1, p) % p
    if (d + a * c * inv2 - 3 * r * r) % p or (e + c * c * inv4 + r**3) % p:
        raise ValueError("配方后不是三重根，不能用尖点参数。")

    def parameter(point):
        if point is None:
            return 0
        x, y = point
        Y = (y + (a * x + c) * inv2) % p
        if Y * Y % p != pow(x - r, 3, p) or not Y:
            raise ValueError("点不在曲线上，或落在奇点。")
        return (x - r) * pow(Y, -1, p) % p

    t = parameter(base)
    if not t:
        raise ValueError("基点不能是单位元。")
    u = parameter(target)
    scalar = u * pow(t, -1, p) % p
    if u:
        inv = pow(u, -1, p)
        x = (r + inv * inv) % p
        y = (pow(inv, 3, p) - (a * x + c) * inv2) % p
        assert (x, y) == tuple(v % p for v in target)
    return scalar


def cbc_from_block_decrypt(iv_and_ciphertext, ecb_output):
    """两份数据按同一序列 IV||C1||… 分组，ECB 输出的第一块丢弃。"""
    if (
        len(iv_and_ciphertext) != len(ecb_output)
        or len(ecb_output) < 32
        or len(ecb_output) % 16
    ):
        raise ValueError("需要长度相同、分组对齐的 IV＋密文与 ECB 输出。")
    return bytes(x ^ y for x, y in zip(iv_and_ciphertext[:-16], ecb_output[16:]))


def field_roots(expr, variable, p):
    """用一次因子取出 GF(p) 中的根；为零的多项式需另行判断。"""
    from sympy import Poly

    poly = Poly(expr, variable, modulus=p)
    if poly.is_zero:
        raise ValueError("等式在整个域恒成立，不能列成有限个根。")
    factors = poly.factor_list()[1]
    return sorted(
        {
            -int(f.nth(0)) * pow(int(f.nth(1)), -1, p) % p
            for f, _ in factors
            if f.degree() == 1
        }
    )


def equation_pairs(p, f, g):
    """Equation：返回已代回两条公开式的 (x,y)。"""
    from sympy import Symbol

    x = Symbol("x")
    expr = 13 * (g - x**2) ** 2 + 7 * x * (g - x**2) + 245 * x - 49 * f
    inv7 = pow(7, -1, p)
    pairs = [(z, (g - z * z) * inv7 % p) for z in field_roots(expr, x, p)]
    assert all(
        (13 * y * y + z * y + 5 * z) % p == f % p and (7 * y + z * z) % p == g % p
        for z, y in pairs
    )
    return pairs


def curve_factor_pairs(n, a, b, P):
    """myez_encode：假设 p,q 均为域内代表元，枚举两者的候选。"""
    from sympy import Symbol, isprime

    x = Symbol("x")
    pairs = []
    for p in field_roots(x**4 + a * x * x + b * x - n, x, P):
        if p > 1 and n % p == 0:
            q = n // p
            if q < P and q == (p**3 + a * p + b) % P and isprime(p) and isprime(q):
                pairs.append((p, q))
    return pairs


def prime_power_roots(c, e, p):
    from sympy import Symbol

    if gcd(e, p - 1) == 1:
        return [pow(c, pow(e, -1, p - 1), p)]
    x = Symbol("x")
    return field_roots(x**e - c % p, x, p)


def two_prime_roots(c, e, p, q):
    """保留所有回验通过的根；适合很小的非互素指数。"""
    n = p * q
    inv = pow(p, -1, q)
    roots = {
        u + p * ((v - u) * inv % q)
        for u, v in product(prime_power_roots(c, e, p), prime_power_roots(c, e, q))
    }
    return sorted(x for x in roots if pow(x, e, n) == c % n)


def cyclic_power(coefficients, exponent, modulus):
    """在模 x^k−1 的多项式环中算幂，k 为系数表长度。"""
    k = len(coefficients)
    if not k or exponent < 0 or modulus < 2:
        raise ValueError("需要非空系数表、非负指数和大于 1 的模数。")

    def multiply(a, b):
        out = [0] * k
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                out[(i + j) % k] = (out[(i + j) % k] + x * y) % modulus
        return out

    acc = [1] + [0] * (k - 1)
    base = list(coefficients)
    while exponent:
        if exponent & 1:
            acc = multiply(acc, base)
        base = multiply(base, base)
        exponent >>= 1
    return acc


def quotient_message(coefficients, exponent, p, q):
    """PolyRSA：从两个素数域上的因子次数，选用共同的逆指数。"""
    from sympy import Poly, Symbol, isprime

    if p == q or not isprime(p) or not isprime(q):
        raise ValueError("需要两个不同的素数。")
    x = Symbol("x")
    k = len(coefficients)
    periods = []
    for prime in (p, q):
        factors = Poly(x**k - 1, x, modulus=prime).factor_list()[1]
        if any(multiplicity != 1 for _, multiplicity in factors):
            raise ValueError("模多项式有重因子，不能把所有分量当成域。")
        periods.extend(prime ** f.degree() - 1 for f, _ in factors)
    period = lcm(*periods)
    n = p * q
    clear = cyclic_power(coefficients, pow(exponent, -1, period), n)
    assert cyclic_power(clear, exponent, n) == [v % n for v in coefficients]
    return clear


def known_nonce_private(r, s, digest, nonce, order):
    """ECDSA：digest 是签名所用哈希字节，按群阶长度取左侧位。"""
    h = int.from_bytes(digest, "big") >> max(0, len(digest) * 8 - order.bit_length())
    return (s * nonce - h) * pow(r, -1, order) % order
