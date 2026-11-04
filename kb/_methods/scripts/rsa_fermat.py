#!/usr/bin/env python3
"""RSA Fermat 分解：p、q 相距很近时从 ceil(sqrt(n)) 向上找完全平方差。

依赖：纯标准库（--selftest 用 sympy 造素数，仓库 .venv 已装）。
用途：p = getPrime(512); q = nextprime(p) 一类题，迭代次数 ≈ (p-q)^2 / (8*sqrt(n))，几十次内收敛。

用法：
  python rsa_fermat.py --n N [--e E --c C] [--max-iter 1000000] [--json]
  python rsa_fermat.py --selftest

输出：p、q（以及给了 e、c 时的明文）；迭代超限时明确报错 exit 1。
"""
from __future__ import annotations

import argparse
import json
import sys


def isqrt_exact(x: int) -> int | None:
    if x < 0:
        return None
    r = x
    if r < 2:
        return r if r * r == x else None
    r = 1 << ((x.bit_length() + 1) // 2)
    while True:
        nr = (r + x // r) // 2
        if nr >= r:
            break
        r = nr
    return r if r * r == x else None


def fermat(n: int, max_iter: int = 1_000_000) -> tuple[int, int, int]:
    """返回 (p, q, iterations)。失败抛 ValueError（附中文说明）。"""
    if n < 4:
        raise ValueError("n 太小（需要合数 n >= 4）")
    a = isqrt_exact(n)
    if a is not None:  # n 本身是完全平方：n = p^2
        return a, a, 0
    a = _isqrt(n) + 1
    for it in range(1, max_iter + 1):
        b2 = a * a - n
        b = isqrt_exact(b2)
        if b is not None:
            p, q = a - b, a + b
            if p * q == n and p > 1:
                return p, q, it
        a += 1
    raise ValueError(f"迭代超过 {max_iter} 次：p 与 q 差距太大，改 Pollard rho / yafu")


def _isqrt(n: int) -> int:
    r = 1 << ((n.bit_length() + 1) // 2)
    while True:
        nr = (r + n // r) // 2
        if nr >= r:
            return r
        r = nr


def closeness_score(n: int) -> int:
    """a^2 - n 越小说明越接近正方形，Fermat 越快；做题时先打印它做判定。"""
    a = _isqrt(n) + 1
    return a * a - n


def solve(n: int, e: int, c: int, max_iter: int = 1_000_000) -> tuple[int, int, bytes]:
    p, q, _ = fermat(n, max_iter)
    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)
    m = pow(c, d, n)
    return p, q, m.to_bytes((m.bit_length() + 7) // 8, "big")


def selftest() -> int:
    from sympy import nextprime

    fails = []

    # ---- 1 正常路径：p、q 相近（差 1234567），分解 + 解密 ----
    p = int(nextprime(1 << 200))
    q = int(nextprime(p + 1234567))
    n = p * q
    e = 65537
    flag = b"flag{f3rm4t_1s_f4st}"
    c = pow(int.from_bytes(flag, "big"), e, n)
    p2, q2, it = fermat(n)
    if {p2, q2} != {p, q}:
        fails.append("case1: 分解结果与真值不符")
    if it > 10:
        fails.append(f"case1: 相近素数应 10 次内收敛，实际 {it}")
    _, _, m = solve(n, e, c)
    if m != flag:
        fails.append("case1: 解密明文错误")

    # ---- 2 边界：n = p^2 必须直接返回 (p, p) ----
    pr = int(nextprime(1 << 100))
    if fermat(pr * pr)[:2] != (pr, pr):
        fails.append("case2: n=p^2 未走平方分支")

    # ---- 3 边界拒绝：n 太小 / 迭代超限必须抛 ValueError ----
    p_far = int(nextprime(1 << 160))
    q_far = int(nextprime(p_far * 7))
    for args, kw in [((3,), {}), ((1,), {}), ((p_far * q_far,), {"max_iter": 1})]:
        try:
            fermat(*args, **kw)
        except ValueError:
            pass
        else:
            fails.append(f"case3: {args} {kw} 未被拒绝")

    # ---- 4 参数不足 / 不适用判定：随机素数差距大时 closeness_score 应远大于 0 ----
    r1 = int(nextprime(1 << 160))
    r2 = int(nextprime(r1 * 7))
    if closeness_score(r1 * r2) == 0:
        fails.append("case4: 差距大的模数不应被识别为平方")
    try:
        fermat(r1 * r2, max_iter=50)
    except ValueError:
        pass
    else:
        fails.append("case4: 差距大的模数不应在 50 次内成功")

    # ---- 5 固定 seed 可复现 ----
    import random

    rnd = random.Random(20261103)
    gaps = [rnd.randrange(1, 1000) for _ in range(3)]
    rnd2 = random.Random(20261103)
    if gaps != [rnd2.randrange(1, 1000) for _ in range(3)]:
        fails.append("case5: 固定 seed 不可复现")
    for g in gaps:
        pp = int(nextprime(1 << 150))
        qq = int(nextprime(pp + g))
        got = fermat(pp * qq)
        if set(got[:2]) != {pp, qq}:
            fails.append(f"case5: gap={g} 分解失败")

    for f in fails:
        print(f"FAIL {f}", file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 5/5（相近素数分解、n=p^2 边界、非法输入拒绝、不适用判定、固定 seed）")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="RSA Fermat 分解（p、q 相近）")
    ap.add_argument("--n", type=lambda s: int(s, 0))
    ap.add_argument("--e", type=lambda s: int(s, 0))
    ap.add_argument("--c", type=lambda s: int(s, 0))
    ap.add_argument("--max-iter", type=lambda s: int(s, 0), default=1_000_000)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.n is None:
        ap.error("参数不足：需要 --n（解密再加 --e --c），或 --selftest")
    if args.e is not None and args.c is None:
        ap.error("参数不足：给了 --e 就必须给 --c（只分解请勿传 --e）")
    if args.max_iter < 1:
        print("报错：--max-iter 必须为正整数", file=sys.stderr)
        return 2

    try:
        p, q, it = fermat(args.n, args.max_iter)
    except ValueError as exc:
        print(f"报错：{exc}", file=sys.stderr)
        return 1

    out = {"p": p, "q": q, "iterations": it, "closeness": closeness_score(args.n)}
    if args.e is not None:
        try:
            m = pow(args.c, pow(args.e, -1, (p - 1) * (q - 1)), args.n)
        except ValueError:
            print("报错：e 与 phi 不互素，换共模/小 e 等分支", file=sys.stderr)
            return 2
        out["m_ascii"] = m.to_bytes((m.bit_length() + 7) // 8, "big").decode("latin-1")
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(f"p = {p}\nq = {q}\n迭代 {it} 次")
        if "m_ascii" in out:
            print(f"m = {out['m_ascii']!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
