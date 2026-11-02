#!/usr/bin/env python3
"""哈希长度扩展（Length Extension）：在不知道 secret 的情况下伪造 md5/sha1(secret+msg) 签名。

依赖：只用标准库（struct、hashlib、math）。
用途：服务端用 md5(secret + data) 当签名（secret 前缀、无 HMAC），已知一对 (data, 签名) 且能猜到
      secret 长度时，可在 data 后追加 glue padding 与任意后缀，并算出对应的新签名，无需知道 secret。
      与 kb/crypto/hash-length-extension.md 配套；md5/sha1 的压缩函数在本文件里重新实现，
      不依赖 hashpump/hash_extender。

用法：
  python hash_length_extension.py --algo md5 --orig-data "user=guest" --orig-sig 3b0f... \
      --append "&admin=1" --secret-len 16
  python hash_length_extension.py --algo md5 --orig-data "user=guest" --orig-sig 3b0f... \
      --append "&admin=1" --secret-len-range 0-64 --json
  python hash_length_extension.py --selftest

输出：新数据的十六进制（含 glue padding，作为原始字节提交）与新签名。
限制：只适用于 Merkle–Damgård 且"输出状态 == 内部状态"的哈希（md5/sha1）；
      sha256/sha512 结构相同但本文未内置压缩函数，沿用 hashpump/hash_extender；
      sha3/blake2/HMAC 免疫此攻击；secret 长度需枚举，服务端校验通过即命中。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import sys

K_MD5 = [int(abs(math.sin(i + 1)) * 2 ** 32) & 0xFFFFFFFF for i in range(64)]
S_MD5 = [7, 12, 17, 22] * 4 + [5, 9, 14, 20] * 4 + [4, 11, 16, 23] * 4 + [6, 10, 15, 21] * 4

ALGOS = {
    "md5": {"digest": 16, "block": 64, "endian": "<"},
    "sha1": {"digest": 20, "block": 64, "endian": ">"},
}


def _rotl(x: int, n: int) -> int:
    x &= 0xFFFFFFFF
    return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF


def _md5_compress(state: tuple[int, ...], block: bytes) -> tuple[int, ...]:
    a, b, c, d = state
    m = struct.unpack("<16I", block)
    for i in range(64):
        if i < 16:
            f, g = (b & c) | (~b & d), i
        elif i < 32:
            f, g = (d & b) | (~d & c), (5 * i + 1) % 16
        elif i < 48:
            f, g = b ^ c ^ d, (3 * i + 5) % 16
        else:
            f, g = c ^ (b | (~d & 0xFFFFFFFF)), (7 * i) % 16
        f = (f + a + K_MD5[i] + m[g]) & 0xFFFFFFFF
        a, d, c = d, c, b
        b = (b + _rotl(f, S_MD5[i])) & 0xFFFFFFFF
    return tuple((x + y) & 0xFFFFFFFF for x, y in zip(state, (a, b, c, d)))


def _sha1_compress(state: tuple[int, ...], block: bytes) -> tuple[int, ...]:
    w = list(struct.unpack(">16I", block)) + [0] * 64
    for i in range(16, 80):
        w[i] = _rotl(w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16], 1)
    a, b, c, d, e = state
    for i in range(80):
        if i < 20:
            f, k = (b & c) | (~b & d), 0x5A827999
        elif i < 40:
            f, k = b ^ c ^ d, 0x6ED9EBA1
        elif i < 60:
            f, k = (b & c) | (b & d) | (c & d), 0x8F1BBCDC
        else:
            f, k = b ^ c ^ d, 0xCA62C1D6
        tmp = (_rotl(a, 5) + (f & 0xFFFFFFFF) + e + k + w[i]) & 0xFFFFFFFF
        a, b, c, d, e = tmp, a, _rotl(b, 30), c, d
    return tuple((x + y) & 0xFFFFFFFF for x, y in zip(state, (a, b, c, d, e)))


COMPRESS = {"md5": _md5_compress, "sha1": _sha1_compress}


def glue_padding(algo: str, msg_len: int) -> bytes:
    """原始消息（secret+data）长度 msg_len 时，其哈希前会补齐的 Merkle-Damgård padding。"""
    spec = ALGOS[algo]
    b = spec["block"]
    return b"\x80" + b"\x00" * ((56 - (msg_len + 1) % b) % b) + struct.pack(spec["endian"] + "Q", msg_len * 8)


def forge(algo: str, orig_data: bytes, orig_sig: bytes, append: bytes, secret_len: int) -> dict:
    """返回 {new_data, new_data_hex, new_sig}；new_data 即"原 data + glue + append"。"""
    if algo not in ALGOS:
        raise ValueError(f"不支持的算法：{algo}（支持 {', '.join(ALGOS)}）")
    spec = ALGOS[algo]
    if len(orig_sig) != spec["digest"]:
        raise ValueError(f"{algo} 摘要应为 {spec['digest']} 字节，实际 {len(orig_sig)}")
    total = secret_len + len(orig_data)
    glue = glue_padding(algo, total)
    new_data = orig_data + glue + append
    # 原始哈希 = H(secret+data)，其内部状态就是 orig_sig；从"已吃满 total+len(glue) 字节"继续喂 append
    state = struct.unpack(spec["endian"] + f"{spec['digest'] // 4}I", orig_sig)
    buf = append + glue_padding(algo, total + len(glue) + len(append))
    compress = COMPRESS[algo]
    b = spec["block"]
    assert len(buf) % b == 0, "对齐失败"
    for i in range(0, len(buf), b):
        state = compress(state, buf[i:i + b])
    new_sig = struct.pack(spec["endian"] + f"{spec['digest'] // 4}I", *state)
    return {"algo": algo, "secret_len": secret_len, "new_data": new_data,
            "new_data_hex": new_data.hex(), "new_sig": new_sig.hex()}


# ---------------------------------------------------------------- 自检

def selftest() -> int:
    checks = []
    secret = b"0123456789abcdef"
    data = b"user=guest"
    append = b"&admin=1"
    for algo in ("md5", "sha1"):
        sig = hashlib.new(algo, secret + data).digest()
        r = forge(algo, data, sig, append, len(secret))
        expect = hashlib.new(algo, secret + r["new_data"]).hexdigest()
        checks.append((f"{algo} 伪造签名可被 {algo}(secret+新data) 复现", r["new_sig"] == expect))
    # 猜错 secret 长度 → 服务端复核不通过
    sig = hashlib.md5(secret + data).digest()
    r = forge("md5", data, sig, append, len(secret) + 1)
    checks.append(("长度猜错不命中", r["new_sig"] != hashlib.md5(secret + r["new_data"]).hexdigest()))
    # 长度枚举 0-64 中恰有一个命中
    base_sig = hashlib.sha1(secret + data).digest()
    hits = []
    for n in range(0, 65):
        f = forge("sha1", data, base_sig, append, n)
        if f["new_sig"] == hashlib.sha1(secret + f["new_data"]).hexdigest():
            hits.append(n)
    checks.append(("长度枚举唯一命中", hits == [len(secret)]))
    # 摘要长度校验
    try:
        forge("md5", data, b"\x00" * 8, append, 16)
        checks.append(("短摘要报错", False))
    except ValueError:
        checks.append(("短摘要报错", True))
    # glue padding 都能把 (msg_len + len(glue)) 补齐到整块
    checks.append(("glue 对齐 64", all((n + len(glue_padding("md5", n))) % 64 == 0
                                       for n in range(70))))

    ok = sum(1 for _, v in checks if v)
    for name, v in checks:
        if not v:
            print(f"FAIL: {name}", file=sys.stderr)
    print(f"selftest ok: {ok}/{len(checks)}（" + "、".join(n for n, _ in checks) + "）")
    return 0 if ok == len(checks) else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="哈希长度扩展伪造（md5/sha1）")
    ap.add_argument("--algo", default="md5", choices=sorted(ALGOS))
    ap.add_argument("--orig-data", default="")
    ap.add_argument("--orig-sig", help="原签名十六进制")
    ap.add_argument("--append", default="")
    ap.add_argument("--secret-len", type=int)
    ap.add_argument("--secret-len-range", help="枚举 secret 长度，如 0-64")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.orig_sig:
        ap.error("需要 --orig-sig")
        return 2
    orig_data = args.orig_data.encode()
    orig_sig = bytes.fromhex(args.orig_sig.strip())
    append = args.append.encode()
    lens: list[int] = []
    if args.secret_len is not None:
        lens.append(args.secret_len)
    if args.secret_len_range:
        lo, hi = args.secret_len_range.split("-")
        lens.extend(range(int(lo), int(hi) + 1))
    if not lens:
        ap.error("需要 --secret-len 或 --secret-len-range")
        return 2
    results = [forge(args.algo, orig_data, orig_sig, append, n) for n in lens]
    if args.json:
        print(json.dumps([{k: v for k, v in r.items() if k != "new_data"} for r in results],
                         ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(f"secret_len={r['secret_len']}")
            print(f"  data(hex) = {r['new_data_hex']}")
            print(f"  sig       = {r['new_sig']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
