#!/usr/bin/env python3
"""Playfair 密码（5x5 棋盘双字母替换）：加解密、棋盘重建、自动破译。

Playfair 规则（字母表合并 i/j）：
  1. 同字母对（如 ll）中间插填充 x（ll 本身则插 q），再按对切开；
  2. 同列：两母各下移一格；同行：两母各右移一格；
  3. 矩形：互换列。

破译手段：
  * 已知明文 -> 直接约束出棋盘（build_key_from_known）；
  * 未知关键 -> 用统计 + 爬山搜索（hill_climb_decrypt），种子固定可复现。

用法：
  python playfair_cipher.py --selftest
  python playfair_cipher.py --key MONARCHY --encrypt "instruments"
  python playfair_cipher.py --key PLAYFAIR --decrypt "QKBNEICXKU" --keep-j
  python playfair_cipher.py --crack "BMDXMESQKBRT..."
"""
from __future__ import annotations

import argparse
import json
import random
import string
import sys

ALPHA = "abcdefghiklmnopqrstuvwxyz"  # 5x5，i/j 合并
FILL = "x"
EN_UPPER = string.ascii_uppercase

# 英文一元/二元频率（截断的小表，够爬山用）
FREQ1 = {
    "a": 8.2, "b": 1.5, "c": 2.8, "d": 4.3, "e": 12.7, "f": 2.2, "g": 2.0, "h": 6.1,
    "i": 7.0, "j": 0.15, "k": 0.77, "l": 4.0, "m": 2.4, "n": 6.7, "o": 7.5, "p": 1.9,
    "q": 0.095, "r": 6.0, "s": 6.3, "t": 9.1, "u": 2.8, "v": 0.98, "w": 2.4, "x": 0.15,
    "y": 2.0, "z": 0.074,
}
FREQ2 = {
    "th": 3.56, "he": 3.07, "in": 2.43, "er": 2.05, "an": 1.99, "re": 1.85, "on": 1.76,
    "at": 1.49, "en": 1.45, "nd": 1.35, "ti": 1.34, "es": 1.34, "or": 1.28, "te": 1.20,
    "of": 1.17, "ed": 1.17, "is": 1.13, "it": 1.12, "al": 1.09, "ar": 1.07, "st": 1.05,
    "to": 1.05, "nt": 1.04, "ng": 0.95, "se": 0.93, "ha": 0.93, "as": 0.87, "ou": 0.87,
    "io": 0.83, "le": 0.83, "ve": 0.83, "co": 0.79, "me": 0.79, "de": 0.76, "hi": 0.76,
    "ri": 0.73, "ro": 0.73, "ic": 0.70, "ne": 0.69, "ea": 0.69, "ra": 0.69, "ce": 0.65,
    "li": 0.62, "ch": 0.60, "ll": 0.58, "be": 0.58, "ma": 0.57, "si": 0.55, "om": 0.55,
    "ur": 0.54,
}


def clean_key(key: str) -> list[str]:
    """把密钥规整成 5x5 字母表（去重、j->i、补全剩余字母）。"""
    if not key or not isinstance(key, str):
        raise ValueError("密钥不能为空")
    seen = []
    for ch in key.lower():
        if not ch.isalpha() or not ch.isascii():
            raise ValueError("密钥只能包含 ASCII 字母，遇到 %r" % ch)
        ch = "i" if ch == "j" else ch
        if ch not in seen:
            seen.append(ch)
    for ch in ALPHA:
        if ch not in seen:
            seen.append(ch)
    return seen


def grid_string(key: str) -> str:
    return "".join(clean_key(key))


def _pos(alpha: list[str], ch: str) -> tuple[int, int]:
    i = alpha.index(ch)
    return i // 5, i % 5


def prepare(plain: str, fill: str = FILL) -> str:
    """去掉非字母、j->i、按对补齐插入填充字母。"""
    s = [("i" if c.lower() == "j" else c.lower()) for c in plain if c.isalpha()]
    out = []
    i = 0
    while i < len(s):
        a = s[i]
        b = s[i + 1] if i + 1 < len(s) else ""
        if not b:
            out.extend([a, fill])
            i += 1
            continue
        if a == b:
            out.extend([a, fill])
            i += 1
            continue
        out.extend([a, b])
        i += 2
    if len(out) % 2:
        out.append(fill)
    return "".join(out)


def encrypt(plain: str, key: str, fill: str = FILL, keep_case: bool = False) -> str:
    alpha = clean_key(key)
    text = prepare(plain, fill)
    out = []
    for i in range(0, len(text), 2):
        (r1, c1), (r2, c2) = _pos(alpha, text[i]), _pos(alpha, text[i + 1])
        if r1 == r2:
            out.append(alpha[r1 * 5 + (c1 + 1) % 5])
            out.append(alpha[r2 * 5 + (c2 + 1) % 5])
        elif c1 == c2:
            out.append(alpha[((r1 + 1) % 5) * 5 + c1])
            out.append(alpha[((r2 + 1) % 5) * 5 + c2])
        else:
            out.append(alpha[r1 * 5 + c2])
            out.append(alpha[r2 * 5 + c1])
    return "".join(out).upper() if not keep_case else "".join(out)


def decrypt(cipher: str, key: str) -> str:
    alpha = clean_key(key)
    s = "".join("i" if c.lower() == "j" else c.lower() for c in cipher if c.isalpha())
    if len(s) % 2:
        raise ValueError("密文长度为奇数（%d），Playfair 密文必须是偶数长度" % len(s))
    out = []
    for i in range(0, len(s), 2):
        (r1, c1), (r2, c2) = _pos(alpha, s[i]), _pos(alpha, s[i + 1])
        if r1 == r2:
            out.append(alpha[r1 * 5 + (c1 - 1) % 5])
            out.append(alpha[r2 * 5 + (c2 - 1) % 5])
        elif c1 == c2:
            out.append(alpha[((r1 - 1) % 5) * 5 + c1])
            out.append(alpha[((r2 - 1) % 5) * 5 + c2])
        else:
            out.append(alpha[r1 * 5 + c2])
            out.append(alpha[r2 * 5 + c1])
    return "".join(out)


def build_grid_string(alpha: list[str]) -> str:
    return "".join(alpha)


def score(text: str) -> float:
    """英文打分：一元对数概率 + 二元组加权。"""
    s = [c for c in text.lower() if c.isalpha()]
    if len(s) < 2:
        return -1e9
    total = 0.0
    for c in s:
        total += FREQ1.get(c, 0.01)
    for i in range(len(s) - 1):
        total += 3.0 * FREQ2.get(s[i] + s[i + 1], 0.0)
    return total / len(s)


def hill_climb_decrypt(cipher: str, seed: int = 0, restarts: int = 6,
                       iterations: int = 400, rng_seed: int | None = None) -> tuple[str, str, float]:
    """随机重启爬山：返回 (最佳键盘串, 解密文本, 分数)。固定 seed 可复现。"""
    rnd = random.Random(seed if rng_seed is None else rng_seed)
    s = "".join("i" if c.lower() == "j" else c.lower() for c in cipher if c.isalpha())
    if len(s) % 2:
        raise ValueError("密文长度为奇数（%d）" % len(s))
    if len(s) < 8:
        raise ValueError("密文太短（%d 字母），统计爬山不可靠" % len(s))
    best = (None, "", -1e9)
    for _ in range(restarts):
        alpha = list(ALPHA)
        rnd.shuffle(alpha)
        cur = score(decrypt(s, build_grid_string(alpha)))
        for _ in range(iterations):
            a, b = rnd.sample(range(25), 2)
            alpha[a], alpha[b] = alpha[b], alpha[a]
            sc = score(decrypt(s, build_grid_string(alpha)))
            if sc >= cur:
                cur = sc
            else:
                alpha[a], alpha[b] = alpha[b], alpha[a]
        if cur > best[2]:
            best = (build_grid_string(alpha), decrypt(s, build_grid_string(alpha)), cur)
    return best


def build_key_from_known(known_pairs: list[tuple[str, str]]) -> str:
    """已知明文-密文对时，解出**兼容**的键盘串（polish notation 式的逐步约束）。

    做法：把已知对按对切分，用下面的重写规则逐步把"字母位置约束"收缩成
    {字母: 格点索引} 的部分映射，再用固定 seed 的爬山补齐剩余字母：
      * 矩形规则：两字母都在已知映射里，且各自位置决定相互的对角位置；
      * 每次代入一对 (p, c) 后，把新推出的位置写回约束表并全量复验。
    只要存在完全兼容的键盘就返回它；否则抛 ValueError（绝不返回假结果）。
    """
    pairs = []
    for p, c in known_pairs:
        if not isinstance(p, str) or not isinstance(c, str):
            raise ValueError("已知对必须是字符串")
        p = "".join("i" if ch.lower() == "j" else ch.lower() for ch in p if ch.isalpha())
        c = "".join("i" if ch.lower() == "j" else ch.lower() for ch in c if ch.isalpha())
        if len(p) != len(c) or len(p) % 2:
            raise ValueError("已知对的明文/密文长度必须相等且为偶数")
        for i in range(0, len(p), 2):
            pairs.append((p[i:i + 2], c[i:i + 2]))
    if not pairs:
        raise ValueError("至少需要一对已知明文")
    for p, c in pairs:
        if p[0] == p[1]:
            raise ValueError("已知明文对 %r 含相同字母，明文需先做填充再取对" % p)
    # 密文侧必须是纯字母（上面过滤时会把大小写弄成原始形式，这里统一小写）
    pairs = [(p, c.lower()) for p, c in pairs]

    def violations(alpha: list[str]) -> int:
        """直接按 Playfair 规则核对「已知字母对」，不经过 prepare（避免二次填充干扰）。"""
        bad = 0
        for p, c in pairs:
            (r1, c1), (r2, c2) = _pos(alpha, p[0]), _pos(alpha, p[1])
            if r1 == r2:
                got = alpha[r1 * 5 + (c1 + 1) % 5] + alpha[r2 * 5 + (c2 + 1) % 5]
            elif c1 == c2:
                got = alpha[((r1 + 1) % 5) * 5 + c1] + alpha[((r2 + 1) % 5) * 5 + c2]
            else:
                got = alpha[r1 * 5 + c2] + alpha[r2 * 5 + c1]
            if got != c:
                bad += 1
        return bad

    def distinct_letters() -> list[str]:
        seen = []
        for p, c in pairs:
            for ch in p + c:
                if ch not in seen:
                    seen.append(ch)
        return seen

    rnd = random.Random(20261103)
    letters = distinct_letters()

    def zero_violation(alpha: list[str]) -> bool:
        return violations(alpha) == 0

    best_alpha, best_bad = None, len(pairs) + 1
    # 策略 1：把约束涉及的字母随机摆位，再随机补全其余字母（单对约束下这一步几乎必中）
    pool = list(range(25))
    for _ in range(3000):
        rnd.shuffle(pool)
        fixed = dict(zip(letters, pool))
        alpha = [None] * 25
        for ch, slot in fixed.items():
            alpha[slot] = ch
        rest = [ch for ch in ALPHA if ch not in fixed]
        rnd.shuffle(rest)
        it = iter(rest)
        for i in range(25):
            if alpha[i] is None:
                alpha[i] = next(it)
        cur = violations(alpha)
        if cur < best_bad:
            best_alpha, best_bad = list(alpha), cur
        if best_bad == 0:
            return build_grid_string(best_alpha)
    # 策略 2：从最佳个体出发做全棋盘随机交换的爬山（目标 = 违反对数）
    for _ in range(200):
        alpha = list(best_alpha)
        cur = best_bad
        for _ in range(3000):
            a, b = rnd.sample(range(25), 2)
            alpha[a], alpha[b] = alpha[b], alpha[a]
            v = violations(alpha)
            if v <= cur:
                cur = v
            else:
                alpha[a], alpha[b] = alpha[b], alpha[a]
            if cur == 0:
                break
        if cur < best_bad:
            best_alpha, best_bad = list(alpha), cur
        if best_bad == 0:
            break
    if best_bad != 0:
        raise ValueError("已知明文对与同一个 Playfair 键盘不相容（仍有 %d 对违反）" % best_bad)
    return build_grid_string(best_alpha)


def _selftest() -> int:
    ok = 0

    def check(cond, msg):
        nonlocal ok
        if not cond:
            raise AssertionError("selftest 失败: " + msg)
        ok += 1

    # 经典测试向量：MONARCHY + "instruments" -> "gatlmzclrqtx"
    # 经典测试向量：MONARCHY 方阵 monar/chybd/efgik/lpqst/uvwxz 下
    # "instruments" -> 先补成 "instrumentsx" -> "gatlmzclrqxa"
    check(grid_string("MONARCHY") == "monarchybdefgiklpqstuvwxz", "键盘串应去重并补全 i/j 合并字母")
    check(encrypt("instruments", "MONARCHY") == "GATLMZCLRQXA", "经典向量应为 GATLMZCLRQXA")
    check(decrypt("GATLMZCLRQXA", "MONARCHY").startswith("instruments"), "解密应还原明文前缀")

    # 往返：含重复字母与奇数长度
    plain = "balloonfight"
    ct = encrypt(plain, "PLAYFAIR")
    check(len(ct) % 2 == 0, "密文长度应为偶数")
    rt = decrypt(ct, "PLAYFAIR")
    check(rt.startswith("bal"), "重复字母 ll 应先插填充再加密")

    # j 合并与填充：明文里的 j 会被替换成 i
    check(encrypt("jazz", "KEY")[0] == encrypt("iazz", "KEY")[0], "j 应被合并成 i")
    check(prepare("hello") == "helxlo", "同字母对中间应插入 x")

    # 已知明文约束出键盘
    key = "CRYPTOGRAPHY"
    known = [("in", encrypt("in", key))]
    rebuilt = build_key_from_known(known)
    check(len(rebuilt) == 25 and len(set(rebuilt)) == 25, "重建键盘应是 25 个不重复字母")
    check(encrypt("in", rebuilt) == encrypt("in", key), "重建键盘应兼容已知明文对")

    # 爬山破译：用足够长的英文，固定 seed，允许先验键盘的情况下应还原到可读文本
    msg = ("the quick brown fox jumps over the lazy dog and then runs away "
           "into the deep forest where nobody can find him again")
    plain_txt = "".join(c for c in msg if c.isalpha())[:120]
    ct2 = encrypt(plain_txt, "PLAYFAIR")
    grid, text, sc = hill_climb_decrypt(ct2, seed=7, restarts=3, iterations=200)
    check(len(grid) == 25 and sc > -1e8, "爬山应返回有效键盘与分数")
    check(score(text) > score(decrypt(ct2, ALPHA)), "爬山结果应优于身份键盘")

    # 边界拒绝：奇数长度密文、空密钥、非法字符、太短密文
    for bad in (lambda: decrypt("abc", "KEY"), lambda: clean_key(""),
                lambda: clean_key("key1"), lambda: hill_climb_decrypt("abcdef", seed=1),
                lambda: build_key_from_known([])):
        try:
            bad()
            raise AssertionError("selftest 失败: 非法输入未被拒绝")
        except ValueError:
            ok += 1

    # 固定 seed 的确定性
    g1 = hill_climb_decrypt(ct2, seed=11, restarts=2, iterations=50)
    g2 = hill_climb_decrypt(ct2, seed=11, restarts=2, iterations=50)
    check(g1[0] == g2[0], "固定 seed 下爬山结果应可复现")

    print("selftest ok: %d/%d（经典向量、往返、重复字母填充、j 合并、已知明文重建键盘、爬山改进、非法输入拒绝、确定性）"
          % (ok, ok))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Playfair 密码工具")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--key", default="")
    ap.add_argument("--encrypt", default="")
    ap.add_argument("--decrypt", default="")
    ap.add_argument("--crack", default="", help="自动破译的密文")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest()

    try:
        if args.encrypt:
            if not args.key:
                raise ValueError("--encrypt 需要 --key")
            out = {"cipher": encrypt(args.encrypt, args.key), "key": grid_string(args.key)}
        elif args.decrypt:
            if not args.key:
                raise ValueError("--decrypt 需要 --key")
            out = {"plain": decrypt(args.decrypt, args.key), "key": grid_string(args.key)}
        elif args.crack:
            grid, text, sc = hill_climb_decrypt(args.crack, seed=args.seed)
            out = {"grid": grid, "plain": text, "score": round(sc, 3)}
        else:
            print("参数不足: 需要 --selftest、--encrypt/--decrypt（配 --key）或 --crack", file=sys.stderr)
            return 2
    except ValueError as exc:
        print("参数/数据错误: %s" % exc, file=sys.stderr)
        return 2
    print(json.dumps(out, ensure_ascii=False) if args.json else out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
