#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pyc 逆向辅助：magic 判版本 / 头部对齐 / 常量挖矿 / 魔改 opcode 还原。

纯标准库、离线、只读：只解析字节，绝不 exec/marshal.loads 之外的执行被分析代码。
"""
import argparse
import dis
import json
import marshal
import sys
import types

# magic(4B) -> 版本；表来自 CPython importlib/_bootstrap_external.py 的 MAGIC_NUMBER 常见值
MAGIC_VERSIONS = {
    "030df30d": "2.7",
    "420d0d0a": "3.9",
    "550d0d0a": "3.8",
    "610d0d0a": "3.10",
    "6f0d0d0a": "3.10",
    "a70d0d0a": "3.11",
    "cb0d0d0a": "3.12",
    "f30d0d0a": "3.13",
}
HEADER_LEN_37_PLUS = 16
HEADER_LEN_33_36 = 12
HEADER_LEN_27 = 8


class PycError(ValueError):
    pass


def read_header(data):
    """返回 (magic_hex, version_str, header_len)。"""
    if not isinstance(data, (bytes, bytearray)) or len(data) < 4:
        raise PycError("文件太短，不足 4 字节 magic")
    magic = bytes(data[:4]).hex()
    ver = MAGIC_VERSIONS.get(magic)
    if ver is None:
        ver = "未知（请用 hexdump 对照 CPython importlib/_bootstrap_external.py 的 MAGIC_NUMBER）"
        hlen = None
    elif ver.startswith("2."):
        hlen = HEADER_LEN_27
    elif ver in ("3.3", "3.4", "3.5", "3.6"):
        hlen = HEADER_LEN_33_36
    else:
        hlen = HEADER_LEN_37_PLUS
    return magic, ver, hlen


def load_code(data, skip=None):
    """把 pyc 字节解析成 code object；skip=None 时按 16/12/8 依次尝试。"""
    _, _, hlen = read_header(data)
    candidates = [skip] if skip is not None else ([hlen] if hlen else []) + [16, 12, 8]
    tried = []
    for off in candidates:
        if off is None or off >= len(data):
            continue
        tried.append(off)
        try:
            co = marshal.loads(bytes(data[off:]))
        except (ValueError, EOFError, TypeError):
            continue
        if isinstance(co, types.CodeType):
            return co, off
    raise PycError("marshal 解析失败（试过头部偏移 %s）：版本不匹配或文件被加密" % tried)


def walk_code(co, depth=0, out=None):
    """递归收集 code object 结构信息。"""
    out = out if out is not None else []
    consts = [("<code %s>" % c.co_name) if isinstance(c, types.CodeType) else c
              for c in co.co_consts]
    out.append({"depth": depth, "name": co.co_name, "argcount": co.co_argcount,
                "names": list(co.co_names)[:20], "consts": consts[:20],
                "n_consts": len(co.co_consts)})
    for c in co.co_consts:
        if isinstance(c, types.CodeType):
            walk_code(c, depth + 1, out)
    return out


def harvest_consts(co, out=None, min_len=1):
    """递归捞出所有 str/bytes 常量。"""
    out = out if out is not None else []
    for c in co.co_consts:
        if isinstance(c, types.CodeType):
            harvest_consts(c, out, min_len)
        elif isinstance(c, (str, bytes)) and len(c) >= min_len:
            out.append(c)
    return out


def unpatch_opcodes(co, mapping, step=2):
    """按 旧op->新op 映射替换 co_code 里的 opcode 字节；非 3.6+ 定宽请改 step。"""
    if not mapping:
        raise PycError("--unpatch 需要 旧=新 映射，例如 23=20,20=23")
    code = bytearray(co.co_code)
    hit = 0
    for i in range(0, len(code), step):
        op = code[i]
        if op in mapping:
            code[i] = mapping[op] & 0xFF
            hit += 1
    if hit == 0:
        raise PycError("映射里没有任何 opcode 出现在字节码中，检查是否写反/版本不符")
    for k, v in mapping.items():
        if not (0 <= k <= 255 and 0 <= v <= 255):
            raise PycError("opcode 必须在 0..255：%r=%r" % (k, v))
    return co.replace(co_code=bytes(code)), hit


def parse_mapping(text):
    m = {}
    for part in text.replace(" ", "").split(","):
        if not part:
            continue
        if "=" not in part:
            raise PycError("映射格式应为 旧=新（十进制或 0x 前缀）：%r" % part)
        a, b = part.split("=", 1)
        m[int(a, 0)] = int(b, 0)
    if not m:
        raise PycError("映射为空")
    return m


def build_demo_pyc(src="flag = 'flag{demo}'"):
    """构造一个可解析的真实 pyc（用当前解释器编译），供 selftest 使用。"""
    import importlib.util
    code = compile(src, "<demo>", "exec")
    magic = importlib.util.MAGIC_NUMBER
    header = magic + b"\x00" * (HEADER_LEN_37_PLUS - len(magic))
    return header + marshal.dumps(code)


def selftest(rng=None):
    fails = []

    # 1. 正常路径：读头部 + 加载 code object
    raw = build_demo_pyc()
    try:
        magic, ver, hlen = read_header(raw)
        co, off = load_code(raw)
        if off != 16:
            fails.append("case1: 头部偏移应为 16，实际 %r" % (off,))
        if co.co_name != "<module>":
            fails.append("case1: co_name 不符 %r" % (co.co_name,))
    except PycError as e:
        fails.append("case1: 报错 %s" % e)

    # 2. 正常路径：常量挖矿能挖出 flag
    consts = harvest_consts(co)
    if "flag{demo}" not in [c for c in consts if isinstance(c, str)]:
        fails.append("case2: 未挖出常量 'flag{demo}'，实际 %r" % (consts,))

    # 3. 边界拒绝：空文件 / 垃圾数据 / 未知 magic 但 dump 头部不崩
    for bad in (b"", b"\x00\x00\x00\x00junk"):
        try:
            if len(bad) < 4:
                read_header(bad)
            else:
                load_code(bad)
            fails.append("case3: %r 未被拒绝" % (bad[:8],))
        except PycError:
            pass
    magic, ver, hlen = read_header(b"\xde\xad\xbe\xef" + b"\x00" * 20)
    if "未知" not in ver:
        fails.append("case3b: 未知 magic 未给出提示，实际 %r" % (ver,))

    # 4. 魔改 opcode 还原：把 LOAD_CONST 与 RETURN_VALUE 互换后还原回来
    std = dis.opmap
    a, b = std.get("LOAD_CONST"), std.get("RETURN_VALUE")
    if a is None or b is None:
        fails.append("case4: 当前解释器缺少 LOAD_CONST/RETURN_VALUE")
    else:
        hacked = [(a, b), (b, a)]
        patched, hit_p = unpatch_opcodes(co, dict(hacked))
        back, hit_b = unpatch_opcodes(patched, dict(hacked))
        if back.co_code != co.co_code:
            fails.append("case4: 两次互换未还原，hit=%r/%r" % (hit_p, hit_b))
        try:
            unpatch_opcodes(co, parse_mapping("200=201"))
            fails.append("case4b: 不存在的 opcode 映射未被拒绝")
        except PycError:
            pass

    # 5. 参数不足：main 空参 / 缺映射
    try:
        main([])
        fails.append("case5: 无参数应报参数不足")
    except SystemExit as e:
        if e.code != 2:
            fails.append("case5: 参数不足退出码应 2，实际 %r" % (e.code,))
    try:
        parse_mapping("23")
        fails.append("case5b: 非法映射格式未被拒绝")
    except PycError:
        pass

    for f in fails:
        print("FAIL %s" % f, file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 5/5（头部与加载、常量挖矿、空文件/未知magic 拒绝、opcode 互换还原、参数不足）")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="pyc 逆向：magic 判版本 / 常量挖矿 / 魔改 opcode 还原（离线）")
    ap.add_argument("pyc", nargs="?", help="pyc 文件路径")
    ap.add_argument("--header", action="store_true", help="只打印 magic 与疑似版本")
    ap.add_argument("--walk", action="store_true", help="打印所有 code object 结构")
    ap.add_argument("--consts", action="store_true", help="递归挖出字符串/字节常量")
    ap.add_argument("--dis", action="store_true", help="反汇编顶层 code object")
    ap.add_argument("--unpatch", help="魔改 opcode 映射，形如 23=20,20=23")
    ap.add_argument("--skip", type=lambda s: int(s, 0), default=None,
                    help="手工指定头部长度（默认 16/12/8 自动尝试）")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.pyc:
        ap.error("缺少 pyc 文件路径（或用 --selftest）")
    try:
        with open(args.pyc, "rb") as f:
            data = f.read()
        magic, ver, hlen = read_header(data)
        if args.header and not (args.walk or args.consts or args.dis or args.unpatch):
            print(json.dumps({"magic": magic, "version": ver, "header_len": hlen},
                             ensure_ascii=False))
            return 0
        co, off = load_code(data, args.skip)
        if args.unpatch:
            co, hit = unpatch_opcodes(co, parse_mapping(args.unpatch))
        print(json.dumps({"magic": magic, "version": ver, "body_offset": off},
                         ensure_ascii=False))
        if args.walk:
            for row in walk_code(co):
                print("%s== %s (argcount=%d, n_consts=%d)"
                      % ("  " * row["depth"], row["name"], row["argcount"], row["n_consts"]))
                print("%s   names: %s" % ("  " * row["depth"], row["names"]))
        if args.consts:
            print("[*] 可疑常量：")
            for c in harvest_consts(co):
                print("   ", repr(c)[:160])
        if args.dis:
            dis.dis(co)
        return 0
    except PycError as e:
        print("错误：%s" % e, file=sys.stderr)
        return 2
    except OSError as e:
        print("错误：读不到文件 %s（%s）" % (args.pyc, e), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
