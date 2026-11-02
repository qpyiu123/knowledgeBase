#!/usr/bin/env python3
"""RSA 共模攻击：同一个 n、两组 (e, c) 还原明文。

依赖：PyCryptodome（仅用于 --selftest 生成密钥）；核心逻辑只用标准库。
用途：题面只给一个 n，却给了两组 (e1,c1)/(e2,c2) 时，用扩展欧几里得组合
      两个密文，直接得到 m，**不需要分解 n**。

用法：
  python rsa_common_modulus.py --n N --e1 E1 --c1 C1 --e2 E2 --c2 C2 [--json]
  python rsa_common_modulus.py --selftest

限制：e1/e2 不互素时本脚本不自动开根（g>1 会如实报错并给出提示）。
"""
from __future__ import annotations

import argparse
import json
import sys


def egcd(a: int, b: int) -> tuple[int, int, int]:
    """扩展欧几里得：返回 (g, x, y) 使 a*x + b*y = g。"""
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    return old_r, old_s, old_t


def long_to_bytes(value: int) -> bytes:
    if value == 0:
        return b"\x00"
    return value.to_bytes((value.bit_length() + 7) // 8, "big")


def bytes_to_long(data: bytes) -> int:
    return int.from_bytes(data, "big")


def common_modulus(n: int, e1: int, c1: int, e2: int, c2: int) -> tuple[int, int]:
    """返回 (g, m_g)：m_g = m**g mod n，g = gcd(e1, e2)。

    g == 1 时 m_g 就是明文；g > 1 时需要额外开 g 次根（本函数不做）。
    """
    g, a, b = egcd(e1, e2)
    if g != 1:
        # 不互素时仍能算出 m**g，但无法直接还原 m
        return g, _combine(n, a, b, c1, c2)
    return 1, _combine(n, a, b, c1, c2)


def _combine(n: int, a: int, b: int, c1: int, c2: int) -> int:
    # 负指数要先取逆元；Python 的 pow(x, 负数, n) 虽支持但语义容易看错，这里显式处理
    if a < 0:
        a, c1 = -a, pow(c1, -1, n)
    if b < 0:
        b, c2 = -b, pow(c2, -1, n)
    return (pow(c1, a, n) * pow(c2, b, n)) % n


def selftest() -> int:
    from Crypto.Util.number import getPrime, inverse

    fails = []
    # ---- 算例 1：小素数，e1=3 e2=5 互素，正常路径 ----
    p, q = getPrime(128), getPrime(128)
    n = p * q
    m = bytes_to_long(b"flag{common_modulus_selftest}")
    e1, e2 = 3, 5
    c1, c2 = pow(m, e1, n), pow(m, e2, n)
    g, rec = common_modulus(n, e1, c1, e2, c2)
    if g != 1 or rec != m:
        fails.append("case1: 互素共模未还原明文")
    if long_to_bytes(rec) != b"flag{common_modulus_selftest}":
        fails.append("case1: 字节串不一致")

    # ---- 算例 2：负系数分支（e1=5 e2=17 时贝祖系数一正一负）----
    e3, e4 = 5, 17
    c3, c4 = pow(m, e3, n), pow(m, e4, n)
    g2, rec2 = common_modulus(n, e3, c3, e4, c4)
    _, a, b = egcd(e3, e4)
    has_neg = a < 0 or b < 0
    if not has_neg:
        fails.append("case2: 期望出现负系数，实际没有（算例失去意义）")
    if rec2 != m:
        fails.append("case2: 负指数分支未还原明文")

    # ---- 算例 3：不互素时 g>1，结果等于 m**g，且不谎报成功 ----
    g3, rec3 = common_modulus(n, 3, pow(m, 3, n), 9, pow(m, 9, n))
    if g3 != 3:
        fails.append("case3: gcd(3,9)=3 未识别")
    if rec3 != pow(m, 3, n):
        fails.append("case3: m**g 计算错误")

    # ---- 算例 4：e 有逆元检查（防止把公钥指数当私钥用）----
    if inverse(e1, n) * e1 % n != 1:
        fails.append("case4: inverse 不可用")

    for f in fails:
        print(f"FAIL {f}", file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 4/4（互素还原、负系数、不互素 g=3、逆元）")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="RSA 共模攻击（同 n 不同 e）")
    ap.add_argument("--n", type=lambda s: int(s, 0), help="模数，支持 0x 前缀")
    ap.add_argument("--e1", type=lambda s: int(s, 0))
    ap.add_argument("--c1", type=lambda s: int(s, 0))
    ap.add_argument("--e2", type=lambda s: int(s, 0))
    ap.add_argument("--c2", type=lambda s: int(s, 0))
    ap.add_argument("--json", action="store_true", help="JSON 输出")
    ap.add_argument("--selftest", action="store_true", help="内置微型算例自检")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if None in (args.n, args.e1, args.c1, args.e2, args.c2):
        ap.error("需要同时提供 --n --e1 --c1 --e2 --c2，或用 --selftest")

    g, m_g = common_modulus(args.n, args.e1, args.c1, args.e2, args.c2)
    out = {
        "g": g,
        "recovered": g == 1,
        "m_int": str(m_g),
        "m_hex": hex(m_g),
        "m_bytes": long_to_bytes(m_g).decode("latin-1") if g == 1 else None,
    }
    if g != 1:
        out["note"] = "e1,e2 不互素：已得到 m**g mod n，还需开 g 次根（或对 m**g+k*n 枚举开方）"
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(f"gcd(e1,e2) = {g}")
        print(f"m (int)    = {m_g}")
        if g == 1:
            print(f"m (bytes)  = {long_to_bytes(m_g)!r}")
    return 0 if g == 1 else 2


if __name__ == "__main__":
    sys.exit(main())
