#!/usr/bin/env python3
"""多格式循环解压链：自动识别并逐层解开 gzip / bz2 / xz / lzma / zlib / zip / tar。

依赖：只用标准库（gzip、bz2、lzma、zlib、zipfile、tarfile、io、json）。
用途：misc 里常见的"压缩套娃"（flag.txt.gz → 里面又是一个 .bz2 → ...）。
      本脚本按魔数（magic bytes）判断格式，逐层解开，每层打印格式与解出内容的名字/大小/前 64 字节，
      直到解出可读文本或不再有已知压缩魔数。

用法：
  python decompress_chain.py --file flag.gz
  python decompress_chain.py --file flag.gz --max-depth 10 --out work/out/
  python decompress_chain.py --file flag.gz --json
  python decompress_chain.py --selftest

限制：不做 7z/rar（标准库无支持）；zip/tar 内有多文件时只跟随第一个非目录成员并提示；
      .gz 带文件名头信息时按 gzip.FEXTRA 解析失败会回退到 zlib.decompressobj(wbits=31)。
"""
from __future__ import annotations

import argparse
import bz2
import gzip
import io
import json
import lzma
import sys
import tarfile
import zipfile
import zlib
from pathlib import Path

MAGIC = [
    ("gzip", b"\x1f\x8b"),
    ("bz2", b"BZh"),
    ("xz", b"\xfd7zXZ\x00"),
    ("lzma_alone", b"\x5d\x00\x00"),
    ("zip", b"PK\x03\x04"),
    ("zip_empty", b"PK\x05\x06"),
    ("zlib", b"\x78"),
    ("tar", None),  # 通过 tarfile.is_tarfile 判定
]


def sniff(data: bytes) -> str:
    if data.startswith(MAGIC[0][1]):
        return "gzip"
    if data.startswith(MAGIC[1][1]):
        return "bz2"
    if data.startswith(MAGIC[2][1]):
        return "xz"
    if data.startswith(b"PK\x03\x04") or data.startswith(b"PK\x05\x06"):
        return "zip"
    # zlib: 头两字节满足 (CMF*256+FLG) % 31 == 0 且 CMF 低四位 == 8
    if len(data) >= 2:
        cmf, flg = data[0], data[1]
        if (cmf & 0x0F) == 8 and (cmf * 256 + flg) % 31 == 0 and not data.startswith(b"\x1f\x8b"):
            return "zlib"
    try:
        if len(data) > 512 and tarfile.is_tarfile(io.BytesIO(data)):
            return "tar"
    except Exception:
        pass
    return ""


def decompress_layer(data: bytes, kind: str) -> tuple[str, bytes]:
    """返回 (成员名, 解出的字节)。"""
    if kind == "gzip":
        with gzip.GzipFile(fileobj=io.BytesIO(data)) as fh:
            return "", fh.read()
    if kind == "bz2":
        return "", bz2.decompress(data)
    if kind == "xz":
        return "", lzma.decompress(data, format=lzma.FORMAT_XZ)
    if kind == "zlib":
        return "", zlib.decompressobj().decompress(data)
    if kind == "zip":
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            names = [n for n in zf.namelist() if not n.endswith("/")]
            if not names:
                raise ValueError("zip 内没有文件成员")
            return names[0], zf.read(names[0])
    if kind == "tar":
        with tarfile.open(fileobj=io.BytesIO(data)) as tf:
            members = [m for m in tf.getmembers() if m.isfile()]
            if not members:
                raise ValueError("tar 内没有普通文件")
            m = members[0]
            return m.name, tf.extractfile(m).read()  # type: ignore[union-attr]
    raise ValueError(f"未识别的压缩格式：{kind}")


def decompress_chain(data: bytes, max_depth: int = 10) -> dict:
    steps: list[dict] = []
    cur = data
    while len(steps) < max_depth:
        kind = sniff(cur)
        if not kind:
            break
        try:
            name, nxt = decompress_layer(cur, kind)
        except Exception as exc:  # 损坏或误判
            steps.append({"format": kind, "error": str(exc), "in_size": len(cur)})
            break
        steps.append({"format": kind, "member": name, "in_size": len(cur), "out_size": len(nxt),
                      "head": nxt[:64].decode("utf-8", "replace")})
        if nxt == cur:
            break
        cur = nxt
    text = ""
    try:
        text = cur.decode("utf-8")
        if sum(ch.isprintable() or ch in "\r\n\t" for ch in text) / max(len(text), 1) < 0.95:
            text = ""
    except UnicodeDecodeError:
        text = ""
    return {"steps": steps, "depth": len(steps), "final_size": len(cur),
            "final_text": text, "final_head_hex": cur[:32].hex()}


# ---------------------------------------------------------------- 自检

def selftest() -> int:
    checks = []
    inner = b"flag{gzip_layer}"
    # 1. 单层 gzip
    r = decompress_chain(gzip.compress(inner))
    checks.append(("gzip 单层", r["depth"] == 1 and r["final_text"] == inner.decode()))
    # 2. gzip → bz2 → xz 三层
    deep = xz = lzma.compress(bz2.compress(gzip.compress(inner), 9), format=lzma.FORMAT_XZ)
    r = decompress_chain(xz)
    checks.append(("xz→bz2→gzip", [s["format"] for s in r["steps"]] == ["xz", "bz2", "gzip"]
                   and r["final_text"] == inner.decode()))
    # 3. zip 成员名与内容
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("readme.txt", inner)
    r = decompress_chain(buf.getvalue())
    checks.append(("zip 取首成员", r["depth"] == 1 and r["steps"][0]["member"] == "readme.txt"
                   and r["final_text"] == inner.decode()))
    # 4. tar 成员
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tf:
        info = tarfile.TarInfo("a/b.txt")
        info.size = len(inner)
        tf.addfile(info, io.BytesIO(inner))
    r = decompress_chain(buf.getvalue())
    checks.append(("tar 取首文件", r["steps"][0]["format"] == "tar" and r["final_text"] == inner.decode()))
    # 5. zlib 裸流
    r = decompress_chain(zlib.compress(inner))
    checks.append(("zlib 裸流", r["depth"] == 1 and r["final_text"] == inner.decode()))
    # 6. 截断的 gzip：报错但已走完第一层记录
    bad = gzip.compress(inner)[:10]
    r = decompress_chain(bad)
    checks.append(("截断报错不崩", r["depth"] == 1 and "error" in r["steps"][0]))
    # 7. 非压缩数据
    r = decompress_chain(b"flag{plain}")
    checks.append(("非压缩数据", r["depth"] == 0 and r["final_text"] == "flag{plain}"))
    # 8. 深度上限
    layers = inner
    for _ in range(4):
        layers = gzip.compress(layers)
    r = decompress_chain(layers, max_depth=2)
    checks.append(("深度上限", r["depth"] == 2))

    ok = sum(1 for _, v in checks if v)
    for name, v in checks:
        if not v:
            print(f"FAIL: {name}", file=sys.stderr)
    print(f"selftest ok: {ok}/{len(checks)}（" + "、".join(n for n, _ in checks) + "）")
    return 0 if ok == len(checks) else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="多格式压缩套娃逐层解压")
    ap.add_argument("--file", help="输入文件")
    ap.add_argument("--max-depth", type=int, default=10)
    ap.add_argument("--out", help="把最终结果写到该路径")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.file:
        ap.error("需要 --file")
        return 2
    data = Path(args.file).read_bytes()
    result = decompress_chain(data, args.max_depth)
    if args.out:
        out = result["final_text"].encode() if result["final_text"] else bytes.fromhex(result["final_head_hex"])
        Path(args.out).write_bytes(out)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for i, s in enumerate(result["steps"], 1):
            if "error" in s:
                print(f"[{i}] {s['format']}: 失败 {s['error']}")
            else:
                print(f"[{i}] {s['format']} {s['in_size']}B → {s['out_size']}B"
                      + (f" member={s['member']}" if s["member"] else "")
                      + f" head={s['head'][:40]!r}")
        if result["final_text"]:
            print(f"final: {result['final_text'][:200]}")
        else:
            print(f"final: <二进制 {result['final_size']}B> hex={result['final_head_hex']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
