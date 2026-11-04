#!/usr/bin/env python3
"""xorshift 伪随机数恢复：已知移位参数预测/反推状态，未知参数时枚举移位。

xorshift 每步都是 GF(2) 上的线性（可逆）变换：
  x ^= x << a;  x ^= x >> b;  x ^= x << c   （32 位掩码）

所以：
  * 已知 (a,b,c) 时，最后一项之后的状态可直接预测，也可靠线性系统反推任意前序状态；
  * 未知 (a,b,c) 时，对 1..31 的三元组枚举，用连续输出自洽性筛出唯一参数；
  * 参数与输出都不全时，可把候选参数喂给后续的 untemper/序列分析。

用法：
  python xorshift_recovery.py --selftest
  python xorshift_recovery.py --shifts 13,17,5 --seed 2463534242 --count 8 --predict 4
  python xorshift_recovery.py --shifts 13,17,5 --outs 0x...,0x... --recover-seed
  python xorshift_recovery.py --outs 0x...,0x...,0x... --brute
"""
from __future__ import annotations

import argparse
import json
import sys

MASK32 = 0xFFFFFFFF


class XorShift32:
    """Marsaglia 32 位 xorshift。"""

    def __init__(self, seed: int, a: int = 13, b: int = 17, c: int = 5):
        for name, v in (("a", a), ("b", b), ("c", c)):
            if not isinstance(v, int) or not 1 <= v <= 31:
                raise ValueError("移位量 %s=%r 必须在 1..31 之间" % (name, v))
        self.a, self.b, self.c = a, b, c
        self.x = seed & MASK32

    def next(self) -> int:
        self.x = xorshift32_step(self.x, self.a, self.b, self.c)
        return self.x

    def state(self) -> int:
        return self.x


def xorshift32_step(x: int, a: int, b: int, c: int) -> int:
    x &= MASK32
    x ^= (x << a) & MASK32
    x ^= x >> b
    x ^= (x << c) & MASK32
    return x & MASK32


def xorshift32_unstep(y: int, a: int, b: int, c: int) -> int:
    """逆向一步：y = step(x) 时由 y 还原 x（每个左/右移是逐比特可逆的）。"""
    y &= MASK32
    # 先逆最后一步 x ^= x << c
    x = y
    shift = c
    while shift < 32:
        x ^= (y << shift) & MASK32
        shift += c
    y = x
    # 逆 x ^= x >> b
    x = y
    shift = b
    while shift < 32:
        x ^= y >> shift
        shift += b
    y = x
    # 逆 x ^= x << a
    x = y
    shift = a
    while shift < 32:
        x ^= (y << shift) & MASK32
        shift += a
    return x & MASK32


def predict(outs, a: int, b: int, c: int, n: int = 1) -> list[int]:
    """从已知连续输出预测接下来的 n 个值（无需种子）。"""
    if not outs:
        raise ValueError("至少需要一个已知输出")
    if n < 0:
        raise ValueError("预测步数不能为负")
    x = outs[-1] & MASK32
    res = []
    for _ in range(n):
        x = xorshift32_step(x, a, b, c)
        res.append(x)
    return res


def verify(outs, a: int, b: int, c: int) -> bool:
    """检查输出序列是否与参数 (a,b,c) 自洽。"""
    if len(outs) < 2:
        raise ValueError("至少两个输出才能验证")
    for i in range(len(outs) - 1):
        if xorshift32_step(outs[i], a, b, c) != (outs[i + 1] & MASK32):
            return False
    return True


def brute_shifts(outs, max_shift: int = 31):

    """枚举 (a,b,c)，返回所有自洽的候选。"""
    if len(outs) < 2:
        raise ValueError("暴力枚举至少需要 2 个连续输出")
    cands = []
    for a in range(1, max_shift + 1):
        for b in range(1, max_shift + 1):
            for c in range(1, max_shift + 1):
                if verify(outs, a, b, c):
                    cands.append((a, b, c))
    if not cands:
        raise ValueError("在 1..%d 的移位范围内找不到匹配参数" % max_shift)
    return cands


def recover_seed(outs, a: int, b: int, c: int) -> int:
    """由 outs[0] 逆推前一个状态；若 outs 从种子的第一次输出开始，这就是种子。"""
    if not outs:
        raise ValueError("至少需要一个输出")
    return xorshift32_unstep(outs[0] & MASK32, a, b, c)


def _selftest() -> int:
    ok = 0

    def check(cond, msg):
        nonlocal ok
        if not cond:
            raise AssertionError("selftest 失败: " + msg)
        ok += 1

    a, b, c = 13, 17, 5

    # 正常：固定 seed 序列稳定可复现
    rng = XorShift32(2463534242, a, b, c)
    outs = [rng.next() for _ in range(8)]
    rng_b = XorShift32(2463534242, a, b, c)
    check([rng_b.next() for _ in range(8)] == outs, "固定 seed 应可复现")
    check(len(set(outs)) == 8, "8 个连续输出不应重复")

    # 正常：自洽性 + 预测
    check(verify(outs, a, b, c), "已知参数下序列应自洽")
    want = [XorShift32(outs[-1], a, b, c).next()]
    check(predict(outs, a, b, c, 1) == want, "预测下一项应与真实迭代一致")
    check(len(set(predict(outs, a, b, c, 5))) == 5, "预测多项应逐项推进")

    # 正常：unstep 与 step 互逆
    check(xorshift32_unstep(outs[1], a, b, c) == outs[0], "unstep 应还原上一状态")

    # 正常：反推种子
    seed = 12345
    rng_s = XorShift32(seed, a, b, c)
    seq = [rng_s.next() for _ in range(6)]
    check(recover_seed(seq, a, b, c) == seed, "应从前序状态反推出种子 12345")

    # 正常：未知参数暴力恢复（用一个不常见的移位三元组，减低碰撞）
    a2, b2, c2 = 7, 9, 13
    rng2 = XorShift32(20260101, a2, b2, c2)
    seq2 = [rng2.next() for _ in range(5)]
    check(len(set(seq2)) == 5, "演示序列应逐项推进（不能每项都重建生成器）")
    cands = brute_shifts(seq2, max_shift=31)
    check((a2, b2, c2) in cands, "暴力枚举应包含真实参数 (7,9,13)")
    pred = predict(seq2, a2, b2, c2, 2)
    check(pred[0] == XorShift32(seq2[-1], a2, b2, c2).next(), "恢复参数后应能正确预测")

    # 边界拒绝：移位量越界 / 空输出 / 负步数
    for bad in (lambda: XorShift32(1, 0, 17, 5), lambda: XorShift32(1, 13, 32, 5),
                lambda: predict([], a, b, c, 1), lambda: predict([1], a, b, c, -1),
                lambda: verify([1], a, b, c), lambda: brute_shifts([1], 31)):
        try:
            bad()
            raise AssertionError("selftest 失败: 非法输入未被拒绝")
        except ValueError:
            ok += 1

    # 参数不足：两个互不相关的数应被判定不自洽
    check(verify([1, 2, 3, 4, 5, 6, 7, 8], a, b, c) is False, "非 xorshift 序列应判定为不自洽")

    print("selftest ok: %d/%d（可复现、自洽性、预测、unstep 互逆、反推种子、暴力恢复参数、非法输入拒绝）"
          % (ok, ok))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="xorshift 状态/参数恢复")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--shifts", default="13,17,5", help="a,b,c")
    ap.add_argument("--seed", type=int, default=None, help="用于生成演示序列")
    ap.add_argument("--count", type=int, default=8)
    ap.add_argument("--outs", default="", help="逗号分隔的已知连续输出")
    ap.add_argument("--predict", type=int, default=0)
    ap.add_argument("--brute", action="store_true")
    ap.add_argument("--recover-seed", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest()

    try:
        a, b, c = [int(v) for v in args.shifts.split(",")]
    except ValueError:
        print("参数错误: --shifts 形如 13,17,5", file=sys.stderr)
        return 2
    if args.outs:
        try:
            outs = [int(v, 0) for v in args.outs.split(",") if v.strip()]
        except ValueError:
            print("参数错误: --outs 必须是十进制或 0x 十六进制整数", file=sys.stderr)
            return 2
    elif args.seed is not None:
        rng = XorShift32(args.seed, a, b, c)
        outs = [rng.next() for _ in range(args.count)]
    else:
        print("参数不足: 需要 --selftest、--seed 或 --outs", file=sys.stderr)
        return 2

    try:
        out = {"params": [a, b, c], "outputs": outs[:16],
               "consistent": verify(outs, a, b, c) if len(outs) > 1 else None}
        if args.brute:
            out["shift_candidates"] = brute_shifts(outs, 31)
        if args.recover_seed:
            out["seed"] = recover_seed(outs, a, b, c)
        if args.predict:
            out["predicted"] = predict(outs, a, b, c, args.predict)
    except ValueError as exc:
        print("数据错误: %s" % exc, file=sys.stderr)
        return 1
    print(json.dumps(out, ensure_ascii=False) if args.json else out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
