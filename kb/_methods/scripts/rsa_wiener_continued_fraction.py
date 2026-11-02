#!/usr/bin/env python3
"""Wiener 攻击：d 很小时用 e/n 的连分数逼近还原私钥指数。

依赖：纯标准库（--selftest 用 PyCryptodome 造密钥，可选）。
用途：RSA 题里 d 远小于 n**0.25（常见于"私钥指数取了很小的值"），
      此时 e/n 的某个渐近分数 k/d 直接给出 d。

用法：
  python rsa_wiener_continued_fraction.py --n N --e E [--c C] [--json]
  python rsa_wiener_continued_fraction.py --selftest

输出：候选 k/d 中能成功分解 n 的那一组，以及还原出的明文（给了 --c 时）。
"""
from __future__ import annotations

import argparse
import json
import sys

MAX_TERMS = 2000  # 连分数项数上限，防止异常输入卡死


def continued_fraction(num: int, den: int) -> list[int]:
    """num/den 的连分数展开 [a0; a1, a2, ...]。"""
    out = []
    while den and len(out) < MAX_TERMS:
        q, r = divmod(num, den)
        out.append(q)
        num, den = den, r
    return out


def convergents(cf: list[int]):
    """逐项生成渐近分数 (num, den)，即 p_i/q_i。"""
    p_prev, p_cur = 0, 1
    q_prev, q_cur = 1, 0
    for a in cf:
        p_prev, p_cur = p_cur, a * p_cur + p_prev
        q_prev, q_cur = q_cur, a * q_cur + q_prev
        yield p_cur, q_cur


def wiener(n: int, e: int) -> list[tuple[int, int, int, int]]:
    """返回 [(k, d, p, q)]：所有能让 phi 解出整数 p、q 且 p*q==n 的候选。"""
    found = []
    for k, d in convergents(continued_fraction(e, n)):
        if k == 0 or d == 0:
            continue
        # ed - 1 = k*phi  =>  phi = (ed-1)/k
        if (e * d - 1) % k != 0:
            continue
        phi = (e * d - 1) // k
        # p + q = n - phi + 1，p*q = n  => 判别式
        s = n - phi + 1
        disc = s * s - 4 * n
        if disc < 0:
            continue
        r = isqrt_exact(disc)
        if r is None:
            continue
        if (s + r) % 2:
            continue
        p = (s + r) // 2
        q = (s - r) // 2
        if p * q == n:
            found.append((k, d, p, q))
    return found


def isqrt_exact(x: int) -> int | None:
    if x < 0:
        return None
    r = x
    if r < 2:
        return r if r * r == x else None
    # 牛顿迭代，标准库 math.isqrt 也可，此处保留以便阅读实现细节
    r = 1 << ((x.bit_length() + 1) // 2)
    while True:
        nr = (r + x // r) // 2
        if nr >= r:
            break
        r = nr
    return r if r * r == x else None


def long_to_bytes(v: int) -> bytes:
    return v.to_bytes((v.bit_length() + 7) // 8, "big") or b"\x00"


def selftest() -> int:
    from Crypto.Util.number import getPrime, inverse

    fails = []

    # ---- 算例 1：经典 Wiener 参数，d 取 5~6 位十进制，远小于 n**0.25 ----
    p, q = getPrime(256), getPrime(256)
    n = p * q
    phi = (p - 1) * (q - 1)
    d = 123457  # 很小的 d
    e = inverse(d, phi)
    hits = wiener(n, e)
    if not hits:
        fails.append("case1: 未还原出 d")
    else:
        k, d_rec, p_rec, q_rec = hits[0]
        if d_rec != d:
            fails.append(f"case1: d 错误 {d_rec} != {d}")
        if {p_rec, q_rec} != {p, q}:
            fails.append("case1: 分解出的 p q 与真值不符")
        m = pow(pow(424242, e, n), d, n)
        if m != 424242:
            fails.append("case1: 用还原的 d 解密失败")

    # ---- 算例 2：d 正常大小（d = e^{-1} mod phi，与 n 同量级）时应明确失败 ----
    n2 = getPrime(128) * getPrime(128)
    if wiener(n2, 65537):
        fails.append("case2: 对正常大小的 d 误报成功（不应命中）")

    # ---- 算例 3：连分数展开本身正确（已知有理数 415/93）----
    cf = continued_fraction(415, 93)
    if cf != [4, 2, 6, 7]:
        fails.append(f"case3: 415/93 连分数错误 {cf}")
    last = list(convergents(cf))[-1]
    if last != (415, 93):
        fails.append(f"case3: 末项渐近分数应为 415/93，实际 {last}")

    # ---- 算例 4：isqrt_exact 边界 ----
    for v, exp in [(0, 0), (1, 1), (4, 2), (15, None), (16, 4), (10**20, 10**10)]:
        got = isqrt_exact(v)
        if got != exp:
            fails.append(f"case4: isqrt_exact({v}) = {got}, 期望 {exp}")

    for f in fails:
        print(f"FAIL {f}", file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 4/4（小 d 还原、正常 d 不误报、连分数展开、整数开方）")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Wiener 小私钥指数攻击")
    ap.add_argument("--n", type=lambda s: int(s, 0))
    ap.add_argument("--e", type=lambda s: int(s, 0))
    ap.add_argument("--c", type=lambda s: int(s, 0), help="可选密文，给了就顺带解密")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.n is None or args.e is None:
        ap.error("需要 --n 和 --e，或用 --selftest")

    hits = wiener(args.n, args.e)
    if not hits:
        print("未找到有效 d（该题不满足 d < n^0.25/3 的 Wiener 条件）", file=sys.stderr)
        return 2
    k, d, p, q = hits[0]
    out = {"k": k, "d": d, "p": p, "q": q, "candidates": len(hits)}
    if args.c is not None:
        m = pow(args.c, d, args.n)
        out["m_int"] = m
        out["m_bytes"] = long_to_bytes(m).decode("latin-1")
    if args.json:
        print(json.dumps({k2: (str(v) if isinstance(v, int) and v > 2**53 else v)
                          for k2, v in out.items()}, ensure_ascii=False, indent=2))
    else:
        print(f"找到 {len(hits)} 组候选，采用第一组：k={k}")
        print(f"d = {d}")
        print(f"p = {p}")
        print(f"q = {q}")
        if args.c is not None:
            print(f"m = {long_to_bytes(pow(args.c, d, args.n))!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
