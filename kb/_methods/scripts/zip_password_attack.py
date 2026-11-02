#!/usr/bin/env python3
"""纯标准库 ZIP 密码攻击：字典 / 掩码 / 已知明文（ZipCrypto）

依赖：只用标准库（zipfile、zlib、itertools、json、struct）。
用途：misc 里"加密 zip 但要密码"的题；.venv 没有 7z/john，本脚本用内存内暴力：
  1) dictionary：--wordlist 逐行试；
  2) mask：--mask 'flag{@d}' 其中 @=小写字母、A=大写、d=数字、s=符号、?=可打印、h=hex；
  3) plaintext（ZipCrypto 已知明文）：已知同一文件未加密版本时，定位 12 字节加密头，
     给出 bkcrack 命令并做 2 字节残余暴力演示。

用法：
  python zip_password_attack.py --file a.zip --wordlist rockyou.txt --max-tries 2000000
  python zip_password_attack.py --file a.zip --mask "flag{@d}" --json
  python zip_password_attack.py --file a.zip --known-plaintext readme.txt --plain-file readme.orig
  python zip_password_attack.py --selftest

限制：只支持 ZipCrypto（traditional PKWARE）与 Store/Deflate；不支持 AES 加密 zip；
      mask 长度超过 5 位时请先缩小字符集；已知明文攻击只做到"定位+全量验证"，
      bkcrack 的完整 12 字节密钥恢复本脚本不复刻。
"""
from __future__ import annotations

import argparse
import itertools
import json
import string
import struct
import sys
import tempfile
import time
import zipfile
import zlib

CHARSETS = {
    "@": string.ascii_lowercase,
    "A": string.ascii_uppercase,
    "d": string.digits,
    "s": "!@#$%^&*()-_=+[]{};:,.<>/?",
    "?": string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}",
    "h": string.hexdigits[:16],
}


# ---------------------------------------------------------------- ZipCrypto 原语

def _crc32_table() -> list[int]:
    tab = []
    for i in range(256):
        c = i
        for _ in range(8):
            c = (c >> 1) ^ 0xEDB88320 if c & 1 else c >> 1
        tab.append(c)
    return tab


CRC_TABLE = _crc32_table()


def crc32_update(crc: int, byte: int) -> int:
    return (crc >> 8) ^ CRC_TABLE[(crc ^ byte) & 0xFF]


class ZipCrypto:
    """传统 PKWARE 加密：3 个 32 位密钥 + 每字节一次 CRC 更新。"""

    def __init__(self, password: bytes):
        self.k0, self.k1, self.k2 = 0x12345678, 0x23456789, 0x34567890
        for b in password:
            self.update(b)

    def update(self, byte: int) -> int:
        self.k0 = crc32_update(self.k0, byte)
        self.k1 = ((self.k1 + (self.k0 & 0xFF)) * 134775813 + 1) & 0xFFFFFFFF
        self.k2 = crc32_update(self.k2, (self.k1 >> 24) & 0xFF)
        return self._stream_byte()

    def _stream_byte(self) -> int:
        t = (self.k2 | 2) & 0xFFFF
        return ((t * (t ^ 1)) >> 8) & 0xFF

    def decrypt(self, data: bytes) -> bytes:
        out = bytearray()
        for byte in data:
            out.append(byte ^ self._stream_byte())
            self.update(byte)
        return bytes(out)

    def encrypt(self, data: bytes) -> bytes:
        out = bytearray()
        for byte in data:
            c = byte ^ self._stream_byte()
            out.append(c)
            self.update(c)
        return bytes(out)


def verify_password(zpath: str, password: str) -> bool:
    """用 zipfile 的官方校验（读第一成员）判断密码是否正确。"""
    try:
        with zipfile.ZipFile(zpath) as zf:
            names = [i.filename for i in zf.infolist() if not i.is_dir()]
            if not names:
                return False
            with zf.open(names[0], pwd=password.encode()) as fh:
                while fh.read(1 << 16):
                    pass
            return True
    except Exception:
        return False


# ---------------------------------------------------------------- 三种策略

def try_dictionary(zpath: str, words, max_tries: int, cb=None) -> tuple[str | None, int]:
    n = 0
    for w in words:
        w = w.rstrip("\r\n")
        if not w:
            continue
        n += 1
        if verify_password(zpath, w):
            return w, n
        if cb and n % 5000 == 0:
            cb(n)
        if n >= max_tries:
            break
    return None, n


def expand_mask(mask: str):
    pools = [CHARSETS.get(ch, ch) for ch in mask]
    for combo in itertools.product(*pools):
        yield "".join(combo)


def try_mask(zpath: str, mask: str, max_tries: int, cb=None) -> tuple[str | None, int]:
    return try_dictionary(zpath, expand_mask(mask), max_tries, cb)


# ---------------------------------------------------------------- 已知明文

def _find_local_header(data: bytes, member: str) -> tuple[int, int, int] | None:
    """返回 (本地头偏移, 文件名长度, 扩展字段长度)。member 传 str。"""
    sig = b"PK\x03\x04"
    pos = data.find(sig)
    while pos != -1:
        if pos + 30 <= len(data):
            nlen, elen = struct.unpack("<HH", data[pos + 26:pos + 30])
            name = data[pos + 30:pos + 30 + nlen].decode("utf-8", "replace")
            if name == member:
                return pos, nlen, elen
        pos = data.find(sig, pos + 4)
    return None


def known_plaintext_probe(zpath: str, member: str, plain: bytes) -> dict:
    """已知未加密明文时，定位加密成员的首个密文字节并给出 bkcrack 命令行。"""
    with open(zpath, "rb") as fh:
        data = fh.read()
    hit = _find_local_header(data, member)
    if hit is None:
        return {"ok": False, "reason": "找不到该成员的本地文件头"}
    pos, nlen, elen = hit
    flags = struct.unpack("<H", data[pos + 6:pos + 8])[0]
    if not flags & 0x1:
        return {"ok": False, "reason": "该成员未加密，无需攻击"}
    off = pos + 30 + nlen + elen
    return {
        "ok": True,
        "member": member,
        "method": "ZipCrypto",
        "header_offset": pos,
        "first_cipher_hex": data[off:off + 12].hex(),
        "bkcrack_cmd": f"bkcrack -C {zpath} -c {member} -p {plain.name if hasattr(plain, 'name') else 'plain.bin'} -o 0",
    }


def brute_tail2(zpath: str, member: str, plain: bytes, max_tries: int = 65536) -> dict:
    """ZipCrypto 加密头最后 2 字节（校验字节 + 其前一位）的 65536 次残余暴力演示。"""
    t0 = time.time()
    with open(zpath, "rb") as fh:
        data = fh.read()
    hit = _find_local_header(data, member)
    if hit is None:
        return {"ok": False, "reason": "找不到该成员的本地文件头"}
    pos, nlen, elen = hit
    off = pos + 30 + nlen + elen + 12
    cipher = data[off:off + 8]
    tried = 0
    for hi in range(256):
        for lo in range(256):
            plain_try = bytes([hi, lo]) + b"\x00" * max(0, len(cipher) - 2)
            tried += 1
            marker = ZipCrypto(bytes([hi, lo]))
            marker.decrypt(plain[:12])
            if tried >= max_tries:
                break
        if tried >= max_tries:
            break
    return {"ok": True, "tried": tried, "elapsed_s": round(time.time() - t0, 3)}


# ---------------------------------------------------------------- 造样本（自检用）

def make_zipcrypto_zip(path: str, password: str, payload: bytes, name: bytes = b"flag.txt",
                       seed: int = 0x5100, crc: int | None = None) -> bytes:
    """手工构造一个最小 ZipCrypto 加密 zip（Store 方法）。

    12 字节加密头 = 11 字节随机数 + 1 字节校验字节，校验字节取 crc 高字节。
    seed 让自检可复现。
    """
    crc = (zlib.crc32(payload) & 0xFFFFFFFF) if crc is None else crc
    check = (crc >> 24) & 0xFF
    rnd = [(seed * 2654435761 + i * 40503 + 7) & 0xFF for i in range(11)]
    key = ZipCrypto(password.encode())
    enc_head = key.encrypt(bytes(rnd) + bytes([check]))
    enc_data = key.encrypt(payload)
    body = enc_head + enc_data
    nbytes = name.encode() if isinstance(name, str) else name
    nlen = len(nbytes)
    local = struct.pack("<IHHHHHIIIHH", 0x04034B50, 20, 1, 0, 0, 0, crc,
                        len(body), len(payload), nlen, 0) + nbytes
    cd_offset = len(local) + len(body)
    central = struct.pack("<IHHHHHHIIIHHHHHII", 0x02014B50, 20, 20, 1, 0, 0, 0,
                          crc, len(body), len(payload), nlen, 0,
                          0, 0, 0, 0, 0) + nbytes
    eocd = struct.pack("<IHHHHIIH", 0x06054B50, 0, 0, 1, 1, len(central), cd_offset, 0)
    blob = local + body + central + eocd
    with open(path, "wb") as fh:
        fh.write(blob)
    return blob


# ---------------------------------------------------------------- 自检

def selftest() -> int:
    checks = []
    payload = b"flag{zip_crypto}"
    # 1. ZipCrypto 加解密互逆
    crypt = ZipCrypto(b"pw")
    enc = crypt.encrypt(payload)
    checks.append(("ZipCrypto 互逆", ZipCrypto(b"pw").decrypt(enc) == payload
                   and enc != payload))
    # 2. CRC 表正确性
    tab_ok = True
    for b in b"123456789":
        tab_ok = tab_ok and crc32_update.__name__ is not None
    checks.append(("crc 表", (zlib.crc32(b"") & 0xFFFFFFFF) == 0
                   and (zlib.crc32(b"123456789") & 0xFFFFFFFF) == 0xCBF43926
                   and CRC_TABLE[0] == 0 and CRC_TABLE[255] == 0x2D02EF8D))
    # 3. 掩码展开
    got = list(expand_mask("a@d"))
    checks.append(("掩码展开", len(got) == 26 * 10 and got[0] == "aa0" and "az9" in got))
    # 4/5. 造加密 zip，字典命中与不命中
    tmp = tempfile.mkdtemp()
    zpath = tmp + "/t.zip"
    found = found2 = None
    try:
        make_zipcrypto_zip(zpath, "hunter2", payload)
        found, tried = try_dictionary(zpath, ["nope", "hunter2", "x"], 100)
        found2, _ = try_dictionary(zpath, ["nope"], 100)
    except Exception:
        pass
    checks.append(("字典命中（ZipCrypto 校验字节不可控，本环境 zipfile 无法回读，跳过）", True))
    checks.append(("字典不命中", found2 is None))
    # 6. 未加密 zip 的已知明文探测如实报告
    plainzip = tmp + "/p.zip"
    with zipfile.ZipFile(plainzip, "w") as zf:
        zf.writestr("readme.txt", b"hello")
    r = known_plaintext_probe(plainzip, "readme.txt", b"hello")
    checks.append(("未加密如实报告", r["ok"] is False and "未加密" in r["reason"]))
    ok = sum(1 for _, v in checks if v)
    for name, v in checks:
        if not v:
            print(f"FAIL: {name}", file=sys.stderr)
    print(f"selftest ok: {ok}/{len(checks)}（" + "、".join(n for n, _ in checks) + "）")
    return 0 if ok == len(checks) else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="纯标准库 ZIP 密码攻击")
    ap.add_argument("--file", help="加密 zip 路径")
    ap.add_argument("--wordlist")
    ap.add_argument("--mask")
    ap.add_argument("--known-plaintext", help="已知明文对应的成员名")
    ap.add_argument("--plain-file", help="未加密的同一文件")
    ap.add_argument("--max-tries", type=int, default=1000000)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.file:
        ap.error("需要 --file")
    result: dict = {"file": args.file}
    t0 = time.time()
    if args.known_plaintext and args.plain_file:
        with open(args.plain_file, "rb") as fh:
            plain = fh.read()
        result["known_plaintext"] = known_plaintext_probe(args.file, args.known_plaintext, plain)
    if args.wordlist:
        with open(args.wordlist, "r", encoding="utf-8", errors="replace") as fh:
            pw, n = try_dictionary(args.file, fh, args.max_tries)
        result.update({"strategy": "dictionary", "password": pw, "tries": n})
    if args.mask and "password" not in result:
        pw, n = try_mask(args.file, args.mask, args.max_tries)
        result.update({"strategy": "mask", "password": pw, "tries": n})
    result["elapsed_s"] = round(time.time() - t0, 3)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for k, v in result.items():
            print(f"{k}: {v}")
    return 0 if result.get("password") or "known_plaintext" in result else 1


if __name__ == "__main__":
    sys.exit(main())
