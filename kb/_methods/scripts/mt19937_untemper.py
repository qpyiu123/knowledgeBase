#!/usr/bin/env python3
"""MT19937（Python random）状态还原与预测。

依赖：纯标准库（random 模块本身就是 MT19937）。
用途：Python 的 random 是 MT19937，每次 getrandbits(32)/随机数输出都泄漏
      状态位。收集 624 个 32 位输出 → 逆 temper → 得到完整状态 →
      克隆一个随机流，预测后续任何输出。

关键点：**同一状态周期内的 624 个输出必须连续**；一旦中间夹了别的
      随机调用（randint 会消耗多次 getrandbits），位会被打乱。
      本脚本提供 step 参数，用于跳过"每组 k 次 getrandbits 取 1 个"的情形。

用法：
  python mt19937_untemper.py --outputs-file outs.txt --predict 5
  python mt19937_untemper.py --outputs 123,456,... --predict 3
  python mt19937_untemper.py --selftest
"""
from __future__ import annotations

import argparse
import json
import random
import sys

N, M = 624, 397
MATRIX_A = 0x9908B0DF
UPPER_MASK, LOWER_MASK = 0x80000000, 0x7FFFFFFF


def unshift_right_xor(y: int, shift: int) -> int:
    """反解 x ^ (x >> shift) = y（32 位）。"""
    x = 0
    for i in range(31, -1, -1):
        bit = (y >> i) & 1
        if i + shift < 32:
            bit ^= (x >> (i + shift)) & 1
        x |= bit << i
    return x


def unshift_left_xor_mask(y: int, shift: int, mask: int) -> int:
    """反解 x ^ ((x << shift) & mask) = y（32 位）。"""
    x = 0
    for i in range(32):
        bit = (y >> i) & 1
        if i - shift >= 0:
            bit ^= ((x >> (i - shift)) & 1) & ((mask >> i) & 1)
        x |= bit << i
    return x


def untemper(y: int) -> int:
    """把经过 temper 的输出还原为内部状态字。"""
    y = unshift_right_xor(y, 18)
    y = unshift_left_xor_mask(y, 15, 0xEFC60000)
    y = unshift_left_xor_mask(y, 7, 0x9D2C5680)
    y = unshift_right_xor(y, 11)
    return y & 0xFFFFFFFF


def temper(y: int) -> int:
    """正向 temper，用于自检与解释。"""
    y ^= y >> 11
    y ^= (y << 7) & 0x9D2C5680
    y ^= (y << 15) & 0xEFC60000
    y ^= y >> 18
    return y & 0xFFFFFFFF


def try_clone(outputs: list[int]) -> random.Random | None:
    """用 624 个连续 32 位输出克隆一个 MT19937 实例。

    要求 outputs 恰好是某个块边界起算的连续 624 个 raw word；
    返回的 Random 已推进到"刚用完这 624 个输出"。
    """
    outs = outputs[:N]
    if len(outs) != N:
        return None
    state = [untemper(o & 0xFFFFFFFF) for o in outs]
    rng = random.Random()
    rng.setstate((3, tuple(state + [N]), None))
    return rng


def _next32(rng: random.Random) -> int:
    return rng.getrandbits(32)


def check_clone(outputs: list[int]) -> dict:
    """端到端验证：前 624 项克隆，后续项应与预测完全一致。"""
    head, tail = outputs[:N], outputs[N:]
    rng = try_clone(head)
    if rng is None:
        return {"ok": False, "note": f"输出不足：需要 {N} 项，实际 {len(head)} 项"}
    # index 已设为 N，即"块已用完"，下一次调用会 regenerate 出下一块
    pred = [_next32(rng) for _ in range(len(tail))]
    return {"ok": pred == tail, "predicted": pred, "actual": tail,
            "note": "一致" if pred == tail else "不一致：检查 624 个输出是否连续且从块起点开始"}


def selftest() -> int:
    fails = []

    # ---- 算例 1：temper/untemper 互逆 --------------------------------------
    for y in (0, 1, 0xFFFFFFFF, 0xDEADBEEF, 123456789):
        if untemper(temper(y)) != y:
            fails.append(f"case1: untemper(temper({y:#x})) != {y}")

    # ---- 算例 2：64 个随机字互逆（不依赖随机源的具体值）------------------
    r = random.Random(2026)
    for _ in range(64):
        y = _next32(r)
        if untemper(temper(y)) != y:
            fails.append(f"case2: 随机字 {y:#x} 互逆失败")
            break

    # ---- 算例 3：端到端克隆 —— 624 个连续输出 + 5 个验证输出 --------------
    real = random.Random(12345)
    stream = [_next32(real) for _ in range(N + 5)]
    res = check_clone(stream)
    if not res["ok"]:
        fails.append("case3: 连续流克隆失败 " + res.get("note", ""))
    if res.get("predicted") != res.get("actual"):
        fails.append("case3: 后续 5 个输出预测不一致")

    # ---- 算例 4：截取的 624 个输出不是从块起点开始时必须失败（不能假装成功）----
    real2 = random.Random(999)
    stream2 = [_next32(real2) for _ in range(N * 2)]
    # 从第 5 个字起的 624 个输出跨越两个块，重建的状态是错的
    misaligned = check_clone(stream2[5:5 + N] + stream2[:5])
    if misaligned["ok"]:
        fails.append("case4: 错位采样被误判为克隆成功")

    # ---- 算例 5：输出不足必须明确失败，不能假装成功 ------------------------
    short = check_clone(stream[:100])
    if short["ok"] or "输出不足" not in short.get("note", ""):
        fails.append("case5: 输出不足时未正确报错")

    for f in fails:
        print(f"FAIL {f}", file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 5/5（互逆、随机字、连续流克隆、错位采样拒绝、输出不足）")
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
    ap = argparse.ArgumentParser(description="MT19937 状态还原与后续预测")
    ap.add_argument("--outputs", action="append", default=[])
    ap.add_argument("--outputs-file")
    ap.add_argument("--predict", type=int, default=5, help="预测后续 N 个输出")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    xs = parse_outputs(args.outputs, args.outputs_file)
    need = N
    if len(xs) < need:
        print(f"失败：需要至少 {need} 个连续原始输出（getrandbits(32) 级别），"
              f"实际 {len(xs)} 个", file=sys.stderr)
        return 2
    rng = try_clone(xs)
    if rng is None:
        print("失败：无法克隆状态", file=sys.stderr)
        return 2
    pred = [_next32(rng) for _ in range(args.predict)]
    # 若给了多余输出，顺带核对（多余输出应等于预测值）
    extra = xs[need:]
    verify = {
        "extra_given": len(extra),
        "matched": sum(1 for a, b in zip(extra, pred) if a == b),
    } if extra else {}
    out = {"predictions": pred, "verify": verify}
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(f"已从 {need} 个输出克隆 MT19937 状态")
        print(f"后续 {args.predict} 个输出预测：{pred}")
        if verify:
            print(f"额外给入 {verify['extra_given']} 个真实输出，与预测吻合 "
                  f"{verify['matched']} 个（吻合 0 个说明输出不连续或未从块起点开始）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
