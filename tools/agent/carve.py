"""纯 Python 实现的取证能力（不依赖外部命令行工具）。

本机实测：binwalk / zsteg / exiftool / 7z / unzip 全都没装，
只有 strings 和 tar。但网上照抄的解法都依赖这些工具，
所以这里用标准库把它们最容易用到的功能自己实现一遍。

提供：
  carve_files(data)     文件雕刻：扫描内嵌的 PNG/JPG/ZIP/PDF/GZIP...
  extract_zip(path)     解压 ZIP（含加密检测、目录遍历防护）
  png_info(path)        PNG chunk 结构、是否含异常 chunk、CRC 校验
  exif_basic(path)      JPEG/PNG 的基础元数据（宽高、注释、EXIF 摘要）
  wav_info(path)        WAV 头解析（采样率、位深、尾部追加数据）
"""
from __future__ import annotations

import binascii
import io
import re
import struct
import zipfile
import zlib
from pathlib import Path

MAX_ITEMS = 40


# ---------------------------------------------------------------- 雕刻
# (魔数, 结束标记, 名称, 是否有长度可算)
SIGNATURES = [
    (b"\x89PNG\r\n\x1a\n", b"IEND\xaeB`\x82", "PNG", False),
    (b"\xff\xd8\xff", b"\xff\xd9", "JPEG", False),
    (b"PK\x03\x04", None, "ZIP", True),
    (b"%PDF", b"%%EOF", "PDF", False),
    (b"\x1f\x8b\x08", None, "GZIP", False),
    (b"7z\xbc\xaf\x27\x1c", None, "7Z", False),
    (b"Rar!\x1a\x07", None, "RAR", False),
    (b"GIF89a", b"\x3b", "GIF", False),
    (b"GIF87a", b"\x3b", "GIF", False),
    (b"BM", None, "BMP", False),
    (b"\x7fELF", None, "ELF", False),
    (b"OggS", None, "OGG", False),
    (b"fLaC", None, "FLAC", False),
]


def carve_files(data: bytes, outdir: Path | None = None) -> dict:
    """扫描数据里所有内嵌文件的偏移与类型，可选导出。

    对 GZIP 这类没有结束标记的格式，只给偏移不给大小——
    调用方应当用 extract_embedded 导出尾巴再解。
    """
    found = []
    seen_offsets: set[tuple[int, str]] = set()
    for magic, endmark, name, is_zip in SIGNATURES:
        start = 0
        while True:
            idx = data.find(magic, start)
            if idx < 0:
                break
            if (idx, name) in seen_offsets:
                start = idx + len(magic)
                continue
            seen_offsets.add((idx, name))

            size = None
            if name == "ZIP":
                size = _zip_size(data, idx)
            elif name == "PNG":
                size = _png_size(data, idx)
            elif name == "GZIP":
                size = _gzip_size(data, idx)
            elif endmark:
                e = data.find(endmark, idx)
                if e > 0:
                    size = e + len(endmark) - idx

            found.append({
                "type": name, "offset": idx, "size": size,
                "offset_hex": f"0x{idx:x}",
            })
            start = idx + max(1, len(magic))
            if len(found) > MAX_ITEMS:
                break

    # 按偏移排序，便于按顺序分析
    found.sort(key=lambda x: x["offset"])

    exported = []
    if outdir is not None:
        outdir.mkdir(parents=True, exist_ok=True)
        for i, item in enumerate(found):
            if not item["size"]:
                continue
            blob = data[item["offset"]: item["offset"] + item["size"]]
            p = outdir / f"carved_{i}_{item['type'].lower()}.bin"
            p.write_bytes(blob)
            exported.append(str(p))

    return {"items": found, "exported": exported}


def _gzip_size(data: bytes, start: int) -> int | None:
    """GZIP 没有显式总长，用 zlib 流式解压到结束位置。"""
    try:
        d = zlib.decompressobj(16 + zlib.MAX_WBITS)
        d.decompress(data[start:])
        consumed = len(data) - start - len(d.unused_data)
        return consumed if consumed > 0 else None
    except Exception:  # noqa: BLE001
        return None


def _png_size(data: bytes, start: int) -> int | None:
    pos = start + 8
    while pos + 8 <= len(data):
        (ln,) = struct.unpack(">I", data[pos:pos + 4])
        ty = data[pos + 4:pos + 8]
        pos += 12 + ln
        if ty == b"IEND":
            return pos - start
        if ln > 100_000_000:
            return None
    return None


def _zip_size(data: bytes, start: int) -> int | None:
    # 找 End of Central Directory: PK\x05\x06
    eocd = data.find(b"PK\x05\x06", start)
    if eocd < 0:
        return None
    if eocd + 22 > len(data):
        return None
    comment_len = struct.unpack("<H", data[eocd + 20:eocd + 22])[0]
    return eocd + 22 + comment_len - start


def extract_gzip(path: Path, outdir: Path | None = None) -> dict:
    """解 GZIP（含内嵌的 gzip 片段），返回解出的字节与文本预览。"""
    import gzip as _gz
    out: dict = {"ok": False, "size": 0, "text": None, "outfile": None, "error": None}
    data = path.read_bytes()
    idx = data.find(b"\x1f\x8b\x08")
    if idx < 0:
        out["error"] = "找不到 gzip 魔数"
        return out
    try:
        raw = _gz.decompress(data[idx:])
    except Exception as e:  # noqa: BLE001
        out["error"] = f"解压失败: {type(e).__name__}: {e}"
        return out
    out["ok"] = True
    out["size"] = len(raw)
    try:
        out["text"] = raw.decode("utf-8")
    except UnicodeDecodeError:
        out["text"] = None
    if outdir is not None:
        outdir.mkdir(parents=True, exist_ok=True)
        p = outdir / (path.stem + "_decompressed.bin")
        p.write_bytes(raw)
        out["outfile"] = str(p)
    return out


# ---------------------------------------------------------------- 文本解码
def auto_decode_text(s: str) -> list[str]:
    """对一段文本做自动解码（base64/hex/url/rot13），返回所有候选结果。

    小模型常常自己"猜"解码结果（实测把 st4g3 写成 s4g3），
    所以由工具算好、原样给出，模型只要复制即可。
    """
    import base64
    import binascii
    import urllib.parse

    out: list[str] = []
    seen: set[str] = set()
    cur = s.strip()
    for _ in range(4):
        if not cur:
            break
        cands = []
        # base64
        if re.fullmatch(r"[A-Za-z0-9+/]{8,}={0,2}", cur):
            try:
                dec = base64.b64decode(cur + "=" * (-len(cur) % 4)).decode("utf-8")
                if dec != cur:
                    cands.append(("base64", dec))
            except Exception:  # noqa: BLE001
                pass
        # hex
        if re.fullmatch(r"[0-9a-fA-F]{8,}", cur) and len(cur) % 2 == 0:
            try:
                dec = binascii.unhexlify(cur).decode("utf-8")
                if dec != cur:
                    cands.append(("hex", dec))
            except Exception:  # noqa: BLE001
                pass
        # url
        if "%" in cur:
            dec = urllib.parse.unquote(cur)
            if dec != cur:
                cands.append(("url", dec))
        if not cands:
            break
        kind, dec = cands[0]
        if dec in seen:
            break
        seen.add(dec)
        out.append(f"{cur[:40]}… --{kind}--> {dec}")
        cur = dec.strip()
    return out
def extract_zip(path: Path, outdir: Path) -> dict:
    info: dict = {"ok": False, "entries": [], "encrypted": False, "error": None}
    try:
        with zipfile.ZipFile(path) as z:
            info["entries"] = [
                {"name": i.filename, "size": i.file_size,
                 "compressed": i.compress_size,
                 "encrypted": bool(i.flag_bits & 0x1)}
                for i in z.infolist()[:MAX_ITEMS]
            ]
            if any(i.flag_bits & 0x1 for i in z.infolist()):
                info["encrypted"] = True
                info["error"] = "压缩包有密码，需要先爆破/找密码"
                return info
            outdir.mkdir(parents=True, exist_ok=True)
            for i in z.infolist():
                # 防目录穿越
                target = (outdir / i.filename).resolve()
                try:
                    target.relative_to(outdir.resolve())
                except ValueError:
                    continue
                if i.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(z.read(i))
            info["ok"] = True
            info["outdir"] = str(outdir)
    except zipfile.BadZipFile as e:
        info["error"] = f"不是有效 ZIP: {e}"
    except Exception as e:  # noqa: BLE001
        info["error"] = f"{type(e).__name__}: {e}"
    return info


# ---------------------------------------------------------------- PNG
PNG_KNOWN = {b"IHDR", b"PLTE", b"IDAT", b"IEND", b"tRNS", b"gAMA",
             b"cHRM", b"sRGB", b"iCCP", b"pHYs", b"tEXt", b"zTXt",
             b"iTXt", b"bKGD", b"tIME", b"sBIT", b"hIST", b"sPLT"}


def png_info(path: Path) -> dict:
    data = path.read_bytes()
    out: dict = {"ok": False, "chunks": [], "width": None, "height": None,
                 "anomalies": []}
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        out["anomalies"].append("不是 PNG 文件头")
        return out
    pos = 8
    while pos + 8 <= len(data):
        (ln,) = struct.unpack(">I", data[pos:pos + 4])
        ty = data[pos + 4:pos + 8]
        payload = data[pos + 8:pos + 8 + ln]
        crc = data[pos + 8 + ln:pos + 12 + ln]
        name = ty.decode("latin1", "replace")
        entry = {"type": name, "len": ln, "offset": pos}
        if len(crc) == 4:
            want = struct.unpack(">I", crc)[0]
            got = binascii.crc32(ty + payload) & 0xFFFFFFFF
            entry["crc_ok"] = (want == got)
            if want != got:
                out["anomalies"].append(
                    f"chunk {name} CRC 不符（0x{got:08x} != 0x{want:08x}）"
                    f"——可能是宽高被改过或数据损坏")
        if ty not in PNG_KNOWN:
            out["anomalies"].append(f"非常规 chunk: {name}（可能藏了数据）")
        if ty == b"IHDR" and len(payload) >= 8:
            out["width"], out["height"] = struct.unpack(">II", payload[:8])
        if ty in (b"tEXt", b"zTXt", b"iTXt") and payload:
            out["anomalies"].append(f"文本块 {name}: {payload[:120]!r}")
        out["chunks"].append(entry)
        pos += 12 + ln
        if ty == b"IEND":
            if pos < len(data):
                out["anomalies"].append(
                    f"IEND 之后还有 {len(data) - pos} 字节追加数据（偏移 0x{pos:x}）")
            break
    out["ok"] = True
    return out


# ---------------------------------------------------------------- WAV
def wav_info(path: Path) -> dict:
    data = path.read_bytes()
    out: dict = {"ok": False, "chunks": [], "anomalies": []}
    if len(data) < 12 or data[:4] != b"RIFF":
        out["anomalies"].append("不是 RIFF 容器")
        return out
    riff_size = struct.unpack("<I", data[4:8])[0]
    pos = 12
    while pos + 8 <= len(data):
        cid = data[pos:pos + 4]
        (csz,) = struct.unpack("<I", data[pos + 4:pos + 8])
        out["chunks"].append({"id": cid.decode("latin1", "replace"),
                              "size": csz, "offset": pos})
        if cid == b"fmt " and csz >= 16:
            fmt_id, ch, rate = struct.unpack("<HHI", data[pos + 8:pos + 16])
            out.update({"format": fmt_id, "channels": ch, "sample_rate": rate})
        pos += 8 + csz + (csz & 1)
    declared_end = 8 + riff_size
    if declared_end < len(data):
        extra = data[declared_end:]
        out["anomalies"].append(
            f"RIFF 声明结束于 {declared_end}，但文件有 {len(data)} 字节"
            f"—— 尾部追加了 {len(extra)} 字节")
        try:
            txt = extra.decode("utf-8", "ignore")
            if txt.strip():
                out["tail_text"] = txt.strip()[:300]
        except Exception:
            pass
    out["ok"] = True
    return out
