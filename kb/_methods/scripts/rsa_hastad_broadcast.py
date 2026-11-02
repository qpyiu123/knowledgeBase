#!/usr/bin/env python3
"""Håstad 低指数广播攻击：同一明文、同一小 e、多个模数。

依赖：纯标准库（--selftest 用 PyCryptodome 造密钥）。
用途：题面给了 e（通常是 3 或 5）和 e 组 (n_i, c_i)，明文相同。
      CRT 把 c_i 合成为 C = m^e mod (prod n_i)，而 m^e < prod n_i，
      于是 C 就是精确的 m^e，对它开 e 次整数根即得 m。

支持"固定 padding 后缀/前缀"：若加密的是 m||suffix（线性关系），
用 CRT 合成后开根得到 (m||suffix) 再剥掉已知字节。

用法：
  python rsa_hastad_broadcast.py --e 3 --pair N1:C1 --pair N2:C2 --pair N3:C3
  python rsa_hastad_broadcast.py --e 3 --pairs pairs.txt   # 每行 N:C 或 N,C
  python rsa_hastad_broadcast.py --selftest
"""
from __future__ import annotations

import argparse
import json
import math
import sys


def parse_pair(text: str) -> tuple[int, int]:
    for sep in (":", ",", " "):
        if sep in text:
            a, b = text.split(sep, 1)
            return int(a.strip(), 0), int(b.strip(), 0)
    raise ValueError(f"无法解析密钥对: {text!r}（需要 N:C）")


def crt_generalized(residues: list[int], moduli: list[int]) -> tuple[int, int]:
    """广义 CRT，不要求模数互素。返回 (x, lcm)，无解时抛 ValueError。"""
    x, m = 0, 1
    for r, n in zip(residues, moduli):
        g = math.gcd(m, n)
        if (r - x) % g != 0:
            raise ValueError("CRT 无解：模数之间存在冲突")
        # 解 (x + m*t) ≡ r (mod n)
        m_g, n_g = m // g, n // g
        t = ((r - x) // g * pow(m_g, -1, n_g)) % n_g
        x += m * t
        m *= n_g
        x %= m
    return x, m


def integer_nth_root(value: int, k: int) -> int | None:
    """精确 k 次根：value 是完全 k 次幂时返回根，否则 None。"""
    if value < 0:
        return None
    if value in (0, 1):
        return value
    # 初值用比特长度估，再牛顿迭代
    hi = 1 << ((value.bit_length() + k - 1) // k + 1)
    lo = 0
    while lo < hi:
        mid = (lo + hi) // 2
        if mid**k < value:
            lo = mid + 1
        else:
            hi = mid
    return lo if lo**k == value else None


def hastad(e: int, pairs: list[tuple[int, int]]) -> dict:
    """返回 {'ok': bool, 'm_int', 'm_bytes', 'exact', 'note'}。"""
    if len(pairs) < e:
        return {"ok": False, "note": f"至少需要 {e} 组 (n,c)，实际只有 {len(pairs)} 组"}
    ns = [n for n, _ in pairs]
    cs = [c for _, c in pairs]
    try:
        x, mod = crt_generalized(cs, ns)
    except ValueError as exc:
        return {"ok": False, "note": str(exc)}
    root = integer_nth_root(x, e)
    if root is None:
        return {"ok": False, "m_int": x, "note": "CRT 合成结果不是完全 e 次幂（可能有 padding 或模数不足）"}
    return {"ok": True, "exact": True, "m_int": root, "m_bytes": long_to_bytes(root),
            "modulus_bits": mod.bit_length()}


def long_to_bytes(v: int) -> bytes:
    return v.to_bytes((v.bit_length() + 7) // 8, "big") or b"\x00"


def bytes_to_long(b: bytes) -> int:
    return int.from_bytes(b, "big")


def selftest() -> int:
    from Crypto.Util.number import getPrime

    fails = []
    e = 3
    m = bytes_to_long(b"flag{hastad_selftest}")

    # ---- 算例 1：标准广播，3 组模数，无 padding ----
    pairs = []
    for _ in range(3):
        n = getPrime(128) * getPrime(128)
        pairs.append((n, pow(m, e, n)))
    res = hastad(e, pairs)
    if not res["ok"] or res["m_int"] != m:
        fails.append("case1: 标准广播未还原明文")
    if res["m_bytes"] != b"flag{hastad_selftest}":
        fails.append("case1: 字节串不一致")

    # ---- 算例 2：固定后缀 padding，m||suffix ----------------------------------
    suffix = b"\x00\x01\x02\x03"
    m_pad = (m << (8 * len(suffix))) | bytes_to_long(suffix)
    pairs2 = []
    for _ in range(3):
        n = getPrime(160) * getPrime(160)
        pairs2.append((n, pow(m_pad, e, n)))
    res2 = hastad(e, pairs2)
    if not res2["ok"]:
        fails.append("case2: 带固定后缀的广播未还原")
    else:
        raw = res2["m_bytes"]
        if not raw.endswith(suffix):
            fails.append("case2: 还原结果未以预期后缀结尾")
        if bytes_to_long(raw[: -len(suffix)]) != m:
            fails.append("case2: 剥掉后缀后与原文不符")

    # ---- 算例 3：组数不足必须明确失败（不谎报）----
    res3 = hastad(e, pairs[:2])
    if res3["ok"]:
        fails.append("case3: 只有 2 组却报告成功")
    if "至少需要" not in res3.get("note", ""):
        fails.append("case3: 缺少组数不足的提示")

    # ---- 算例 4：整数开方边界 ----
    for v, k, exp in [(27, 3, 3), (28, 3, None), (1, 5, 1), (0, 3, 0), (1024, 10, 2)]:
        got = integer_nth_root(v, k)
        if got != exp:
            fails.append(f"case4: integer_nth_root({v},{k}) = {got}, 期望 {exp}")

    # ---- 算例 5：不互素模数的广义 CRT 不崩（解 x=9 满足 x≡1 mod 4、x≡3 mod 6）----
    x, mod = crt_generalized([1, 3], [4, 6])
    if mod != 12 or x % 4 != 1 or x % 6 != 3:
        fails.append(f"case5: 广义 CRT 结果错误 x={x} mod={mod}")
    if x != 9:
        fails.append(f"case5: 期望最小非负解 9，实际 {x}")

    for f in fails:
        print(f"FAIL {f}", file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 5/5（标准广播、固定后缀、组数不足、开根边界、广义 CRT）")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Håstad 低指数广播攻击")
    ap.add_argument("--e", type=lambda s: int(s, 0), default=3, help="公钥指数，默认 3")
    ap.add_argument("--pair", action="append", default=[], help="N:C，可重复")
    ap.add_argument("--pairs", help="文件，每行一个 N:C")
    ap.add_argument("--strip-suffix-hex", help="可选：剥掉已知的后缀（十六进制）")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    raw_pairs = list(args.pair)
    if args.pairs:
        with open(args.pairs, encoding="utf-8", errors="replace") as fh:
            raw_pairs += [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
    if not raw_pairs:
        ap.error("需要至少一个 --pair 或 --pairs 文件，或用 --selftest")
    pairs = [parse_pair(p) for p in raw_pairs]

    res = hastad(args.e, pairs)
    if res.get("ok") and args.strip_suffix_hex:
        suffix = bytes.fromhex(args.strip_suffix_hex)
        data = res["m_bytes"]
        if data.endswith(suffix):
            res["m_bytes_stripped"] = data[: -len(suffix)]
            res["m_int"] = bytes_to_long(res["m_bytes_stripped"])
        else:
            res["strip_note"] = "还原结果不以给定后缀结尾，未剥离"

    if args.json:
        out = dict(res)
        if isinstance(out.get("m_bytes"), (bytes, bytearray)):
            out["m_bytes"] = bytes(out["m_bytes"]).decode("latin-1")
        if isinstance(out.get("m_bytes_stripped"), (bytes, bytearray)):
            out["m_bytes_stripped"] = bytes(out["m_bytes_stripped"]).decode("latin-1")
        out["m_int"] = str(out.get("m_int", ""))
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        if res.get("ok"):
            print(f"还原成功（{len(pairs)} 组，e={args.e}）")
            print(f"m = {res.get('m_bytes_stripped', res['m_bytes'])!r}")
        else:
            print(f"失败：{res.get('note')}", file=sys.stderr)
    return 0 if res.get("ok") else 2


if __name__ == "__main__":
    sys.exit(main())
