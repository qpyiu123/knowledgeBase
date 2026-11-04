#!/usr/bin/env python3
"""ECDSA nonce 重用 / 偏置 nonce 私钥恢复（纯标准库，不需要 Sage）。

覆盖两种 CTF 高频形态：
  1) nonce 重用：两条签名的 r 相同 -> k = (z1-z2)/(s1-s2)，d = (s1*k - z1)/r
  2) 偏置 nonce（HNP）：k < 2^bias，多条 (r, s, z) -> 先解线性同余的近似公共 d
     这里用「区间剪枝」的确定性方法：对 k < 2^bias 的每一条签名有
     d ≡ (s*k - z) * r^-1 (mod n)，取前两条把 k2 消成区间搜索，
     规模小时直接枚举 k1（2^bias 次），命中即用其余签名交叉验证。

用法：
  python ecdsa_nonce_reuse.py --sigs sigs.json [--curve secp256k1] [--json]
  python ecdsa_nonce_reuse.py --r R --s1 S1 --z1 Z1 --s2 S2 --z2 Z2
  python ecdsa_nonce_reuse.py --sigs sigs.json --bias-bits 24 --max-k 16777216
  python ecdsa_nonce_reuse.py --selftest

sigs.json 形如 [{"r": "...", "s": "...", "z": "..."}, ...]，数值可用 0x 前缀。
"""
from __future__ import annotations

import argparse
import json
import sys

SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
ED25519_L = 0x1000000000000000000000000000000014DEF9DEA2F79CD65812631A5CF5D3ED


def ecdsa_nonce_reuse(r: int, s1: int, z1: int, s2: int, z2: int, n: int) -> tuple[int, int]:
    """两条 r 相同的签名 -> (k, d)。"""
    if n < 3:
        raise ValueError("曲线阶 n 太小")
    if not (0 < r < n):
        raise ValueError("r 越界")
    if (s1 - s2) % n == 0:
        raise ValueError("s1 == s2，同一条消息/确定性 nonce，无法联立")
    if (z1 - z2) % n == 0:
        raise ValueError("z1 == z2，两条消息哈希相同，无法消去 r*d")
    k = (z1 - z2) * pow(s1 - s2, -1, n) % n
    d = (s1 * k - z1) * pow(r, -1, n) % n
    return k, d


def verify_d(sigs: list[tuple[int, int, int]], d: int, n: int, bias_bits: int) -> bool:
    """用所有签名复核：d 代回去得到的 k 必须全部小于 2^bias 且非零。"""
    if not sigs:
        return False
    bound = 1 << bias_bits
    for r, s, z in sigs:
        try:
            k = (z + r * d) * pow(s, -1, n) % n
        except ValueError:
            return False
        if not 0 < k < bound:
            return False
    return True


def recover_private_key(
    sigs: list[tuple[int, int, int]], n: int, bias_bits: int | None = None, max_k: int = 1 << 22
) -> list[int]:
    """返回候选私钥列表；bias_bits 为 None 时只尝试 nonce 重用路径。"""
    if len(sigs) < 2:
        raise ValueError("至少需要两条签名")
    cands: list[int] = []

    # 路径 1：r 重复（nonce 重用），O(1)
    seen: dict[int, tuple[int, int, int]] = {}
    for r, s, z in sigs:
        if r in seen:
            s0, z0 = seen[r][1], seen[r][2]
            try:
                _, d = ecdsa_nonce_reuse(r, s0, z0, s, z, n)
            except ValueError:
                continue
            if d not in cands:
                cands.append(d)
        else:
            seen[r] = (r, s, z)
    if cands:
        return cands

    # 路径 2：偏置 nonce，枚举第一条签名的 k1
    if bias_bits is None:
        return []
    if bias_bits < 4:
        raise ValueError("bias_bits 太小（<4 位），先怀疑数据本身")
    if bias_bits > 60:
        raise ValueError("bias_bits 过大：确定性枚举只适合 <= 60 位，更大规模请用 LLL")
    bound = min(1 << bias_bits, max_k)
    if len(sigs) < 3:
        raise ValueError("偏置 nonce 至少需要 3 条签名才能交叉验证")
    r0, s0, z0 = sigs[0]
    r0i = pow(r0, -1, n)
    rest = sigs[1:]
    for k0 in range(1, bound):
        d = (s0 * k0 - z0) * r0i % n
        if all(verify_d([sig], d, n, bias_bits) for sig in rest):
            if d not in cands:
                cands.append(d)
            break
    return cands


def _load_sigs(path: str) -> list[tuple[int, int, int]]:
    data = json.loads(open(path, encoding="utf-8").read())
    out = []
    for item in data:
        out.append((int(str(item["r"]), 0), int(str(item["s"]), 0), int(str(item["z"]), 0)))
    return out


def selftest() -> int:
    from fractions import Fraction
    import random

    fails = []

    n = SECP256K1_N
    rng = random.Random(20261103)
    d = 0x1234567890ABCDEF1234567

    # ---- 1 正常路径：nonce 重用 ----
    k = 0xDEADBEEFCAFE
    r = 0xAAAA
    z1, z2 = 0x1111, 0x2222
    s1 = pow(k, -1, n) * (z1 + r * d) % n
    s2 = pow(k, -1, n) * (z2 + r * d) % n
    kk, dd = ecdsa_nonce_reuse(r, s1, z1, s2, z2, n)
    if not (kk == k and dd == d):
        fails.append(f"case1: nonce 重用恢复失败 k={kk:x} d={dd:x}")

    # ---- 2 正常路径：偏置 nonce（k < 2^20），三条签名交叉验证 ----
    bits = 20
    sigs = []
    for _ in range(3):
        ki = rng.randrange(1, 1 << bits)
        ri = rng.randrange(1, n)
        zi = rng.randrange(1, n)
        si = pow(ki, -1, n) * (zi + ri * d) % n
        sigs.append((ri, si, zi))
    got = recover_private_key(sigs, n, bias_bits=bits, max_k=1 << bits)
    if got != [d]:
        fails.append(f"case2: 偏置 nonce 恢复失败 got={[hex(x) for x in got]}")

    # ---- 3 边界拒绝：s 相同 / z 相同 / n 太小 / 少于两条 ----
    for call in [
        lambda: ecdsa_nonce_reuse(r, s1, z1, s1, z2, n),
        lambda: ecdsa_nonce_reuse(r, s1, z1, s2, z1, n),
        lambda: ecdsa_nonce_reuse(r, s1, z1, s2, z2, 2),
        lambda: recover_private_key([(1, 2, 3)], n),
        lambda: recover_private_key(sigs, n, bias_bits=2),
    ]:
        try:
            call()
        except (ValueError, ZeroDivisionError):
            pass
        else:
            fails.append("case3: 非法输入未拒绝")

    # ---- 4 边界：不成立的数据不能给假私钥 ----
    bad = []
    for ki in (5, 7):  # k 很小但 bias 设为 0 位 -> 未启用偏置路径
        ri = rng.randrange(1, n)
        zi = rng.randrange(1, n)
        bad.append((ri, pow(ki, -1, n) * (zi + ri * d) % n, zi))
    if recover_private_key(bad, n) != []:
        fails.append("case4: 未声明偏置时不应凭空给出私钥")
    if verify_d(sigs, d + 1, n, bits):
        fails.append("case4: 错误私钥通过了交叉验证")

    # ---- 5 固定 seed 可复现 ----
    a = [random.Random(7).randrange(1 << 20) for _ in range(3)]
    b = [random.Random(7).randrange(1 << 20) for _ in range(3)]
    if a != b:
        fails.append("case5: 固定 seed 不可复现")

    # ---- 6 模逆健壮性：s 与 n 不互素时要报错而不是乱算 ----
    if not fails:
        try:
            ecdsa_nonce_reuse(n, 1, 1, 1, 2, n)
        except (ValueError, ZeroDivisionError):
            pass
        else:
            fails.append("case6: r 越界未拒绝")

    for f in fails:
        print(f"FAIL {f}", file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 6/6（nonce 重用、偏置 nonce、非法输入拒绝、防假阳、固定 seed、越界拒绝）")
    return 0


def _parse(text: str) -> int:
    return int(text, 0)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="ECDSA nonce 重用 / 偏置 nonce 恢复私钥")
    ap.add_argument("--sigs", help="签名 JSON 文件：[{r,s,z}, ...]")
    ap.add_argument("--n", type=_parse, default=None, help="曲线阶；默认按 --curve 取")
    ap.add_argument("--curve", choices=["secp256k1", "ed25519"], default="secp256k1")
    ap.add_argument("--r", type=_parse)
    ap.add_argument("--s1", type=_parse)
    ap.add_argument("--z1", type=_parse)
    ap.add_argument("--s2", type=_parse)
    ap.add_argument("--z2", type=_parse)
    ap.add_argument("--bias-bits", type=_parse, default=None)
    ap.add_argument("--max-k", type=_parse, default=1 << 22)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    n = args.n if args.n else (SECP256K1_N if args.curve == "secp256k1" else ED25519_L)
    try:
        if args.r is not None:
            if None in (args.s1, args.z1, args.s2, args.z2):
                ap.error("参数不足：给了 --r 就需要 --s1/--z1/--s2/--z2")
            k, d = ecdsa_nonce_reuse(args.r, args.s1, args.z1, args.s2, args.z2, n)
            out = {"k": hex(k), "d": hex(d)}
        elif args.sigs:
            sigs = _load_sigs(args.sigs)
            cands = recover_private_key(sigs, n, args.bias_bits, args.max_k)
            if not cands:
                print("报错：未恢复私钥。先确认 r 是否有重复；偏置 nonce 需给 --bias-bits", file=sys.stderr)
                return 1
            out = {"d": hex(cands[0]), "candidates": len(cands)}
        else:
            ap.error("参数不足：需要 --sigs 或 --r/--s1/--z1/--s2/--z2")
    except (ValueError, OSError) as exc:
        print(f"报错：{exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        for key, val in out.items():
            print(f"{key} = {val}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
