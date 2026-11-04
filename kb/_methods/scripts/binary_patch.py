#!/usr/bin/env python3
"""逆向补丁与 keygen：字节级判断 x86/x64 跳转、生成 patch 字节、示范 crackme 的注册机。

依赖：纯标准库，离线。patch 只写 `<原名>.patched`，绝不覆盖原文件、不删文件。
用途：crackme 题里"成功/失败只差一条 jz"时，快速判断目标偏移的指令类型并出补丁。

用法：
  python binary_patch.py --keygen --target 0x1A2B --length 16
  python binary_patch.py --check-serial 'AAAAAAAAAAAAAA??'
  python binary_patch.py --patch --file chall.bin --offset 0x1140 --mode jz2jnz
  python binary_patch.py --dis-bytes 740a300000
  python binary_patch.py --selftest
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

# 条件跳转 8 位：opcode -> (助记符, 反转后 opcode)
JCC8 = {
    0x74: ("jz", 0x75), 0x75: ("jnz", 0x74),
    0x72: ("jb", 0x73), 0x73: ("jnb", 0x72),
    0x7C: ("jl", 0x7D), 0x7D: ("jge", 0x7C),
    0x7E: ("jle", 0x7F), 0x7F: ("jg", 0x7E),
}
JCC32 = {0x84: ("jz", 0x85), 0x85: ("jnz", 0x84),
         0x82: ("jb", 0x83), 0x83: ("jnb", 0x82),
         0x8C: ("jl", 0x8D), 0x8D: ("jge", 0x8C),
         0x8E: ("jle", 0x8F), 0x8F: ("jg", 0x8E)}
NOP = 0x90
TRUE_RET = b"\xB8\x01\x00\x00\x00\xC3"   # mov eax,1; ret
FALSE_RET = b"\x31\xC0\xC3"                # xor eax,eax; ret  (x86-64)
MODES = ("jz2jnz", "jmp", "nop-call", "true-ret")


def classify_jump(b: bytes) -> dict:
    """给一段字节，判断开头是不是条件跳转 / 调用 / nop 填充。"""
    if not b:
        raise ValueError("空字节流")
    b0 = b[0]
    if b0 in JCC8:
        return {"kind": "jcc8", "mnemonic": JCC8[b0][0], "len": 2,
                "rel": b[1] - 256 if (len(b) > 1 and b[1] > 127) else (b[1] if len(b) > 1 else None)}
    if b0 == 0x0F and len(b) > 1 and b[1] in JCC32:
        return {"kind": "jcc32", "mnemonic": JCC32[b[1]][0], "len": 6,
                "rel": int.from_bytes(b[2:6], "little", signed=True) if len(b) >= 6 else None}
    if b0 == 0xEB:
        return {"kind": "jmp8", "mnemonic": "jmp", "len": 2,
                "rel": b[1] - 256 if len(b) > 1 and b[1] > 127 else (b[1] if len(b) > 1 else None)}
    if b0 == 0xE8:
        return {"kind": "call", "mnemonic": "call", "len": 5,
                "rel": int.from_bytes(b[1:5], "little", signed=True) if len(b) >= 5 else None}
    if b0 == NOP:
        return {"kind": "nop", "mnemonic": "nop", "len": 1, "rel": None}
    return {"kind": "other", "mnemonic": None, "len": 1, "rel": None}


def patch_bytes(mode: str, data: bytes, off: int) -> bytes:
    """返回改写后的整段字节（不改原对象）。"""
    if mode not in MODES:
        raise ValueError("未知 --mode %r，可选 %s" % (mode, "/".join(MODES)))
    if not isinstance(off, int) or off < 0 or off >= len(data):
        raise ValueError("offset %r 越界（文件长度 %d）" % (off, len(data)))
    out = bytearray(data)
    if mode == "true-ret":
        need = len(TRUE_RET)
        if off + need > len(out):
            raise ValueError("空间不足：true-ret 需要 %d 字节" % need)
        out[off:off + need] = TRUE_RET
        return bytes(out)
    info = classify_jump(bytes(out[off:]))
    if mode == "jz2jnz":
        if info["kind"] == "jcc8":
            out[off] = JCC8[out[off]][1]
        elif info["kind"] == "jcc32":
            out[off + 1] = JCC32[out[off + 1]][1]
        else:
            raise ValueError("偏移 0x%x 处不是条件跳转（识别为 %s）" % (off, info["kind"]))
        return bytes(out)
    if mode == "jmp":
        if info["kind"] == "jcc8":
            out[off] = 0xEB
        elif info["kind"] == "jcc32":
            if off + 6 > len(out):
                raise ValueError("rel32 跳转空间不足")
            # 0F 8x rel32 -> E9 rel32（同长度，位移不变），前面那个 0F 用 90 覆盖
            out[off] = 0xE9
            out[off + 1:off + 5] = _rel32_from_jcc32(bytes(data[off:]))
            out[off + 5] = NOP
        else:
            raise ValueError("偏移 0x%x 处不是条件跳转（识别为 %s）" % (off, info["kind"]))
        return bytes(out)
    # nop-call
    if info["kind"] != "call":
        raise ValueError("偏移 0x%x 处不是 call（识别为 %s），nop-call 只用于 E8 rel32" % (off, info["kind"]))
    if off + 5 > len(out):
        raise ValueError("call 指令被截断")
    out[off:off + 5] = b"\x90" * 5
    return bytes(out)


def _rel32_from_jcc32(b6: bytes) -> bytes:
    """0F 8x <rel32> -> E9 <rel32'>：指令长度 6 -> 5，位移需 -1。"""
    rel = int.from_bytes(b6[2:6], "little", signed=True)
    return (rel - 1).to_bytes(4, "little", signed=True)


def checksum(serial: str) -> int:
    if not isinstance(serial, str) or not serial:
        raise ValueError("serial 为空")
    return sum(ord(c) * (i + 1) for i, c in enumerate(serial))


def keygen(target: int, length: int = 8, base: int = 0x30) -> str:
    """示范 crackme：sum(s[i]*(i+1)) == target，返回可打印 serial。

    权重：下标 i 的字节权重是 (i+1)，所以 s[0] 权重 1、s[1] 权重 2、s[-1] 权重 length。
    固定 s[2..length-2] 为 base，只用 s[0]/s[1]/s[-1] 三个自由度凑 target（三个未知数
    一个方程，可打印区间足够宽时必然有解）。
    """
    if not isinstance(target, int) or target <= 0:
        raise ValueError("target 必须是正整数")
    if not 3 <= length <= 64:
        raise ValueError("length 需在 3..64")
    if not 32 <= base <= 126:
        raise ValueError("base 需是可打印字符 ASCII(32..126)")
    w = length
    # 只统计真正固定的中段：下标 2..length-2
    rest = sum(base * (i + 1) for i in range(2, length - 1))
    lo = 32 + 64 + 32 * w + rest
    hi = 126 + 252 + 126 * w + rest
    if not lo <= target <= hi:
        raise ValueError(
            "target=0x%X 超出 length=%d、字符集 32..126 的可达区间 [0x%X,0x%X]；"
            "请调整 --length 或 --base" % (target, length, lo, hi))
    for v_last in range(32, 127):
        rem = target - v_last * w - rest     # 剩 b0*1 + b1*2
        for b1 in range(32, 127):
            b0 = rem - b1 * 2
            if 32 <= b0 <= 126:
                out = [b0, b1] + [base] * (length - 2)
                out[-1] = v_last              # 末字节必须最后覆盖
                s = "".join(map(chr, out))
                if len(s) == length and checksum(s) == target:
                    return s
    raise ValueError("target=0x%X 在 length=%d 下反解失败" % (target, length))


def verify_serial(serial: str, target: int) -> bool:
    if not isinstance(target, int) or target <= 0:
        raise ValueError("target 必须是正整数")
    try:
        return checksum(serial) == target
    except ValueError:
        return False


def _read_file(path: str) -> bytes:
    p = Path(path)
    if not p.is_file():
        raise ValueError("文件不存在：%s" % path)
    return p.read_bytes()


def selftest(rng: random.Random | None = None) -> int:
    rng = rng or random.Random(20261103)
    fails = []

    # 1. 正常路径：keygen 生成的 serial 必然通过校验
    s = keygen(0x1A2B, 16)
    if not verify_serial(s, 0x1A2B):
        fails.append("case1: keygen 结果未通过校验 %r" % s)
    if len(s) != 16 or not all(32 <= ord(c) <= 126 for c in s):
        fails.append("case1: keygen 结果长度/可打印性不符 %r" % s)

    # 2. 正常路径：跳转分类与 patch
    if classify_jump(b"\x74\x0a")["mnemonic"] != "jz":
        fails.append("case2: 0x74 应识别为 jz")
    pd = patch_bytes("jz2jnz", b"\x74\x0a\x90\x90", 0)
    if pd[0] != 0x75:
        fails.append("case2: jz2jnz 未生效 %r" % pd)
    pj = patch_bytes("jmp", b"\x74\x0a\x90\x90", 0)
    if pj[0] != 0xEB:
        fails.append("case2: jmp 未生效 %r" % pj)
    pn = patch_bytes("nop-call", b"\xE8\x11\x22\x33\x44\x90", 0)
    if pn[:5] != b"\x90" * 5:
        fails.append("case2: nop-call 未生效 %r" % pn)
    pr = patch_bytes("true-ret", b"\x00" * 8, 0)
    if pr[:6] != TRUE_RET:
        fails.append("case2: true-ret 未生效 %r" % pr)
    p32 = patch_bytes("jmp", b"\x0F\x84\x10\x00\x00\x00", 0)
    if p32[0] != 0xE9:
        fails.append("case2: rel32 jz->jmp 未生效 %r" % p32)

    # 3. 边界拒绝：偏移越界 / 非跳转处 patch / 非法 mode / target 非法
    for bad in [("jz2jnz", b"\x74\x0a", 5), ("jz2jnz", b"\x74\x0a", -1)]:
        try:
            patch_bytes(bad[0], bad[1], bad[2])
            fails.append("case3: 越界 offset %r 未被拒绝" % (bad[2],))
        except ValueError:
            pass
    try:
        patch_bytes("jz2jnz", b"\xE8\x00\x00\x00\x00", 0)
        fails.append("case3: call 处做 jz2jnz 未被拒绝")
    except ValueError:
        pass
    try:
        patch_bytes("nope", b"\x74\x0a", 0)
        fails.append("case3: 非法 mode 未被拒绝")
    except ValueError:
        pass
    for t in [0, -5]:
        try:
            keygen(t, 16)
            fails.append("case3: 非法 target %r 未被拒绝" % t)
        except ValueError:
            pass

    # 4. 参数不足：main 无参数退出码 2
    try:
        main([])
        fails.append("case4: 无参数应报参数不足")
    except SystemExit as e:
        if e.code != 2:
            fails.append("case4: 参数不足退出码应 2，实际 %r" % e.code)

    # 5. 固定 seed 随机：多组 target 都能生成并通过校验
    for _ in range(8):
        t = rng.randrange(0x1900, 0x1F00)
        r = keygen(t, 16)
        if checksum(r) != t:
            fails.append("case5: 随机 target 0x%x 生成失败 %r" % (t, r))
            break

    for f in fails:
        print("FAIL %s" % f, file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 5/5（keygen 反解通过、跳转分类与四种 patch、越界/非跳转拒绝、参数不足、固定 seed 随机）")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="crackme 补丁字节与 keygen（离线）")
    ap.add_argument("--keygen", action="store_true")
    ap.add_argument("--check-serial")
    ap.add_argument("--target", type=lambda s: int(s, 0), default=0x1A2B)
    ap.add_argument("--length", type=int, default=16)
    ap.add_argument("--patch", action="store_true")
    ap.add_argument("--file")
    ap.add_argument("--offset", type=lambda s: int(s, 0))
    ap.add_argument("--mode", choices=MODES)
    ap.add_argument("--dis-bytes", help="十六进制字节串，判断指令类型")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    try:
        if args.keygen:
            s = keygen(args.target, args.length)
            print(json.dumps({"serial": s, "sum": checksum(s), "target": args.target},
                             ensure_ascii=False) if args.json else
                  "%s\n(sum=0x%X)" % (s, checksum(s)))
            return 0
        if args.check_serial is not None:
            ok = verify_serial(args.check_serial, args.target)
            print(json.dumps({"serial": args.check_serial, "sum": checksum(args.check_serial),
                              "target": args.target, "ok": ok}, ensure_ascii=False)
                  if args.json else ("通过" if ok else "不通过"))
            return 0 if ok else 1
        if args.patch:
            if not args.file or args.offset is None or not args.mode:
                ap.error("--patch 需要 --file --offset --mode")
            data = _read_file(args.file)
            new = patch_bytes(args.mode, data, args.offset)
            dst = Path(args.file + ".patched")
            dst.write_bytes(new)
            print(json.dumps({"out": dst.name, "mode": args.mode,
                              "orig": data[args.offset:args.offset + 8].hex(),
                              "new": new[args.offset:args.offset + 8].hex()}, ensure_ascii=False)
                  if args.json else "已写出 %s（%s）" % (dst.name, args.mode))
            return 0
        if args.dis_bytes:
            h = "".join(args.dis_bytes.split())
            if len(h) % 2:
                raise ValueError("十六进制长度必须为偶数")
            b = bytes.fromhex(h)
            info = classify_jump(b)
            if not args.json:
                print("类型：%s  助记符：%s  长度：%d  相对位移：%r"
                      % (info["kind"], info["mnemonic"], info["len"], info["rel"]))
                print("可 patch：" + ("是" if info["kind"].startswith(("jcc", "call")) else "否"))
            else:
                print(json.dumps(info, ensure_ascii=False))
            return 0
    except (ValueError, OSError) as e:
        print("错误：%s" % e, file=sys.stderr)
        return 2
    ap.error("需要 --keygen / --check-serial / --patch / --dis-bytes 之一，或用 --selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main())
