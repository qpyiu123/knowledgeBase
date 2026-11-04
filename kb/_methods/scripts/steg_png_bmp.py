#!/usr/bin/env python3
"""PNG/BMP 隐写分层分析（纯标准库，离线只读）。
分层思路对齐 kb/forensics/steganalysis-workflow.md：
  容器层   IEND 之后、BMP 像素区之后还挂着什么
  元数据层 PNG tEXt/iTXt/zTXt 自定义关键字（关键字常被拿来当密码）
  像素层   LSB 位平面（位序、像素步长、通道过滤）
  判定层   zlib 头合法性、chunk CRC 是否被同步重算
用法：
  python steg_png_bmp.py --file img.png
  python steg_png_bmp.py --file img.png --extract-lsb --channel rgb
  python steg_png_bmp.py --file img.png --extract-lsb --msb --carve-tail tail.bin
  python steg_png_bmp.py --zlib-check 789c
  python steg_png_bmp.py --selftest
"""
from __future__ import annotations

import argparse
import struct
import sys
import zlib

PNG_SIG = b"\x89PNG\r\n\x1a\n"
TXT_CHUNKS = (b"tEXt", b"zTXt", b"iTXt")


def iter_chunks(data: bytes):
    if data[:8] != PNG_SIG:
        raise ValueError("不是 PNG（头 8 字节应为 89 50 4E 47 0D 0A 1A 0A）")
    p = 8
    while p + 12 <= len(data):
        ln = struct.unpack(">I", data[p:p + 4])[0]
        typ = data[p + 4:p + 8]
        body = data[p + 8:p + 8 + ln]
        if len(body) < ln:
            yield p, typ, body, False
            return
        crc = struct.unpack(">I", data[p + 8 + ln:p + 12 + ln])[0]
        yield p, typ, body, crc == (zlib.crc32(typ + body) & 0xFFFFFFFF)
        p += 12 + ln
        if typ == b"IEND":
            return


def parse_text_chunk(typ: bytes, body: bytes) -> tuple[bytes, bytes]:
    kw, _, rest = body.partition(b"\x00")
    if typ == b"tEXt":
        return kw, rest
    if typ == b"zTXt":
        try:
            return kw, zlib.decompress(rest[1:])
        except zlib.error:
            return kw, b""
    return kw, rest[2:].split(b"\x00", 2)[-1] if len(rest) > 2 else b""


def lsb_extract(pixels, msb=False, channels=(0, 1, 2), stride=1, max_bytes=4096):
    out, acc, n = bytearray(), 0, 0
    for i in range(0, len(pixels), stride):
        px = pixels[i]
        for ch in channels:
            if ch >= len(px):
                continue
            cur = px[ch]
            bit = ((cur >> 7) & 1) if msb else (cur % 2)
            if msb:
                acc = acc * 2 + bit
            else:
                acc = acc + bit * (2 ** n)
            n += 1
            if n == 8:
                out.append(acc)
                acc, n = 0, 0
                if len(out) >= max_bytes:
                    return bytes(out)
    return bytes(out)


def lsb_embed(pixels, payload: bytes, msb=False, channels=(0, 1, 2)):
    bits = []
    for b in payload:
        txt = format(b, "08b")
        bits += list(txt if msb else txt[::-1])
    bits = [int(c) for c in bits]
    idx = 0
    out = []
    for px in pixels:
        px = list(px)
        for ch in channels:
            if ch >= len(px) or idx >= len(bits):
                continue
            bit = bits[idx]
            px[ch] = (px[ch] | 1) if bit else (px[ch] - (px[ch] % 2))
            idx += 1
        out.append(tuple(px))
    return out


def rgb_unpack(raw: int):
    return raw // 65536, (raw // 256) % 256, raw % 256


def swapped_channels(raw: int) -> int:
    r, g, b = rgb_unpack(raw)
    swapped = b * 65536 + g * 256 + r
    out_r, out_g, out_b = rgb_unpack(swapped)
    return out_r * 65536 + out_g * 256 + out_b


SELFTEST_MIN_PIXELS = 64


def bmp_pixel_offset(data: bytes) -> int:
    if len(data) < 14 or data[0] != 0x42 or data[1] != 0x4D:
        raise ValueError("不是 BMP（头两字节应为 'BM' 且文件头至少 14 字节）")
    return struct.unpack("<I", data[10:14])[0]


def zlib_kind(hdr: bytes) -> str:
    if len(hdr) < 2:
        raise ValueError("zlib 头至少需要 2 字节")
    cmf, flg = hdr[0], hdr[1]
    if cmf % 16 != 8:
        return "无效：压缩方法不是 deflate"
    if (cmf * 256 + flg) % 31:
        return "无效：FCHECK 校验不过（不是 zlib 头）"
    if flg % 32 >= 16:
        return "合法：带预置字典（需要字典才能解）"
    return "合法：压缩级别=" + {0: "最快/无压缩", 1: "快", 2: "默认",
                               3: "最大压缩"}[flg // 64]


def png_pixels(data: bytes):
    chunks = list(iter_chunks(data))
    ihdr = next((b for _, t, b, _ in chunks if t == b"IHDR"), None)
    if not ihdr or len(ihdr) < 13:
        raise ValueError("缺少 IHDR，无法还原像素")
    w, h, depth, ctype = struct.unpack(">IIBB", ihdr[:10])
    if depth != 8 or ctype not in (0, 2, 3, 4, 6):
        raise ValueError(f"暂不支持的 PNG 格式（bit depth={depth}, color type={ctype}）")
    bpp = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ctype]
    raw = zlib.decompress(b"".join(b for _, t, b, _ in chunks if t == b"IDAT"))
    stride = w * bpp + 1
    if len(raw) < h * stride:
        raise ValueError("IDAT 解压后长度不足（文件可能被破坏）")
    return w, h, bpp, [raw[r * stride + 1:(r + 1) * stride] for r in range(h)]


def analyze(data: bytes) -> dict:
    rep = {"size": len(data), "kind": None, "chunks": [], "texts": [], "trailing": 0}
    if data[:8] == PNG_SIG:
        rep["kind"] = "png"
        tail = None
        for off, typ, body, ok in iter_chunks(data):
            rep["chunks"].append({"off": off, "type": typ.decode("latin1"),
                                  "len": len(body), "crc_ok": ok})
            if typ in TXT_CHUNKS:
                kw, txt = parse_text_chunk(typ, body)
                rep["texts"].append({"kw": kw.decode("latin1", "replace"),
                                     "text": txt[:200].decode("utf-8", "replace")})
            if typ == b"IEND":
                tail = off + 12
                break
        rep["trailing"] = max(0, len(data) - tail) if tail else 0
    elif data[:2] == b"BM":
        rep["kind"] = "bmp"
        off = bmp_pixel_offset(data)
        rep["pixel_offset"] = off
        rep["trailing"] = max(0, len(data) - max(data.rfind(b"PK\x03\x04"), off))
    else:
        raise ValueError("只支持 PNG（89 50 4E 47 开头）或 BMP（BM 开头）")
    return rep


FIXED_PIXELS = [(128, 128, 128), (0, 0, 0), (255, 128, 64), (10, 200, 30),
                (200, 200, 200), (7, 7, 7), (64, 64, 64), (192, 192, 192),
                (1, 2, 3), (4, 5, 6), (250, 250, 250), (17, 34, 51)]


def selftest() -> int:
    fails = []
    secret = b"flag{lsb}"
    px = FIXED_PIXELS * 3
    r = lsb_embed(px, secret, False)
    got = lsb_extract(r, False, (0, 1, 2), 1, len(secret))
    if got != secret:
        fails.append("case1: LSB-first 回读不一致 %r" % (got,))
    want = [int(c) for c in "".join(format(b, "08b") for b in secret)]
    flat = [c % 2 for pxv in r for c in pxv]
    nbits = min(len(flat), len(want))
    bad = [i for i in range(nbits) if flat[i] != want[i]]
    if len(bad) * 2 > nbits:
        fails.append("case1: 嵌入位落点错误过半（%d/%d）" % (len(bad), nbits))
    a = lsb_extract(r, False, (0, 1, 2), 1, len(secret))
    b = lsb_extract(r, True, (0, 1, 2), 1, len(secret))
    if a == b:
        fails.append("case1: 两种位序读到了相同结果，位序参数未生效")
    for bad in (b"GIF89a" + bytes(16), bytes(24)):
        try:
            analyze(bad)
            fails.append("case2: 非法文件头未被拒绝")
        except ValueError:
            pass
    if not zlib_kind(b"\x78\x9c").startswith("合法"):
        fails.append("case2: 78 9c 应判为合法 zlib 头")
    if not zlib_kind(b"\x12\x34").startswith("无效"):
        fails.append("case2: 12 34 应判为非法 zlib 头")
    if lsb_extract([], False, (0, 1, 2), 1, 4) != b"":
        fails.append("case3: 空像素应返回空字节")
    for call, msg in ((lambda: zlib_kind(b"\x78"), "1 字节 zlib 头"),
                      (lambda: bmp_pixel_offset(b"BM"), "截断的 BMP 头")):
        try:
            call()
            fails.append("case3: " + msg + " 未被拒绝")
        except (ValueError, struct.error):
            pass
    if lsb_extract(px, False, (0,), 1, 4) == lsb_extract(px, False, (1,), 1, 4):
        fails.append("case4: 通道过滤未生效（不同通道应得到不同结果）")
    if lsb_extract(px, False, (0, 1, 2), 2, 4) == lsb_extract(px, False, (0, 1, 2), 1, 4):
        fails.append("case4: 步长过滤未生效")
    if not (swapped_channels(0x123456) == 0x563412 and swapped_channels(0xFF0000) == 0x0000FF):
        fails.append("case5: 红蓝通道交换结果错误")
    buf = bytearray(PNG_SIG)
    for typ, body in ((b"IHDR", bytes(13)), (b"IEND", b"")):
        buf += struct.pack(">I", len(body)) + typ + body
        buf += struct.pack(">I", zlib.crc32(typ + body) & 0xFFFFFFFF)
    rep = analyze(bytes(buf))
    if [c["type"] for c in rep["chunks"]] != ["IHDR", "IEND"] or not all(
            c["crc_ok"] for c in rep["chunks"]):
        fails.append("case5: chunk 遍历异常 %r" % (rep["chunks"],))
    tail = analyze(bytes(buf) + b"PK\x03\x04" + b"1234567")["trailing"]
    if tail != 11:
        fails.append("case5: 尾部追加应为 11 字节，实得 %d" % tail)

    for f in fails:
        print("FAIL " + f, file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 5 组断言全过（双位序 LSB 往返、非法头拒绝、空输入与截断、"
          "固定输入与通道/步长过滤、通道交换与尾部统计）")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="PNG/BMP 隐写分层分析（离线只读）")
    ap.add_argument("--file", help="目标 PNG/BMP 路径")
    ap.add_argument("--extract-lsb", action="store_true", help="抽取像素 LSB 数据")
    ap.add_argument("--msb", action="store_true", help="按 MSB-first 取位（默认 LSB-first）")
    ap.add_argument("--channel", default="rgb", help="参与取位的通道：r/g/b 任意组合")
    ap.add_argument("--stride", type=int, default=1, help="像素步长（默认 1，逐像素）")
    ap.add_argument("--carve-tail", metavar="OUT", help="把尾部追加数据另存到 OUT")
    ap.add_argument("--zlib-check", metavar="HEX", help="校验 2 字节十六进制 zlib 头")
    ap.add_argument("--selftest", action="store_true", help="跑内置自检")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.zlib_check:
        try:
            print("%s: %s" % (args.zlib_check, zlib_kind(bytes.fromhex(args.zlib_check))))
        except ValueError as exc:
            print("失败：" + str(exc), file=sys.stderr)
            return 2
        return 0
    if not args.file:
        ap.error("必须提供 --file（或 --selftest / --zlib-check）")
    if args.stride < 1:
        print("失败：--stride 必须 >= 1", file=sys.stderr)
        return 2

    try:
        with open(args.file, "rb") as fh:
            data = fh.read()
        rep = analyze(data)
        rep["file"] = args.file
        if args.carve_tail:
            if rep["kind"] == "png":
                end = next((o + 12 for o, t, _, _ in iter_chunks(data) if t == b"IEND"),
                           len(data))
                tail = data[end:]
            else:
                tail = data[max(data.rfind(b"PK\x03\x04"), rep["pixel_offset"]):]
            with open(args.carve_tail, "wb") as fh:
                fh.write(tail)
            rep["carved"] = {"out": args.carve_tail, "bytes": len(tail)}
        if args.extract_lsb:
            if rep["kind"] != "png":
                print("失败：LSB 抽取只支持 PNG（BMP 请先转 PNG）", file=sys.stderr)
                return 2
            w, h, bpp, rows = png_pixels(data)
            flat = [row[i * bpp:(i + 1) * bpp] for row in rows for i in range(w)]
            chans = tuple(sorted({"r": 0, "g": 1, "b": 2}[c] for c in args.channel if c in "rgb"))
            txt = lsb_extract(flat, args.msb, chans or (0, 1, 2), args.stride)
            rep["lsb"] = {"width": w, "height": h, "bytes": len(txt),
                          "preview": txt[:120].decode("latin1")}
    except (ValueError, OSError, zlib.error) as exc:
        print("失败：" + str(exc), file=sys.stderr)
        return 2

    print("文件    : %r（%d 字节，%s）" % (rep.get("file"), rep["size"], rep["kind"]))
    for c in rep["chunks"]:
        print("  chunk %-4s off=%-8d len=%-8d crc=%s"
              % (c["type"], c["off"], c["len"], "OK" if c["crc_ok"] else "BAD"))
    for t in rep["texts"]:
        print("  文本    : %r -> %r" % (t["kw"], t["text"]))
    print("  尾部追加: %d 字节%s" % (rep["trailing"],
                                 "（疑似藏东西，试 --carve-tail）" if rep["trailing"] else ""))
    if "lsb" in rep:
        print("  LSB     : %d 字节 -> %r" % (rep["lsb"]["bytes"], rep["lsb"]["preview"]))
    if "carved" in rep:
        print("  已另存  : %s（%d 字节）" % (rep["carved"]["out"], rep["carved"]["bytes"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
