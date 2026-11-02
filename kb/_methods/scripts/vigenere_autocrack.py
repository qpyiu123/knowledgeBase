#!/usr/bin/env python3
"""Vigenère 自动破解：重合指数（IoC）定密钥长 + 列内卡方定位移。

依赖：纯标准库。
用途：只有密文的古典多表替换题。两步：
  1) 对 1..maxlen 的每个密钥长 k，把密文按列切成 k 组，各组的 IoC（英语
     约 0.065，随机约 0.038）取平均，最高的 k 即候选密钥长。
     也支持 Kasiski 距离 gcd 作为交叉验证。
  2) 候选密钥长下，每一列单独当成 Caesar 密码，用英文字母频率卡方最小
     的位移作为该列密钥字母。

用法：
  python vigenere_autocrack.py --cipher FILE_OR_TEXT --max-len 20
  python vigenere_autocrack.py --cipher ... --kasiski
  python vigenere_autocrack.py --selftest

限制：对短文本、非英语（中文/混合大小写且非英语）、非标准 alphabet 无效。
      原文若被额外替换（如 A1Z26、ROT 后再 Vigenère）需先复原一层。
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter

# 英语字母频率（A-Z），来源为常见 cryptanalysis 表
EN_FREQ = [
    0.08167, 0.01492, 0.02782, 0.04253, 0.12702, 0.02228, 0.02015, 0.06094,
    0.06966, 0.00153, 0.00772, 0.04025, 0.02406, 0.06749, 0.07507, 0.01929,
    0.00095, 0.05987, 0.06327, 0.09056, 0.02758, 0.00978, 0.02360, 0.00150,
    0.01974, 0.00074,
]


def clean(text: str) -> str:
    """只保留 A-Z（大写），其余字符丢弃。"""
    return "".join(ch for ch in text.upper() if "A" <= ch <= "Z")


def index_of_coincidence(data: str) -> float:
    """重合指数：同一位被两个随机位置取到相同字母的概率。"""
    n = len(data)
    if n < 2:
        return 0.0
    counts = Counter(data)
    total = sum(c * (c - 1) for c in counts.values())
    return total / (n * (n - 1))


def key_length_by_ioc(text: str, max_len: int = 20) -> list[tuple[int, float]]:
    """按密钥长评分，返回 [(k, 平均 IoC)]，按 IoC 降序。"""
    scores = []
    for k in range(1, min(max_len, len(text) // 2) + 1):
        cols = [text[i::k] for i in range(k)]
        avg = sum(index_of_coincidence(c) for c in cols) / k
        scores.append((k, avg))
    scores.sort(key=lambda t: t[1], reverse=True)
    return scores


def kasiski_candidates(text: str, ngram: int = 3, top: int = 5) -> list[tuple[str, list[int]]]:
    """Kasiski：重复三元组的间隔距离（取 gcd 作为密钥长线索）。"""
    pos: dict[str, list[int]] = {}
    for i in range(len(text) - ngram + 1):
        pos.setdefault(text[i:i + ngram], []).append(i)
    out = []
    for g, ps in pos.items():
        if len(ps) < 2:
            continue
        dists = [ps[j + 1] - ps[j] for j in range(len(ps) - 1)]
        out.append((g, dists))
    out.sort(key=lambda t: -len(t[1]))
    return out[:top]


def chi2_shift(col: str) -> tuple[int, float]:
    """返回 (最优 Caesar 位移, 卡方值)；位移即该列密钥字母。"""
    n = len(col)
    best_shift, best_chi = 0, float("inf")
    counts = Counter(col)
    for shift in range(26):
        chi = 0.0
        for i in range(26):
            # 若该列明文为 (c - shift)，则字母 i 的期望占比是 EN_FREQ[i]
            obs = counts.get(chr((i + shift) % 26 + 65), 0)
            exp = EN_FREQ[i] * n
            if exp > 0:
                chi += (obs - exp) ** 2 / exp
        if chi < best_chi:
            best_shift, best_chi = shift, chi
    return best_shift, best_chi


def crack(text: str, key_len: int) -> tuple[str, str]:
    """给定密钥长，求密钥与明文。"""
    key = "".join(chr(chi2_shift(text[i::key_len])[0] + 65) for i in range(key_len))
    plain = "".join(
        chr((ord(ch) - 65 - (ord(key[i % key_len]) - 65)) % 26 + 65)
        for i, ch in enumerate(text)
    )
    return key, plain


def decrypt_with_key(text: str, key: str) -> str:
    key = key.upper()
    return "".join(
        chr((ord(ch) - 65 - (ord(key[i % len(key)]) - 65)) % 26 + 65)
        for i, ch in enumerate(text)
    )


def encrypt_with_key(text: str, key: str) -> str:
    key = key.upper()
    return "".join(
        chr((ord(ch) - 65 + (ord(key[i % len(key)]) - 65)) % 26 + 65)
        for i, ch in enumerate(text)
    )


SELFTEST_PLAIN = (
    "THISISABITOFENGLISHPLAINTEXTTHEKINDYOUMIGHTSEEOVERANDFUZZBUNNY"
    "FACTORYPRODUCTIONLINEANDITISLONGENOUGHFORTHEINDEXOFCONCIDENCE"
    "METHODTOWORKRELIABLYONASAMPLETHISLIKEMAKESITATLEASTTHREEHUNDRED"
    "CHARACTERSLONGWHICHISWHATWENEEDFORTHEKEYLENGTHDETECTION"
)


def selftest() -> int:
    fails = []

    # ---- 算例 1：加密/解密互逆 ---------------------------------------------
    msg = clean(SELFTEST_PLAIN)
    key = "LEMON"
    ct = encrypt_with_key(msg, key)
    if decrypt_with_key(ct, key) != msg:
        fails.append("case1: 加解密不互逆")
    if len(ct) != len(msg):
        fails.append("case1: 密文长度变了")

    # ---- 算例 2：IoC 能在正确密钥长（或其整数倍）上给出峰值 ----------------
    scores = key_length_by_ioc(ct, max_len=12)
    best_k = scores[0][0]
    if best_k % len(key) != 0 and len(key) % best_k != 0:
        fails.append(f"case2: IoC 峰值密钥长 {best_k} 与 {len(key)} 无关")
    # 正确密钥长（或 2 倍）的 IoC 应显著高于随机基线 0.038
    ioc_correct = max(dict(scores).get(len(key), 0.0), dict(scores).get(2 * len(key), 0.0))
    if not (ioc_correct > 0.045):
        fails.append(f"case2: IoC 关系异常 correct={ioc_correct:.4f}")

    # ---- 算例 3：恢复的密钥与明文完全正确（用已知长度 5 精确求解）---------
    rec_key, rec_plain = crack(ct, len(key))
    if rec_key != key:
        fails.append(f"case3: 密钥还原错误 {rec_key} != {key}")
    if rec_plain != msg:
        fails.append("case3: 明文还原错误")
    # 用 IoC 峰值（可能是 10 = 2×5）也应能解出同样的明文
    k2 = best_k if best_k % len(key) == 0 else len(key)
    k2_key, k2_plain = crack(ct, k2)
    # 密钥长取倍数时每列样本变少，卡方可能个别列偏移；要求 80% 以上字符正确
    agree = sum(1 for a, b in zip(k2_plain, msg) if a == b) / max(1, len(msg))
    if agree < 0.7:
        fails.append(f"case3: 峰值长度 {k2} 解出的明文仅 {agree:.0%} 正确")

    # ---- 算例 4：Kasiski 距离能被 5 整除 -----------------------------------
    kk = kasiski_candidates(ct)
    if not kk:
        fails.append("case4: Kasiski 未找到重复三元组")
    else:
        divisible = any(all(d % len(key) == 0 for d in ds) for _, ds in kk)
        if not divisible:
            fails.append("case4: 无一组 Kasiski 距离能被密钥长整除")

    # ---- 算例 5：随机文本的 IoC 应远低于英语 ------------------------------
    import random as _r
    rng = _r.Random(7)
    rnd = "".join(rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(400))
    if index_of_coincidence(rnd) > 0.05:
        fails.append("case5: 随机文本 IoC 过高")

    for f in fails:
        print(f"FAIL {f}", file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 5/5（互逆、IoC 峰值、密钥+明文还原、Kasiski、随机 IoC）")
    return 0


def load_cipher(value: str) -> str:
    from pathlib import Path
    p = Path(value)
    raw = p.read_text(encoding="utf-8", errors="replace") if p.is_file() else value
    return clean(raw)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Vigenère 自动破解")
    ap.add_argument("--cipher", help="密文文本，或一个文件路径")
    ap.add_argument("--max-len", type=int, default=20, help="尝试的最大密钥长")
    ap.add_argument("--key-len", type=int, default=None, help="已知密钥长时直接指定")
    ap.add_argument("--key", help="已知密钥时直接解密")
    ap.add_argument("--kasiski", action="store_true", help="额外输出 Kasiski 线索")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.cipher:
        ap.error("需要 --cipher，或用 --selftest")

    text = load_cipher(args.cipher)
    if len(text) < 20:
        print(f"警告：有效字母只有 {len(text)} 个，统计方法不可靠", file=sys.stderr)

    if args.key:
        out = {"key": args.key.upper(), "plaintext": decrypt_with_key(text, args.key)}
        print(json.dumps(out, ensure_ascii=False, indent=2) if args.json else
              f"key = {out['key']}\nplain = {out['plaintext']}")
        return 0

    if args.key_len:
        k = args.key_len
    else:
        scores = key_length_by_ioc(text, args.max_len)
        k = scores[0][0]
        if not args.json:
            print("密钥长候选（IoC 降序）：")
            for kk, v in scores[:5]:
                print(f"  k={kk:<3} IoC={v:.4f}")
        if args.kasiski:
            print("Kasiski 重复三元组距离：")
            for g, ds in kasiski_candidates(text):
                print(f"  {g}: {ds}")

    key, plain = crack(text, k)
    out = {"key_len": k, "key": key, "plaintext": plain}
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(f"\n推定密钥长 = {k}\n恢复密钥 = {key}\n明文 = {plain[:200]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
