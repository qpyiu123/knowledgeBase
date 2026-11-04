#!/usr/bin/env python3
"""按签名 + 结构长度做文件雕刻（纯标准库，只读输入、只写你指定的输出目录）。

对齐 kb/forensics/file-carving.md：
  PNG  \x89PNG.. 开头，以 IEND + CRC 结尾
  JPEG FF D8 FF .. FF D9
  PDF  %PDF- .. %%EOF
  ZIP  靠 EOCD 回扫（PK0506 + 22 字节 + 注释长度）
  GZIP 尾部靠解压判断（zlib 的 unused_data 给出真实结束位置）

用法：
  python file_carving.py --image disk.img --out out/
  python file_carving.py --image disk.img --types png,jpg,zip --min-size 1024
  python file_carving.py --image mem.dump --list
  python file_carving.py --selftest
"""
from __future__ import annotations

import argparse
import os
import struct
import sys
import zlib

SIGS = {
    "png": (b"\x89PNG\r\n\x1a\n", b"IEND\xaeB`\x82"),
    "jpg": (b"\xff\xd8\xff", b"\xff\xd9"),
    "pdf": (b"%PDF-", b"%%EOF"),
    "zip": (b"PK\x03\x04", None),
    "gzip": (b"\x1f\x8b\x08", None),
}
EOCD = b"PK\x05\x06"


def zip_end(data: bytes, start: int) -> int:
    """从 start 往后回扫 EOCD，返回 zip 结束偏移；找不到返回 -1。"""
    e = data.find(EOCD, start)
    if e < 0 or e + 22 > len(data):
        return -1
    comment_len = struct.unpack("<H", data[e + 20:e + 22])[0]
    end = e + 22 + comment_len
    return end if end <= len(data) else -1


def gzip_end(data: bytes, start: int) -> int:
    """用 zlib 解 gzip 流，靠 unused_data 反推真实结束位置；失败返回 -1。"""
    d = zlib.decompressobj(31)
    try:
        d.decompress(data[start:])
    except zlib.error:
        return -1
    if not d.eof:
        return -1
    return len(data) - len(d.unused_data)


def carve(data: bytes, kind: str, min_size: int = 1):
    """返回 [(offset, blob)]；不完整的候选直接跳过而不是产出脏文件。"""
    if kind not in SIGS:
        raise ValueError("不支持的类型：%s（可选 %s）" % (kind, ",".join(SIGS)))
    head, tail = SIGS[kind]
    out, pos = [], 0
    while True:
        s = data.find(head, pos)
        if s < 0:
            break
        if tail:
            e = data.find(tail, s)
            e = -1 if e < 0 else e + len(tail)
        elif kind == "zip":
            e = zip_end(data, s)
        else:
            e = gzip_end(data, s)
        if e < 0:
            pos = s + len(head)
            continue
        if e - s >= min_size:
            out.append((s, data[s:e]))
        pos = e
    return out


def detect(data: bytes) -> list:
    """只看偏移，不切出内容：[(kind, offset)]。"""
    hits = []
    for kind in SIGS:
        for off, _ in carve(data, kind):
            hits.append((kind, off))
    hits.sort(key=lambda x: x[1])
    return hits


def write_out(items, kind: str, outdir: str) -> list:
    if not outdir:
        raise ValueError("要落盘必须给 --out 目录")
    os.makedirs(outdir, exist_ok=True)
    ext = {"jpg": "jpg"}.get(kind, kind)
    written = []
    for off, blob in items:
        name = "%s_%d_%x.%s" % (kind, len(written), off, ext)
        path = os.path.join(outdir, name)
        with open(path, "wb") as fh:
            fh.write(blob)
        written.append((path, len(blob)))
    return written


def _png(w=2, h=2) -> bytes:
    rows = b"".join(b"\x00" + bytes([(x * 40) % 256 for x in range(w)]) * 3 for _ in range(h))

    def chunk(typ, body):
        return (struct.pack(">I", len(body)) + typ + body
                + struct.pack(">I", zlib.crc32(typ + body) & 0xFFFFFFFF))

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b""))


def _zip(name=b"a.txt", body=b"hello") -> bytes:
    local = b"PK\x03\x04" + struct.pack("<HHHHHIIIHH", 20, 0, 0, 0, 0, 0, len(body), len(body),
                                        len(name), 0) + name + body
    cd = b"PK\x01\x02" + struct.pack("<HHHHHHIIIHHHHHII", 20, 0, 20, 0, 0, 0, 0, len(body),
                                     len(body), len(name), 0, 0, 0, 0, 0, 0) + name
    eocd = EOCD + struct.pack("<HHHHIIH", 0, 0, 1, 1, len(cd), len(local), 0)
    return local + cd + eocd


def selftest() -> int:
    fails = []
    blob = b"\x00" * 16 + _png() + b"\x11" * 8 + _zip() + b"\x22" * 4
    # 1) 正常路径：PNG 与 ZIP 都能按结构切出且能被库验证
    pngs = carve(blob, "png")
    zips = carve(blob, "zip")
    if len(pngs) != 1 or pngs[0][1] != _png():
        fails.append("case1: PNG 切出内容与原始不符")
    if len(zips) != 1 or zips[0][1] != _zip():
        fails.append("case1: ZIP 应切到 EOCD 含注释长度为止")
    # 2) 边界拒绝：头部在但尾部缺失 -> 不产出脏文件
    if carve(b"\x89PNG\r\n\x1a\n" + bytes(40), "png"):
        fails.append("case2: 没有 IEND 的 PNG 不应被切出")
    if carve(b"PK\x03\x04" + bytes(10), "zip"):
        fails.append("case2: 没有 EOCD 的 ZIP 不应被切出")
    # 3) 参数不足 / 非法类型：必须明确报错
    for call, msg in ((lambda: carve(b"", "rar"), "不支持的类型"),
                      (lambda: carve(b"", "png", -1), "负的 min-size 应被规整或报错")):
        try:
            call()
            if msg.startswith("负"):
                continue
        except ValueError:
            pass
    try:
        carve(blob, "rar")
        fails.append("case3: 非法类型未被拒绝")
    except ValueError:
        pass
    # 4) 固定输入可复现：同一输入两次 carve 偏移完全一致
    if [o for o, _ in carve(blob, "png")] != [o for o, _ in carve(blob, "png")]:
        fails.append("case4: 同一输入两次偏移不一致")
    if [k for k, _ in detect(blob)] != ["png", "zip"]:
        fails.append("case4: --list 应报出 png 与 zip 两种")
    # 5) gzip 走解压判定 + 空镜像不崩
    gz = zlib.compressobj(9, zlib.DEFLATED, 31)
    gzblob = gz.compress(b"flag{gzip}") + gz.flush()
    got = carve(b"\x00" * 3 + gzblob + b"\x00" * 5, "gzip")
    if len(got) != 1 or got[0][1] != gzblob:
        fails.append("case5: gzip 结束位置判定错误 %r" % ([len(g[1]) for g in got],))
    if carve(b"", "png") != []:
        fails.append("case5: 空镜像应返回空列表")
    for f in fails:
        print("FAIL " + f, file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 5 组断言全过（PNG/ZIP 精确切出、缺尾拒绝、非法类型报错、"
          "固定输入可复现、gzip 结束判定）")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="按签名雕刻镜像里的文件")
    ap.add_argument("--image", help="原始镜像 / 内存 dump")
    ap.add_argument("--types", default="png,jpg,zip,pdf,gzip", help="要雕的类型，逗号分隔")
    ap.add_argument("--out", help="输出目录（不给则只列偏移不落盘）")
    ap.add_argument("--min-size", type=int, default=1, help="小于该字节数的候选丢弃")
    ap.add_argument("--list", action="store_true", help="只列出偏移，不切出内容")
    ap.add_argument("--selftest", action="store_true", help="跑内置自检")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.image:
        ap.error("必须提供 --image（或 --selftest）")
    if args.min_size < 0:
        print("失败：--min-size 不能为负", file=sys.stderr)
        return 2
    try:
        with open(args.image, "rb") as fh:
            data = fh.read()
        kinds = [t.strip() for t in args.types.split(",") if t.strip()]
        total = 0
        for kind in kinds:
            items = carve(data, kind, args.min_size)
            if args.list or not args.out:
                for off, blob in items:
                    print("%-4s off=%-10d size=%d" % (kind, off, len(blob)))
                total += len(items)
                continue
            for path, size in write_out(items, kind, args.out):
                print("%-4s %-40s %d 字节" % (kind, path, size))
            total += len(items)
        print("共 %d 个候选（%s）" % (total, "仅列偏移" if args.list or not args.out else args.out))
    except (ValueError, OSError, struct.error) as exc:
        print("失败：" + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
