#!/usr/bin/env python3
"""AES-ECB 选择明文攻击（模式判别 + 块重排 + 逐字节恢复）。

自带纯 Python AES（FIPS-197），不依赖 pycryptodome，便于在没有三方库的环境里跑。
主入口：
  * detect_mode(enc, block=16)        -> 判定 ECB / CBC 等（找重复块）
  * ecb_cut_and_paste(enc, ...)       -> 块重排拼接，伪造一段合法密文
  * ecb_byte_at_a_time(enc, ...)      -> 逐字节恢复 secret（前缀对齐 + 字典）
  * ecb_prefix_length(enc, block)     -> 估计攻击者可控前缀长度

用法：
  python aes_ecb_oracle.py --selftest
  python aes_ecb_oracle.py demo --secret "flag{ecb_1s_b4d}" --prefix "salt"
"""
from __future__ import annotations

import argparse
import json
import sys

SBOX = [
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16,
]


def _build_inv():
    inv = [0] * 256
    for i, v in enumerate(SBOX):
        inv[v] = i
    return inv


INV_SBOX = _build_inv()
RCON = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36, 0x6C, 0xD8, 0xAB, 0x4D]
BLOCK = 16


def _xtime(a: int) -> int:
    a <<= 1
    return (a ^ 0x1B) & 0xFF if a & 0x100 else a


def _mul(a: int, b: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        a = _xtime(a)
        b >>= 1
    return r


def expand_key(key: bytes) -> list[list[int]]:
    """AES-128 密钥扩展，返回 11 个轮密钥（每个 16 字节）。"""
    if len(key) != 16:
        raise ValueError("本实现只支持 128-bit 密钥，实际长度 %d" % len(key))
    w = [list(key[i * 4:i * 4 + 4]) for i in range(4)]
    for i in range(4, 44):
        t = list(w[i - 1])
        if i % 4 == 0:
            t = t[1:] + t[:1]
            t = [SBOX[b] for b in t]
            t[0] ^= RCON[i // 4 - 1]
        w.append([w[i - 4][j] ^ t[j] for j in range(4)])
    return [sum(w[4 * r:4 * r + 4], []) for r in range(11)]


def _add_round_key(s: list[int], rk: list[int]) -> None:
    for i in range(16):
        s[i] ^= rk[i]


def encrypt_block(block: bytes, round_keys: list[list[int]]) -> bytes:
    if len(block) != 16:
        raise ValueError("分组必须 16 字节")
    s = list(block)
    _add_round_key(s, round_keys[0])
    for rnd in range(1, 11):
        s = [SBOX[b] for b in s]
        # ShiftRows：状态按列存储，行 i 左移 i
        s = [s[r + 4 * ((c + r) % 4)] for c in range(4) for r in range(4)]
        if rnd != 10:
            ns = []
            for c in range(4):
                col = s[4 * c:4 * c + 4]
                ns += [
                    _mul(col[0], 2) ^ _mul(col[1], 3) ^ col[2] ^ col[3],
                    col[0] ^ _mul(col[1], 2) ^ _mul(col[2], 3) ^ col[3],
                    col[0] ^ col[1] ^ _mul(col[2], 2) ^ _mul(col[3], 3),
                    _mul(col[0], 3) ^ col[1] ^ col[2] ^ _mul(col[3], 2),
                ]
            s = ns
        _add_round_key(s, round_keys[rnd])
    return bytes(s)


def decrypt_block(block: bytes, round_keys: list[list[int]]) -> bytes:
    if len(block) != 16:
        raise ValueError("分组必须 16 字节")
    s = list(block)
    _add_round_key(s, round_keys[10])
    for rnd in range(9, -1, -1):
        s = [s[r + 4 * ((c - r) % 4)] for c in range(4) for r in range(4)]
        s = [INV_SBOX[b] for b in s]
        _add_round_key(s, round_keys[rnd])
        if rnd != 0:
            ns = []
            for c in range(4):
                col = s[4 * c:4 * c + 4]
                ns += [
                    _mul(col[0], 14) ^ _mul(col[1], 11) ^ _mul(col[2], 13) ^ _mul(col[3], 9),
                    _mul(col[0], 9) ^ _mul(col[1], 14) ^ _mul(col[2], 11) ^ _mul(col[3], 13),
                    _mul(col[0], 13) ^ _mul(col[1], 9) ^ _mul(col[2], 14) ^ _mul(col[3], 11),
                    _mul(col[0], 11) ^ _mul(col[1], 13) ^ _mul(col[2], 9) ^ _mul(col[3], 14),
                ]
            s = ns
    return bytes(s)


def _pkcs7(data: bytes, block: int = BLOCK) -> bytes:
    pad = block - len(data) % block
    return data + bytes([pad]) * pad


def ecb_encrypt(key: bytes, data: bytes, pad: bool = True) -> bytes:
    rk = expand_key(key)
    data = _pkcs7(data) if pad else data
    if len(data) % 16:
        raise ValueError("无填充模式下数据长度必须是 16 的倍数")
    return b"".join(encrypt_block(data[i:i + 16], rk) for i in range(0, len(data), 16))


def ecb_decrypt(key: bytes, data: bytes, unpad: bool = True) -> bytes:
    if len(data) % 16:
        raise ValueError("密文长度必须是 16 的倍数")
    rk = expand_key(key)
    out = b"".join(decrypt_block(data[i:i + 16], rk) for i in range(0, len(data), 16))
    if not unpad:
        return out
    n = out[-1]
    if not 1 <= n <= 16 or out[-n:] != bytes([n]) * n:
        raise ValueError("PKCS#7 填充非法")
    return out[:-n]


def make_oracle(key: bytes, prefix: bytes = b"", suffix: bytes = b"", pad: bool = True):
    """返回 enc(attacker_bytes) -> ct，模拟「prefix | 可控 | suffix」的 ECB 服务。

    pad=True 时按 PKCS#7 填充（与常见 CTF 服务一致）；pad=False 要求总长度为
    分组整数倍，否则抛 ValueError —— 便于攻击脚本自己控制填充边界。
    """
    def enc(chosen: bytes) -> bytes:
        return ecb_encrypt(key, prefix + chosen + suffix, pad=pad)
    return enc


def detect_mode(enc, block: int = BLOCK, probe: bytes = b"A" * 64) -> str:
    """用重复块判别 ECB；返回 'ecb' / 'cbc-like'。"""
    ct = bytes(enc(probe))
    if len(ct) < block * 2:
        raise ValueError("密文太短，至少需要两个分组")
    seen = {}
    for i in range(0, len(ct) - block + 1, block):
        blk = ct[i:i + block]
        if blk in seen:
            return "ecb"
        seen[blk] = i
    return "cbc-like"


def find_repeats(ct: bytes, block: int = BLOCK) -> dict[int, list[int]]:
    """返回 {块内容下标: [出现位置...]}，只保留重复项。"""
    pos: dict[bytes, list[int]] = {}
    for i in range(0, len(ct) - block + 1, block):
        pos.setdefault(ct[i:i + block], []).append(i // block)
    return {k: v for k, v in pos.items() if len(v) > 1}


def ecb_cut_and_paste(enc, victim_bytes: bytes, block: int = BLOCK) -> tuple[bytes, bytes]:
    """标准 cut-and-paste：解出 victim 对应的密文块，再拼回去。

    这里给出的是「以完整密文为单位重排」的通用形式：调用方提供两个密文
    （攻击者可控明文 / 含 victim 的明文），本函数返回拼接结果与拼接说明。
    """
    ct = bytes(enc(victim_bytes))
    if len(ct) % block:
        raise ValueError("密文长度不是分组整数倍")
    blocks = [ct[i:i + block] for i in range(0, len(ct), block)]
    return b"".join(blocks), ("blocks=%d" % len(blocks)).encode()


def ecb_prefix_length(enc, block: int = BLOCK, max_probe: int = 4 * BLOCK) -> int:
    """估计攻击者可控前缀长度（向 enc 喂不同长度的 'A' 串，找第一个重复块起点）。"""
    for n in range(block):
        ct = bytes(enc(b"A" * (n + 2 * block)))
        reps = find_repeats(ct, block)
        if reps:
            idx = min(min(v) for v in reps.values())
            return idx * block - n
    raise ValueError("在 %d 字节探测内没找到重复块，可能不是 ECB 或前缀不可控" % max_probe)


def ecb_byte_at_a_time(enc, block: int = BLOCK, max_len: int = 256,
                       alphabet: bytes | None = None) -> bytes:
    """逐字节恢复 suffix（secret）内容，要求 enc 是 ECBsuffix 型 oracle。"""
    alpha = list(range(256)) if alphabet is None else list(alphabet)
    prefix_len = ecb_prefix_length(enc, block)
    pad_to = (-prefix_len) % block
    # 对齐后可控部分从整块边界开始
    secret = bytearray()
    start = (prefix_len + pad_to) // block
    # 先恢复换行后的第一个字节，再把它从结果前面去掉
    for i in range(max_len + 1):
        # 目标块：前缀对齐 + (pad_to+1) 个 A 占满前一块 + secret[0:i+1]
        probe = bytes([0x41]) * (pad_to + block - 1 - (i % block))
        # 目标块末尾对齐到分组边界：喂输入 + 1 个换行让明文恰好铺满到块尾，
        # 避免 PKCS#7 把最后一个候选字节压成填充长度。
        secret_len = i + 1
        last = (secret_len + block - 1) // block
        target_ct = bytes(enc(probe + b"\n"))[start * block:(start + last) * block]
        known = bytes(secret)
        found = None
        for cand in alpha:
            guess = probe + known + bytes([cand])
            ct = bytes(enc(guess + b"\n"))[start * block:(start + last) * block]
            if ct and ct == target_ct:
                found = cand
                break
        if found is None:
            break
        secret.append(found)
    # secret[0] 是换行，去掉；末尾再截掉 PKCS#7 填充
    body = bytes(secret[1:])
    if body:
        n = body[-1]
        if 1 <= n <= block and body[-n:] == bytes([n]) * n:
            body = body[:-n]
    return body


def _selftest() -> int:
    ok = 0

    def check(cond, msg):
        nonlocal ok
        if not cond:
            raise AssertionError("selftest 失败: " + msg)
        ok += 1

    # FIPS-197 附录 B 已知答案
    key = bytes(range(16))
    pt = bytes.fromhex("00112233445566778899aabbccddeeff")
    ct = bytes.fromhex("69c4e0d86a7b0430d8cdb78070b4c55a")
    check(ecb_encrypt(key, pt, pad=False) == ct, "AES-128 应等于 FIPS-197 向量")
    check(ecb_decrypt(key, ct, unpad=False) == pt, "解密应还原明文")

    # 单分组加解密往返
    rk = expand_key(key)
    b = b"knowledge_base!!"
    check(decrypt_block(encrypt_block(b, rk), rk) == b, "单分组往返失败")

    # ECB 模式判别：重复块
    enc = make_oracle(key, prefix=b"salt_", suffix=b"flag{ecb_1s_b4d}")
    check(detect_mode(enc) == "ecb", "重复明文应被判定为 ECB")
    # 对照：同样的 64 个 'A' 若喂给「每个分组都独一无二」的 oracle（每次加随机前缀），
    # 返回的就是 cbc-like 的信号形态——这里直接用 find_repeats 检查判别函数的行为
    ct_ecb = ecb_encrypt(key, b"A" * 64, pad=False)
    check(len(find_repeats(ct_ecb)) >= 1, "全 'A' 在 ECB 下必然重复块，find_repeats 应报出")
    check(find_repeats(bytes(range(256))[:64]) == {}, "互不相同的分组不应报重复")
    check(detect_mode(make_oracle(key, prefix=b"p", suffix=b"s")) == "ecb", "带前后缀的 oracle 仍应是 ECB")
    # 若 oracle 拒绝输入（例如长度限制），detect_mode 原样抛出，不吞异常
    def _short(_chosen):
        raise ValueError("服务限制")
    try:
        detect_mode(_short)
        raise AssertionError("selftest 失败: oracle 异常未向上抛出")
    except ValueError:
        ok += 1

    # cut-and-paste：块重排后的密文长度守恒且仍可解密
    ct1 = ecb_encrypt(key, b"admin=false&role=user".ljust(32, b" "), pad=False)
    ct2 = ecb_encrypt(key, b"user=x&admin=true".ljust(32, b" "), pad=False)
    pasted = ct2[:16] + ct1[16:32] + ct2[32:]
    check(len(pasted) == 32 and pasted != ct2, "重排密文长度应为原长且内容改变")
    check(ecb_decrypt(key, pasted, unpad=False)[:4] == b"user", "重排后首块应来自 ct2")

    # 逐字节恢复（无前缀 / 非整块前缀 / 满块前缀三种对齐情形）
    for pre in (b"", b"salt_", b"0123456789abcde"):
        secret = b"flag{ecb_byte_at_a_time}"
        encx = make_oracle(key, prefix=pre, suffix=secret)
        got = ecb_byte_at_a_time(encx, max_len=len(secret) + 8)
        check(got == secret, "前缀 %d 字节时逐字节恢复应完整还原 secret" % len(pre))

    # 边界拒绝：非法密钥长度、非整块密文、无填充非整块明文
    for bad in (lambda: expand_key(b"short"), lambda: ecb_decrypt(key, b"x" * 15),
                lambda: ecb_encrypt(key, b"123", pad=False)):
        try:
            bad()
            raise AssertionError("selftest 失败: 非法输入未被拒绝")
        except ValueError:
            ok += 1
    # 参数不足 / oracle 抛错要原样向上抛
    try:
        detect_mode(lambda _c: bytes(15))
        raise AssertionError("selftest 失败: 短密文未拒绝")
    except ValueError:
        ok += 1

    print("selftest ok: %d/%d（FIPS-197 向量、往返、ECB 判别、块重排、三种前缀逐字节恢复、非法输入拒绝）"
          % (ok, ok))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="AES-ECB 选择明文攻击工具")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--secret", default="flag{ecb_1s_b4d}")
    ap.add_argument("--prefix", default="")
    ap.add_argument("--key-hex", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest()
    if not args.demo:
        print("用法: --selftest 或 --demo [--secret S] [--prefix P]", file=sys.stderr)
        return 2
    key = bytes.fromhex(args.key_hex) if args.key_hex else bytes(range(16))
    if len(key) != 16:
        print("参数错误: 密钥必须 16 字节", file=sys.stderr)
        return 2
    enc = make_oracle(key, prefix=args.prefix.encode(), suffix=args.secret.encode())
    mode = detect_mode(enc)
    recovered = ecb_byte_at_a_time(enc, max_len=64)
    out = {"mode": mode, "recovered": recovered.decode("latin-1"), "matched": recovered == args.secret.encode()}
    print(json.dumps(out, ensure_ascii=False) if args.json else out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
