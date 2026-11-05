#!/usr/bin/env python3
"""RSA 小公钥指数攻击：m^e < n 直接开 e 次整数根，否则枚举 k 解 c + k*n。

依赖：纯标准库（--selftest 用 sympy 生成小素数，仓库 .venv 已装）。
用途：题面 e = 3（或 5、17）且明文很短、没有填充时，单个 (n, e, c) 即可还原明文。

用法：
  python rsa_small_e.py --n N --e 3 --c C [--max-k 1048576] [--prefix auto] [--json]
  python rsa_small_e.py --selftest

输出：命中的 k 与明文字节；多个候选（分段明文变体）按可打印程度排序后全部列出。
"""
from __future__ import annotations

import argparse
import json
import sys

PRINTABLE = set(range(0x20, 0x7F)) | {0x09, 0x0A, 0x0D}


def iroot(x: int, e: int) -> tuple[int, bool]:
    """整数 e 次根（牛顿迭代），返回 (root, 是否精确)。x < 0 或 e < 1 时抛 ValueError。"""
    if x < 0:
        raise ValueError("iroot 不接受负数")
    if e < 1:
        raise ValueError("根次数必须是正整数")
    if x < 2:
        return x, True
    if e == 1:
        return x, True
    r = 1 << ((x.bit_length() + e - 1) // e)  # 上界初值 2^ceil(bits/e)
    while True:
        nr = ((e - 1) * r + x // r ** (e - 1)) // e
        if nr >= r:
            break
        r = nr
    while r ** e > x:
        r -= 1
    while (r + 1) ** e <= x:
        r += 1
    return r, r ** e == x


def long_to_bytes(v: int) -> bytes:
    if v < 0:
        raise ValueError("负数无法转 bytes")
    return v.to_bytes((v.bit_length() + 7) // 8, "big") or b"\x00"


def printable_ratio(b: bytes) -> float:
    return sum(1 for x in b if x in PRINTABLE) / max(1, len(b))


def small_e_attack(n: int, e: int, c: int, max_k: int = 1 << 20) -> list[tuple[int, bytes]]:
    """返回 [(k, m_bytes)]；k=0 表示没有发生模约减。找不到返回空列表。"""
    if n <= 0 or e < 2 or not 0 <= c < n or max_k < 0:
        raise ValueError("参数需要 n>0、e>=2、0<=c<n、max_k>=0")
    out: list[tuple[int, bytes]] = []
    for k in range(max_k + 1):
        r, ok = iroot(c + k * n, e)
        if ok and r < n:
            out.append((k, long_to_bytes(r)))
    return out


def split_plaintext(n: int, e: int, c: int, prefix: bytes, max_k: int = 1 << 16):
    """已知明文以 prefix 开头（m = m1*m2 形式）时，从开出的整数里剥出 prefix。"""
    m1 = int.from_bytes(prefix, "big")
    if m1 == 0:
        raise ValueError("prefix 不能是全零")
    for k in range(max_k + 1):
        r, ok = iroot(c + k * n, e)
        if ok and r % m1 == 0:
            return k, prefix + long_to_bytes(r // m1)
    return None


def selftest() -> int:
    from sympy import nextprime

    fails = []

    # ---- 1 正常路径：e=3，m^3 < n，直接开根 ----
    # 先构造测试 n，再扩大到可覆盖这条固定明文的立方；这里只检查整数关系。
    n1 = int(nextprime(1 << 60)) * int(nextprime((1 << 60) + 12345))
    e1 = 3
    flag = b"flag{sm4ll_3xp0n3nt}"
    m1 = int.from_bytes(flag, "big")
    while m1 ** e1 >= n1:
        n1 *= 2
    c1 = pow(m1, e1, n1)
    hits = small_e_attack(n1, e1, c1, max_k=4)
    if not hits or hits[0][1] != flag:
        fails.append("case1: 小 e 直接开根失败")

    # ---- 2 枚举 k：m 略大于 n^(1/e)，需要 k>=1 ----
    n2 = n1
    m2 = int(nextprime(int(iroot(n2, 3)[0]) + 1000))  # 略大于 n^(1/3)
    c2 = pow(m2, 3, n2)
    hits2 = small_e_attack(n2, 3, c2, max_k=8)
    if not hits2 or hits2[0][1] != long_to_bytes(m2) or hits2[0][0] == 0:
        fails.append(f"case2: 枚举 k 失败 {hits2[:2]}")

    # ---- 3 边界拒绝：参数非法必须抛 ValueError ----
    for args in [(-1, 3, 5), (n1, 1, c1), (n1, 3, -5)]:
        try:
            small_e_attack(*args, max_k=1)
        except ValueError:
            pass
        else:
            fails.append(f"case3: 非法参数 {args} 未拒绝")
    try:
        iroot(-4, 3)
    except ValueError:
        pass
    else:
        fails.append("case3: iroot 负数未拒绝")

    # ---- 4 参数不足 / 找不到解时的行为（有界搜索返回空而不是瞎猜） ----
    c4 = pow(m2, 3, n2)  # 与 case2 相同的密文：最小精确根在 k>=1 处
    if small_e_attack(n2, 3, c4, max_k=0):
        fails.append("case4: max_k=0 且需要 k>0 时应返回空")
    if len(small_e_attack(n2, 3, c2, max_k=5000)) != 1:
        fails.append("case4: 枚举区间内应恰好一个精确根")

    # ---- 5 固定 seed 可复现 ----
    import random

    rnd = random.Random(20261103)
    n5 = int(nextprime(1 << 40)) * int(nextprime((1 << 40) + 777))
    gen = [rnd.randrange(1, 1 << 20) for _ in range(3)]
    rnd2 = random.Random(20261103)
    same = [rnd2.randrange(1, 1 << 20) for _ in range(3)]
    if gen != same:
        fails.append("case5: 固定 seed 序列不可复现")
    ok5 = all(small_e_attack(n5, 3, pow(v, 3, n5), max_k=0)[0][1] == long_to_bytes(v) for v in gen)
    if not ok5:
        fails.append("case5: 固定 seed 生成的明文还原失败")

    # ---- 6 iroot 边界 ----
    for v, e, exp in [(0, 3, (0, True)), (1, 5, (1, True)), (26, 3, (2, False)), (27, 3, (3, True))]:
        if iroot(v, e) != exp:
            fails.append(f"case6: iroot({v},{e})={iroot(v, e)} 期望 {exp}")

    for f in fails:
        print(f"FAIL {f}", file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 6/6（直接开根、枚举 k、边界拒绝、有界搜索、固定 seed、iroot 边界）")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="RSA 小公钥指数攻击（开 e 次根 + 枚举 k）")
    ap.add_argument("--n", type=lambda s: int(s, 0))
    ap.add_argument("--e", type=lambda s: int(s, 0), default=None)
    ap.add_argument("--c", type=lambda s: int(s, 0))
    ap.add_argument("--max-k", type=lambda s: int(s, 0), default=1 << 20, help="枚举 k 的上界，默认 2^20")
    ap.add_argument("--prefix", default=None, help="已知明文前缀（可写 flag{ 或 hex 串用 hex: ...）")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.n is None or args.e is None or args.c is None:
        ap.error("参数不足：需要 --n --e --c（或用 --selftest）")
    if args.e < 2:
        print("报错：--e 必须 >= 2（e=1 时 m 就是 c，不需要本脚本）", file=sys.stderr)
        return 2
    if args.n <= 0 or args.c < 0:
        print("报错：--n 必须为正、--c 必须非负", file=sys.stderr)
        return 2

    try:
        hits = small_e_attack(args.n, args.e, args.c, max_k=args.max_k)
    except ValueError as exc:
        print(f"报错：{exc}", file=sys.stderr)
        return 2

    if not hits:
        print(f"未找到精确 e 次根（已枚举 k <= {args.max_k}）："
              "m 可能带填充/高位未知，转 Coppersmith 或广播攻击", file=sys.stderr)
        return 1

    hits.sort(key=lambda kv: -printable_ratio(kv[1]))
    out = {
        "e": args.e,
        "candidates": [{"k": k, "m_hex": m.hex(), "m_ascii": m.decode("latin-1"),
                        "printable_ratio": round(printable_ratio(m), 3)} for k, m in hits],
    }
    if args.prefix:
        want = bytes.fromhex(args.prefix[4:]) if args.prefix.startswith("hex:") else args.prefix.encode()
        out["prefix_hits"] = [c["m_ascii"] for c in out["candidates"] if c["m_hex"].startswith(want.hex())]
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        for k, m in hits:
            print(f"k={k}  m={m!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
