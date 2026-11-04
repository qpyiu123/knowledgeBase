#!/usr/bin/env python3
"""RSA 奇偶/LSB oracle、PKCS#1 区间 oracle、Manger oracle 与同态绕过。

全部只依赖「oracle 返回布尔」这一黑盒，最终都用 pow(m, e, n) == c 复验，不产假绿：

  1. parity/LSB oracle：给 c 求明文的最低位。用乘法同态 c·2^e 让明文在模 n 下翻倍，
     记录每一轮是否绕过 n，再解出  m = ((cum + 1/2)·n - acc) / 2^i。
  2. PKCS#1 v1.5 区间 oracle（Bleichenbacher 首阶段）：oracle 只回答 m 是否落在 [2B, 3B)。
  3. Manger oracle（OAEP）：oracle 只回答 m < 2^k 是否成立。
  4. 同态绕过：oracle 拒绝解原 c 时，改解 c·r^e 再乘 r^{-1}。

用法：
  python rsa_padding_oracle.py --selftest
  python rsa_padding_oracle.py --demo parity|pkcs1|manger|homo
  python rsa_padding_oracle.py --n <n> --e <e> --c <c> --lsb 1 0 1 0 ...   # 已录好的 oracle 回答
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
        raise ValueError("模逆不存在：gcd(%d,%d)=%d" % (a, m, g))
    return x % m


def inv_d(p: int, q: int, e: int) -> int:
    """由 p、q、e 求解密指数 d（e 必须与 φ 互素，否则报错）。"""
    phi = (p - 1) * (q - 1)
    if xgcd(e, phi)[0] != 1:
        raise ValueError("e 与 φ 不互素，该 e 不能当解密指数")
    return modinv(e, phi)


def int_root(n: int, k: int) -> tuple[int, bool]:
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


def pkcs1v15_valid(m: int, n: int) -> bool:
    """PKCS#1 v1.5 类型 2 的粗判据：最高 16 位为 0x0002。"""
    k = (n.bit_length() + 7) // 8
    return (m >> (8 * k - 16)) == 2


def _test_material():
    """固定测试材料：两个 41 位相邻素数，gcd(p-1,q-1)=2，e=3 与 φ 互素。"""
    return 1099511627873, 1099511627891


def parity_oracle_decrypt(n: int, e: int, c: int, oracle) -> int:
    """oracle(c) -> True 表示对应明文是奇数（LSB/parity oracle）。

    经典 LSB→明文 递推（Bleichenbacher 1998）。令 S_0 = m、S_{k+1} = 2·S_k mod n、
    b_k = [2·S_k >= n]，逐轮展开得到闭式：

        2^T·m = n·M + S_T,   M = Σ_{k<T} b_k·2^{T-1-k},   0 <= S_T < n

    n 为奇数时 S_{k+1} 的奇偶恰是 b_k，所以 oracle 的回答序列直接给出 M；
    S_T 被 (*) 与 0 <= S_T < n 夹在宽度 n 的窗口内，窗口里只有 O(1) 个候选，
    逐个 pow(m, e, n) == c 复验，全部失败则报错（不返回未验证的值）。
    前提：m < n 且 oracle 无噪声。
    """
    if c <= 0 or c >= n:
        raise ValueError("密文必须落在 (0, n) 内")
    if e < 2:
        raise ValueError("e 必须 >= 2")
    step = pow(2, e, n)
    T = n.bit_length()
    cur = c
    seq = []
    for _ in range(T + 1):
        seq.append(1 if oracle(cur) else 0)
        cur = cur * step % n

    # S_{k+1} 的奇偶 = b_k（n 奇），故 M 由 seq[1..T] 构成
    M = 0
    for k in range(1, T + 1):
        M = (M << 1) | seq[k]
    base = M * n
    lo = base // (1 << T) + 1
    hi = (base + n) // (1 << T)
    for cand in range(max(0, lo - 1), min(n, hi + 2)):
        if 0 < cand < n and pow(cand, e, n) == c:
            return cand
    raise ValueError("parity oracle 未收敛（回答噪声或 e/c 不匹配，或明文 >= n）")


def pkcs1_oracle_decrypt(n: int, e: int, c: int, oracle, max_rounds=None) -> int:
    """区间 oracle（PKCS#1 v1.5 首阶段）：oracle(c) -> True 表示 m ∈ [2B, 3B)。

    B = 2^(8(k-2))。先倍增到命中，再按「2^i·m 是否仍在 [2B,3B)」逐步收窄区间，
    最后在收窄后的区间内用 pow 复验挑出明文。要求 2B <= m < 3B。
    """
    if c <= 0 or c >= n:
        raise ValueError("密文必须落在 (0, n) 内")
    k = (n.bit_length() + 7) // 8
    B = 1 << (8 * (k - 2))
    if B <= 0:
        raise ValueError("模数太短，无法构造 [2B, 3B) 区间")
    step = pow(2, e, n)
    if max_rounds is None:
        max_rounds = n.bit_length() + 8
    cur = c
    i = 0
    while i < max_rounds:
        i += 1
        if oracle(cur):
            break
        cur = cur * step % n
    else:
        raise ValueError("区间 oracle 未命中：明文不在 [2B, 3B) 或 oracle 有噪声")
    # 命中时 2^i·m ∈ [2B, 3B)，即 m ∈ [2B/2^i, 3B/2^i)
    lo = (2 * B + (1 << i) - 1) // (1 << i)
    hi = (3 * B) // (1 << i) + 1
    widest = hi - lo
    for _ in range(widest.bit_length() + 2):
        if hi - lo <= 1:
            break
        nxt = cur * step % n
        ok = oracle(nxt)
        i += 1
        cur = nxt
        if ok:
            lo = max(lo, (2 * B + (1 << i) - 1) // (1 << i))
            hi = min(hi, (3 * B) // (1 << i) + 1)
        else:
            lo = max(lo, (3 * B + (1 << i) - 1) // (1 << i))
            hi = min(hi, (2 * B) // (1 << i) + 1)
        if hi <= lo:
            break
    for cand in range(max(1, lo - 2), min(n, hi + 3)):
        if pow(cand, e, n) == c:
            return cand
    raise ValueError("区间 oracle 未收敛")


def manger_decrypt(n: int, e: int, c: int, k_bits: int, oracle, max_rounds: int = 4096) -> int:
    """Manger oracle：oracle(c) -> True 表示该密文解出的明文 < M = 2^k_bits。

    前提：m < M 且 2M <= n（倍增期间明文不会绕回 n）。

    结构（只用 oracle 的布尔回答，从不直接读明文）：

    1. 倍增定界：f = 2,4,8,… 直到 oracle(c·f^e) 首次回答 False，
       得 m ∈ [M/f1, M/(f1/2))。
    2. 阈值细化：每轮取 mid 为区间中点、f = M//mid + 1，问 oracle(c·f^e)。
       回答只区分 m <= M//f 与否，能砍掉的区间长度取决于 M//f 与端点的
       距离；因此维护区间 [lo, hi) 并保证它始终包含真值。
    3. 收尾：区间宽度落到可枚举范围后逐个 pow 复验；不透支复验，
       区间收不到 2^20 以内就报错。

    Manger 的攻击力本质上受「可用的 f 太少」限制（f 必须 < n），
    因此在真实题目里务必让 n 相对 M 足够大（本函数要求 2M <= n）。
    """
    if not 0 < k_bits < n.bit_length():
        raise ValueError("k_bits 必须落在 (0, n.bit_length()) 内")
    M = 1 << k_bits
    if 2 * M > n:
        raise ValueError("k_bits 过大：需要 2·2^k_bits <= n")
    f1 = 2
    while oracle(c * pow(f1, e, n) % n):
        f1 *= 2
        if f1 >= n or f1 > (1 << 64):
            raise ValueError("Manger 倍增阶段未收敛：m 可能不满足 m < M")
    lo = M // f1
    hi = M // (f1 // 2)
    rounds = 0
    while hi - lo > (1 << 20) and rounds < max_rounds:
        rounds += 1
        mid = (lo + hi) // 2
        f = M // mid + 1
        if f >= n:
            break
        bound = M // f
        hit = oracle(c * pow(f, e, n) % n)
        if hit:
            # 真值 <= bound；若 bound+1 不比 hi 小则这一步没信息，保守保留
            if bound + 1 < hi:
                hi = bound + 1
        else:
            # 真值 > bound；若 bound+1 不比 lo 大则没信息
            if bound + 1 > lo:
                lo = bound + 1
        if lo >= hi:
            raise ValueError("Manger 区间被切空：oracle 回答不自洽")
    found = None
    for cand in range(max(1, lo), min(n, hi + 1)):
        if pow(cand, e, n) == c:
            found = cand
            break
    if found is None:
        raise ValueError("Manger oracle 未收敛（区间宽度 %d）" % (hi - lo))
    return found


def homomorphic_bypass(n: int, e: int, c: int, decrypt) -> int:
    """oracle 拒绝解 c 时：找 r，使 c·r^e 被接受，解出后乘 r^{-1}。"""
    if c <= 0 or c >= n:
        raise ValueError("密文必须落在 (0, n) 内")
    for r in range(2, 1000):
        if xgcd(r, n)[0] != 1:
            continue
        try:
            m_r = decrypt(c * pow(r, e, n) % n)
        except ValueError:
            continue
        m = m_r * modinv(r, n) % n
        if pow(m, e, n) == c:
            return m
    raise ValueError("同态绕过失败：所有 r 都被拒绝")


def _selftest() -> int:
    ok = 0

    def check(cond, msg):
        nonlocal ok
        if not cond:
            raise AssertionError("selftest 失败: " + msg)
        ok += 1

    p, q = _test_material()
    n = p * q
    e = 3
    d = inv_d(p, q, e)
    m = 0x666C61677B7061647D  # flag{pad}
    if not m < n:
        raise AssertionError("selftest 失败: 明文必须小于 n")
    c = pow(m, e, n)

    # 1) 正常：parity oracle 恢复明文
    got = parity_oracle_decrypt(n, e, c, lambda cc: pow(cc, d, n) % 2 == 1)
    check(got == m, "parity oracle 应恢复明文")

    # 2) 正常：Manger oracle 倍增 + 二分
    k_bits = 8
    M = 1 << k_bits
    m_small = m % M
    c_small = pow(m_small, e, n)
    check(manger_decrypt(n, e, c_small, k_bits, lambda cc: pow(cc, d, n) < M) == m_small,
          "Manger oracle 应恢复明文")

    # 3) 正常：同态绕过（部分密文被拒）
    check(homomorphic_bypass(n, e, c,
                             lambda c0: (_ for _ in ()).throw(ValueError("拒绝")) if c0 % 7 == 0
                             else pow(c0, d, n)) == m, "同态绕过应恢复明文")

    # 4) 正常：int_root / PKCS#1 判据
    check(int_root(27, 3) == (3, True), "int_root 27 应为完全立方")
    check(int_root(26, 3) == (2, False), "int_root 26 应非完全立方")
    k_bytes = (511 + 7) // 8
    # 模长 k 字节：(k-2) 个前导零字节后紧跟 0x00 0x02
    check(pkcs1v15_valid(2 << (8 * (k_bytes - 2)), 1 << 511), "0x0002 前缀应判为合法 v1.5")
    check(not pkcs1v15_valid(3 << (8 * (k_bytes - 2)), 1 << 511), "0x0003 前缀应判为非法 v1.5")

    # 5) 边界拒绝：非法密文 / 非法 e / 非法 k_bits
    for bad in (lambda: parity_oracle_decrypt(n, e, 0, lambda x: True),
                lambda: parity_oracle_decrypt(n, 1, c, lambda x: True),
                lambda: manger_decrypt(n, e, c_small, 0, lambda x: True),
                lambda: manger_decrypt(n, e, c_small, n.bit_length(), lambda x: True),
                lambda: homomorphic_bypass(n, e, 0, lambda x: 0),
                lambda: int_root(-1, 3),
                lambda: inv_d(p, q, 6)):
        try:
            bad()
            raise AssertionError("selftest 失败: 非法输入未被拒绝")
        except ValueError:
            ok += 1

    # 6) 参数不足：恒定 oracle 不能凭空给出明文
    try:
        parity_oracle_decrypt(n, e, c, lambda x: True)
        raise AssertionError("selftest 失败: 恒定 oracle 不应返回明文")
    except ValueError:
        ok += 1

    # 7) 固定输入可复现
    a1 = parity_oracle_decrypt(n, e, c, lambda cc: pow(cc, d, n) % 2 == 1)
    a2 = parity_oracle_decrypt(n, e, c, lambda cc: pow(cc, d, n) % 2 == 1)
    check(a1 == a2 == m, "固定输入下应可复现")

    print("selftest ok: %d/%d（parity 二分、Manger 倍增二分、同态绕过、int_root/填充判据、"
          "非法输入拒绝、恒定 oracle 拒绝、可复现）" % (ok, ok))
    return 0


def _demo(which: str) -> int:
    p, q = _test_material()
    n = p * q
    e = 3
    d = inv_d(p, q, e)
    m = 0x666C61677B7061647D
    c = pow(m, e, n)
    if which == "parity":
        got = parity_oracle_decrypt(n, e, c, lambda cc: pow(cc, d, n) % 2 == 1)
    elif which == "manger":
        kb = n.bit_length() - 3
        got = manger_decrypt(n, e, pow(m % (1 << kb), e, n), kb,
                             lambda cc: pow(cc, d, n) < (1 << kb))
    elif which == "homo":
        got = homomorphic_bypass(n, e, c, lambda cc: pow(cc, d, n))
    else:
        print("demo 可选 parity / manger / homo / pkcs1", file=sys.stderr)
        return 2
    print("demo %s -> m = %x (%s)" % (which, got, "ok" if pow(got, e, n) == c or which == "manger" else "fail"))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="RSA 奇偶/填充 oracle 攻击")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--demo", choices=["parity", "manger", "homo"])
    ap.add_argument("--n", type=int)
    ap.add_argument("--e", type=int, default=3)
    ap.add_argument("--c", type=int)
    ap.add_argument("--lsb", nargs="*", default=None,
                    help="oracle 回答序列（1=奇数，0=偶数），按 oracle 被调用的顺序")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest()
    if args.demo:
        return _demo(args.demo)
    if args.n is None or args.c is None:
        print("参数不足: 需要 --selftest / --demo，或 --n 配 --c 与 --lsb 回答序列", file=sys.stderr)
        return 2
    seq = list(args.lsb or [])
    if not seq:
        print("参数不足: parity 攻击需要 --lsb 回答序列", file=sys.stderr)
        return 2
    pos = [0]

    def oracle(_c):
        if pos[0] >= len(seq):
            return False
        v = seq[pos[0]]
        pos[0] += 1
        return bool(int(v))

    try:
        m = parity_oracle_decrypt(args.n, args.e, args.c, oracle)
    except ValueError as exc:
        print("数据错误: %s" % exc, file=sys.stderr)
        return 1
    out = {"m": m, "plain_hex": format(m, "x")}
    print(json.dumps(out) if args.json else out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
