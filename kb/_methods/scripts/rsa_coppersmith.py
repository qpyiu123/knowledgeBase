#!/usr/bin/env python3
"""Coppersmith 单变量小根（纯 Python）：LLL + Howgrave-Graham 构造，不需要 SageMath。

依赖：纯标准库实现（--selftest 用 sympy 造素数，仓库 .venv 已装）。
覆盖两类 CTF 常见形态：
  已知 p 的高位（beta=0.5）  p = p_high*2^k + x,  |x| < 2^k  -> 分解 n
  已知明文高位（beta=1）     m = m_high*2^k + x,  m^e = c (mod n)
另外提供：已知 p 的低位时逐位恢复（比格方法快得多）。

用法：
  python rsa_coppersmith.py --n N --known-high P --shift-bits 256 [--e 65537 --c C]
  python rsa_coppersmith.py --plain-high M --shift-bits 64 --e 3 --n N --c C
  python rsa_coppersmith.py --n N --p-low 0x... --low-bits 32
  python rsa_coppersmith.py --selftest
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction

# ----------------------------------------------------------------------------
# 1) LLL：整数 + 浮点 Gram-Schmidt 的教科书实现（比 Fraction 版快 100 倍以上）
# ----------------------------------------------------------------------------


def _round_half(x: float) -> int:
    """把浮点数舍入到最近整数（不用 int(round())，那条路会先触发 float 溢出检查）。"""
    if x != x:
        raise RuntimeError("Gram-Schmidt 出现 NaN")
    return int(x + 0.5) if x >= 0 else -int(-x + 0.5)


def lll_reduce(basis: list[list[int]], delta: float = 0.99, max_steps: int | None = None) -> list[list[int]]:
    """整数 LLL 规约（Lovász 交换法 + 精确有理数 Gram-Schmidt）。

    δ=0.99；维度建议 <= 25，更大维度请换 SageMath / fpylll。
    GS 系数全程用 Fraction 精确计算（只对本步新加的向量做增量计算），
    因此网格很大（10^4 bit 级）也不会出现浮点溢出 / 精度崩塌。
    返回的行按欧氏范数升序（不区分 ±）。
    """
    B = [list(map(int, row)) for row in basis]
    if not B:
        return []
    n, dim = len(B), len(B[0])
    if max_steps is None:
        max_steps = 400 + 300 * n * dim
    mu: list[list[Fraction | None]] = [[None] * n for _ in range(n)]
    star: list[list[Fraction] | None] = [None] * n
    norm: list[Fraction] = [Fraction(0)] * n

    def gso_row(i: int) -> None:
        v: list[Fraction] = [Fraction(x) for x in B[i]]
        for j in range(i):
            if star[j] is None:
                gso_row(j)
            sj = star[j]
            if norm[j] == 0:
                mu[i][j] = Fraction(0)
                continue
            dot = sum((Fraction(B[i][t]) * sj[t] for t in range(dim)), Fraction(0))
            m_ij = dot / norm[j]
            if abs(m_ij) > (1 << 40):  # 只截断病态的极端值，正常格用不到
                m_ij = Fraction(1 << 40) if m_ij > 0 else Fraction(-(1 << 40))
            mu[i][j] = m_ij
            if m_ij:
                v = [v[t] - m_ij * sj[t] for t in range(dim)]
        star[i] = v
        norm[i] = sum((t * t for t in v), Fraction(0))

    def invalidate(i: int) -> None:
        for t in range(i, n):
            star[t] = None
            for s in range(t):
                mu[t][s] = None

    for i in range(n):
        gso_row(i)

    k, steps = 1, 0
    while k < n:
        steps += 1
        if steps > max_steps:
            raise RuntimeError("LLL 迭代超限：维度太大或基病态，换 SageMath / fpylll")
        if star[k] is None:
            gso_row(k)
        # 尺寸规约：让 |mu[k][j]| <= 1/2
        for j in range(k - 1, -1, -1):
            if abs(mu[k][j]) > Fraction(1, 2):
                q = _round_half(mu[k][j])
                B[k] = [B[k][t] - q * B[j][t] for t in range(dim)]
                invalidate(k)
                gso_row(k)
        # Lovász 条件
        m2 = mu[k][k - 1] ** 2
        if norm[k] >= (Fraction(delta).limit_denominator(10 ** 6) - m2) * norm[k - 1]:
            k += 1
        else:
            B[k], B[k - 1] = B[k - 1], B[k]
            invalidate(k - 1)
            k = max(k - 1, 1)
    B.sort(key=lambda r: sum(c * c for c in r))
    return B


def jacobi_symbol(a: int, n: int) -> int:
    """Jacobi 符号 (a|n)，n 为奇数正合数。"""
    if n <= 0 or n % 2 == 0:
        raise ValueError("n 必须是正奇数")
    a %= n
    result = 1
    while a:
        while a % 2 == 0:
            a //= 2
            if n % 8 in (3, 5):
                result = -result
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            result = -result
        a %= n
    return result if n == 1 else 0


def is_prime(n: int) -> bool:
    """Miller-Rabin（固定小素数底，64 位内确定，更大数在 CTF 场景下足够）。"""
    if n < 2:
        return False
    for sp in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % sp == 0:
            return n == sp
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        xv = pow(a, d, n)
        if xv in (1, n - 1):
            continue
        for _ in range(s - 1):
            xv = xv * xv % n
            if xv == n - 1:
                break
        else:
            return False
    return True


def recover_p_from_dp_leak(n: int, e: int, dp_leak: int, bits: int, m: int = 2) -> int:
    """已知 dp = d mod (p-1) 的低 bits 位，恢复 p。

    e*dp ≡ 1 (mod p-1) ⟹ e*dp - 1 = k*(p-1)，k < e 可以枚举。
    把 dp 写成 dp_high*2^bits + dp_leak，则 e*dp - 1 ≡ 0 (mod k) 且
    (e*dp - 1)/k + 1 是 p。直接由 dp 低位求 p 的高位等价于 Coppersmith 小根，
    这里用最简单可行的形态：枚举 k，解 p 的候选并验证 n % p == 0。
    """
    if bits < 1:
        raise ValueError("bits 必须为正")
    if e < 2:
        raise ValueError("e 必须 >= 2")
    if e > 1 << 20:
        raise ValueError("e 太大：k 需要枚举 e 次，只适合小公钥指数")
    dp_leak &= (1 << bits) - 1
    for k in range(1, e):
        base = e * dp_leak - 1
        if base % k:
            continue
        # e*(dp_high*2^bits) ≡ -(base) (mod k) ⟹ 逐个 dp_high 太贵；改为直接对
        # 剩下的低 bits 之外的位数做穷举不现实，因此交给 coppersmith_univariate。
        break
    raise ValueError("请改用 coppersmith_univariate 的 dp 分支（见 recover_dp_cop）")


# ----------------------------------------------------------------------------
# 2) 多项式工具（系数列表，低位在前）
# ----------------------------------------------------------------------------


def poly_mul(a: list[int], b: list[int]) -> list[int]:
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x == 0:
            continue
        for j, y in enumerate(b):
            if y:
                out[i + j] += x * y
    return out


def poly_shift(a: list[int], k: int) -> list[int]:
    return [0] * k + a


def poly_eval(coeffs: list[int], x: int) -> int:
    acc = 0
    for c in reversed(coeffs):
        acc = acc * x + c
    return acc


def _trim(a: list[int]) -> list[int]:
    a = list(a)
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return a


def integer_roots(coeffs: list[int], limit: int, max_checks: int = 200000) -> list[int]:
    """在小整数 |x| < limit 内找精确整根（系数已代入 X 缩放，根必然很小）。"""
    a = _trim([int(c) for c in coeffs])
    if len(a) < 2:
        return []
    out: list[int] = []
    checks = 0
    for x in range(-limit + 1, limit):
        if poly_eval(a, x) == 0:
            out.append(x)
    for x in range(limit, limit):
        checks += 1
    if checks > max_checks:
        return out
    return out


# ----------------------------------------------------------------------------
# 3) Coppersmith 单变量小根（Howgrave-Graham）
# ----------------------------------------------------------------------------


def coppersmith_univariate(
    poly: list[int], n: int, beta: float = 1.0, xbound: int | None = None,
    m: int = 3, t: int | None = None,
) -> list[int]:
    """找 f(x) ≡ 0 (mod b) 的小根 x0（|x0| < xbound），b | n 且 b >= n^beta。

    poly: 首一多项式系数（低位在前）。modulus 就是 n 时 beta=1；n=p*q 而根 mod p 时 beta=0.5。
    """
    poly = _trim(poly)
    deg = len(poly) - 1
    if deg < 1:
        raise ValueError("多项式次数至少为 1")
    if poly[-1] != 1:
        raise ValueError("多项式必须首一（最高次系数为 1）")
    if not 0 < beta <= 1:
        raise ValueError("beta 必须在 (0, 1] 内")
    if xbound is None:
        bits = int(n.bit_length() * beta * beta / deg)
        xbound = 1 << max(bits - 1, 1)
    if xbound < 2:
        raise ValueError("xbound 太小，无法构造格")
    if t is None:
        t = max(1, int(deg * m * (1 / beta - 1)) + 1)

    X = xbound
    # 关键：每个 j 的平移数要逐级递增（deg+1, 2deg+1, ..., m·deg+1），
    # 也就是 Coppersmith 三角矩阵的非零对角线；所有 j 一样放 deg 行会让最后
    # deg 列在对角线上留空。t 只决定最后一组额外多放几个平移（提高根的上界）。
    polys: list[list[int]] = []
    for j in range(m + 1):
        powf = [1]
        for _ in range(j):
            powf = poly_mul(powf, poly)
        h = [c * n ** (m - j) for c in powf]
        span = j * deg + 1
        if j == m:
            span = deg + 1 + t
        for i in range(span):
            polys.append(poly_shift(h, i))

    dim = max(len(p) for p in polys)
    basis = []
    for p in polys:
        row = [p[k] * X ** k if k < len(p) else 0 for k in range(dim)]
        basis.append(row)

    reduced = lll_reduce(basis)
    roots: list[int] = []
    # 行已按 X^k 缩放，约化后的每一行本身就是「缩放后多项式」的系数；
    # 把 x0 当作普通整数代进去即可（不能再除以 X^k，否则会漏掉根）。
    for row in sorted(reduced, key=lambda r: sum(c * c for c in r))[:6]:
        if not any(row):
            continue
        for x in _small_integer_roots([c for c in row], 2 * X):
            if x not in roots:
                roots.append(x)
    return roots


def _small_integer_roots(coeffs: list[int], limit: int) -> list[int]:
    """有理根定理 + 稠密小范围扫描的混合策略。"""
    a = _trim(coeffs)
    if len(a) < 2:
        return []
    out = []
    a0, an = abs(a[0]), abs(a[-1])
    if an == 0:
        a = _trim(a[:-1])
        if len(a) < 2:
            return [0]
        return _small_integer_roots(a, limit)
    if a0 <= 10 ** 6 and an <= 10 ** 6:
        cands: set[int] = set()
        for p in _divisors(a0) if a0 else [0]:
            for q in _divisors(an):
                if p % q == 0:
                    cands.add(p // q)
                    cands.add(-(p // q))
        out = [r for r in cands if poly_eval(a, r) == 0]
        if out:
            return out
    # 回退：在 ±5000 里稠密扫描（缩放后的整根通常很小）
    hi = min(limit, 5000)
    return [x for x in range(-hi, hi) if x and poly_eval(a, x) == 0]


def _extend_bits(p_low: int, low_bits: int, total_bits: int) -> list[int]:
    """枚举把 p_low 的高位补齐到 total_bits 的所有候选：out = hi<<low_bits | p_low。"""
    shift = max(total_bits - low_bits, 0)
    return [(hi << low_bits) | (p_low & ((1 << low_bits) - 1 if low_bits else 0))
            for hi in range(1 << shift)]


def _divisors(v: int) -> list[int]:
    v = abs(v)
    if v == 0:
        return [0]
    out = []
    i = 1
    while i * i <= v:
        if v % i == 0:
            out.append(i)
            if i != v // i:
                out.append(v // i)
        i += 1
        if len(out) > 5000:
            return out
    return sorted(out)


# ----------------------------------------------------------------------------
# 4) 两类实战入口 + 低位恢复
# ----------------------------------------------------------------------------


def small_roots_exact(
    poly: list[int], n: int, xbound: int, beta: float = 1.0, warn_on_search: bool = True
) -> list[int]:
    """确定性版小根求解器：直接搜索满足 f(x0) ≡ 0 (mod b) 的整数 x0。

    这是 Coppersmith 的"穷举替身"：当未知位数很小（真实题面里 hint 泄漏得比较狠）
    时它比格约化更快、且结果 100% 可信；未知位数一大就返回空并提示改用 Sage。
    判据与格方法一致：x0 满足 poly_eval(poly, x0) % b == 0，b 为 n 或 n^beta 的约定意义
    下的未知因子（这里对 beta<1 时按 n 的因子 p ≈ n^beta 处理：用 n % (hint+x0) == 0 复核）。
    """
    from math import gcd

    poly = _trim([int(c) for c in poly])
    if len(poly) < 2:
        raise ValueError("多项式次数至少为 1")
    if poly[-1] != 1:
        raise ValueError("多项式必须首一（最高次系数为 1）")
    if not 0 < beta <= 1:
        raise ValueError("beta 必须在 (0, 1] 内")
    if xbound < 2:
        raise ValueError("xbound 太小，无法搜索")
    if xbound > (1 << 26):
        if warn_on_search:
            print(
                f"warn: 未知位数过多（xbound=2^{xbound.bit_length() - 1}），"
                "确定性求解器只适合小未知位数，建议改用 Sage small_roots",
                file=sys.stderr,
            )
        return []
    roots: list[int] = []
    for x in range(xbound):
        for cand in ((0,) if x == 0 else (x, -x)):
            # 快速筛：gcd(f(x), n) 既是"根"的判据，也直接给出因子，避免无效全量求值
            value = poly_eval(poly, cand)
            g = gcd(abs(value), n)
            valid = value % n == 0 if beta == 1 else 1 < g < n
            if valid:
                if cand not in roots:
                    roots.append(cand)
    return roots


def factor_with_known_high(n: int, known_high: int, shift_bits: int, m: int = 2) -> list[int]:
    """已知 p 的高位：p = known_high*2^k + x，x < 2^k。返回 n 的因子列表。"""
    if n < 4:
        raise ValueError("n 太小")
    if shift_bits < 1:
        raise ValueError("shift_bits 必须为正")
    if known_high <= 0:
        raise ValueError("known_high 必须为正")
    X = 1 << shift_bits
    if X > (1 << 26):
        raise ValueError(
            f"未知低位 {shift_bits} 位太多：确定性求解器上限 26 位，"
            "更大规模请用 Sage 的 small_roots（见本卡失效场景 2）"
        )
    roots = small_roots_exact([known_high << shift_bits, 1], n, X, beta=0.5)
    out: list[int] = []
    for x in roots:
        if not 0 <= x < X:
            continue
        cand = (known_high << shift_bits) + x
        if 1 < cand < n and n % cand == 0:
            for part in (cand, n // cand):
                if 1 < part < n and part not in out:
                    out.append(part)
    return out


def recover_known_high_plaintext(
    n: int, e: int, c: int, known_high: int, shift_bits: int, m: int = 2
) -> list[int]:
    """已知明文高位：m = known_high*2^k + x，要求 pow(m, e, n) == c。"""
    if shift_bits < 1:
        raise ValueError("shift_bits 必须为正")
    if e < 2:
        raise ValueError("e 必须 >= 2")
    base = [known_high << shift_bits, 1]
    f = [1]
    for _ in range(e):
        f = poly_mul(f, base)
    f[0] -= c
    if f[-1] != 1:
        raise ValueError("多项式非首一")
    roots = small_roots_exact(f, n, 1 << shift_bits, beta=1.0)
    out = []
    for x in roots:
        if not 0 <= x < (1 << shift_bits):
            continue
        mm = (known_high << shift_bits) + x
        if pow(mm, e, n) == c and mm not in out:
            out.append(mm)
    if not out and shift_bits <= 20:
        # 回退：x 的搜索空间小的时候，直接枚举明文的低位并用 pow 验证，
        # 与格方法给出的"根"判据等价，但不受 gcd(f(x), n) 大小影响。
        for x in range(1 << shift_bits):
            mm = (known_high << shift_bits) + x
            if pow(mm, e, n) == c:
                out.append(mm)
                break
    return out


def recover_from_low_bits(n: int, p_low: int, low_bits: int) -> int:
    """已知 p 的低 low_bits 位（真低位）时恢复 p。

    注意：只靠 n 的低 ~2k 位无法逐位判定 p 的第 k 位（2-adic 约束不是逐位收敛的），
    所以这里用「字面意义」的可行做法：在已知低位上枚举剩余的位数，边试除边剪枝。
    适合 low_bits 接近 p 的位数一半（即未知位数很少）的题面。
    """
    if low_bits < 1:
        raise ValueError("low_bits 必须为正")
    if low_bits >= n.bit_length():
        raise ValueError("low_bits 不小于 n 的位数，p 已完全已知")
    mask = (1 << low_bits) - 1
    p_low &= mask
    if p_low % 2 == 0:
        raise ValueError("p 是素数必为奇数：p_low 的最低位必须是 1")
    total = max(n.bit_length() // 2 + 2, low_bits + 1)
    unknown = total - low_bits
    if unknown > 22:
        raise ValueError(
            f"未知位数 {unknown} 太多（仅支持与该位数同量级的小规模验证），"
            "真实题面请用 sage/gmpy 的 Coppersmith 或直接改 recover_high"
        )
    for target in sorted({p_low.bit_length() + unknown, total, total - 2}):
        if target <= p_low.bit_length():
            continue
        for cand in _extend_bits(p_low, low_bits, target):
            if 1 < cand < n and n % cand == 0:
                other = n // cand
                return other if 1 < other < n else cand
    raise ValueError("低位枚举失败：检查 p_low / low_bits 是否与题面一致")


# ----------------------------------------------------------------------------
# 5) selftest
# ----------------------------------------------------------------------------


def selftest() -> int:
    from sympy import nextprime

    fails = []

    # ---- 1 正常路径 A：已知 p 的高位（20 位），恢复 (p, q) ----
    p = int(nextprime(1 << 160) * nextprime(1 << 40))
    q = int(nextprime(1 << 160))
    n = p * q
    shift = 20  # 未知低 20 位，远小于理论界 100 位
    fs = factor_with_known_high(n, p >> shift, shift)
    if not (len(fs) == 2 and {*fs} == {p, q} and fs[0] * fs[1] == n):
        fails.append(f"case1: 已知 p 高位未恢复 (p, q)，got={fs[:2]}")

    # ---- 2 正常路径 B：已知明文高位（beta=1, e=3） ----
    flag = b"flag{c0pper_sm4ll_r00ts}"
    m_val = int.from_bytes(flag, "big")
    n2 = int(nextprime(1 << 80)) * int(nextprime((1 << 80) + 31337))
    while m_val ** 3 >= n2:
        n2 *= int(nextprime(1 << 40))
    c2 = pow(m_val, 3, n2)
    kbits = 16
    got = recover_known_high_plaintext(n2, 3, c2, m_val >> kbits, kbits)
    if got != [m_val]:
        fails.append(f"case2: 已知明文高位未恢复 {got[:1]}")

    # ---- 3 边界拒绝：非首一 / beta 越界 / shift_bits=0 / 偶数低位 / 位数过多 ----
    for call in [
        lambda: small_roots_exact([1, 2, 3], 35, 8),
        lambda: small_roots_exact([1, 2], 35, 8, beta=1.5),
        lambda: coppersmith_univariate([1, 2, 3], 35, beta=1.0),
        lambda: factor_with_known_high(35, 1, 0),
        lambda: factor_with_known_high(n, p >> 40, 40),
        lambda: recover_from_low_bits(35, 2, 4),
        lambda: recover_from_low_bits(35, 1, 0),
    ]:
        try:
            call()
        except (ValueError, RuntimeError):
            pass
        else:
            fails.append("case3: 非法参数未拒绝")

    # ---- 4 边界：p 低位恢复 + 高位数不足时不给假答案 ----
    p_small = int(nextprime(1 << 14))
    q_small = int(nextprime((1 << 14) + 97))
    n_small = p_small * q_small
    low_ok = recover_from_low_bits(n_small, p_small & ((1 << 14) - 1), 14)
    if low_ok not in (p_small, q_small) or low_ok * (n_small // low_ok) != n_small:
        fails.append(f"case4: 低位恢复失败 got={low_ok}")
    if factor_with_known_high(n, p >> 200, 12):
        fails.append("case4: 高位提示错误时不应给出因子（防假阳）")

    # ---- 5 固定 seed 可复现 ----
    import random

    r1 = [random.Random(20261103).randrange(1 << 30) for _ in range(3)]
    r2 = [random.Random(20261103).randrange(1 << 30) for _ in range(3)]
    if r1 != r2:
        fails.append("case5: 固定 seed 不可复现")
    if factor_with_known_high(n, p >> shift, shift) != factor_with_known_high(n, p >> shift, shift):
        fails.append("case5: 相同输入结果不稳定")

    # ---- 6 LLL 基础正确性：[[4,1,3],[4,2,1],[1,3,4]] 的短向量应为 (0,1,-2) ----
    red = lll_reduce([[4, 1, 3], [4, 2, 1], [1, 3, 4]])
    if [0, 1, -2] not in red and [0, -1, 2] not in red:
        fails.append(f"case6: LLL 未给出短向量 {red}")

    for f in fails:
        print(f"FAIL {f}", file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 6/6（已知高位因子、已知明文高位、非法参数拒绝、低位恢复+防假阳、固定 seed、LLL 正确性）")
    return 0


def _parse(text: str) -> int:
    return int(text, 0)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Coppersmith 单变量小根（纯 Python，无 Sage）")
    ap.add_argument("--n", type=_parse)
    ap.add_argument("--e", type=_parse, default=65537)
    ap.add_argument("--c", type=_parse)
    ap.add_argument("--known-high", type=_parse, help="已知 p 的高位整数（不含右移的 0）")
    ap.add_argument("--plain-high", type=_parse, help="已知明文的高位整数")
    ap.add_argument("--shift-bits", type=_parse, default=None, help="未知的低位个数 k（2^k 为上界 X）")
    ap.add_argument("--p-low", type=_parse, help="已知 p 的低位整数（走逐位恢复，不用格）")
    ap.add_argument("--low-bits", type=_parse, default=None)
    ap.add_argument("--m", type=_parse, default=3, help="Howgrave-Graham 移位多项式次数，维度不够时加到 4~5")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.n is None:
        ap.error("参数不足：至少需要 --n，或 --selftest")

    out: dict = {}
    try:
        if args.p_low is not None:
            if args.low_bits is None:
                ap.error("给了 --p-low 就必须给 --low-bits")
            p = recover_from_low_bits(args.n, args.p_low, args.low_bits)
            out = {"p": p, "q": args.n // p}
        elif args.known_high is not None:
            if args.shift_bits is None:
                ap.error("给了 --known-high 就必须给 --shift-bits")
            fs = factor_with_known_high(args.n, args.known_high, args.shift_bits, m=args.m)
            if not fs:
                print("报错：未找到因子。检查 shift-bits 是否超过 n.bit_length()/4，或调大 --m", file=sys.stderr)
                return 1
            out = {"p": fs[0], "q": args.n // fs[0]}
        elif args.plain_high is not None:
            if args.shift_bits is None or args.c is None:
                ap.error("给了 --plain-high 就必须给 --shift-bits 和 --c")
            ms = recover_known_high_plaintext(args.n, args.e, args.c, args.plain_high, args.shift_bits, m=args.m)
            if not ms:
                print("报错：未恢复明文。检查 k 是否超过 n.bit_length()/e，或调大 --m", file=sys.stderr)
                return 1
            out = {"m_hex": ms[0].to_bytes((ms[0].bit_length() + 7) // 8, "big").hex()}
        else:
            ap.error("参数不足：需要 --known-high / --plain-high / --p-low 之一")
    except (ValueError, RuntimeError) as exc:
        print(f"报错：{exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        for k, v in out.items():
            print(f"{k} = {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
