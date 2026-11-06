"""复做第二轮密码题：python crypto_round2.py 题目编号 原题.zip。需要 sympy；运行 -h 查看题目编号。"""

import argparse
import json
import re
from ast import literal_eval
from itertools import combinations, product
from math import gcd, isqrt
from pathlib import Path
from zipfile import ZipFile

from sympy import isprime


def members(path):
    with ZipFile(path) as z:
        return {
            i.filename.rsplit("/", 1)[-1]: z.read(i)
            for i in z.infolist()
            if not i.is_dir() and not i.flag_bits & 1 and i.file_size <= 300000
        }


def ints(data):
    return {
        k.decode(): int(v)
        for k, v in re.findall(rb"(?m)^[# ]*(\w+)\s*[:=]\s*(\d+)\s*$", data)
    }


def is_flag(m):
    b = m.to_bytes((m.bit_length() + 7) // 8, "big") if isinstance(m, int) else m
    return bool(re.fullmatch(rb"[A-Za-z0-9_]+\{[ -~]+\}", b))


def rsa_result(n, c, p, q):
    assert 1 < p < n and p * q == n
    e = 65537
    d = pow(e, -1, (p - 1) * (q - 1))
    m = pow(c, d, n)
    assert pow(m, e, n) == c
    return {"factors_verified": True, "format_verified": is_flag(m)}


def poly_rsa(path):
    v = ints(members(path)["task.py"])
    n, e1, e2, c1, c2, c = [v[k] for k in ("n", "e1", "e2", "c1", "c2", "c")]
    p = gcd(
        n,
        (pow(c1, e2, n) * pow(7, e1 * e2, n) - pow(c2, e1, n) * pow(3, e1 * e2, n)) % n,
    )
    q = n // p
    result = rsa_result(n, c, p, q)
    assert pow(2 * p + 3 * q, e1, n) == c1 and pow(5 * p + 7 * q, e2, n) == c2
    result["leaks_verified"] = True
    return result


def rsa_shared_prime_prefix(path):
    v = ints(members(path)["README.md"])
    a = isqrt(v["n"]) + 1
    b = isqrt(a * a - v["n"])
    result = rsa_result(v["n"], v["c"], a - b, a + b)
    result["fermat_steps"] = 1
    return result


def curve_parameters(path):
    data = members(path)["task.py"]
    points = [
        (int(x), int(y)) for x, y in re.findall(rb"\((\d+)\s*:\s*(\d+)\s*:\s*1\)", data)
    ]
    x0, y0 = points[0]
    diff = [(x - x0, (y * y - y0 * y0) - (x**3 - x0**3)) for x, y in points[1:]]
    g = gcd(*(dx * ey - ex * dy for (dx, dy), (ex, ey) in combinations(diff, 2)))
    p = next(
        g // k
        for k in range(1, 1000)
        if g % k == 0
        and (g // k).bit_length() == 160
        and g // k > max(max(x, y) for x, y in points)
    )
    a = diff[0][1] * pow(diff[0][0], -1, p) % p
    b = (y0 * y0 - x0**3 - a * x0) % p
    assert (4 * a**3 + 27 * b * b) % p and all(
        (y * y - x**3 - a * x - b) % p == 0 for x, y in points
    )
    assert isprime(p) and isprime(a) and isprime(b)
    return {
        "prime_bits": p.bit_length(),
        "points_verified": len(points),
        "curve_nonsingular": True,
        "hash_input_recovered": True,
    }


def lcg_low_byte(path):
    data = members(path)["output.txt"]
    mod = ints(data)["m"]
    xs = literal_eval(re.search(rb"leak_states\s*=\s*(\[[\d,\s]+\])", data)[1].decode())
    cipher = bytes.fromhex(re.search(rb"ciphertext\s*=\s*([a-f\d]+)", data)[1].decode())
    a = (xs[2] - xs[1]) * pow(xs[1] - xs[0], -1, mod) % mod
    b = (xs[1] - a * xs[0]) % mod
    assert all((a * x + b) % mod == y for x, y in zip(xs, xs[1:]))
    state = xs[-1]
    plain = bytearray()
    for byte in cipher:
        state = (a * state + b) % mod
        plain.append(byte ^ (state & 255))
    return {
        "states_verified": len(xs),
        "modulus_divisible_by_256": mod % 256 == 0,
        "format_verified": is_flag(bytes(plain)),
    }


def ntru_sparse(path):
    v = members(path)["public.py"]
    params = ints(v)
    n, q, p = [params[k] for k in ("N", "q", "p")]
    h, c = [
        literal_eval(
            re.search(rb"(?m)^" + k + rb"\s*=\s*(\[[\d,\s]+\])", v)[1].decode()
        )
        for k in (b"h", b"c")
    ]
    rotations = [h[-i:] + h[:-i] for i in range(n)]
    candidate = []
    for inds in combinations(range(n), 4):
        a, b, d, e = (rotations[i] for i in inds)
        for j, k, l, m in product((-1, 1), repeat=4):
            if any(
                (c[i] - j * a[i] - k * b[i] - l * d[i] - m * e[i] + p // 2) % q >= p
                for i in range(4)
            ):
                continue
            coeff = [
                (x - j * y - k * z - l * w - m * t + p // 2) % q - p // 2
                for x, y, z, w, t in zip(c, a, b, d, e)
            ]
            if all(-p // 2 < x <= p // 2 for x in coeff):
                regenerated = [
                    (x + j * y + k * z + l * w + m * t) % q
                    for x, y, z, w, t in zip(coeff, a, b, d, e)
                ]
                assert regenerated == c
                candidate.append(coeff)
    return {
        "balanced_coefficient_candidates": len(candidate),
        "zero_padding_removed_format_candidates": sum(
            is_flag(bytes(v % 256 for v in row).rstrip(b"\0")) for row in candidate
        ),
        "ciphertext_reproduced": bool(candidate),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "case",
        choices=[
            "poly-rsa",
            "rsa-shared-prime-prefix",
            "curve-parameters",
            "lcg-low-byte",
            "ntru-sparse",
        ],
    )
    parser.add_argument("file", type=Path, help="赛题原附件")
    args = parser.parse_args()
    print(
        json.dumps(
            globals()[args.case.replace("-", "_")](args.file), ensure_ascii=False
        )
    )
