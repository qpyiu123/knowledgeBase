#!/usr/bin/env python3
"""编码套娃层层解码：base64 / b32 / b85 / b16 / url / hex-escape / rot13 / unicode-escape。

依赖：只用标准库（base64、urllib.parse、codecs、re、json）。
用途：题面给一长串"看起来不像明文"的字符串时，按识别顺序逐层试解码，
      每一层打印"编码名 → 结果预览"，直到输出里出现 flag{ 之类的停止标志或没有可解的层。
      与 kb/misc/encoding-chain.md 配套（CyberChef Magic 的纯 Python 版）。

用法：
  python enc_chain_decode.py --data "ZmxhZ3t0ZXN0fQ=="
  python enc_chain_decode.py --file flag.txt --max-depth 8 --stop "flag{"
  python enc_chain_decode.py --file chain.bin --json
  python enc_chain_decode.py --selftest

限制：不处理图片/压缩包（解出非文本就停在上一层并提示 --raw-out）；
      不做凯撒/维吉尼亚等有噪音的分支搜索，只走"确定可逆"的编码。
"""
from __future__ import annotations

import argparse
import base64
import binascii
import codecs
import json
import re
import sys
import urllib.parse

MAX_SAFE_TEXT = 4096


def _is_printable(data: bytes) -> bool:
    if not data:
        return False
    text = data.decode("utf-8", errors="ignore")
    if not text:
        return False
    good = sum(1 for ch in text if ch.isprintable() or ch in "\r\n\t")
    return good / len(text) > 0.95


# ---------------------------------------------------------------- 单层解码器

B64_RE = re.compile(r"^[A-Za-z0-9+/]*={0,2}$")
B64URL_RE = re.compile(r"^[A-Za-z0-9_-]*={0,2}$")
B32_RE = re.compile(r"^[A-Z2-7]*={0,6}$", re.IGNORECASE)
HEX_RE = re.compile(r"^[0-9a-fA-F\s]+$")
ESCAPE_RE = re.compile(r"(\\x[0-9a-fA-F]{2}|\\u[0-9a-fA-F]{4}|%[0-9a-fA-F]{2})")
ROT13_RE = re.compile(r"^[A-Za-z\s.,!?'\-]+$")


def _b64(text: str) -> bytes:
    t = text.strip()
    if len(t) % 4:
        t += "=" * (-len(t) % 4)
    return base64.b64decode(t, validate=True)


def _b64url(text: str) -> bytes:
    t = text.strip()
    if len(t) % 4:
        t += "=" * (-len(t) % 4)
    return base64.urlsafe_b64decode(t)


def _b32(text: str) -> bytes:
    t = text.strip().upper()
    if len(t) % 8:
        t += "=" * (-len(t) % 8)
    return base64.b32decode(t)


def _b85(text: str) -> bytes:
    return base64.b85decode(text.strip().encode("ascii"))


def _hex(text: str) -> bytes:
    return binascii.unhexlify(re.sub(r"\s+", "", text))


def _url(text: str) -> bytes:
    return urllib.parse.unquote_to_bytes(text.strip())


def _utf8_salvage(raw: bytes) -> bytes:
    """把 URL 按字节解开后若含 UTF-8 多字节序列，按 utf-8 重新落地，避免乱码。"""
    try:
        return raw.decode("utf-8").encode("utf-8")
    except UnicodeDecodeError:
        return raw


def _escape(text: str) -> bytes:
    # \xNN: latin-1 语义；\uNNNN: 走 unicode_escape
    if re.search(r"\\u[0-9a-fA-F]{4}", text):
        return text.strip().encode("ascii", "backslashreplace").decode("unicode_escape").encode("utf-8")
    body = re.sub(r"%([0-9a-fA-F]{2})", lambda m: "\\x" + m.group(1), text.strip())
    return _utf8_salvage(body.encode("ascii", "backslashreplace").decode("unicode_escape").encode("latin-1"))


def _rot13(text: str) -> bytes:
    return codecs.decode(text.strip(), "rot13").encode("utf-8")


def _only_hex(s: str) -> bool:
    return bool(s) and bool(re.fullmatch(r"[0-9a-fA-F]+", s))


def _looks_b64(s: str) -> bool:
    if not _only_b64(s):
        return False
    # 全 hex 且有数字的短串更像 hex/base16，让 hex 解码器优先
    if _only_hex(s) and any(c.isdigit() for c in s):
        return False
    return True


def _only_b64(s: str) -> bool:
    return len(s) >= 8 and len(s) % 4 in (0, 2, 3) and bool(B64_RE.match(s)) \
        and any(c.isupper() for c in s) and any(c.islower() for c in s)


def _looks_b32(s: str) -> bool:
    up = s.upper()
    return len(up) >= 16 and len(up) % 8 in (0, 2, 4, 5, 7) and bool(B32_RE.match(up)) \
        and len(up.rstrip("=")) % 8 in (0, 2, 4, 5, 7) and not _only_hex(s)


# 顺序 = 优先级：越"专一"的格式越先试
# 顶层（第一层）检测顺序：%xx 先按 URL 处理（URL 语义最强），\x/\u 转义次之
TOP_DETECTORS = [
    ("url", lambda s: "%" in s, _url),
    ("escape", lambda s: bool(ESCAPE_RE.search(s)), _escape),
]

DETECTORS = [
    ("escape", lambda s: bool(ESCAPE_RE.search(s)), _escape),
    ("url", lambda s: "%" in s, _url),
    ("hex", lambda s: bool(HEX_RE.match(s)) and len(re.sub(r"\s+", "", s)) % 2 == 0
     and len(re.sub(r"\s+", "", s)) >= 4, _hex),
    ("base64", _looks_b64, _b64),
    ("base64url", lambda s: len(s) >= 8 and ("-" in s or "_" in s) and bool(B64URL_RE.match(s)), _b64url),
    ("base32", _looks_b32, _b32),
    ("base85", lambda s: len(s) >= 8 and any(c in s for c in "<>#~"), _b85),
]
# rot13 不保真（普通英文单词也会被"解"成别的词），只在显式开启时作为最后一层尝试
ROT13_RE = re.compile(r"^[A-Za-z0-9\s.,!?';:\-{}\[\]]+$")
ROT13_DETECTOR = ("rot13", lambda s: bool(ROT13_RE.match(s)) and any(c.isalpha() for c in s), _rot13)


def detect_layer(text: str, allow_rot13: bool = False,
                 top_level: bool = False) -> tuple[str, bytes] | None:
    """返回第一个"能解且解出可打印文本"的 (编码名, 结果)；不可打印的二进制也返回（标记 raw）。"""
    stripped = text.strip()
    if not stripped:
        return None
    detectors = (TOP_DETECTORS + DETECTORS if top_level else DETECTORS)
    if allow_rot13:
        detectors = detectors + [ROT13_DETECTOR]
    for name, cond, fn in detectors:
        try:
            if not cond(stripped):
                continue
            out = fn(stripped)
        except Exception:
            continue
        if not out or out.strip() == stripped.encode("utf-8", "ignore").strip():
            continue
        if _is_printable(out):
            return name, out
        if name in ("base64", "base64url", "base64", "base32", "base85", "hex"):
            return name, out
    return None


def decode_chain(text: str, max_depth: int = 8, stop: str = "flag{",
                 allow_rot13: bool = False) -> dict:
    steps: list[dict] = []
    cur = text.strip()
    hit_stop = ""
    while len(steps) < max_depth:
        if stop and stop.lower() in cur.lower():
            hit_stop = stop
            break
        layer = detect_layer(cur, allow_rot13, top_level=not steps)
        if layer is None:
            break
        name, raw = layer
        try:
            nxt = raw.decode("utf-8")
        except UnicodeDecodeError:
            steps.append({"encoding": name, "result": None, "binary": True,
                          "len": len(raw), "hex_head": raw[:24].hex()})
            break
        steps.append({"encoding": name, "result": nxt[:MAX_SAFE_TEXT], "binary": False,
                      "len": len(nxt)})
        if nxt.strip() == cur:
            break  # 原地循环
        cur = nxt.strip()
        if name == "rot13" and allow_rot13:
            break  # rot13 只解一层（两次即还原）
        if not _is_printable(raw):
            break
    if stop and stop.lower() in cur.lower():
        hit_stop = stop
    return {"input_len": len(text), "steps": steps, "final": cur[:MAX_SAFE_TEXT],
            "stop_hit": hit_stop, "depth": len(steps)}


# ---------------------------------------------------------------- 自检

def selftest() -> int:
    checks = []
    # 1. 单层 base64
    r = decode_chain("ZmxhZ3tzZWxmdGVzdH0=", stop="flag{")
    checks.append(("单层 base64", r["final"] == "flag{selftest}" and r["depth"] == 1))
    # 2. 双层：hex(base64(flag))
    inner = base64.b64encode(b"flag{layer2}").decode()
    outer = inner.encode().hex()
    r = decode_chain(outer, stop="flag{")
    names = [s["encoding"] for s in r["steps"]]
    checks.append(("两层 hex→base64", names[:2] == ["hex", "base64"] and r["final"] == "flag{layer2}"))
    # 3. url 编码
    r = decode_chain("flag%7Bweb%7D", stop="flag{")
    checks.append(("url 解码", r["final"] == "flag{web}" and r["steps"][0]["encoding"] == "url"))
    r = decode_chain("%66%6C%61%67%7Bu%7D", stop="flag{")
    checks.append(("%xx 二字节 url", r["final"] == "flag{u}" and r["steps"][0]["encoding"] == "url"))
    # 4. \x 转义
    r = decode_chain(r"\x66\x6c\x61\x67\x7bhex\x7d", stop="flag{")
    checks.append(("\\x 转义", r["final"] == "flag{hex}"))
    # 5. rot13（默认关闭；开启后能解，且默认不误判普通英文）
    r = decode_chain("syn{cevag}", stop="flag", allow_rot13=True)
    checks.append(("rot13 显式开启", r["final"] == "fla{print}" and r["depth"] == 1))
    r = decode_chain("hello world", stop="flag{")
    checks.append(("默认不误判英文", r["depth"] == 0))
    # 6. 深度上限
    deep = base64.b64encode(b"flag{deep}").decode()
    for _ in range(3):
        deep = base64.b64encode(deep.encode()).decode()
    r = decode_chain(deep, max_depth=2, stop="flag{")
    checks.append(("深度上限", r["depth"] == 2 and not r["stop_hit"]))
    # 7. 无编码原文
    r = decode_chain("flag{plain}", stop="flag{")
    checks.append(("原文直接命中", r["depth"] == 0 and r["stop_hit"] == "flag{"))

    ok = sum(1 for _, v in checks if v)
    for name, v in checks:
        if not v:
            print(f"FAIL: {name}", file=sys.stderr)
    print(f"selftest ok: {ok}/{len(checks)}（"
          + "、".join(n for n, _ in checks) + "）")
    return 0 if ok == len(checks) else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="编码套娃逐层解码")
    ap.add_argument("--data", help="直接给字符串")
    ap.add_argument("--file", help="从文件读取")
    ap.add_argument("--max-depth", type=int, default=8)
    ap.add_argument("--stop", default="flag{", help="出现该子串即停止（给空串关闭）")
    ap.add_argument("--allow-rot13", action="store_true", help="允许 rot13 作为最后一层（可能误报）")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.file:
        text = open(args.file, "rb").read().decode("utf-8", errors="replace")
    elif args.data:
        text = args.data
    else:
        ap.error("需要 --data 或 --file")
        return 2

    result = decode_chain(text, args.max_depth, args.stop, args.allow_rot13)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for i, s in enumerate(result["steps"], 1):
            if s.get("binary"):
                print(f"[{i}] {s['encoding']}: 二进制 {s['len']} 字节 head={s['hex_head']}")
            else:
                print(f"[{i}] {s['encoding']}: {s['result'][:120]}")
        print(f"final: {result['final'][:200]}")
        if result["stop_hit"]:
            print(f"stop: 命中 {result['stop_hit']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
