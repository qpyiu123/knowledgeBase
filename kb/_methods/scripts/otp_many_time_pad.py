#!/usr/bin/env python3
"""Many-Time-Pad（OTP / CTR 密钥流复用）恢复工具。

思路：c_i = m_i XOR k，所以 c_i XOR c_j = m_i XOR m_j，密钥在异或里被消掉。
本脚本提供：
  * xor_bytes / xor_table：两两异或的可读率矩阵；
  * crib_drag：在每段每个偏移拖 crib，用「解其它段的英文质量」打分；
  * best_space_positions：无 crib 时用「空格 XOR 字母仍是字母」定位空格；
  * recover_key_stream / apply_key：把 (offset, key_part) 合成部分 key 并解密；
  * solve：拼装上面的步骤，接受人工确认过的锚点（--anchor seg:off:text）。

只依赖标准库。退出码：0 成功、2 参数非法、1 未能恢复任何内容。
"""

from __future__ import annotations

import argparse
import itertools
import json
import string
import sys

PRINTABLE = set(bytes(string.printable, "ascii"))

# 英文字符频率（相对值），用于给候选明文打分
_FREQ = {
    " ": 0.182, "e": 0.102, "t": 0.075, "a": 0.065, "o": 0.061, "i": 0.057,
    "n": 0.057, "s": 0.053, "h": 0.049, "r": 0.049, "d": 0.034, "l": 0.033,
    "u": 0.022, "c": 0.022, "m": 0.020, "f": 0.018, "w": 0.017, "g": 0.016,
    "p": 0.015, "y": 0.014, "b": 0.012, "v": 0.008, "k": 0.006, "x": 0.0015,
    "j": 0.001, "q": 0.001, "z": 0.0007,
}


def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def _is_alpha(b: int) -> bool:
    return 65 <= b <= 90 or 97 <= b <= 122


def _norm_length(cts: list[bytes]) -> list[bytes]:
    """长度不一致时截到最短（补 0 会污染异或结果）。"""
    if not cts:
        raise ValueError("至少需要一段密文")
    L = min(len(c) for c in cts)
    if L <= 0:
        raise ValueError("密文为空")
    return [c[:L] for c in cts]


def xor_table(cts: list[bytes]):
    """逐对返回 (i, j, 可读率, 异或结果)，按可读率降序。"""
    cts = _norm_length(cts)
    rows = []
    for i, j in itertools.combinations(range(len(cts)), 2):
        x = xor_bytes(cts[i], cts[j])
        ratio = sum(b in PRINTABLE for b in x) / max(1, len(x))
        rows.append((i, j, ratio, x))
    rows.sort(key=lambda r: r[2], reverse=True)
    return rows


def english_score(buf: bytes) -> float:
    """每字节平均英文似然：字母/空格按词频给分，其它字符给很小的分。"""
    if not buf:
        return 0.0
    total = 0.0
    for b in buf:
        if b == 0x20:
            total += _FREQ[" "]
        elif _is_alpha(b):
            total += _FREQ.get(chr(b).lower(), 0.002)
        else:
            total += 0.0001
    return total / len(buf)


def _wordiness(buf: bytes) -> float:
    """连续可读字母串长度占比：真明文里字母成词，伪命中里字母被切碎。"""
    if not buf:
        return 0.0
    best = run = 0
    for b in buf:
        if _is_alpha(b):
            run += 1
            best = max(best, run)
        else:
            run = 0
    return best / len(buf)


def crib_drag(cts: list[bytes], crib: bytes, min_printable: float = 0.8):
    """在每段每个偏移尝试 crib，命中返回 [(评分, 段号, 偏移, key_part)]。

    评分 = 可打印率 + 英文似然 + 最长字母串占比；只有可打印率过线的进入候选。
    """
    if not crib:
        raise ValueError("crib 不能为空")
    cts = _norm_length(cts)
    hits = []
    for idx, c in enumerate(cts):
        for off in range(0, len(c) - len(crib) + 1):
            key_part = xor_bytes(c[off:off + len(crib)], crib)
            ok = total = 0
            decoded = bytearray()
            for other in cts:
                seg = xor_bytes(other[off:off + len(crib)], key_part)
                decoded.extend(seg)
                total += len(seg)
                ok += sum(b in PRINTABLE for b in seg)
            ratio = ok / total if total else 0.0
            if ratio < min_printable:
                continue
            score = ratio + english_score(bytes(decoded)) + 0.5 * _wordiness(bytes(decoded))
            hits.append((score, idx, off, key_part))
    hits.sort(key=lambda h: h[0], reverse=True)
    return hits


def recover_key_stream(cts: list[bytes], known) -> tuple[bytearray, bytearray]:
    """known: [(offset, key_part)] -> (key, mask)。mask=1 表示该位置已知。"""
    L = max(len(c) for c in cts)
    key = bytearray(L)
    mask = bytearray(L)
    for off, part in known:
        for i, b in enumerate(part):
            if 0 <= off + i < L:
                key[off + i] = b
                mask[off + i] = 1
    return key, mask


def apply_key(cts: list[bytes], key: bytes, mask: bytes) -> list[bytes]:
    """用 mask 标记的 key 字节解密，未覆盖的位置填 '.'。"""
    out = []
    for c in cts:
        buf = bytearray()
        for pos, b in enumerate(c):
            if pos < len(mask) and mask[pos]:
                d = b ^ key[pos]
                buf.append(d if d in PRINTABLE else ord("."))
            else:
                buf.append(ord("."))
        out.append(bytes(buf))
    return out


def best_space_positions(cts: list[bytes]):
    """每个位置找「最像空格」的段：与其余段异或后字母最多的那个。

    返回 [(hits, seg, byte)]，byte 是该段在该位置的密文字节。
    """
    cts = _norm_length(cts)
    L = len(cts[0])
    res = []
    for pos in range(L):
        cands = []
        for i, c in enumerate(cts):
            hits = sum(1 for j, d in enumerate(cts) if j != i and _is_alpha(c[pos] ^ d[pos]))
            cands.append((hits, i, c[pos]))
        cands.sort(reverse=True)
        res.append(cands[0])
    return res


def parse_anchor(text: str) -> tuple[int, bytes]:
    """'1:0:flag{' -> (1, b'flag{')。"""
    parts = text.split(":", 2)
    if len(parts) != 3:
        raise ValueError("锚点格式应为 seg:offset:text")
    seg, off, plain = parts
    if not plain:
        raise ValueError("锚点明文不能为空")
    return int(seg), plain.encode()


def solve(cts, cribs, min_printable=0.8, anchors=None, max_rounds=6):
    """拼装恢复流程，返回 (key, mask, plaintexts)。

    anchors 是 [(offset, key_part)]（人类已确认的密钥流片段）。
    1) crib 拖拽：每个 crib 取最佳命中，与已知 key 冲突就丢弃；
    2) 用已解出的连续片段当 crib 再拖拽，直到没有新增字节；
    3) 一个字节都没解出时才退回空格位置统计（只能粗定位，需人眼确认）。
    """
    cts = _norm_length(cts)
    L = len(cts[0])
    # anchors 直接合并 key 片段，不再对同一段重复解码
    key, mask = recover_key_stream(cts, [(int(off), bytes(part)) for off, part in (anchors or [])])

    def accept(key_part, off):
        nonlocal key, mask
        if any(mask[off + i] and key[off + i] != key_part[i] for i in range(len(key_part))):
            return False
        if all(mask[off + i] for i in range(len(key_part))):
            return False
        for i, b in enumerate(key_part):
            key[off + i] = b
            mask[off + i] = 1
        return True

    for crib in cribs:
        if not crib:
            continue
        hits = crib_drag(cts, crib, min_printable)
        if hits:
            accept(hits[0][3], hits[0][2])

    for _ in range(max_rounds):
        before = sum(mask)
        for start, end in _known_runs(bytes(mask)):
            if end - start < 4:
                continue
            crib = bytes(key[start:end])
            for _score, _idx, off, key_part in crib_drag(cts, crib, min_printable):
                if accept(key_part, off):
                    break
        if sum(mask) == before:
            break

    if not any(mask):
        guessed = [(pos, bytes([byte ^ 0x20]))
                   for pos, (_hits, _seg, byte) in enumerate(best_space_positions(cts))]
        key, mask = recover_key_stream(cts, guessed)

    return bytes(key[:L]), mask[:L], apply_key(cts, key, mask)


def _known_runs(mask):
    """mask 里连续的已知区间 [start, end)。"""
    runs = []
    start = None
    for pos in range(len(mask)):
        if mask[pos] and start is None:
            start = pos
        elif not mask[pos] and start is not None:
            runs.append((start, pos))
            start = None
    if start is not None:
        runs.append((start, len(mask)))
    return runs


def _parse_cts(args) -> list[bytes]:
    if args.hex:
        return [bytes.fromhex(s) for s in args.hex]
    if args.files:
        out = []
        for path in args.files:
            with open(path, "rb") as fh:
                out.append(fh.read().strip())
        return out
    raise ValueError("需要 --hex 或 --files")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Many-Time-Pad / 密钥流复用恢复")
    ap.add_argument("--hex", nargs="+", help="多段 hex 密文")
    ap.add_argument("--files", nargs="+", help="多个密文文件")
    ap.add_argument("--cribs", nargs="*", default=["flag{", "the "], help="可猜的固定明文片段")
    ap.add_argument("--anchor", dest="anchor_raw", nargs="*", default=[],
                    help="人工确认的锚点 seg:off:text")
    ap.add_argument("--min-printable", type=float, default=0.8)
    ap.add_argument("--table", action="store_true", help="只打印两两异或可读率")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    try:
        cts = _parse_cts(args)
        if len(cts) < 2:
            raise ValueError("至少需要两段密文")
        cribs = [c.encode() if isinstance(c, str) else c for c in args.cribs]
        anchor_keys = [(parse_anchor(a)) for a in args.anchor_raw]
        anchors = [(off, xor_bytes(cts[seg][off:off + len(text)], text))
                   for seg, off, text in anchor_keys]
        if any(seg >= len(cts) for seg, _o, _t in anchor_keys):
            raise ValueError("锚点段号超出范围")
        if any(off + len(text) > len(cts[seg]) for seg, off, text in anchor_keys):
            raise ValueError("锚点超出密文长度")
        if args.table:
            for i, j, r, x in xor_table(cts):
                print(f"{i}^{j} ratio={r:.3f} {x!r}")
            return 0
        key, mask, plain = solve(cts, cribs, args.min_printable, anchors)
        known = sum(mask)
        if known == 0:
            print("未恢复任何密钥字节：换更长的 crib 或先手工定位空格", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps({
                "known_bytes": known,
                "key": key.hex(),
                "plaintexts": [p.decode("latin-1") for p in plain],
            }, ensure_ascii=False, indent=2))
        else:
            print(f"已知密钥流字节: {known}")
            for i, p in enumerate(plain):
                print(f"[{i}] {p.decode('latin-1')}")
        return 0
    except (ValueError, TypeError, OSError) as exc:
        print(f"参数错误: {exc}", file=sys.stderr)
        return 2


# ---------------------------------------------------------------- selftest
MSGS = [
    b"the quick brown fox jumps over the lazy dog and runs",
    b"flag{otp_is_only_pad_once_and_never_more_than_once}",
    b"never reuse a one time pad because it becomes plain xor",
    b"attack at dawn with the second battalion near the ridge",
    b"cryptography is fun when the nonce is not random at all!",
]
KEY = bytes((i * 7 + 0x41) & 0xFF for i in range(60))


def selftest() -> int:
    ok = 0
    total = 0

    def check(cond, msg):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print(f"FAIL: {msg}", file=sys.stderr)

    cts = [xor_bytes(m, KEY) for m in MSGS]

    # case1 正常：c_i ^ c_j == m_i ^ m_j（密钥在异或里被消掉）
    check(xor_bytes(cts[0], cts[1]) == xor_bytes(MSGS[0], MSGS[1]), "两段密文异或应等于明文异或")

    # case2 正常：crib 'flag{' 的最佳命中是第 1 段偏移 0，且能还原出正确 key 片段
    hits = crib_drag(cts, b"flag{", 0.9)
    check(bool(hits) and hits[0][1] == 1 and hits[0][2] == 0, "crib 'flag{' 应命中第 1 段偏移 0")
    key_part = hits[0][3]
    check(key_part == KEY[:5], "命中的 key 片段应等于真实密钥前缀")

    # case3 正常：人工锚点写入 key 后，用同一段密文解密应还原出锚点明文
    key_share = xor_bytes(cts[0][:5], b"the q")
    key, mask = recover_key_stream(cts, [(0, key_share)])
    check(bytes(key[:5]) == KEY[:5] and sum(mask) == 5, "锚点应把 5 字节 key 前缀写进 mask")
    check(xor_bytes(cts[0][:5], key[:5]) == b"the q", "解出的明文应等于锚点内容")

    # case4 正常：空格统计在位置 3 命中满分（"the " 尾空格）
    guess = best_space_positions(cts)
    check(guess[3][0] == 4, "位置 3 其余 4 段都是字母，空格应得满分")
    check(guess[3][1] == 0 and MSGS[0][3:4] == b" ", "被选中的段该位置确实是空格")

    # case5 边界拒绝：长度不一致自动截断；空密文/空 crib/坏锚点报错
    norm = _norm_length([b"abcdef", b"abc"])
    check(all(len(c) == 3 for c in norm), "长度不一致应截到最短")
    for bad in ([], [b""]):
        try:
            _norm_length(bad)
            check(False, "空密文应报错")
        except ValueError:
            check(True, "")
    try:
        crib_drag(cts, b"")
        check(False, "空 crib 应报错")
    except ValueError:
        check(True, "")
    try:
        parse_anchor("1:0")
        check(False, "坏锚点应报错")
    except ValueError:
        check(True, "")

    # case6 参数不足 + 确定性
    import io
    from contextlib import redirect_stderr, redirect_stdout
    buf = io.StringIO()
    with redirect_stderr(buf), redirect_stdout(io.StringIO()):
        rc = main(["--cribs", "flag{"])
    check(rc == 2, "缺少 --hex/--files 应返回 2")
    a = solve(cts, [b"flag{"], 0.8, [(0, key_share)])
    b = solve(cts, [b"flag{"], 0.8, [(0, key_share)])
    check(bytes(a[0]) == bytes(b[0]) and bytes(a[1]) == bytes(b[1]), "相同输入应得到相同结果")

    if ok != total:
        print(f"selftest FAILED: {ok}/{total}", file=sys.stderr)
        return 1
    print(f"selftest ok: {ok}/{total}（异或恒等、crib 定位、key 片段校验、锚点解密、"
          f"空格统计、长度截断/空输入/坏锚点拒绝、参数不足 exit 2、确定性）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
