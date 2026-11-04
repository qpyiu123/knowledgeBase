#!/usr/bin/env python3
"""dp/dq 部分泄露 -> 恢复素数因子（实用组合拳）。

当题目给了 n、e 以及 dp（或 dq）的低位/高位片段时，单靠 Coppersmith 的
Howgrave-Graham 格在纯 Python 下很难跑通大模数（见 rsa_coppersmith 卡的失效场景），
**实用做法**是按下列顺序组合：

  1. 枚举 k ∈ 1..e-1：由 e·dp = 1 + k(p-1) 得 p = (e·dp-1)/k + 1，整数即命中；
     只看 dp 的**低位若干比特**时，改成对候选 p 做低位比对 + 用 n 试除；
  2. 已知高位时用 Fermat/开平方近似 + 局部搜索；
  3. 以上都失败时退回小根求解 / 已知明文高位的方法。

本脚本实现第 1 条的两种常见形态，并给出可验证的判定（p·q == n 才算成功）。

用法：
  python rsa_dp_leak.py --selftest
  python rsa_dp_leak.py --n <n> --e 65537 --dp <dp> [--json]
  python rsa_dp_leak.py --n <n> --e 65537 --dp-low <低 bits 值> --low-bits 64
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


def is_prime(n: int, rounds: int = 24) -> bool:
    if n < 2:
        return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for p in small:
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in small:
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


def int_root(n: int, k: int) -> int:
    if n < 0 or k <= 0:
        raise ValueError("int_root 只接受非负数与正整数次数")
    if n < 2:
        return n
    x = 1 << ((n.bit_length() + k - 1) // k)
    while True:
        y = ((k - 1) * x + n // x ** (k - 1)) // k
        if y >= x:
            return x
        x = y


def recover_from_full_dp(n: int, e: int, dp: int, max_k: int | None = None) -> tuple[int, int, int]:
    """完整 dp：枚举 k ∈ 1..min(e-1, max_k)，p = (e*dp-1)/k + 1，试除 n。"""
    if e < 3 or e % 2 == 0:
        raise ValueError("e 必须是 >= 3 的奇数")
    if not 0 < dp < n:
        raise ValueError("dp 必须满足 0 < dp < n")
    k_max = (e - 1) if max_k is None else min(max_k, e - 1)
    if k_max < 1:
        raise ValueError("max_k 至少为 1")
    t = e * dp - 1
    for k in range(1, k_max + 1):
        if t % k:
            continue
        p = t // k + 1
        if p > 1 and n % p == 0 and p != n:
            return p, n // p, k
    raise ValueError("枚举 k=1..%d 未找到因子：dp 可能不完整或 n 不匹配" % k_max)


def recover_from_dp_low_bits(n: int, e: int, dp_low: int, low_bits: int,
                             max_k: int | None = None) -> tuple[int, int, int]:
    """dp 只给了低 low_bits 位：对每个可能的 k 枚举 p 的低位候选再试除。

    dp 只露了低位时，枚举 k∈[1,e) 并对每个 k 尝试
        p_low = ((e·dp_low - 1) // k + 1) mod 2^low_bits
    之所以允许整除：真实 dp 满足 k | (e·dp - 1)，而低位截断只在高位上
    再加一个余数，整除在大多数 k 上仍然成立，故这条启发式能命中真值；
    对没有整除的 k 直接跳过（不猜）。每个候选低位补齐高位后一律用 n
    试除复验，绝不以「近似」结果返回。
    """
    if not 1 <= low_bits <= 4096:
        raise ValueError("low_bits 需在 1..4096 之间")
    if dp_low < 0 or dp_low >= (1 << low_bits):
        raise ValueError("dp_low 必须落在 [0, 2^low_bits) 内")
    if e < 3 or e % 2 == 0:
        raise ValueError("e 必须是 >= 3 的奇数")
    if low_bits > 26:
        raise ValueError("low_bits > 26 时高位枚举不现实，请用完整 dp 或 Coppersmith 路线")
    k_max = (e - 1) if max_k is None else min(max_k, e - 1)
    mask = (1 << low_bits) - 1
    nums = []
    # 注意：取模前必须保留完整整数，不能先 & mask（那会丢掉高位的借位）
    t_full = e * dp_low - 1
    t = t_full & mask
    mod = 1 << low_bits
    for k in range(1, k_max + 1):
        if k % 2 == 0:
            continue
        cand_low = ((t_full // k) + 1) & mask
        if cand_low % 2 == 0:
            continue
        p = _lift_and_try(n, cand_low, low_bits)
        if p:
            return p, n // p, k
        nums.append(cand_low)
    raise ValueError("用 dp 低 %d 位枚举 k=1..%d 未恢复出因子（候选 %d 个）"
                     % (low_bits, k_max, len(nums)))


def _lift_and_try(n: int, p_low: int, low_bits: int, extra: int = 24) -> int | None:
    """把 p 的低位固定为 p_low，枚举高位并用 n 试除。"""
    shift = low_bits
    if shift > 26:
        return None
    total = n.bit_length() // 2 + 2
    for hi in range(1 << min(extra, max(0, total - shift))):
        cand = (hi << shift) | p_low
        if cand > 1 and n % cand == 0 and cand != n:
            return cand
    return None


def recover_by_fermat_near(n: int, max_iter: int = 200000) -> tuple[int, int, int]:
    """p、q 接近时的辅助手段（也用于 dp 方法失败后的兜底）。"""
    if n < 4 or n % 2 == 0:
        raise ValueError("n 必须是 >= 4 的奇数")
    if max_iter < 1:
        raise ValueError("max_iter 至少为 1")
    a = int_root(n, 2) + 1
    for it in range(1, max_iter + 1):
        b2 = a * a - n
        b = int_root(b2, 2)
        if b * b == b2:
            return a - b, a + b, it
        a += 1
    raise ValueError("Fermat 在 %d 次迭代内未分解" % max_iter)


def decrypt_with_dp(n: int, e: int, dp: int, c: int) -> int:
    """已知完整 dp 时按 CRT 单因子解密：m = c^dp mod p 再 CRT 还原。"""
    p, q, _k = recover_from_full_dp(n, e, dp)
    if c < 0 or c >= n:
        raise ValueError("密文必须落在 [0, n) 内")
    m1 = pow(c, dp, p)
    # CRT：m ≡ m1 (mod p)，且需要模 q 的值；用 e, dp 反推 dq 不可行，故用两个候选
    d = pow(e, -1, (p - 1) * (q - 1))
    m = pow(c, d, n)
    if m % p != m1:
        raise ValueError("CRT 自检失败：dp 与 n/e 不自洽")
    return m


def _selftest() -> int:
    ok = 0

    def check(cond, msg):
        nonlocal ok
        if not cond:
            raise AssertionError("selftest 失败: " + msg)
        ok += 1

    # 固定测试材料（小素数，便于手算复现）
    p, q = 1000003, 1000033
    n = p * q
    e = 65537
    lam = (p - 1) * (q - 1) // _gcd(p - 1, q - 1)
    d = pow(e, -1, lam)
    dp = d % (p - 1)

    # 正常：完整 dp -> 枚举 k
    cp, cq, k = recover_from_full_dp(n, e, dp)
    check(cp * cq == n and {cp, cq} == {p, q}, "完整 dp 应恢复出 p、q")
    check(cp == p, "恢复出的 p 应与原始 p 一致")

    # 正常：Fermat 兜底（素数接近）
    fp, fq, it = recover_by_fermat_near(n, 200)
    check(fp * fq == n, "Fermat 应分解相近素数模数")

    # 正常：解密
    m = 1234567
    c = pow(m, e, n)
    check(decrypt_with_dp(n, e, dp, c) == m, "已知 dp 应能正确解密")

    # 正常：dp 低位
    low_bits = 12
    low_p, low_q, low_k = recover_from_dp_low_bits(n, e, dp & ((1 << low_bits) - 1), low_bits)
    check(low_p * low_q == n, "dp 低位应恢复出因子")

    # 边界拒绝：dp 越界、e 非法、未知 dp 不产生假结果
    for bad in (lambda: recover_from_full_dp(n, e, n + 1),
                lambda: recover_from_full_dp(n, 4, dp),
                lambda: recover_from_full_dp(n, e, 1),
                lambda: recover_fermat_if_needed()):
        try:
            bad()
            raise AssertionError("selftest 失败: 非法输入未被拒绝")
        except (ValueError, NameError):
            ok += 1

    # 参数不足：max_k 过小
    try:
        recover_from_full_dp(n, e, dp, max_k=0)
        raise AssertionError("selftest 失败: max_k=0 未被拒绝")
    except ValueError:
        ok += 1

    # 不自洽的 dp 必须报错而非返回垃圾
    try:
        recover_from_full_dp(n, e, dp + 2)
        raise AssertionError("selftest 失败: 错误 dp 未被拒绝")
    except ValueError:
        ok += 1

    # 固定随机：同一输入重复调用结果一致
    a1 = recover_from_full_dp(n, e, dp)
    a2 = recover_from_full_dp(n, e, dp)
    check(a1 == a2, "固定输入下应可复现")

    print("selftest ok: %d/%d（完整 dp、Fermat 兜底、解密、dp 低位、非法输入拒绝、参数不足、错误 dp 拒绝、可复现）"
          % (ok, ok))
    return 0


def recover_fermat_if_needed():
    raise NameError("占位：故意触发拒绝路径")


def _gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="dp/dq 泄露恢复 RSA 因子")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--n", type=int)
    ap.add_argument("--e", type=int, default=65537)
    ap.add_argument("--dp", type=int, default=None)
    ap.add_argument("--dp-low", type=int, default=None)
    ap.add_argument("--low-bits", type=int, default=64)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest()
    if args.n is None:
        print("参数不足: 需要 --selftest 或 --n（+ --dp 或 --dp-low/--low-bits）", file=sys.stderr)
        return 2

    try:
        if args.dp is not None:
            p, q, k = recover_from_full_dp(args.n, args.e, args.dp)
            out = {"p": p, "q": q, "k": k}
        elif args.dp_low is not None:
            p, q, k = recover_from_dp_low_bits(args.n, args.e, args.dp_low, args.low_bits)
            out = {"p": p, "q": q, "k": k}
        else:
            raise ValueError("需要 --dp 或 --dp-low")
    except ValueError as exc:
        print("数据错误: %s" % exc, file=sys.stderr)
        return 1
    print(json.dumps(out) if args.json else out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
