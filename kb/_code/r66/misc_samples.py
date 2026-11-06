"""复做杂项和取证题：python misc_samples.py 题目编号 原附件。需要 numpy 和 pycryptodome；Miniscule 另需 Zstandard 动态库。"""

import argparse
import json
import re
import struct
import wave
import xml.etree.ElementTree as ET
import zlib
from base64 import b64decode
from collections import Counter
from ctypes import CDLL, c_char, c_size_t, c_void_p
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import numpy as np
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


def get_wav(path):
    with wave.open(str(path)) as w:
        bits = w.getsampwidth()
        data = np.frombuffer(w.readframes(w.getnframes()), "u1" if bits == 1 else "<i2")
        samples = data.astype(float).reshape(-1, w.getnchannels())
        if bits == 1:
            samples -= 128
        return samples, w.getframerate()


def png_parts(data):
    assert data.startswith(bytes.fromhex("89504e470d0a1a0a"))
    offset = 8
    while offset + 12 <= len(data):
        length, name = struct.unpack_from(">I4s", data, offset)
        end = offset + 12 + length
        assert end <= len(data)
        yield name, data[offset + 8 : end - 4], end
        if name == b"IEND":
            return
        offset = end


def png_chunk(name, payload):
    return (
        struct.pack(">I", len(payload))
        + name
        + payload
        + struct.pack(">I", zlib.crc32(name + payload))
    )


def miniscule(path, args):
    data = path.read_bytes()
    parts = {name: payload for name, payload, _ in png_parts(data)}
    ihdr = bytearray(parts[b"IHDR"])
    width, height, bits, color, compress, filter_type, interlace = struct.unpack(
        ">IIBBBBB", ihdr
    )
    encoded = parts[b"IDAT"]
    assert compress == 1 and encoded.startswith(bytes.fromhex("28b52ffd"))
    assert (bits, color, filter_type, interlace) == (8, 2, 0, 0)
    expected = height * (3 * width + 1)
    lib = CDLL(str(args.zstd))
    decompress = lib.ZSTD_decompress
    decompress.argtypes = [c_void_p, c_size_t, c_void_p, c_size_t]
    decompress.restype = c_size_t
    out = bytearray(expected)
    n = decompress(
        (c_char * expected).from_buffer(out), expected, encoded, len(encoded)
    )
    assert n == expected
    assert all(out[i] in range(5) for i in range(0, expected, 3 * width + 1))
    ihdr[10] = 0
    normalized = (
        data[:8]
        + png_chunk(b"IHDR", ihdr)
        + png_chunk(b"IDAT", zlib.compress(out))
        + png_chunk(b"IEND", b"")
    )
    assert (
        zlib.decompress(dict((k, v) for k, v, _ in png_parts(normalized))[b"IDAT"])
        == out
    )
    if args.output:
        args.output.write_bytes(normalized)
    result = {"行数据字节数": len(out), "尺寸": [width, height], "zlib 回读通过": True}

    return result


def nothing_to_see(path, args):
    data = path.read_bytes()
    end = list(png_parts(data))[-1][2]
    assert data[end : end + 4] == b"PK\x03\x04"
    parts = list(png_parts(data))
    title = next(
        v.split(b"\0", 1)[1]
        for k, v, _ in parts
        if k == b"tEXt" and v.startswith(b"Title\0")
    )
    with ZipFile(BytesIO(data[end:])) as z:
        answer = z.read("flag.txt", pwd=title)
    assert re.fullmatch(rb"[A-Za-z0-9_]+\{[^{}\r\n]+\}", answer.strip())
    result = {
        "ZIP 起点": end,
        "ZIP 字节数": len(data) - end,
        "解压校验通过": True,
        "解出的文件字节数": len(answer),
    }

    return result


def beep_boop_robot(path, args):
    samples, rate = get_wav(path)
    v = samples[:, 0]
    window = round(rate * 0.005)
    rows = v[: len(v) // window * window].reshape(-1, window)
    rms = np.sqrt(np.mean(rows * rows, axis=1))
    on = rms > rms.max() * 0.25
    bounds = np.r_[0, 1 + np.flatnonzero(np.diff(on)), len(on)]
    groups = [""]
    for a, b in zip(bounds, bounds[1:]):
        length = (b - a) * window / rate
        if on[a]:
            groups[-1] += "-" if length > 0.08 else "."
        elif length > 0.1 and groups[-1]:
            if length > 0.3:
                groups.extend(["/", ""])
            else:
                groups.append("")
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    codes = ".- -... -.-. -.. . ..-. --. .... .. .--- -.- .-.. -- -. --- .--. --.- .-. ... - ..- ...- .-- -..- -.-- --.. ----- .---- ..--- ...-- ....- ..... -.... --... ---.. ----."
    mapping = dict(zip(codes.split(), letters))
    mapping.update(
        {
            ".-.-.-": ".",
            "--..--": ",",
            "..--..": "?",
            "-....-": "-",
            "..--.-": "_",
            "-..-.": "/",
        }
    )
    plain = "".join(" " if g == "/" else mapping.get(g, "?") for g in groups if g)
    result = {
        "morse_symbols": sum(bool(x) and x != "/" for x in groups),
        "unrecognized": plain.count("?"),
        "word_count": len(plain.split()),
        "leading_english_confirmed": plain.startswith("HI "),
    }
    return result


def wacky_recipe(path, args):
    text = path.read_text(encoding="utf-8")
    ingredients = {}
    for line in text.split("Ingredients.\n", 1)[1].split("\n\n", 1)[0].splitlines():
        q, _, name = line.split(" ", 2)
        ingredients[name] = (
            {"pain": (1, 0, 0), "effort": (0, 1, 0)}[name]
            if q == "??"
            else (0, 0, int(q))
        )
    stack = []
    for line in text.split("Method.\n", 1)[1].splitlines():
        match = re.fullmatch(
            r"(Put|Add|Combine|Remove) (.+) (?:into|to|from) 1st mixing bowl\.", line
        )
        if not match:
            continue
        op, name = match.groups()
        term = ingredients[name]
        if op == "Put":
            stack.append(term)
        elif op == "Combine":
            a, b, value = stack[-1]
            assert a == b == 0 and name == "pain"
            stack[-1] = (value, 0, 0)
        else:
            sign = 1 if op == "Add" else -1
            stack[-1] = tuple(x + sign * y for x, y in zip(stack[-1], term))
    prefix = b"DUCTF{"
    candidates = []
    for seq in (stack, stack[::-1]):
        for pain in range(256):
            for effort in range(256):
                if any(
                    a * pain + b * effort + c != e for (a, b, c), e in zip(seq, prefix)
                ):
                    continue
                values = [a * pain + b * effort + c for a, b, c in seq]
                if values[-1] == 125 and all(32 <= v <= 126 for v in values):
                    candidates.append((pain, effort))
    result = {
        "linear_expressions": len(stack),
        "matching_flag_format_candidates": len(candidates),
    }
    return result


def bad_policies(path, args):
    with ZipFile(path) as z:
        attrs = []
        for n in z.namelist():
            if n.endswith("Groups.xml"):
                attrs.extend(
                    x.attrib for x in ET.fromstring(z.read(n)).iter("Properties")
                )
        passwords = [x["cpassword"] for x in attrs if x.get("cpassword")]
        key = bytes.fromhex(
            "4e9906e8fcb66cc9faf49310620ffee8f496e806cc057990209b09a433b66c1b"
        )
        matches = 0
        for pw in passwords:
            raw = b64decode(pw + "=" * (-len(pw) % 4), validate=True)
            decoded = unpad(AES.new(key, AES.MODE_CBC, iv=bytes(16)).decrypt(raw), 16)
            assert (
                AES.new(key, AES.MODE_CBC, iv=bytes(16)).encrypt(pad(decoded, 16))
                == raw
            )
            matches += bool(
                re.fullmatch(r"[A-Za-z0-9_]+\{[^\r\n]+\}", decoded.decode("utf-16le"))
            )
        result = {
            "gpp_groups_password_fields": len(passwords),
            "matching_flag_format_candidates": matches,
        }
    return result


def usb_hacker(path, args):
    data = path.read_bytes()
    i = 0
    counts = Counter()
    reports = []
    while i + 12 <= len(data):
        kind, size = struct.unpack_from("<II", data, i)
        assert (
            size >= 12
            and i + size <= len(data)
            and struct.unpack_from("<I", data, i + size - 4)[0] == size
        )
        if kind == 1:
            assert struct.unpack_from("<H", data, i + 8)[0] == 220
        if kind == 6:
            captured = struct.unpack_from("<I", data, i + 20)[0]
            packet = data[i + 28 : i + 28 + captured]
            assert len(packet) >= 64
            event, typ, ep, device = packet[8:12]
            size_cap = struct.unpack_from("<I", packet, 36)[0]
            counts[(chr(event), typ, ep, size_cap)] += 1
            if (event, typ, ep, device, size_cap) == (ord("C"), 1, 0x81, 3, 8):
                reports.append(packet[64:72])
        i += size
    keys = {
        **dict(zip(range(4, 30), "abcdefghijklmnopqrstuvwxyz")),
        **dict(zip(range(30, 40), "1234567890")),
        40: "\n",
        42: "\b",
        44: " ",
        45: "-",
        46: "=",
        47: "[",
        48: "]",
        49: "\\",
        51: ";",
        52: "'",
        53: "\x60",
        54: ",",
        55: ".",
        56: "/",
    }
    shift = dict(zip("1234567890-=[]\\;\x27\x60,./", '!@#$%^&*()_+{}|:"~<>?'))
    typed = ""
    last = set()
    caps = False
    for report in reports:
        now = set(report[2:]) - {0}
        for k in report[2:]:
            if k == 0 or k in last:
                continue
            if k == 57:
                caps = not caps
                continue
            value = keys.get(k, "?")
            if value == "\b":
                typed = typed[:-1]
                continue
            shifted = bool(report[0] & 0x22)
            if value.isalpha():
                value = value.upper() if shifted != caps else value
            elif shifted:
                value = shift.get(value, value)
            typed += value
        last = now
    result = {
        "linux_usbmon_link_type": 220,
        "interrupt_input_reports": len(reports),
        "unmapped_keys": typed.count("?"),
        "matched_flag_format": bool(re.search(r"[A-Za-z0-9_]+\{[^{}\r\n]+\}", typed)),
    }
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "case",
        choices=[
            "miniscule",
            "nothing-to-see",
            "beep-boop-robot",
            "wacky-recipe",
            "bad-policies",
            "usb-hacker",
        ],
    )
    parser.add_argument("file", type=Path, help="赛题原附件")
    parser.add_argument("--zstd", help="Miniscule 使用的 Zstandard 动态库路径")
    parser.add_argument("--output", type=Path, help="可选：另存修复后的 PNG")
    args = parser.parse_args()
    if args.case == "miniscule" and not args.zstd:
        parser.error("复做 Miniscule 请用 --zstd 指定 Zstandard 动态库。")
    print(
        json.dumps(
            globals()[args.case.replace("-", "_")](args.file, args), ensure_ascii=False
        )
    )
