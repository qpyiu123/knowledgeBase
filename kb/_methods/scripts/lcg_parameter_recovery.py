#!/usr/bin/env python3
"""LCG 求解器：已知若干连续输出，还原 modulus/multiplier/increment/seed。

依赖：纯标准库（可选 sympy 做符号演示，本脚本不需要）。
用途：随机数题里 `s = (a*s + c) % m` 最常见。拿到连续 6+ 个输出就能
      反推参数；只有部分参数未知时用"方程求解"模式。

核心恒等式（输出 x_i）：
  d_i = x_{i+1} - x_i
  t_i = d_{i+2}*d_i - d_{i+1}^2      ≡ 0 (mod m)
  => m = gcd(t_0, t_1, ...)
  a = (x_2 - x_1) * (x_1 - x_0)^{-1} mod m
  c = x_1 - a*x_0 mod m

用法：
  python lcg_parameter_recovery.py --outputs 1,2,3,...        # 逗号或空格分隔
  python lcg_parameter_recovery.py --outputs-file outs.txt   # 每行一个
  python lcg_parameter_recovery.py --outputs ... --predict 5  # 再预测后续 5 个
  python lcg_parameter_recovery.py --selftest
"""
from __future__ import annotations

import argparse
import json
import math
import sys


def recover_modulus(xs: list[int]) -> int:
    """由连续输出求 modulus：gcd 所有 t_i。至少需要 6 个输出。"""
    if len(xs) < 6:
        raise ValueError(f"求 modulus 至少需要 6 个连续输出，只给了 {len(xs)} 个")
    ds = [xs[i + 1] - xs[i] for i in range(len(xs) - 1)]
    ts = []
    for i in range(len(ds) - 2):
        t = ds[i + 2] * ds[i] - ds[i + 1] * ds[i + 1]
        if t:
            ts.append(abs(t))
    if not ts:
        raise ValueError("所有 t_i 为 0（输出可能全相同），无法求解 modulus")
    m = 0
    for t in ts:
        m = math.gcd(m, t)
    if m <= 1:
        raise ValueError("gcd 结果为 1，输入不是同一 LCG 的连续输出或数据有误")
    return m


def recover_a_c(xs: list[int], m: int) -> tuple[int, int]:
    """已知 m，求 a、c。"""
    if (xs[1] - xs[0]) % m == 0:
        raise ValueError("x1 - x0 ≡ 0 mod m，无法取逆")
    a = (xs[2] - xs[1]) * pow((xs[1] - xs[0]) % m, -1, m) % m
    c = (xs[1] - a * xs[0]) % m
    c %= m
    return a % m, c % m


def recover_modulus_with_c_zero(xs: list[int]) -> int:
    """c = 0（纯乘法 LCG）时：x_{i+1}/x_i 恒等，m = gcd(x1^2-x0*x2, ...)。"""
    if len(xs) < 3:
        raise ValueError("c=0 求 modulus 至少需要 3 个输出")
    m = 0
    for i in range(len(xs) - 2):
        v = xs[i + 1] * xs[i + 1] - xs[i] * xs[i + 2]
        m = math.gcd(m, abs(v))
    if m <= 1:
        raise ValueError("c=0 模式下 gcd 结果为 1，参数不符或有噪声")
    return m


def recover_all(xs: list[int]) -> dict:
    m = recover_modulus(xs)
    a, c = recover_a_c(xs, m)
    # 验证：全部已知输出都要能被这组参数复现
    ok = all((a * xs[i] + c) % m == xs[i + 1] for i in range(len(xs) - 1))
    return {"modulus": m, "multiplier": a, "increment": c, "seed": xs[0],
            "verified": ok, "used": len(xs)}


def predict(state: int, a: int, c: int, m: int, k: int) -> list[int]:
    out = []
    for _ in range(k):
        state = (a * state + c) % m
        out.append(state)
    return out


def unshift_right_xor(y: int, shift: int, bits: int) -> int:
    """反解 x ^ (x >> shift) = y（bits 为整数位宽）。MT19937 同款技巧。"""
    x = 0
    for i in range(bits - 1, -1, -1):
        bit = (y >> i) & 1
        if i + shift < bits:
            bit ^= (x >> (i + shift)) & 1
        x |= bit << i
    return x


def selftest() -> int:
    fails = []
    m = (1 << 31) - 1  # 经典 glibc 风格 modulus
    a, c, seed = 1103515245, 12345, 20261102

    # ---- 算例 1：完整参数还原 ------------------------------------------------
    st = seed
    xs = []
    for _ in range(10):
        st = (a * st + c) % m
        xs.append(st)
    res = recover_all(xs)
    if res["modulus"] != m:
        fails.append(f"case1: modulus 还原错误 {res['modulus']} != {m}")
    if res["multiplier"] != a % m:
        fails.append(f"case1: a 还原错误 {res['multiplier']} != {a % m}")
    if res["increment"] != c:
        fails.append(f"case1: c 还原错误 {res['increment']} != {c}")
    if res["seed"] != xs[0]:
        fails.append("case1: seed 应为第一个输出")
    if not res["verified"]:
        fails.append("case1: 参数未能复现全部输出")

    # ---- 算例 2：预测后续输出与实际一致 -------------------------------------
    nxt = predict(xs[-1], res["multiplier"], res["increment"], res["modulus"], 3)
    stt = xs[-1]
    real = []
    for _ in range(3):
        stt = (a * stt + c) % m
        real.append(stt)
    if nxt != real:
        fails.append(f"case2: 预测 {nxt} 与实际 {real} 不符")

    # ---- 算例 3：c = 0 纯乘法模式 -------------------------------------------
    a2, m2 = 48271, (1 << 31) - 1
    st2, xs2 = 123456789, []
    for _ in range(8):
        st2 = (a2 * st2) % m2
        xs2.append(st2)
    m2r = recover_modulus_with_c_zero(xs2)
    if m2r != m2:
        fails.append(f"case3: c=0 模式 modulus 还原错误 {m2r} != {m2}")
    a2r = (xs2[1] * pow(xs2[0], -1, m2r)) % m2r
    if a2r != a2:
        fails.append(f"case3: c=0 模式 a 还原错误 {a2r} != {a2}")

    # ---- 算例 4：输出不足应报错而不是给出错误结果 ---------------------------
    try:
        recover_modulus(xs[:4])
        fails.append("case4: 只有 4 个输出却未报错")
    except ValueError:
        pass

    # ---- 算例 5：位数恢复 x ^ (x>>k) ----------------------------------------
    x = 0b1101_0110_1010_0101
    for shift in (1, 3, 7):
        y = x ^ (x >> shift)
        if unshift_right_xor(y, shift, 16) != x:
            fails.append(f"case5: unshift_right_xor shift={shift} 失败")

    for f in fails:
        print(f"FAIL {f}", file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 5/5（参数还原、预测、c=0、输出不足、xorshift 反解）")
    return 0


def parse_outputs(values: list[str], path: str | None) -> list[int]:
    out: list[int] = []
    for v in values:
        out += [int(t, 0) for t in v.replace(",", " ").split()]
    if path:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for ln in fh:
                ln = ln.strip()
                if ln and not ln.startswith("#"):
                    out += [int(t, 0) for t in ln.replace(",", " ").split()]
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="LCG 参数还原与预测")
    ap.add_argument("--outputs", action="append", default=[],
                    help="连续输出，逗号或空格分隔，可重复")
    ap.add_argument("--outputs-file", help="每行若干输出的文件")
    ap.add_argument("--predict", type=int, default=0, help="再预测 N 个后续输出")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    xs = parse_outputs(args.outputs, args.outputs_file)
    if len(xs) < 6:
        ap.error(f"至少需要 6 个连续输出（当前 {len(xs)} 个），或用 --selftest")
    try:
        res = recover_all(xs)
    except ValueError as exc:
        print(f"失败：{exc}", file=sys.stderr)
        return 2
    if args.predict:
        res["next"] = predict(xs[-1], res["multiplier"], res["increment"],
                              res["modulus"], args.predict)
    if args.json:
        print(json.dumps({k: (str(v) if isinstance(v, int) and v > 2**53 else v)
                          for k, v in res.items()}, ensure_ascii=False, indent=2))
    else:
        print(f"modulus    = {res['modulus']}")
        print(f"multiplier = {res['multiplier']}")
        print(f"increment  = {res['increment']}")
        print(f"seed(x0)   = {res['seed']}")
        print(f"自洽校验   = {'通过' if res['verified'] else '失败（检查是否连续输出）'}")
        if args.predict:
            print(f"后续 {args.predict} 个 = {res['next']}")
    return 0 if res["verified"] else 2


if __name__ == "__main__":
    sys.exit(main())
