#!/usr/bin/env python3
"""共享素数（多组 n 的 gcd ≥ 两个因子）：一次 gcd 批量爆破多份公钥。

依赖：PyCryptodome（仅 --selftest 造密钥）；核心只用标准库。
用途：题面给了一堆 RSA 公钥（n 列表）——只要其中任意两个 n 共享素数 p，
      两两 gcd 就能把 n 分解，进而算出 d、解出全部密文。

用法：
  python rsa_shared_prime.py --n-file ns.txt            # 每行一个十进制/0x 整数
  python rsa_shared_prime.py --n N1 --n N2 --n N3 ...   # 直接给多个
  python rsa_shared_prime.py --selftest

输出：哪些 n 被分解（给出行号与 p、q），以及每个 n 分解后的 phi / d。
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from itertools import combinations


def long_to_bytes(value: int) -> bytes:
    return value.to_bytes((value.bit_length() + 7) // 8, "big") or b"\x00"


def parse_int_line(line: str) -> int | None:
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    return int(line, 16) if line.lower().startswith("0x") else int(line, 10)


def pairwise_gcd(ns: list[int]) -> list[tuple[int, int, int]]:
    """返回 [(i, j, g)]：所有 gcd(n_i, n_j) > 1 的对（含相等 n 的情况单独说明）。"""
    hits = []
    for i, j in combinations(range(len(ns)), 2):
        g = math.gcd(ns[i], ns[j])
        if g > 1:
            # g == n 说明两个模数完全相同，不是"共享素数"，另作标记
            hits.append((i, j, g))
    return hits


def factor_via_shared(n: int, hits: list[tuple[int, int, int]], idx: int) -> int | None:
    for i, j, g in hits:
        if i == idx and g != n:
            return g
        if j == idx and g != n:
            return g
    return None


def recover_d(e: int, p: int, q: int) -> int:
    return pow(e, -1, (p - 1) * (q - 1))


def selftest() -> int:
    from Crypto.Util.number import getPrime

    fails = []
    # ---- 算例：用同一组素数造 3 个 n，其中第 2、3 个共享 p ----
    p_shared, q1, q2, q3 = getPrime(128), getPrime(128), getPrime(128), getPrime(128)
    n1, n2, n3 = p_shared * q1, p_shared * q2, p_shared * q3
    ns = [n1, n2, n3]
    if math.gcd(n1, n2) == 1:
        fails.append("setup: 构造的 n 未共享素数")
    hits = pairwise_gcd(ns)
    pairs = {(i, j) for i, j, g in hits}
    expect = {(0, 1), (0, 2), (1, 2)}
    if pairs != expect:
        fails.append(f"gcd 对不完整: {sorted(pairs)} != {sorted(expect)}")
    if {g for _, _, g in hits} != {p_shared}:
        fails.append("gcd 结果不等于共享素数 p")

    # ---- 分解后能解密 ----
    e = 65537
    for k in range(3):
        p = factor_via_shared(ns[k], hits, k)
        if p != p_shared:
            fails.append(f"第 {k} 个 n 未分解出 p")
            continue
        q = ns[k] // p
        if p * q != ns[k]:
            fails.append(f"第 {k} 个 n 的 p*q != n")
        d = recover_d(e, p, q)
        if pow(pow(12345, e, ns[k]), d, ns[k]) != 12345:
            fails.append(f"第 {k} 个 n 解密往返失败")

    # ---- 不同素数应判为不共享 ----
    r1, r2 = getPrime(64), getPrime(64)
    if pairwise_gcd([r1 * r2, getPrime(64) * getPrime(64)]):
        fails.append("无关 n 被误判为共享素数")

    # ---- 行解析 ----
    if parse_int_line("0x1f") != 31 or parse_int_line("31") != 31:
        fails.append("parse_int_line 十六进制/十进制解析错误")
    if parse_int_line("# comment") is not None:
        fails.append("parse_int_line 未跳过注释")

    for f in fails:
        print(f"FAIL {f}", file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 5/5（3 组共享素数、分解解密、无关 n 不误报、行解析）")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="多份 RSA 公钥的共享素数爆破")
    ap.add_argument("--n", action="append", type=lambda s: int(s, 0), default=[],
                    help="模数，可重复给多次")
    ap.add_argument("--n-file", help="每行一个模数（十进制或 0x），# 开头为注释")
    ap.add_argument("--e", type=lambda s: int(s, 0), default=65537, help="公钥指数，默认 65537")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    ns = list(args.n)
    if args.n_file:
        lines = open(args.n_file, encoding="utf-8", errors="replace").read().splitlines()
        ns += [v for v in (parse_int_line(x) for x in lines) if v is not None]
    if len(ns) < 2:
        ap.error("至少需要两个 n（--n 或 --n-file），或用 --selftest")

    hits = pairwise_gcd(ns)
    rows = []
    for k, n in enumerate(ns):
        p = factor_via_shared(n, hits, k)
        if p is None:
            rows.append({"index": k, "n": str(n), "factored": False})
            continue
        q = n // p
        rows.append({
            "index": k, "n": str(n), "factored": True,
            "p": str(p), "q": str(q),
            "d": str(recover_d(args.e, p, q)),
            "phi": str((p - 1) * (q - 1)),
        })
    out = {"shared_pairs": [[i, j, str(g)] for i, j, g in hits],
           "same_n_pairs": [[i, j] for i, j, g in hits if g == ns[i]],
           "results": rows}
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        same = out["same_n_pairs"]
        if same:
            print(f"注意：以下下标是完全相同的 n（不是共享素数）：{same}")
        print(f"共享素数对：{[ (i,j) for i,j,_ in hits ]}")
        for r in rows:
            if r["factored"]:
                print(f"[{r['index']}] 已分解 p={r['p'][:24]}… q={r['q'][:24]}…")
            else:
                print(f"[{r['index']}] 未分解（无共享素数）")
        print("d 值见 --json 输出；p、q 可直接喂给 RSA 解密脚本")
    return 0 if any(r["factored"] for r in rows) else 2


if __name__ == "__main__":
    sys.exit(main())
