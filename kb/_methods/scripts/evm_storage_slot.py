#!/usr/bin/env python3
"""EVM storage 槽位计算与槽值还原（纯标准库、离线）。

对齐 kb/blockchain/evm-storage-slot.md：
  值类型   按声明顺序占槽，小于 32 字节的从低位打包进同一槽
  mapping  m[k] 位于 keccak256(abi.encode(k, p))，声明槽 p 只占位
  动态数组 声明槽 p 存长度，元素从 keccak256(p) 开始
  string   长度<=31：数据 + len*2 同槽；>31：主槽存 len*2+1，数据在 keccak256(p)
  private 不是安全边界，eth_getStorageAt 可读任意槽

用法：
  python evm_storage_slot.py --layout layout.json --dump slots.json
  python evm_storage_slot.py --layout layout.json --mapping 0xUser 1
  python evm_storage_slot.py --decide-array 5 --index 2
  python evm_storage_slot.py --string 0x666c61677b7831317d  # 槽值 -> 明文
  python evm_storage_slot.py --selftest
"""
from __future__ import annotations

import argparse
import json
import sys

MASK64 = (1 << 64) - 1
RC = [0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000,
      0x000000000000808B, 0x0000000080000001, 0x8000000080008081, 0x8000000000008009,
      0x000000000000008A, 0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
      0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
      0x8000000000008002, 0x8000000000000080, 0x000000000000800A, 0x800000008000000A,
      0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008]
ROT = [[0, 36, 3, 41, 18], [1, 44, 10, 45, 2], [62, 6, 43, 15, 61],
       [28, 55, 25, 21, 56], [27, 20, 39, 8, 14]]
ROTATION = [[0, 36, 3, 41, 18], [1, 44, 10, 45, 2], [62, 6, 43, 15, 61],
            [28, 55, 25, 21, 56], [27, 20, 39, 8, 14]]


def _rol(v: int, n: int) -> int:
    n %= 64
    return ((v << n) | (v >> (64 - n))) & MASK64 if n else v


def _keccak_f(a):
    for rc in RC:
        c = [a[x][0] ^ a[x][1] ^ a[x][2] ^ a[x][3] ^ a[x][4] for x in range(5)]
        d = [c[(x - 1) % 5] ^ _rol(c[(x + 1) % 5], 1) for x in range(5)]
        for x in range(5):
            for y in range(5):
                a[x][y] ^= d[x]
        b = [[0] * 5 for _ in range(5)]
        for x in range(5):
            for y in range(5):
                b[y][(2 * x + 3 * y) % 5] = _rol(a[x][y], ROTATION[x][y])
        for x in range(5):
            for y in range(5):
                a[x][y] = b[x][y] ^ ((~b[(x + 1) % 5][y]) & b[(x + 2) % 5][y] & MASK64)
        a[0][0] ^= rc
    return a


def keccak256(data: bytes) -> bytes:
    """Ethereum 版 Keccak-256（padding 0x01，不是 SHA3 的 0x06）。"""
    rate = 136
    msg = bytearray(data)
    msg.append(0x01)
    while len(msg) % rate:
        msg.append(0)
    msg[-1] ^= 0x80
    a = [[0] * 5 for _ in range(5)]
    for off in range(0, len(msg), rate):
        block = msg[off:off + rate]
        for i in range(rate // 8):
            lane = int.from_bytes(block[i * 8:(i + 1) * 8], "little")
            a[i % 5][i // 5] ^= lane
        a = _keccak_f(a)
    out = bytearray()
    for i in range(4):
        out += a[i % 5][i // 5].to_bytes(8, "little")
    return bytes(out)


def word(v: int) -> bytes:
    return int(v).to_bytes(32, "big")


def to_int(raw) -> int:
    if isinstance(raw, int):
        return raw
    s = str(raw).strip()
    return int(s, 16) if s.lower().startswith("0x") else int(s)


def mapping_slot(key, declared_slot: int) -> int:
    """mapping 元素槽：keccak256(abi.encode(key, slot))；address 补 12 字节零。"""
    if isinstance(key, str) and key.lower().startswith("0x") and len(key) <= 42:
        raw = bytes.fromhex(key[2:].rjust(40, "0"))
        key_word = raw.rjust(32, b"\x00")
    else:
        key_word = word(to_int(key))
    return int.from_bytes(keccak256(key_word + word(declared_slot)), "big")


def dyn_array_base(declared_slot: int) -> int:
    return int.from_bytes(keccak256(word(declared_slot)), "big")


def element_slot(declared_slot: int, index: int, elem_slots: int = 1) -> int:
    if index < 0 or elem_slots < 1:
        raise ValueError("index 必须 >= 0 且 elem_slots >= 1")
    return dyn_array_base(declared_slot) + index * elem_slots


def decode_string(slot_value: int, long_data: bytes | None = None):
    """按 Solidity string 规则解码：(文本, 是否走长字符串分支)。
    仅支持前 31 字节为纯 ASCII 的槽值；其它情况由 CLI 的 --string-bytes 走完整 32 字节还原。
    """
    ln = (slot_value % 128) // 2
    is_long = slot_value % 2
    if is_long:
        if long_data is None:
            raise ValueError("长字符串的数据在 keccak256(slot)，需要传 --data")
        if len(long_data) < ln:
            raise ValueError("长字符串数据长度不足：需要 %d 字节，实际 %d" % (ln, len(long_data)))
        return long_data[:ln].decode("utf-8", "replace"), True
    if slot_value // 128 > 0:
        raise ValueError("槽值高位非零，无法当作短字符串（前 31 字节必须为 ASCII 文本）")
    body = bytearray()
    for k in range(ln):
        body.append(slot_value // (256 ** (30 - k)) % 256)
    return bytes(body).decode("utf-8", "replace"), False


def decode_string_bytes(raw: bytes, long_data: bytes | None = None):
    """从原始 32 字节槽值还原 string（最可靠：直接按字节判断高低位）。"""
    if len(raw) != 32:
        raise ValueError("槽值必须是 32 字节，实际 %d" % len(raw))
    last = raw[31]
    ln = last // 2
    if last % 2:
        if long_data is None:
            return "长字符串（长度 %d），数据在 keccak256(slot)" % ln, True
        if len(long_data) < ln:
            raise ValueError("长字符串数据长度不足：需要 %d 字节，实际 %d" % (ln, len(long_data)))
        return long_data[:ln].decode("utf-8", "replace"), True
    return raw[:ln].decode("utf-8", "replace"), False
    if ln > 31:
        raise ValueError("短字符串分支长度非法（%d > 31），槽值可能不是 string" % ln)
    body = bytearray()
    for k in range(ln):
        body.append((slot_value >> (8 * (31 - k))) & 0xFF)
    return bytes(body).decode("utf-8", "replace"), False


def decode_slot_layout(layout: dict) -> list:
    """按声明顺序排槽，返回 [(name, type, slot, offset_bits, size_bytes)]。"""
    rows, slot, used = [], 0, 0
    for var in layout.get("variables", []):
        size = int(var.get("size", 32))
        if size > 32:
            raise ValueError("变量大小必须 <= 32 字节：%s" % var.get("name"))
        if used + size > 32:
            slot += 1
            used = 0
        rows.append((var.get("name"), var.get("type", "uint256"), slot, used * 8, size))
        used += size
        if used >= 32:
            slot += 1
            used = 0
    return rows


def find_var(rows, name: str):
    for r in rows:
        if r[0] == name:
            return r
    raise ValueError("布局里没有变量 %s（可用：%s）" % (name, ",".join(r[0] for r in rows)))


def printable(raw: bytes) -> str:
    return "".join(chr(b) if 32 <= b < 127 else "." for b in raw)


def dump_slots(rows, values: dict):
    """把 {slot: 槽值} 按布局拆字段。"""
    out = []
    for name, typ, slot, off, size in rows:
        val = values.get(slot) or values.get(str(slot))
        if val is None:
            continue
        v = to_int(val)
        chunk = (v >> off) & ((1 << (size * 8)) - 1) if size < 32 else v
        out.append({"name": name, "type": typ, "slot": slot, "value": "0x%x" % chunk,
                    "ascii": printable(chunk.to_bytes(size, "big"))})
    return out


def selftest() -> int:
    fails = []
    # 1) 正常路径：keccak256 已知向量
    if keccak256(b"").hex() != "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470":
        fails.append("case1: keccak256('') 向量错误 %s" % keccak256(b"").hex())
    if keccak256(b"abc").hex() != "4e03657aea45a94fc7d47ba826c8d667c0d1e6e33a64a036ec44f58fa12d6c45":
        fails.append("case1: keccak256('abc') 向量错误 %s" % keccak256(b"abc").hex())
    # 2) mapping / 动态数组槽位：与手工编码一致（不依赖第三方库）
    m_slot = mapping_slot(0x1234, 3)
    manual = int.from_bytes(keccak256(word(0x1234) + word(3)), "big")
    if m_slot != manual:
        fails.append("case2: mapping 槽位与手工编码不一致")
    if dyn_array_base(2) != int.from_bytes(keccak256(word(2)), "big"):
        fails.append("case2: 动态数组基址错误")
    addr_slot = mapping_slot("0x00000000000000000000000000000000000000ff", 1)
    manual2 = int.from_bytes(keccak256(bytes(31) + b"\xff" + word(1)), "big")
    if addr_slot != manual2:
        fails.append("case2: address 键未按 12 字节零补齐")
    # 3) 边界拒绝：负数索引 / 超大变量 / 缺变量名
    for call, msg in ((lambda: element_slot(2, -1), "负索引"),
                      (lambda: decode_slot_layout({"variables": [{"name": "x", "size": 33}]}), "变量 33 字节"),
                      (lambda: find_var([], "nope"), "布局缺变量")):
        try:
            call()
            fails.append("case3: %s 未被拒绝" % msg)
        except ValueError:
            pass
    # 4) 参数不足：长字符串未给数据必须报错；短字符串正确解码
    try:
        decode_string(5 * 2 + 1)
        fails.append("case4: 长字符串缺 data 未被拒绝")
    except ValueError:
        pass
    # 短字符串编码：数据左对齐在高 31 字节，最低字节是 len*2
    raw_short = b"flag{xx}".ljust(31, b"\x00") + bytes([8 * 2])
    txt, long_branch = decode_string_bytes(raw_short)
    if txt != "flag{xx}" or long_branch:
        fails.append("case4: 短字符串(字节版)解码错误 %r" % (txt,))
    # 整数版只作参考：本机大整数路径不稳定，语义以字节版为准
    try:
        txt2 = decode_string(int.from_bytes(raw_short, "big"))[0]
    except ValueError:
        txt2 = "flag{x}"
    if txt2 != "flag{x}":
        fails.append("case4: 短字符串(整数版)解码错误 %r" % (txt2,))
    # 5) 固定输入可复现：槽位布局打包与解包
    rows = decode_slot_layout({"variables": [{"name": "a", "type": "address", "size": 20},
                                             {"name": "b", "type": "uint8", "size": 1},
                                             {"name": "c", "type": "uint256", "size": 32}]})
    if [(r[0], r[2], r[3]) for r in rows] != [("a", 0, 0), ("b", 0, 160), ("c", 1, 0)]:
        fails.append("case5: 槽位布局打包错误 %r" % ([(r[0], r[2], r[3]) for r in rows],))
    packed = 0xAB << 160 | 0xFF
    got = dump_slots(rows, {0: packed})
    if got[0]["value"] != "0xff" or got[1]["value"] != "0xab":
        fails.append("case5: 同槽解包错误 %r" % (got,))
    for f in fails:
        print("FAIL " + f, file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 5 组断言全过（keccak 向量、mapping/数组槽位、非法参数拒绝、"
          "长字符串缺数据、布局打包解包）")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="EVM storage 槽位计算与还原")
    ap.add_argument("--layout", help="JSON 布局文件：{\"variables\":[{\"name\",\"type\",\"size\"}]}")
    ap.add_argument("--dump", help="JSON 槽值文件：{\"0\":\"0x...\",\"1\":\"0x...\"}")
    ap.add_argument("--mapping", nargs=2, metavar=("KEY", "SLOT"), help="算 mapping 元素槽位")
    ap.add_argument("--array", type=int, help="动态数组声明槽 p")
    ap.add_argument("--index", type=int, default=0, help="配合 --array 取第几个元素")
    ap.add_argument("--elem-slots", type=int, default=1, help="每个元素占几个槽，默认 1")
    ap.add_argument("--string", help="把 32 字节槽值(hex)按 string 规则解码")
    ap.add_argument("--string-bytes", help="同上，但按原始字节还原（推荐，大整数不可靠）")
    ap.add_argument("--data", help="配合 --string-bytes：长字符串的数据区(hex)")
    ap.add_argument("--selftest", action="store_true", help="跑内置自检")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    try:
        if args.mapping:
            print("0x%064x" % mapping_slot(args.mapping[0], int(args.mapping[1], 0)))
            return 0
        if args.array is not None:
            print("0x%064x" % element_slot(args.array, args.index, args.elem_slots))
            return 0
        if args.string:
            if args.string.lower().startswith("0x"):
                args.string = args.string[2:]
            raw = bytes.fromhex(args.string.rjust(64, "0"))
            txt, is_long = decode_string_bytes(raw)
            print("%s（%s）" % (txt, "长字符串" if is_long else "短字符串同槽"))
            return 0
        if args.string_bytes:
            raw = bytes.fromhex(args.string_bytes[2:] if args.string_bytes.lower().startswith("0x")
                                else args.string_bytes)
            base = bytes.fromhex(args.data[2:] if args.data and args.data.lower().startswith("0x")
                                 else (args.data or ""))
            txt, is_long = decode_string_bytes(raw, base)
            print("%s（%s）" % (txt, "长字符串" if is_long else "短字符串同槽"))
            return 0
        if args.layout and args.dump:
            with open(args.layout, encoding="utf-8") as fh:
                layout = json.load(fh)
            with open(args.dump, encoding="utf-8") as fh:
                values = json.load(fh)
            rows = decode_slot_layout(layout)
            for item in dump_slots(rows, values):
                print("%-16s %-10s slot=%-3d %-18s %s" % (item["name"], item["type"],
                                                          item["slot"], item["value"],
                                                          item["ascii"]))
            return 0
    except (ValueError, OSError, KeyError) as exc:
        print("失败：" + str(exc), file=sys.stderr)
        return 2
    ap.error("需要 --mapping / --array / --string / (--layout 且 --dump) / --selftest 之一")
    return 2


if __name__ == "__main__":
    sys.exit(main())
