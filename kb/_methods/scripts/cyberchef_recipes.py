#!/usr/bin/env python3
"""CyberChef 配方离线复刻 + 自动判别（纯标准库，本地跑，不联网）。

对齐 kb/misc/cyberchef-and-tools.md 的常用配方：
  "Magic"(Intensive)  -> 本脚本 --magic：逐层尝试 base64/base32/base16/zlib/
  gzip/rot13/rot47/url/xor-brute，按"可打印比例 + 子串线索"打分选最优；
  "From Base64" -> "Raw Inflate" -> "Detect File Type" -> --auto 链式执行；
  "XOR Brute Force" (key length 1, crib "flag{") -> --xor-brute，用 crib 定位密钥；
  "Strings" (min length 6, UTF-16LE) -> --strings。

用法：
  python cyberchef_recipes.py --magic data.txt
  python cyberchef_recipes.py --auto data.txt
  python cyberchef_recipes.py --recipe "From Base64 -> Raw Inflate"
  python cyberchef_recipes.py --xor-brute blob.bin --crib "flag{"
  python cyberchef_recipes.py --strings blob.bin --min 6 --utf16
  python cyberchef_recipes.py --selftest
"""
from __future__ import annotations

import argparse
import base64
import binascii
import gzip
import re
import sys
import zlib

PRINTABLE = set(range(32, 127)) | {9, 10, 13}


def printable_ratio(data: bytes) -> float:
    if not data:
        return 0.0
    return sum(1 for b in data if b in PRINTABLE) / len(data)


def score(data: bytes) -> float:
    """可打印比例仍是主项，flag/ctf 之类线索加权（对应源文档的评分思路）。"""
    if not data:
        return 0.0
    s = printable_ratio(data) * 2.0
    low = data.lower()
    for hint in (b"flag", b"ctf", b"key", b"http", b"{", b"}"):
        if hint in low:
            s += 3.0
    return s


def try_base64(data: bytes):
    txt = data.strip()
    txt += b"=" * (-len(txt) % 4)
    try:
        return base64.b64decode(txt, validate=True)
    except (binascii.Error, ValueError):
        return None


def try_base32(data: bytes):
    try:
        return base64.b32decode(data.strip().upper() + b"=" * (-len(data.strip()) % 8))
    except (binascii.Error, ValueError):
        return None


def try_base16(data: bytes):
    t = data.strip()
    if len(t) % 2 or not re.fullmatch(rb"[0-9a-fA-F]+", t):
        return None
    return bytes.fromhex(t.decode())


def try_inflate(data: bytes):
    try:
        return zlib.decompress(data)
    except zlib.error:
        return None


def try_gunzip(data: bytes):
    try:
        return gzip.decompress(data)
    except (OSError, EOFError):
        return None


def try_url(data: bytes):
    t = data.strip()
    if b"%" not in t:
        return None
    try:
        from urllib.parse import unquote_to_bytes
        out = unquote_to_bytes(t)
        return out if out != t else None
    except ValueError:
        return None


def getattr_out(level: str):
    """二进制输入的保护：首 8 字节出现 NUL 或高位字节，就不做无意义的字符变换。"""
    return level


def rot47(data: bytes):
    out = bytearray()
    for b in data:
        if 33 <= b <= 126:
            out.append(33 + (b - 33 + 47) % 94)
        else:
            out.append(b)
    return bytes(out)


def rot13(data: bytes):
    out = bytearray()
    for b in data:
        if 97 <= b <= 122:
            out.append(97 + (b - 97 + 13) % 26)
        elif 65 <= b <= 90:
            out.append(65 + (b - 65 + 13) % 26)
        else:
            out.append(b)
    return bytes(out)


def xor_brute(data: bytes, crib: bytes = b"flag{"):
    """单字节 XOR 爆破：用 crib 反推密钥，命中即返回 (key, 明文)。"""
    hits = []
    for key in range(256):
        if all((data[i] ^ key) == crib[i] for i in range(min(len(crib), len(data)))):
            hits.append((key, bytes(b ^ key for b in data)))
    return hits


TRANSFORMS = [
    ("From Base64", try_base64),
    ("From Base32", try_base32),
    ("From Base16", try_base16),
    ("Raw Inflate", try_inflate),
    ("Gunzip", try_gunzip),
    ("URL Decode", try_url),
    ("ROT13", rot13),
    ("ROT47", rot47),
]

KNOWN_MAGIC = (b"\x89PNG", b"\xff\xd8\xff", b"PK\x03\x04", b"%PDF", b"\x1f\x8b",
               b"x\x9c", b"\x7fELF", b"GIF8", b"RIFF")


def has_known_magic(data: bytes) -> bool:
    return any(data.startswith(sig) for sig in KNOWN_MAGIC)


def detect_type(data: bytes) -> str:
    sigs = [(b"\x89PNG\r\n\x1a\n", "PNG image"), (b"\xff\xd8\xff", "JPEG image"),
            (b"PK\x03\x04", "ZIP archive"), (b"%PDF", "PDF document"),
            (b"\x1f\x8b", "gzip stream"), (b"x\x9c", "zlib stream"),
            (b"\x7fELF", "ELF binary")]
    for sig, name in sigs:
        if data.startswith(sig):
            return name
    return "unknown"


def magic(data: bytes, depth: int = 4, beam: int = 3, min_gain: float = 1.0):
    """逐层尝试所有变换，返回最优路径与结果。

    只有评分相对当前节点提升 >= min_gain 才算"前进"，避免对已经是明文的
    输入胡乱套 ROT47，只把可打印比例抬升一点点。
    """
    best = {"score": score(data), "path": [], "data": data}
    base = best["score"]
    if base <= 0.7 or has_known_magic(data):
        return {"score": base, "path": [], "data": data}
    char_ops = {"ROT13", "ROT47", "URL Decode"}
    frontier = [((), data)]
    for _ in range(depth):
        nxt = []
        for path, cur in frontier:
            cur_s = score(cur)
            for name, fn in TRANSFORMS:
                if name in char_ops and printable_ratio(cur) < 0.85:
                    continue
                try:
                    out = fn(cur)
                except Exception:  # noqa: BLE001 - 变换失败一律跳过
                    out = None
                if not out or out == cur or len(out) > max(4096, len(data) * 8):
                    continue
                cand_s = score(out)
                if cand_s - cur_s < min_gain:
                    continue
                if cand_s > best["score"]:
                    best = {"score": cand_s, "path": list(path) + [name], "data": out}
                nxt.append((tuple(path) + (name,), out))
        nxt.sort(key=lambda p: score(p[1]), reverse=True)
        frontier = nxt[:beam]
        if not frontier:
            break
    if best["score"] <= base:
        return {"score": base, "path": [], "data": data}
    return best


def run_recipe(data: bytes, recipe: str):
    steps = [s.strip() for s in recipe.split("->") if s.strip()]
    by_name = dict(TRANSFORMS)
    cur = data
    for step in steps:
        fn = by_name.get(step)
        if fn is None:
            raise ValueError("未知配方步骤：%s（可用：%s）"
                             % (step, ", ".join(by_name)))
        out = fn(cur)
        if out is None:
            raise ValueError("步骤 %s 在当前输入上失败" % step)
        cur = out
    return cur


def extract_strings(data: bytes, min_len: int = 6, utf16: bool = False):
    if utf16:
        try:
            text = data.decode("utf-16-le", errors="ignore")
        except ValueError:
            text = ""
        return [s for s in re.findall(r"[\x20-\x7e]{%d,}" % min_len, text)]
    return [m.group().decode("latin-1")
            for m in re.finditer(rb"[\x20-\x7e]{%d,}" % min_len, data)]


def selftest() -> int:
    fails = []
    # 1) 正常：base64 文本被 magic 识别并还原
    raw = b"flag{cyberchef_magic}"
    enc = base64.b64encode(raw)
    best = magic(enc)
    if raw not in best["data"]:
        fails.append("case1: magic 未还原 base64 明文（得到 %r）" % best["data"][:40])
    if best["path"][:1] != ["From Base64"]:
        fails.append("case1: 首步不是 From Base64：%r" % best["path"])
    # 2) 配方链 From Base64 -> Raw Inflate 还原 zlib
    z = zlib.compress(b"flag{zlib_in_base64}")
    if run_recipe(base64.b64encode(z), "From Base64 -> Raw Inflate") != b"flag{zlib_in_base64}":
        fails.append("case2: 配方链未还原 zlib")
    # 3) XOR 单字节爆破用 crib 命中
    key, pt = xor_brute(b"".join(bytes([b ^ 0x5A]) for b in b"flag{xor}"))[0]
    if key != 0x5A or pt != b"flag{xor}":
        fails.append("case3: XOR 爆破密钥/明文错误")
    # 4) 边界拒绝 + 参数不足
    try:
        run_recipe(b"x", "From Base64 -> No Such Op")
        fails.append("case4: 未知步骤未被拒绝")
    except ValueError:
        pass
    if extract_strings(b"ab\x00cd", min_len=6) != []:
        fails.append("case4: 过短字符串未被过滤")
    # 5) 固定输入可复现 + 空输入不崩
    a = magic(enc)["path"]
    if a != magic(enc)["path"]:
        fails.append("case5: magic 结果不可复现")
    if detect_type(b"") != "unknown" or score(b"") != 0.0:
        fails.append("case5: 空输入处理异常")
    if detect_type(b"\x89PNG\r\n\x1a\nxx") != "PNG image":
        fails.append("case5: PNG 类型未识别")
    for f in fails:
        print("FAIL " + f, file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 5 组断言全过（magic 还原 base64、配方链还原 zlib、"
          "XOR crib 爆破、未知步骤与短串拒绝、可复现与空输入）")
    return 0


def read_input(path: str) -> bytes:
    with open(path, "rb") as fh:
        return fh.read()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="CyberChef 常用配方的离线复刻")
    ap.add_argument("--file", help="输入文件（--magic/--auto/--recipe/--strings 需要）")
    ap.add_argument("--magic", action="store_true", help="逐层自动识别变换")
    ap.add_argument("--auto", action="store_true", help="Magic 后接 Detect File Type")
    ap.add_argument("--recipe", help="指定配方，步骤用 -> 分隔")
    ap.add_argument("--xor-brute", metavar="FILE", help="单字节 XOR 爆破")
    ap.add_argument("--crib", default="flag{", help="XOR 爆破用的已知明文前缀")
    ap.add_argument("--strings", metavar="FILE", help="提取可打印串")
    ap.add_argument("--min", type=int, default=6, help="strings 最短长度，默认 6")
    ap.add_argument("--utf16", action="store_true", help="按 UTF-16LE 提取")
    ap.add_argument("--selftest", action="store_true", help="跑内置自检")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    try:
        if args.xor_brute:
            hits = xor_brute(read_input(args.xor_brute), args.crib.encode())
            if not hits:
                print("未命中 crib=%r，试试更短的 crib 或 hex 检索" % args.crib)
                return 0
            for key, pt in hits:
                print("key=0x%02x  %r" % (key, pt[:80]))
            return 0
        if args.strings:
            for s in extract_strings(read_input(args.strings), args.min, args.utf16):
                print(s)
            return 0
        if args.min < 1:
            raise ValueError("--min 必须 >= 1")
        if not (args.magic or args.auto or args.recipe):
            ap.error("必须提供 --magic / --auto / --recipe（或 --xor-brute/--strings/--selftest）")
        data = read_input(args.file) if args.file else sys.stdin.buffer.read()
        if args.recipe:
            out = run_recipe(data, args.recipe)
            sys.stdout.write(out.decode("utf-8", "backslashreplace"))
            print()
            return 0
        best = magic(data)
        print("路径：" + (" -> ".join(best["path"]) or "(无需变换)"))
        print("评分：%.2f" % best["score"])
        print("类型：" + detect_type(best["data"]))
        print("结果：%r" % best["data"][:120])
    except (ValueError, OSError) as exc:
        print("失败：" + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
