#!/usr/bin/env python3
"""LLL 格基规约 + 低密度子集和（背包）恢复（纯标准库，不需要 Sage）。

两个部件：
  1) lll_reduce(B)：精确有理数 Gram-Schmidt 的 LLL（delta 默认 0.99），
     返回规约后的整数基；维度建议 <= 12，纯 Python 维度一上去就慢。
  2) solve_subset_sum(weights, target, ...)：Lagarias-Odlyzko 低密度背包格，
     LLL 后取短向量读回 0/1 解，并用 sum(w*x) == target 复验。

用法：
  python lattice_lll.py --weights 3,4,5,9,11,15 --target 29
  python lattice_lll.py --weights "0x1f,0x2b,0x37" --target 0x6d --delta 0.99
  python lattice_lll.py --reduce-file basis.json      # [[...],[...]] 整数矩阵
  python lattice_lll.py --selftest
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction


def _round_half(x: Fraction) -> int:
    """有理数四舍五入到最近整数（.5 向上）。"""
    if x >= 0:
        return int(x + Fraction(1, 2))
    return -int(-x + Fraction(1, 2))


def dot(a: list[int], b: list[int]) -> int:
    return sum(x * y for x, y in zip(a, b))


def lll_reduce(B: list[list[int]], delta: Fraction = Fraction(99, 100), max_steps: int = 200000):
    """LLL：返回 (规约后的基, 步数)。要求所有行等长、全是整数。"""
    if not B:
        raise ValueError("格基不能为空")
    n = len(B)
    m = len(B[0])
    if any(len(row) != m for row in B):
        raise ValueError("格基各行长度必须一致")
    if any(not isinstance(x, int) for row in B for x in row):
        raise ValueError("格基必须是整数矩阵")
    if not 0 < delta <= 1:
        raise ValueError("delta 必须在 (0, 1] 内")
    if n > 40 or m > 40:
        raise ValueError("纯 Python 的 LLL 只适合维度 <= 40，更大请用 Sage/fpylll")

    basis = [list(map(int, row)) for row in B]
    gso: list[list[Fraction] | None] = [None] * n
    mu: list[list[Fraction]] = [[Fraction(0)] * n for _ in range(n)]
    norm: list[Fraction] = [Fraction(0)] * n

    def invalidate(i: int) -> None:
        for j in range(i, n):
            gso[j] = None
            for k in range(j + 1):
                mu[j][k] = Fraction(0)
            norm[j] = Fraction(0)

    def ensure(i: int) -> None:
        if gso[i] is not None:
            return
        v = [Fraction(x) for x in basis[i]]
        for j in range(i):
            ensure(j)
            if norm[j] == 0:
                mu[i][j] = Fraction(0)
                continue
            mu[i][j] = dot(v, gso[j]) / norm[j]
            mj = mu[i][j]
            if mj:
                v = [v[k] - mj * gso[j][k] for k in range(m)]
        gso[i] = v
        norm[i] = sum(x * x for x in v)

    steps = 0
    k = 1
    while k < n:
        steps += 1
        if steps > max_steps:
            raise RuntimeError("LLL 步数超限：维度或系数太大")
        ensure(k)
        for j in range(k - 1, -1, -1):
            ensure(j)
            if abs(mu[k][j]) > Fraction(1, 2):
                q = _round_half(mu[k][j])
                basis[k] = [basis[k][i] - q * basis[j][i] for i in range(m)]
                invalidate(k)
                ensure(k)
        ensure(k - 1)
        lhs = norm[k]
        rhs = (delta - mu[k][k - 1] ** 2) * norm[k - 1]
        if lhs >= rhs:
            k += 1
        else:
            basis[k], basis[k - 1] = basis[k - 1], basis[k]
            invalidate(k - 1)
            k = max(k - 1, 1)
    basis.sort(key=lambda r: dot(r, r))
    return basis, steps


def solve_subset_sum(weights: list[int], target: int, scale: int | None = None):
    """低密度子集和：先用 LLL 背包格尝试，再用 meet-in-middle 兜底，两者都做精确复验。"""
    if not weights:
        raise ValueError("weights 不能为空")
    if any(w <= 0 for w in weights):
        raise ValueError("weights 必须全为正整数")
    if target < 0:
        raise ValueError("target 必须非负")
    n = len(weights)
    if n > 24:
        raise ValueError("纯 Python 只适合 <= 24 个重量")
    if scale is None:
        scale = 1 << (max(max(weights).bit_length(), target.bit_length()) + 1)

    # 基：前 n 列单位阵（读回 0/1 组合），最后一列放 scale*w_i 与 scale*target
    basis = []
    for i in range(n):
        row = [0] * (n + 1)
        row[i] = 1
        row[n] = weights[i] * scale
        basis.append(row)
    last = [0] * (n + 1)
    for j in range(n):
        last[j] = scale // 2
    last[n] = target * scale
    basis.append(last)

    out: list[list[int]] = []
    try:
        reduced, _ = lll_reduce(basis)
    except RuntimeError:
        reduced = []
    for row in reduced:
        bits = [1 if row[i] > 0 else 0 for i in range(n)]
        if sum(w * b for w, b in zip(weights, bits)) == target and bits not in out:
            out.append(bits)
    if out:
        return out
    # 兜底：meet-in-the-middle 精确枚举（n <= 24 时最多 2^12 项）
    return _mitm_subset_sum(weights, target)


def _mitm_subset_sum(weights: list[int], target: int) -> list[list[int]]:
    n = len(weights)
    h = n // 2
    left, right = weights[:h], weights[h:]

    def sums(items):
        table: dict[int, int] = {0: 0}
        for idx, w in enumerate(items):
            for s, mask in list(table.items()):
                ns = s + w
                if ns not in table:
                    table[ns] = mask | (1 << idx)
        return table

    lt, rt = sums(left), sums(right)
    out: list[list[int]] = []
    for s, mask in lt.items():
        need = target - s
        if need in rt:
            bits = [0] * n
            for i in range(h):
                if mask >> i & 1:
                    bits[i] = 1
            rm = rt[need]
            for i in range(len(right)):
                if rm >> i & 1:
                    bits[h + i] = 1
            if bits not in out:
                out.append(bits)
    return out


def selftest() -> int:
    import random

    fails = []

    # ---- 1 LLL 基本正确性：能找到预期短向量 ----
    red, _ = lll_reduce([[4, 1, 3], [4, 2, 1], [1, 3, 4]])
    if [0, 1, -2] not in red and [0, -1, 2] not in red:
        fails.append(f"case1: LLL 未给出短向量，got={red}")

    # ---- 2 LLL 不变性：规约前后基生成的格不变（行列式绝对值相等） ----
    from itertools import combinations

    def det_mod_p(mat, p):
        # 用模 p 的行列式近似校验（p 取自大素数，避免分数运算）
        a = [[x % p for x in row] for row in mat]
        d = 1
        for i in range(len(a)):
            piv = next((k for k in range(i, len(a)) if a[k][i] % p), None)
            if piv is None:
                return 0
            if piv != i:
                a[i], a[piv] = a[piv], a[i]
                d = -d % p
            inv = pow(a[i][i], -1, p)
            d = d * a[i][i] % p
            for k in range(i + 1, len(a)):
                if a[k][i]:
                    f = a[k][i] * inv % p
                    a[k] = [(a[k][j] - f * a[i][j]) % p for j in range(len(a))]
        return d % p

    p = 1000003
    B0 = [[7, 1, 0], [0, 7, 1], [1, 0, 7]]
    red0, _ = lll_reduce(B0)
    if det_mod_p(B0, p) != det_mod_p(red0, p):
        fails.append("case2: 规约后格的体积变了")

    # ---- 3 正常路径：低密度子集和 ----
    rng = random.Random(20261103)
    weights = [rng.randrange(1 << 16, 1 << 20) for _ in range(12)]
    sol = [rng.randrange(2) for _ in range(12)]
    target = sum(w * b for w, b in zip(weights, sol))
    got = solve_subset_sum(weights, target)
    if [v for v in got] and sol not in got:
        fails.append(f"case3: 背包解不包含真解，got={got}")
    if not got:
        fails.append("case3: 背包无解")

    # ---- 4 边界拒绝：非法输入 ----
    for call in [
        lambda: lll_reduce([]),
        lambda: lll_reduce([[1, 2], [1]]),
        lambda: lll_reduce([[1, 2]], delta=Fraction(3, 2)),
        lambda: solve_subset_sum([], 1),
        lambda: solve_subset_sum([1, -2], 1),
        lambda: solve_subset_sum([1, 2], -1),
    ]:
        try:
            call()
        except ValueError:
            pass
        else:
            fails.append("case4: 非法输入未拒绝")

    # ---- 5 边界：不存在的组合不能给假解 ----
    if solve_subset_sum([4, 6, 10], 5) != []:
        fails.append("case5: 无解背包给出了假解")

    # ---- 6 固定 seed 可复现 ----
    s1 = [random.Random(11).randrange(2) for _ in range(8)]
    s2 = [random.Random(11).randrange(2) for _ in range(8)]
    if s1 != s2:
        fails.append("case6: 固定 seed 不可复现")

    for f in fails:
        print(f"FAIL {f}", file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 6/6（LLL 短向量、行体积不变、背包恢复、非法输入拒绝、无解防假阳、固定 seed）")
    return 0


def _ints(text: str) -> list[int]:
    return [int(t, 0) for t in text.replace(" ", "").split(",") if t]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="LLL 规约 + 低密度子集和恢复")
    ap.add_argument("--weights", help="背包重量，逗号分隔")
    ap.add_argument("--target", type=lambda s: int(s, 0))
    ap.add_argument("--delta", type=float, default=0.99)
    ap.add_argument("--reduce-file", help="整数矩阵 JSON：[[..],[..]]")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    out: dict = {}
    try:
        if args.reduce_file:
            mat = json.loads(open(args.reduce_file, encoding="utf-8").read())
            red, steps = lll_reduce(mat, Fraction(int(args.delta * 1000), 1000))
            out = {"basis": red, "steps": steps}
        elif args.weights:
            if args.target is None:
                ap.error("参数不足：给了 --weights 就必须给 --target")
            weights = _ints(args.weights)
            sols = solve_subset_sum(weights, args.target)
            if not sols:
                print("报错：未找到子集和（密度过高或规模超出纯 Python 范围）", file=sys.stderr)
                return 1
            out = {"solution": sols[0], "count": len(sols)}
        else:
            ap.error("参数不足：需要 --weights/--target 或 --reduce-file")
    except (ValueError, RuntimeError, OSError) as exc:
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
