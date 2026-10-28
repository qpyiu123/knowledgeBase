#!/usr/bin/env python
"""RSA 数论只读探针：小型试除、素性判断、位长与余因子。

用途：把题目给的 n / p / e 先做一遍确定性检查，判断是否存在小因子、
余因子是否像素数、位长是否异常。**只读**：不分解大数、不联网、不写文件。

输入：
  --n / --n-file     待检查的整数（十进制或 0x 十六进制）
  --limit            试除上界（默认 2,000,000）
  --check-prime N    额外判断一个数是否（概率）素数
  --json             输出 JSON

输出：bits、small_factors、cofactor_bits、cofactor_probable_prime 等。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared import add_json_flag, configure_stdio, emit, read_int_arg  # noqa: E402


def small_primes(limit: int) -> list[int]:
    limit = max(2, int(limit))
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(limit ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = b"\x00" * (((limit - i * i) // i) + 1)
    return [i for i in range(2, limit + 1) if sieve[i]]


def is_probable_prime(n: int) -> bool:
    """确定性 Miller-Rabin（<2^64），更大数用固定基底概率判定。"""
    if n < 2:
        return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for p in small:
        if n == p:
            return True
        if n % p == 0:
            return False
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    bases = (2, 325, 9375, 28178, 450775, 9780504, 1795265022) \
        if n < 2 ** 64 else (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for a in bases:
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def probe(n: int, limit: int) -> dict:
    if n <= 0:
        raise SystemExit("n 必须是正整数")
    factors: dict[str, int] = {}
    rest = n
    for p in small_primes(limit):
        if p * p > rest:
            break
        while rest % p == 0:
            factors[str(p)] = factors.get(str(p), 0) + 1
            rest //= p
    return {
        "read_only": True,
        "n_bits": n.bit_length(),
        "small_factor_limit": limit,
        "small_factors": factors,
        "cofactor": str(rest) if rest.bit_length() <= 4096 else "<too big to print>",
        "cofactor_bits": rest.bit_length(),
        "cofactor_probable_prime": is_probable_prime(rest),
        "fully_factored": rest == 1,
    }


def main(argv: list[str] | None = None) -> int:
    configure_stdio()
    ap = argparse.ArgumentParser(description="RSA 数论只读探针")
    ap.add_argument("--n", help="待检查整数")
    ap.add_argument("--n-file", help="从文件读取整数")
    ap.add_argument("--limit", type=int, default=2_000_000)
    ap.add_argument("--check-prime", help="额外判断一个数是否概率素数")
    add_json_flag(ap)
    args = ap.parse_args(argv)
    if not args.n and not args.n_file and not args.check_prime:
        ap.error("至少给出 --n / --n-file / --check-prime")
    out: dict = {}
    if args.n or args.n_file:
        out.update(probe(read_int_arg(args.n, args.n_file), args.limit))
    if args.check_prime:
        value = int(args.check_prime, 0)
        out["check_prime"] = {
            "value": str(value),
            "probable_prime": is_probable_prime(value),
            "bits": value.bit_length(),
        }
    emit(out, args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
