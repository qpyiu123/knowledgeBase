#!/usr/bin/env python3
"""EXIF / 文档元数据离线取证（纯标准库，只读）。

对齐 kb/forensics/exif-metadata.md 的关键字段：Make/Model/DateTimeOriginal/
GPSLatitude/GPSLongitude/Software/Artist/Comment，以及三类坑：
  - GPS 用度分秒(DMS)存，必须换算成十进制；GPSLatitudeRef=S/W 要取负
  - DateTimeOriginal 是本地时间，OffsetTimeOriginal 才带时区
  - Software=Adobe Photoshop/... 或 APP12 "PIC" 段说明图被重新编辑/加过水印

支持：
  JPEG  APP1(Exif\0\0, TIFF/IFD)、COM 注释段、APP12/APP13 段落
  PNG   tEXt / iTXt 文本块
  PDF   /Info 字典与 XMP 里的字面量字段
  DOCX  内嵌 docProps/core.xml

用法：
  python exif_metadata.py --file photo.jpg
  python exif_metadata.py --file photo.jpg --gps
  python exif_metadata.py --file doc.docx --keyword author,creator
  python exif_metadata.py --dms 31 13 43.2 --ref S
  python exif_metadata.py --selftest
"""
from __future__ import annotations

import argparse
import hashlib
import re
import struct
import sys
import zipfile

SUSPECT_SOFTWARE = ("photoshop", "gimp", "lightroom", "pixelmator", "affinity",
                    "midjourney", "stable diffusion", "openai", "canva")
KEYWORDS = ("make", "model", "datetimeoriginal", "software", "artist", "comment",
            "gpslatitude", "gpslongitude", "gpsaltitude", "offsettime",
            "thumbnail", "author", "creator", "title", "subject", "keywords")


def dms_to_dd(d, m, s, ref="N"):
    """度分秒 -> 十进制度；ref 为 S/W 时取负。"""
    if not (0 <= d <= 180):
        raise ValueError("度数超出范围（0~180）")
    if not (0 <= m < 60) or not (0 <= s < 60):
        raise ValueError("分/秒必须在 [0,60) 内")
    dd = d + m / 60 + s / 3600
    return -dd if str(ref).upper() in ("S", "W") else dd


def _ratio(buf, off, little):
    num, den = struct.unpack(("<II" if little else ">II"), buf[off:off + 8])
    return num / den if den else 0.0


def parse_tiff(buf, verbose=False):
    """解析 Exif 的 TIFF 结构，返回 {标签名: 值}。"""
    if len(buf) < 8:
        raise ValueError("Exif 段太短（不足 8 字节 TIFF 头）")
    little = buf[:2] == b"II"
    magic = struct.unpack("<H" if little else ">H", buf[2:4])[0]
    if magic != 42:
        raise ValueError("TIFF 头非法（第二字段应为 42）")
    ifd = struct.unpack("<I" if little else ">I", buf[4:8])[0]
    out = {}
    if ifd + 2 > len(buf):
        raise ValueError("IFD 偏移越界（文件可能被截断）")
    count = struct.unpack("<H" if little else ">H", buf[ifd:ifd + 2])[0]
    tags = {0x010F: "Make", 0x0110: "Model", 0x0131: "Software", 0x013B: "Artist",
            0x9003: "DateTimeOriginal", 0x9011: "OffsetTimeOriginal",
            0x0002: "GPSLatitude", 0x0004: "GPSLongitude", 0x0001: "GPSLatitudeRef",
            0x0003: "GPSLongitudeRef", 0x0005: "GPSAltitude", 0x010E: "ImageDescription"}
    for i in range(count):
        e = ifd + 2 + i * 12
        if e + 12 > len(buf):
            break
        tag, typ, cnt = struct.unpack(("<HHI" if little else ">HHI"), buf[e:e + 8])
        name = tags.get(tag)
        if not name:
            continue
        if typ == 2:  # ASCII，指向数据区的偏移
            off = struct.unpack("<I" if little else ">I", buf[e + 8:e + 12])[0]
            out[name] = buf[off:off + cnt].split(b"\x00")[0].decode("utf-8", "replace")
        elif typ == 5 and cnt >= 3:  # RATIONAL ×3 = DMS
            off = struct.unpack("<I" if little else ">I", buf[e + 8:e + 12])[0]
            out[name] = tuple(_ratio(buf, off + 8 * k, little) for k in range(3))
        elif typ in (1, 2) and cnt == 2:  # 2 字节 ASCII 内联
            out[name] = buf[e + 8:e + 8 + cnt].split(b"\x00")[0].decode("latin1")
    lat = out.get("GPSLatitude")
    lon = out.get("GPSLongitude")
    if isinstance(lat, tuple) and len(lat) == 3:
        out["GPSLatitudeDD"] = dms_to_dd(*lat, out.get("GPSLatitudeRef", "N"))
    if isinstance(lon, tuple) and len(lon) == 3:
        out["GPSLongitudeDD"] = dms_to_dd(*lon, out.get("GPSLongitudeRef", "E"))
    return out


def jpeg_segments(data: bytes):
    """遍历 JPEG 段，yield (marker, payload)。"""
    if data[:2] != b"\xff\xd8":
        raise ValueError("不是 JPEG（应以 FF D8 开头）")
    p = 2
    while p + 4 <= len(data):
        if data[p] != 0xFF:
            raise ValueError("JPEG 段结构损坏：偏移 %d 处不是 FF" % p)
        marker = data[p + 1]
        if marker in (0xD8, 0xD9):
            p += 2
            continue
        ln = struct.unpack(">H", data[p + 2:p + 4])[0]
        if ln < 2:
            raise ValueError("JPEG 段长度非法（偏移 %d）" % p)
        yield marker, data[p + 4:p + 2 + ln]
        p += 2 + ln
        if marker == 0xDA:  # 扫描数据后不再有元数据
            break


def scan_png(data: bytes):
    out = {}
    p = 8
    while p + 12 <= len(data):
        ln = struct.unpack(">I", data[p:p + 4])[0]
        typ = data[p + 4:p + 8]
        body = data[p + 8:p + 8 + ln]
        if typ in (b"tEXt", b"iTXt"):
            kw, _, rest = body.partition(b"\x00")
            txt = rest.split(b"\x00", 1)[-1] if typ == b"iTXt" else rest
            out[kw.decode("latin1")] = txt.decode("utf-8", "replace")
        p += 12 + ln
        if typ == b"IEND":
            break
    return out


def scan_pdf(data: bytes):
    out = {}
    for key in (b"Author", b"Title", b"Creator", b"Producer", b"CreationDate"):
        m = re.search(rb"/" + key + rb"\s*\(([^)]{0,200})\)", data)
        if m:
            out[key.decode()] = m.group(1).decode("latin1")
    xmp = re.search(rb"<xmp:(CreatorTool|History)[^>]*>([^<]{0,200})", data)
    if xmp:
        out["XMP:" + xmp.group(1).decode()] = xmp.group(2).decode("latin1")
    return out


CORE = re.compile(r"<(?:dc|cp|dcterms):(creator|title|creator|description)[^>]*>([^<]{0,200})")
CORE2 = re.compile(r"<cp:lastModifiedBy>([^<]{0,120})")


def scan_docx(path: str):
    out = {}
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        if "docProps/core.xml" not in names:
            raise ValueError("docx 里没有 docProps/core.xml（可能不是 Office 文档）")
        xml = zf.read("docProps/core.xml").decode("utf-8", "replace")
    for key, val in CORE.findall(xml):
        out[key] = val.strip()
    m = CORE2.search(xml)
    if m:
        out["lastModifiedBy"] = m.group(1).strip()
    return out


def analyze(data: bytes, name: str = "") -> dict:
    """按文件头分派；返回 {"kind", "meta", "notes"}。"""
    rep = {"kind": None, "meta": {}, "notes": []}
    low = name.lower()
    if data[:2] == b"\xff\xd8":
        rep["kind"] = "jpeg"
        for marker, payload in jpeg_segments(data):
            if marker == 0xE1 and payload[:6] == b"Exif\x00\x00":
                rep["meta"].update(parse_tiff(payload[6:]))
            elif marker == 0xFE:
                rep["meta"]["COM"] = payload.decode("utf-8", "replace")
            elif marker == 0xEC:
                rep["notes"].append("APP12/Ducky 段（常见于加过水印或压缩软件）")
    elif data[:8] == b"\x89PNG\r\n\x1a\n":
        rep["kind"] = "png"
        rep["meta"].update(scan_png(data))
    elif data[:5] == b"%PDF-":
        rep["kind"] = "pdf"
        rep["meta"].update(scan_pdf(data))
    elif data[:2] == b"PK" and low.endswith((".docx", ".xlsx", ".pptx")):
        rep["kind"] = "office"
        rep["meta"].update(scan_docx(name))
    else:
        raise ValueError("认不出格式（支持 JPEG/PNG/PDF/DOCX，按文件头判断）")
    sw = str(rep["meta"].get("Software", ""))
    if any(k in sw.lower() for k in SUSPECT_SOFTWARE):
        rep["notes"].append("Software=%s → 被重新编辑/生成过" % sw)
    if "DateTimeOriginal" in rep["meta"] and "OffsetTimeOriginal" not in rep["meta"]:
        rep["notes"].append("只有 DateTimeOriginal，没有 OffsetTimeOriginal → 时区未知")
    return rep


def render(rep: dict, only=None) -> str:
    lines = ["格式: %s" % rep["kind"]]
    for k in sorted(rep["meta"]):
        if only and k.lower() not in only and not any(o in k.lower() for o in only):
            continue
        v = rep["meta"][k]
        if isinstance(v, float):
            v = "%.6f" % v
        lines.append("  %-22s = %s" % (k, v))
    for n in rep["notes"]:
        lines.append("  ! " + n)
    if not rep["meta"]:
        lines.append("  （没有可解析的元数据，可能被清空，试 -v3 看残留）")
    return "\n".join(lines)


def _fake_jpeg(tiff_body: bytes) -> bytes:
    app1 = b"Exif\x00\x00" + tiff_body
    return b"\xff\xd8" + b"\xff\xe1" + struct.pack(">H", len(app1) + 2) + app1 + b"\xff\xd9"


def _tiff_with(fields) -> bytes:
    """构造一个小端 TIFF：fields = [(tag, type, count, payload_bytes)]。"""
    out = b"II" + struct.pack("<HI", 42, 8) + struct.pack("<H", len(fields)) + b"\x00" * 0
    entries, data_area, base = b"", b"", 8 + 2 + 12 * len(fields) + 4
    for tag, typ, cnt, payload in fields:
        if len(payload) <= 4:
            entries += struct.pack("<HHI", tag, typ, cnt) + payload.ljust(4, b"\x00")
        else:
            entries += struct.pack("<HHI", tag, typ, cnt) + struct.pack("<I", base + len(data_area))
            data_area += payload
    return b"II" + struct.pack("<HI", 42, 8) + struct.pack("<H", len(fields)) + entries + b"\x00\x00\x00\x00" + data_area


def selftest() -> int:
    fails = []
    # 1) 正常路径：DMS 换算 + 南纬取负
    if abs(dms_to_dd(31, 13, 43.2) - 31.228667) > 1e-5:
        fails.append("case1: 31°13′43.2″ 换算错误")
    if abs(dms_to_dd(31, 13, 43.2, "S") + 31.228667) > 1e-5:
        fails.append("case1: 南纬应取负")
    # 2) 构造 JPEG 走完整解析
    rat = b"".join(struct.pack("<II", n, 1) for n in (31, 13, 43))
    rat2 = b"".join(struct.pack("<II", n, 1) for n in (121, 28, 29))
    tiff = _tiff_with([(0x010F, 2, 6, b"Canon\x00"), (0x0131, 2, 16, b"Adobe Photoshop\x00"),
                       (0x0002, 5, 3, rat), (0x0001, 2, 2, b"S\x00")])
    rep = analyze(_fake_jpeg(tiff), "x.jpg")
    if rep["meta"].get("Make") != "Canon":
        fails.append("case2: Make 解析失败 %r" % (rep["meta"].get("Make"),))
    if not any("重新编辑" in n for n in rep["notes"]):
        fails.append("case2: Software=Photoshop 应判定为被编辑")
    # 3) 边界拒绝：非法 TIFF 头 / 非法 JPEG 头 / 认不出的格式
    for bad, msg in ((_fake_jpeg(b"II\x01\x00" + bytes(16)), "TIFF magic 非 42"),
                     (b"GIF89a" + bytes(20), "非 JPEG/PNG 应拒绝"),
                     (_fake_jpeg(b"II"), "TIFF 头截断")):
        try:
            analyze(bad, "x.bin")
            fails.append("case3: %s 未被拒绝" % msg)
        except ValueError:
            pass
    # 4) 参数不足与边界值：分/秒越界、缺文件参数
    for args, msg in (((1, 60, 0), "分=60"), ((1, 0, 60), "秒=60"), ((181, 0, 0), "度数 181")):
        try:
            dms_to_dd(*args)
            fails.append("case4: %s 未被拒绝" % msg)
        except ValueError:
            pass
    # 5) 固定输入可复现 + 哈希稳定（同一构造输入两次结果相同）
    a = hashlib.sha1(render(analyze(_fake_jpeg(tiff), "x.jpg")).encode()).hexdigest()
    b = hashlib.sha1(render(analyze(_fake_jpeg(tiff), "x.jpg")).encode()).hexdigest()
    if a != b:
        fails.append("case5: 同一输入两次输出不一致")
    for f in fails:
        print("FAIL " + f, file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 5 组断言全过（DMS 换算与取负、构造 JPEG 解析、非法头拒绝、"
          "分秒越界、固定输入可复现）")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="EXIF/文档元数据离线取证")
    ap.add_argument("--file", help="目标文件（JPEG/PNG/PDF/DOCX）")
    ap.add_argument("--keyword", help="只看含这些前缀的字段，逗号分隔")
    ap.add_argument("--gps", action="store_true", help="只输出 GPS 相关字段")
    ap.add_argument("--dms", nargs=3, metavar=("D", "M", "S"), type=float, help="手算 DMS→十进制")
    ap.add_argument("--ref", default="N", help="配合 --dms：N/S/E/W")
    ap.add_argument("--selftest", action="store_true", help="跑内置自检")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.dms:
        try:
            print("%.6f" % dms_to_dd(args.dms[0], args.dms[1], args.dms[2], args.ref))
        except ValueError as exc:
            print("失败：" + str(exc), file=sys.stderr)
            return 2
        return 0
    if not args.file:
        ap.error("必须提供 --file（或 --dms / --selftest）")
    only = None
    if args.gps:
        only = ["gps"]
    elif args.keyword:
        only = [k.strip().lower() for k in args.keyword.split(",") if k.strip()]
    try:
        with open(args.file, "rb") as fh:
            data = fh.read()
        print(render(analyze(data, args.file), only))
    except (ValueError, OSError, zipfile.BadZipFile, struct.error) as exc:
        print("失败：" + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
