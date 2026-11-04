#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自研 VM 逆向辅助：字节码反汇编 / 模拟执行 / handler 语义差分判定。

纯标准库、离线、只读。用法示例见 kb/_methods/vm_obfuscation.md。
"""
import argparse
import json
import random
import sys

MASK32 = 0xFFFFFFFF

# opcode -> (名字, 立即数字节数)  示范指令集，换成题目真实表即可
OPCODES = {
    0x01: ("ADD", 2),    # 立即数 = (b<<4)|c 的寄存器编号对
    0x02: ("XOR", 1),    # r[a] = r[b] ^ imm8
    0x03: ("MOV", 1),    # r[a] = imm8
    0x04: ("SHL", 1),    # r[a] = r[b] << (imm8 & 31)
    0x05: ("CMP", 0),    # zf = (r[a] == r[b])
    0x06: ("JNZ", 1),    # if !zf: pc = imm8
    0x07: ("PRINT", 0),  # 输出 r[a] 的低 8 位（demo 用）
    0xFF: ("EXIT", 0),
}
INS_LEN = {k: v[1] for k, v in OPCODES.items()}
NAME_OF = {k: v[0] for k, v in OPCODES.items()}


class VMError(ValueError):
    pass


def _imm(code, pc, n):
    if pc + 1 + n > len(code):
        raise VMError("偏移 0x%X 处立即数越界：需要 %d 字节，剩余 %d" % (pc, n, len(code) - pc - 1))
    return int.from_bytes(code[pc + 1:pc + 1 + n], "little")


def disasm(code, base=0):
    """逐条切分字节码，返回行列表；遇到未知 opcode 报错并指出偏移。"""
    if not isinstance(code, (bytes, bytearray)):
        raise VMError("code 必须是 bytes")
    pc, out = 0, []
    while pc < len(code):
        op = code[pc]
        if op not in OPCODES:
            raise VMError("未知 opcode 0x%02X @ 0x%04X" % (op, pc + base))
        name, n = NAME_OF[op], INS_LEN[op]
        if pc + 1 + n > len(code):
            raise VMError("0x%04X 处 %s 的立即数被截断" % (pc + base, name))
        imm = int.from_bytes(code[pc + 1:pc + 1 + n], "little")
        out.append("%04x: %-6s%s" % (pc + base, name,
                                     (" 0x%x" % imm) if n else ""))
        pc += 1 + n
    return out


def emulate(code, entry=0, max_steps=100000, trace=False):
    """纯 Python 解释器。返回 (regs, trace, output)。"""
    regs = {"a": 0, "b": 0, "c": 0, "pc": entry, "zf": 0, "halt": False}
    steps, trace_log, output = 0, [], []
    while not regs["halt"]:
        if steps >= max_steps:
            raise VMError("超过 max_steps=%d，疑似死循环（pc=0x%X）" % (max_steps, regs["pc"]))
        pc = regs["pc"]
        if pc < 0 or pc >= len(code):
            break
        op = code[pc]
        if op not in OPCODES:
            raise VMError("未知 opcode 0x%02X @ 0x%04X" % (op, pc))
        name, n = NAME_OF[op], INS_LEN[op]
        imm = int.from_bytes(code[pc + 1:pc + 1 + n], "little")
        if trace:
            trace_log.append((pc, name, imm, dict(regs)))
        regs["pc"] = pc + 1 + n
        a, b, c = regs["a"], regs["b"], regs["c"]
        if name == "ADD":
            # 立即数高 4 位是源寄存器号、低 4 位是目标寄存器号
            src, dst = (imm >> 4) & 0xF, imm & 0xF
            regs[dst] = (regs[dst] + regs[src]) & MASK32
        elif name == "XOR":
            regs["a"] = (b ^ imm) & MASK32
        elif name == "MOV":
            regs["a"] = imm & MASK32
        elif name == "SHL":
            regs["a"] = (b << (imm & 31)) & MASK32
        elif name == "CMP":
            regs["zf"] = int(a == b)
        elif name == "JNZ":
            if not regs["zf"]:
                regs["pc"] = imm
        elif name == "PRINT":
            output.append(chr(a & 0xFF))
        elif name == "EXIT":
            regs["halt"] = True
        steps += 1
    return regs, trace_log, "".join(output)


def _solve_linear(pts):
    """在 mod 2^32 下解 out = x + k2*y + c：先算 g = ((out1-x1)-(out0-x0)) = k2*dy，dy 必须为奇数。"""
    dy = pts[1][1] - pts[0][1]          # 用 (y_i - y_0)*k2 = out_i - x_i - c 消掉 c：差分后 g 必须为偶数
    g = (pts[1][2] - pts[1][0]) - (pts[0][2] - pts[0][0])
    if g % dy != 0:
        return None
    k2 = (g // dy) & MASK32
    c = (pts[0][2] - pts[0][0] - k2 * pts[0][1]) & MASK32
    if all((x + k2 * y + c) & MASK32 == o & MASK32 for x, y, o in pts):
        return {"kind": "linear", "k1": 1, "k2": k2, "c": c}
    return None


def judge_handler(samples):
    """从 (x, y, out) 采样推断 handler 语义。

    依次尝试：常数搬运 / out = x ^ k / out = x + k2*y + c (mod 2^32)。
    至少 3 组采样，且第 1、2 组的 y 差必须为奇数（2^32 下才可逆），否则返回 None 而不是乱猜。
    """
    pts = [tuple(s) for s in samples if len(s) == 3]
    if len(pts) < 3:
        raise VMError("judge_handler 至少需要 3 组 (x, y, out) 采样，当前 %d 组" % len(pts))
    if len({p[0] for p in pts}) == 1 and len({p[1] for p in pts}) == 1:
        return {"kind": "const", "value": pts[0][2] & MASK32}
    k = pts[0][0] ^ pts[0][2]          # 异或是加法的对偶，必须用 ^ 反解，不能相减
    if all((x ^ k) == o for x, y, o in pts):
        return {"kind": "xor_const", "value": k & MASK32}
    for order in (pts, pts[1:] + pts[:1]):
        res = _solve_linear(order)
        if res is not None:
            return res
    return None


def parse_hex(text):
    s = text.replace(" ", "").replace(",", "").replace("0x", "").replace("\\x", "")
    try:
        return bytes.fromhex(s)
    except ValueError:
        raise VMError("字节码不是合法十六进制：%r" % text)


def selftest(rng=None):
    rng = rng or random.Random(20261103)
    fails = []

    # 1. 正常路径：反汇编 demo 字节码（MOV a=0x41; XOR a=r[b]^0x00; EXIT），共 3 条
    code = bytes.fromhex("0341" "0200" "ff")
    try:
        lines = disasm(code)
        if len(lines) != 3 or "MOV" not in lines[0] or "EXIT" not in lines[2]:
            fails.append("case1: 反汇编结果不符 %r" % lines)
    except VMError as e:
        fails.append("case1: 反汇编报错 %s" % e)

    # 2. 正常路径：模拟执行 + PRINT 输出（MOV a=0x41; PRINT a; MOV a=0x42; PRINT a; EXIT）
    prog = bytes.fromhex("0341" "07" "0342" "07" "ff")
    try:
        regs, _, out = emulate(prog)
        if out != "AB":
            fails.append("case2: PRINT 输出应为 'AB'，实际 %r" % out)
    except VMError as e:
        fails.append("case2: 模拟报错 %s" % e)

    # 2b. 条件跳转 + 死循环护栏：JNZ 目标指回自身，zf=0 必然自跳 => 触发 max_steps
    loop_prog = bytes.fromhex("0341" "05" "0602" "ff")
    try:
        emulate(loop_prog, max_steps=50)
        fails.append("case2b: 自跳死循环应被 max_steps 拦下")
    except VMError:
        pass

    # 3. 边界拒绝：未知 opcode / 立即数截断（MOV 缺立即数、ADD 缺寄存器字节）
    bad_cases = [b"\x99", b"\x03", b"\x01"]
    rejected = 0
    for bc in bad_cases:
        try:
            disasm(bc)
        except VMError:
            rejected += 1
    if rejected != len(bad_cases):
        fails.append("case3: 应拒绝 %d 例，实际 %d" % (len(bad_cases), rejected))

    # 4. handler 语义差分：构造 x+y+c 与 x^c 两类
    c = 0x1234
    lin = []
    for i in range(4):
        x = rng.randrange(1 << 20)
        y = 2 * i + 1              # y 差为奇数，2^32 下可逆
        lin.append((x, y, (x + y + c) & MASK32))
    got = judge_handler(lin)
    if not got or got["kind"] != "linear" or got["c"] != c:
        fails.append("case4: 线性语义判定不符 %r" % (got,))
    xo = [(x, rng.randrange(1 << 20), (x ^ 0x5A5A) & MASK32) for x in
          (rng.randrange(1 << 20) for _ in range(4))]
    got2 = judge_handler(xo)
    if not got2 or got2["kind"] != "xor_const" or got2["value"] != 0x5A5A:
        fails.append("case4b: 异或语义判定不符 %r" % (got2,))
    try:
        judge_handler([(1, 2, 3)])
        fails.append("case4c: 采样不足未被拒绝")
    except VMError:
        pass

    # 5. 参数不足：main 空参退出码 2
    try:
        main([])
        fails.append("case5: 无参数应报参数不足")
    except SystemExit as e:
        if e.code != 2:
            fails.append("case5: 参数不足退出码应 2，实际 %r" % (e.code,))

    for f in fails:
        print("FAIL %s" % f, file=sys.stderr)
    if fails:
        return 1
    print("selftest ok: 5/5（反汇编、模拟执行 PRINT、未知 opcode/截断/死循环拒绝、语义差分、参数不足）")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="自研 VM 逆向：字节码反汇编 / 模拟 / handler 语义判定（离线）")
    ap.add_argument("--dis", help="十六进制字节码，反汇编")
    ap.add_argument("--emu", action="store_true", help="模拟执行 --hex 指定的字节码")
    ap.add_argument("--hex", help="模拟执行的十六进制字节码")
    ap.add_argument("--entry", type=lambda s: int(s, 0), default=0)
    ap.add_argument("--max-steps", type=int, default=100000)
    ap.add_argument("--trace", action="store_true", help="打印寄存器轨迹")
    ap.add_argument("--judge", nargs=3, action="append", metavar=("X", "Y", "OUT"),
                    help="handler 采样：x y out（可重复给多组）")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    try:
        if args.dis:
            print("\n".join(disasm(parse_hex(args.dis))))
            return 0
        if args.emu:
            if not args.hex:
                ap.error("--emu 需要 --hex <字节码>")
            _, tr, out = emulate(parse_hex(args.hex), entry=args.entry,
                                 max_steps=args.max_steps, trace=args.trace)
            if args.trace:
                for pc, name, imm, regs in tr:
                    print("%04x %-6s 0x%-8x a=%08x b=%08x c=%08x"
                          % (pc, name, imm, regs["a"], regs["b"], regs["c"]))
            n_steps = len(tr) if args.trace else "未记录（加 --trace 可见）"
            print(json.dumps({"output": out, "steps": n_steps}, ensure_ascii=False))
            return 0
        if args.judge:
            samples = [tuple(int(v, 0) for v in row) for row in args.judge]
            res = judge_handler(samples)
            if res is None:
                print("判不出语义：请再给 2~3 组线性无关采样")
                return 1
            print(json.dumps(res, ensure_ascii=False))
            return 0
    except VMError as e:
        print("错误：%s" % e, file=sys.stderr)
        return 2
    ap.error("需要 --dis / --emu / --judge 之一，或用 --selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main())
