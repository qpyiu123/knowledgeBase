"""把内层模数作为指数乘子，做有界的 Pollard p−1 分解。依赖 sympy，可用 gmpy2 加速。"""

# 取自《密码学题解汇编》shared/src/cryptoexp/utils/nested_pm1.py。
# 原作者 coolmoon & guaidao2，MIT 许可见同目录 LICENSE.txt。

import math

from sympy import isprime


class CapacityGap(ValueError):
    pass


def primes(limit, check):
    sieve = bytearray(b"\1") * (limit + 1)
    sieve[:2] = b"\0\0"
    for p in range(2, math.isqrt(limit) + 1):
        if p % 128 == 0:
            check()
        if sieve[p]:
            sieve[p * p :: p] = b"\0" * ((limit - p * p) // p + 1)
    return (p for p in range(2, limit + 1) if sieve[p])


def recover(
    inner, outer, bound=1 << 21, check=lambda: None, progress=lambda *args: None
):
    if (
        any(type(x) is not int or x <= 2 for x in (inner, outer))
        or not inner < outer
        or inner.bit_length() > 4096
        or outer.bit_length() > 8192
    ):
        raise ValueError("内外 RSA 模数大小或关系无效")
    if type(bound) is not int or not 32 <= bound <= 1 << 22:
        raise ValueError("p-1 平滑界须在 32–2^22 内")
    try:
        import gmpy2

        convert = gmpy2.mpz
        power = gmpy2.powmod
        gcd = gmpy2.gcd
    except ImportError:
        convert = int
        power = pow
        gcd = math.gcd
    modulus = convert(outer)
    remainder = inner
    value = power(2, inner, modulus)
    start = value
    batch = []
    pairs = []
    count = 0

    def prime(x):
        return isprime(int(x))

    prime_list = list(primes(bound, check))
    for index, p in enumerate(prime_list):
        check()
        exponent = p
        while exponent * p <= bound:
            exponent *= p
        value = power(value, exponent, modulus)
        batch.append(exponent)
        count += 1
        if count % 16384 == 0:
            progress(count, p, len(pairs))
        if len(batch) < 128 and index < len(prime_list) - 1:
            continue
        if gcd(value - 1, modulus) > 1:
            replay = start % modulus
            for exponent in batch:
                check()
                replay = power(replay, exponent, modulus)
                factor = int(gcd(replay - 1, modulus))
                if 1 < factor < int(modulus) and prime(factor):
                    inside = math.gcd(factor - 1, remainder)
                    if 1 < inside < remainder and prime(inside):
                        pairs.append((inside, factor))
                        remainder //= inside
                        modulus //= factor
                        replay %= modulus
                        progress(count, p, len(pairs))
            value = replay
            if (
                pairs
                and prime(remainder)
                and prime(modulus)
                and math.gcd(int(modulus) - 1, inner) == remainder
            ):
                pairs.append((remainder, int(modulus)))
                break
        start = value
        batch = []
    if (
        math.prod(i for i, o in pairs) != inner
        or math.prod(o for i, o in pairs) != outer
    ):
        raise CapacityGap("当前平滑界 / 基数未分离全部内外因子；未声称输入冲突或无解")
    if any((o - 1) % i for i, o in pairs):
        raise ValueError("内外素因子整除关系不匹配")
    return pairs, {
        "prime_steps": count,
        "smooth_bound": bound,
        "base": 2,
        "factor_products_verified": True,
        "outer_minus_one_links_verified": True,
    }
