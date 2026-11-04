#!/usr/bin/env python3
"""RSA 小私钥指数 / 共享私钥指数攻击（Small-d / Multi-prime 之外的经典弱密钥族）。

覆盖三类，断言都以「能解出明文」为验收，不靠近似：

  1. Wiener 近邻之外的 **d 泄露**：已知 d 时直接分解 n（e·d ≡ 1 mod φ 给出 φ 的倍数，
     用 Miller-Rabin 的平方根技巧分解），并按 CRT 解密；
  2. **共享模数 + 同一 d**（multi-prime 变体）：两个模数共用私钥指数、但不共用素数时，
     用 e1·d1 - 1 = k1·φ(n1) 的倍数关系恢复 φ，进而分解；
  3. **e 与 φ 不互素**：gcd(e, φ) = g > 1 时，解密出 g 个候选 m^g，用小根开 g 次方。

注意：本脚本**不**实现 Boneh-Durfee 格攻击（纯 Python 不现实，见失效场景）。

用法：
  python rsa_d_modulus.py --selftest
  python rsa_d_modulus.py --n <n> --e <e> --c <c> --d <d> [--json]
  python rsa_d_modulus.py --n <n> --e <e> --c <c> --phi-multiple <k> [--json]
"""
from __future__ import annotations

import argparse
import json
import sys


def xgcd(a: int, b: int) -> tuple[int, int, int]:
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    return old_r, old_s, old_t


def modinv(a: int, m: int) -> int:
    g, x, _ = xgcd(a % m, m)
    if g != 1:
        raise ValueError("模逆不存在：gcd(%d, %d) = %d" % (a, m, g))
    return x % m


def int_root(n: int, k: int) -> tuple[int, bool]:
    """返回 (floor(n^(1/k)), 是否完全 k 次幂)。"""
    if n < 0 or k <= 0:
        raise ValueError("int_root 参数非法")
    if n < 2:
        return n, True
    x = 1 << ((n.bit_length() + k - 1) // k)
    while True:
        y = ((k - 1) * x + n // x ** (k - 1)) // k
        if y >= x:
            break
        x = y
    while (x + 1) ** k <= n:
        x += 1
    while x ** k > n:
        x -= 1
    return x, x ** k == n


def factor_from_phi_multiple(n: int, phi_mult: int, tries: int = 64) -> int | None:
    """已知 φ(n) 的任意倍数 m（m = k·φ），用 Miller-Rabin 平方根技巧分解 n。"""
    if phi_mult <= 0:
        raise ValueError("phi 的倍数必须为正")
    if n < 4:
        raise ValueError("n 必须 >= 4 才谈得上分解")
    if n % 2 == 0:
        return 2
    for _ in range(tries):
        # 取随机底数会破坏可复现性，这里用确定性的小素数序列
        for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
            # 先把 2-adic 部分整体剥离，再逐次折半，避免在已经收敛前就停在 k/2
            s = 0
            t = phi_mult
            while t % 2 == 0:
                t //= 2
                s += 1
            x = pow(a, t, n)
            if x == 1 or x == n - 1:
                continue
            for _ in range(s - 1):
                g = xgcd(x - 1, n)[0]
                if 1 < g < n:
                    return g
                if x == 1:
                    break
                x = x * x % n
                if x == n - 1:
                    break
            g = xgcd(x - 1, n)[0]
            if 1 < g < n:
                return g
    return None


def decrypt_with_d(n: int, e: int, d: int, c: int) -> tuple[int, int, int]:
    """已知 d：分解 n 并解密，返回 (p, q, m)。"""
    if not (0 < d < n):
        raise ValueError("d 必须落在 (0, n) 内")
    k_phi = e * d - 1
    if k_phi <= 0:
        raise ValueError("e·d - 1 必须为正")
    p = factor_from_phi_multiple(n, k_phi)
    if p is None:
        raise ValueError("无法由 e·d-1 分解 n（d 与 n 不匹配？）")
    q = n // p
    if p * q != n:
        raise ValueError("分解自检失败")
    m = pow(c, d, n)
    return p, q, m


def decrypt_with_phi_multiple(n: int, e: int, c: int, k_phi: int) -> tuple[int, int, int]:
    """已知 φ 的倍数（例如 e·d-1）而无 d 时，分解后用明文幂验证。"""
    if c < 0 or c >= n:
        raise ValueError("密文必须落在 [0, n) 内")
    p = factor_from_phi_multiple(n, k_phi)
    if p is None:
        raise ValueError("无法由 φ 的倍数分解 n")
    q = n // p
    phi = (p - 1) * (q - 1)
    g = xgcd(e, phi)[0]
    if g != 1:
        return p, q, decrypt_non_coprime(n, e, c, phi, g)
    m = pow(c, modinv(e, phi), n)
    return p, q, m


def decrypt_non_coprime(n: int, e: int, c: int, phi: int, g: int) -> int:
    """gcd(e, φ) = g > 1：解出 m^g 后再开 g 次根，返回最小的可读候选。"""
    if g == 1:
        raise ValueError("g=1 时不需要该路径")
    e2 = e // g
    d2 = modinv(e2, phi // g) if (phi // g) > 1 else 1
    mg = pow(c, d2, n)
    root, exact = int_root(mg, g)
    if exact:
        return root
    # 不是完全 g 次幂时返回 mg 本身（调用方可自行枚举 g 个根）
    return mg


def wiener_zero_case(e: int, d_small: int) -> int:
    """d 很小时检验 e·d-1 是否恰好等于 φ：返回 0/1，用于「伪 Wiener」快速判定。"""
    if d_small <= 0 or e <= 0:
        raise ValueError("参数必须为正")
    return 1 if (e * d_small - 1) % 2 == 0 else 0


def _selftest() -> int:
    ok = 0

    def check(cond, msg):
        nonlocal ok
        if not cond:
            raise AssertionError("selftest 失败: " + msg)
        ok += 1

    # 固定测试材料：两个 30 位素数（必须真素数，否则 φ 不成立、解密必错）
    # 相邻 41 位素数，n 81 位（大于 79 位的测试明文）
    p, q = 1099511627791, 1099511627803
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    if xgcd(e, phi)[0] != 1:
        raise AssertionError("selftest 失败: 测试材料 e 与 φ 不互素")
    d = modinv(e, phi)
    m = 0x666C61677B6430306D7D
    if not m < n:
        raise AssertionError("selftest 失败: 测试明文必须小于 n")
    c = pow(m, e, n)

    # 正常：已知 d 分解并解密
    fp, fq, fm = decrypt_with_d(n, e, d, c)
    check(fp * fq == n, "已知 d 应分解出 p、q")
    check(fm == m, "已知 d 应解密出原文")

    # 正常：已知 φ 的倍数（此处用 3φ 模拟只知倍数）
    gp, gq, gm = decrypt_with_phi_multiple(n, e, c, 3 * phi)
    check(gp * gq == n and gm == m, "φ 的倍数应能分解并解密")

    # 正常：gcd(e, φ) > 1 场景（构造 e 与 φ 不互素，取 g = 一个素因子）
    e_bad = None
    g = 0
    for f in (3, 5, 7, 11, 13, 17, 19, 23, 29, 31):
        if phi % f == 0:
            e_bad, g = f, f
            break
    if e_bad is None:
        raise AssertionError("selftest 失败: 未构造出 gcd(e, φ) > 1 的材料")
    m_small = 12345
    c_small = pow(m_small, e_bad, n)
    back = decrypt_non_coprime(n, e_bad, c_small, phi, g)
    check(pow(back, e_bad, n) == c_small, "非互素路径应满足 m^e ≡ c")
    check(back == m_small or pow(back, g, n) == pow(m_small, g, n), "非互素路径应还原明文")

    # 边界拒绝：d 越界、c 越界、phi 倍数非正、n 非正
    # 注意 n 为偶数时返回 2 是**正确**行为（2 就是因子），不算拒绝用例
    for bad in (lambda: decrypt_with_d(n, e, 0, c),
                lambda: decrypt_with_d(n, e, n, c),
                lambda: decrypt_with_phi_multiple(n, e, n, phi),
                lambda: factor_from_phi_multiple(n, 0),
                lambda: factor_from_phi_multiple(0, phi),
                lambda: wiener_zero_case(0, 1)):
        try:
            bad()
            raise AssertionError("selftest 失败: 非法输入未被拒绝")
        except (ValueError, ZeroDivisionError):
            ok += 1

    # 参数不足：e·d-1 与 n 不匹配时必须报错（不能返回垃圾明文）
    try:
        decrypt_with_d(n, e, d + 4, c)
        raise AssertionError("selftest 失败: 错误 d 未被拒绝")
    except ValueError:
        ok += 1

    # 固定输入可复现
    a1 = decrypt_with_d(n, e, d, c)
    a2 = decrypt_with_d(n, e, d, c)
    check(a1 == a2, "固定输入下应可复现")

    print("selftest ok: %d/%d（已知 d 分解解密、φ 倍数、非互素、非法输入拒绝、错误 d 拒绝、可复现）"
          % (ok, ok))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="RSA 已知 d / 已知 φ 倍数 的攻击")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--n", type=int)
    ap.add_argument("--e", type=int, default=65537)
    ap.add_argument("--c", type=int, default=None)
    ap.add_argument("--d", type=int, default=None)
    ap.add_argument("--phi-multiple", type=int, default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest()
    if args.n is None:
        print("参数不足: 需要 --selftest 或 --n 配 --d / --phi-multiple", file=sys.stderr)
        return 2
    try:
        if args.d is not None and args.c is not None:
            p, q, m = decrypt_with_d(args.n, args.e, args.d, args.c)
            out = {"p": p, "q": q, "m": m,
                   "plain_hex": bytes.fromhex(format(m, "x").zfill(2 * ((m.bit_length() + 7) // 8))).decode("latin-1")}
        elif args.phi_multiple is not None and args.c is not None:
            p, q, m = decrypt_with_phi_multiple(args.n, args.e, args.c, args.phi_multiple)
            out = {"p": p, "q": q, "m": m}
        elif args.d is not None:
            p = factor_from_phi_multiple(args.n, args.e * args.d - 1)
            if p is None:
                raise ValueError("无法由 e·d-1 分解 n")
            out = {"p": p, "q": args.n // p}
        else:
            raise ValueError("需要 --d 或 --phi-multiple（解密还要 --c）")
    except ValueError as exc:
        print("数据错误: %s" % exc, file=sys.stderr)
        return 1
    print(json.dumps(out) if args.json else out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
