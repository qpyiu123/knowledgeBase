"""复做较难的密码题：python lattice_samples.py 题目编号 原附件。需要 sympy 和 pycryptodome。"""

import argparse
import json
import re
from ast import literal_eval
from itertools import product
from math import comb, gcd, prod
from pathlib import Path
from zipfile import ZipFile

from Crypto.Util.Padding import unpad
from sympy import Matrix, Poly, Rational, isprime, symbols
from sympy.polys.matrices import lll as exact_lll

# 用有理数精确取整，避免大整数转为浮点数。
exact_lll.mfloor = lambda v: v.numerator // v.denominator


def source(path, member):
    with ZipFile(path) as z:
        return z.read(member).decode("utf-8")


def named(source, names):
    return [
        literal_eval(re.search(r"(?m)^" + k + r"\s*=\s*(.+)$", source)[1])
        for k in names
    ]


def flag_int(value):
    return value.to_bytes((value.bit_length() + 7) // 8, "big")


def format_ok(data):
    return bool(re.fullmatch(rb"[A-Za-z0-9_]+\{[ -~]+\}", data))


def rsa_middle_bits(path):
    c, n, pxor = named(source(path, "highlow.py").split("'''")[1], ("c", "n", "pxor"))
    width = 352
    shift = 400
    X = 1 << width
    known = pxor & ~((X - 1) << shift)
    a = known * pow(1 << shift, -1, n) % n
    # 取 n^(m-i)*(a+x)^i 及 x^j*(a+x)^m；每列乘以 X 的相应次幂。
    for m, t in [(4, 4), (5, 5)]:
        dim = m + t
        rows = []
        for i in range(m):
            rows.append(
                [
                    comb(i, k) * a ** (i - k) * n ** (m - i) * X**k if k <= i else 0
                    for k in range(dim)
                ]
            )
        for j in range(t):
            rows.append(
                [
                    comb(m, k - j) * a ** (m - k + j) * X**k if j <= k <= j + m else 0
                    for k in range(dim)
                ]
            )
        y = symbols("y")
        reduced = Matrix(rows).lll(delta=Rational(3, 4))
        for row in reduced.tolist():
            poly = Poly(sum((coef // X**k) * y**k for k, coef in enumerate(row)), y)
            for x in poly.ground_roots():
                if not x.is_Integer or not 0 <= x < X:
                    continue
                p = known + (int(x) << shift)
                if not (1 < p < n and n % p == 0):
                    continue
                value = (pxor ^ p) >> shift
                assert pow(value, 65537, n) == c and format_ok(flag_int(value))
                return {
                    "known_middle_offset": shift,
                    "unknown_bits": width,
                    "lattice_dim": dim,
                    "factor_and_cipher_verified": True,
                }
    raise ValueError("未找到可回验的小根")


def invert(rows, p):
    n = len(rows)
    work = [
        list(map(int, r)) + [int(i == j) for j in range(n)] for i, r in enumerate(rows)
    ]
    for j in range(n):
        k = next(i for i in range(j, n) if work[i][j] % p)
        work[j], work[k] = work[k], work[j]
        u = pow(work[j][j], -1, p)
        work[j] = [x * u % p for x in work[j]]
        for i in range(n):
            if i == j or not work[i][j]:
                continue
            v = work[i][j]
            work[i] = [(x - v * y) % p for x, y in zip(work[i], work[j])]
    return [r[n:] for r in work]


def matmul(a, b, p):
    return [[sum(x * y for x, y in zip(row, col)) % p for col in zip(*b)] for row in a]


def matvec(a, b, p):
    return [sum(x * y for x, y in zip(row, b)) % p for row in a]


def embedding(rows, target, tau):
    basis = [r + [0] for r in rows] + [list(target) + [tau]]
    for r in Matrix(basis).lll(delta=Rational(3, 4)).tolist():
        if abs(r[-1]) == tau:
            yield [int(x) * int(r[-1] // tau) for x in r[:-1]]


def lwe_error_band(path):
    txt = path.read_text(encoding="utf-8").split("'''")[1]
    A, b, p, cc = named(txt, ("A", "b", "p", "CC"))
    m, n = len(A), len(A[0])
    inv = invert(A[:n], p)
    H = matmul(A, inv, p)
    rows = list(map(list, zip(*H))) + [
        [p * int(i == j) for j in range(m)] for i in range(n, m)
    ]
    target = [(v - 5950) % p for v in b]
    for err in embedding(rows, target, 50):
        if max(map(abs, err)) > 50:
            continue
        head = [(v - e) % p for v, e in zip(target[:n], err)]
        secret = matvec(inv, head, p)
        errors = [(v - t) % p for v, t in zip(b, matvec(A, secret, p))]
        assert all(5900 <= x <= 6000 for x in errors)
        plain = flag_int(cc ^ prod(secret[:10]))
        assert format_ok(plain)
        return {
            "observations": m,
            "unknowns": n,
            "dimension": m + 1,
            "errors_in_range": True,
            "flag_format": True,
        }
    raise ValueError("未得到误差区间内的候选")


def groebner_composite(path):
    pub = literal_eval(source(path, "keyTask.chall"))
    p = pub["p"]
    rhs = pub["c"]
    M = [pub["M"][i : i + 16] for i in range(0, 512, 16)]
    A = list(map(list, zip(*M)))
    inv = invert([r[:16] for r in A], p)
    rel = matmul(inv, [r[16:] for r in A], p)
    head = matvec(inv, rhs, p)
    basis = [[p * int(i == j) for j in range(32)] for i in range(16)]
    basis += [
        [(-r[k]) % p for r in rel] + [int(k == j) for j in range(16)] for k in range(16)
    ]
    center = 128
    target = [(v - center) % p for v in head + [0] * 16]
    key = None
    for d in embedding(basis, target, 128):
        candidate = [v + center for v in d]
        if all(0 <= v < 256 for v in candidate) and matvec(A, candidate, p) == rhs:
            key = bytes(candidate)
            break
    assert key is not None
    p, total, *powers = literal_eval(source(path, "groebnerTask.chall"))
    x = symbols("x")
    candidates = []
    for c in powers:
        opts = set()
        for e in (2, 3, 5):
            if gcd(e, p - 1) == 1:
                vals = [pow(c, pow(e, -1, p - 1), p)]
            else:
                _, fs = Poly(x**e - c, x, modulus=p).factor_list()
                vals = [
                    int((-f.nth(0) * pow(int(f.nth(1)), -1, p)) % p)
                    for f, _ in fs
                    if f.degree() == 1
                ]
            opts.update(v for v in vals if v < 1 << 256 and pow(v, e, p) == c)
        candidates.append(sorted(opts))
    accepted = []
    for zs in product(*candidates):
        if sum(zs) != total:
            continue
        data = [bytes(a ^ b for a, b in zip(z.to_bytes(32, "big"), key)) for z in zs]
        for length in (12, 24):
            if not all(v == bytes(v[i % length] for i in range(32)) for v in data):
                continue
            try:
                plain = unpad(b"".join(v[:length] for v in data), 36)
            except ValueError:
                continue
            if format_ok(plain):
                accepted.append((plain, length))
    assert len(set(accepted)) == 1
    return {
        "key_equations_verified": len(rhs),
        "roots_per_block": [len(v) for v in candidates],
        "sum_verified": True,
        "flag_format": True,
        "slice_bytes": accepted[0][1],
    }


def rabin_eight(path):
    c, n, pq = named(source(path, "task.py").split("'''")[1], ("C", "n", "hint"))
    r, remainder = divmod(n, pq)
    assert not remainder and r % 4 == 3 and isprime(r)
    roots = {c % r}
    for _ in range(3):
        candidates = set()
        for v in roots:
            t = pow(v, (r + 1) // 4, r)
            candidates.update(x for x in (t, (-t) % r) if x * x % r == v)
        roots = candidates
    matched = [
        flag_int(m) for m in roots if pow(m, 8, n) == c and format_ok(flag_int(m))
    ]
    assert len(matched) == 1
    return {"模根候选": len(roots), "通过完整模数回验的明文长度": len(matched[0])}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "case",
        choices=[
            "rsa-middle-bits",
            "lwe-error-band",
            "groebner-composite",
            "rabin-eight",
        ],
    )
    parser.add_argument("file", type=Path, help="赛题原附件")
    args = parser.parse_args()
    print(
        json.dumps(
            globals()[args.case.replace("-", "_")](args.file), ensure_ascii=False
        )
    )
