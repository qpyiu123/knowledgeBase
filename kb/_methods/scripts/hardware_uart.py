"""UART 波形解码与波特率估算：从采样点还原 8N1 字节流。纯标准库。"""
from __future__ import annotations

import argparse
import sys


def samples_to_bits(samples, threshold=None):
    """把模拟采样归一化成 0/1；阈值默认取 (最小+最大)/2。"""
    if not samples:
        raise ValueError("采样序列为空，无法解码")
    lo, hi = min(samples), max(samples)
    if hi - lo < 2:
        raise ValueError("采样值动态范围过小（%d..%d），疑似没有信号" % (lo, hi))
    thr = (lo + hi) // 2 if threshold is None else threshold
    return [1 if v > thr else 0 for v in samples], thr


def estimate_baud(bits, sample_rate):
    """量最短电平游程当 1 比特宽度，波特率 ≈ 1/w。"""
    if sample_rate <= 0:
        raise ValueError("sample_rate 必须 > 0，当前 %d" % sample_rate)
    run = 1
    widths = []
    for i in range(1, len(bits)):
        if bits[i] == bits[i - 1]:
            run += 1
        else:
            widths.append(run)
            run = 1
    widths.append(run)
    if not widths:
        raise ValueError("没有可用的电平游程")
    w = min(widths)
    if w <= 0:
        raise ValueError("最短游程为 0，数据无效")
    return float(sample_rate) / float(w), w


def decode_uart(bits, spb, idle_high=1, bits_per_char=8):
    """8N1：空闲高、起始位低、8 数据位 LSB first、停止位高。"""
    if spb < 2:
        raise ValueError("每比特采样数 spb=%.2f 太小（应 >= 2），请提高采样率或降低波特率" % spb)
    if bits_per_char < 5 or bits_per_char > 8:
        raise ValueError("bits_per_char 只支持 5..8，当前 %d" % bits_per_char)
    out = []
    errors = 0
    i = 0
    n = len(bits)
    while i < n:
        if bits[i] != (1 - idle_high):
            i += 1
            continue
        start = i + (spb / 2.0)
        vals = []
        for k in range(bits_per_char):
            p = int(start + spb * (k + 1))
            if p >= n:
                return bytes(out), errors, "采样越界，波形末尾不完整"
            vals.append(1 if bits[p] == idle_high else 0)
        stop = int(start + spb * (bits_per_char + 1))
        if stop >= n:
            return bytes(out), errors, "停止位越界，波形末尾不完整"
        if bits[stop] == idle_high:
            value = 0
            for k in range(bits_per_char):
                value += vals[k] * (2 ** k)
            out.append(value)
        else:
            errors += 1
        i = int(start + spb * (bits_per_char + 1.5))
    return bytes(out), errors, ""


def parse_hex(text):
    """接受 "01 23 ff" 或 "0123ff" 的十六进制采样描述（每个字节一个采样值）。"""
    t = "".join(text.split())
    if not t or len(t) % 2:
        raise ValueError("十六进制采样串长度必须是偶数且非空：%r" % text[:20])
    try:
        return list(bytes.fromhex(t))
    except ValueError:
        raise ValueError("采样串不是合法十六进制：%r" % text[:20])


def selftest():
    fails = []
    spb = 8
    # 造 "Hi!"：0x48 0x69 0x21，8N1，起始位低、LSB first、停止位高
    frame = []
    for ch in b"Hi!":
        frame.append(0)
        for k in range(8):
            frame.append((ch >> k) % 2)
        frame.append(1)
    frame = [1] * 4 + frame + [1] * 4
    bits = []
    for b in frame:
        bits.extend([b] * spb)
    samples = [0 if b == 0 else 200 for b in bits]
    norm, thr = samples_to_bits(samples)
    if thr != 100 or sum(norm) != sum(bits):
        fails.append("case1: 采样归一化阈值/比特数错误")
    data, errs, msg = decode_uart(norm, spb)
    if data != b"Hi!" or errs != 0 or msg:
        fails.append("case1: 8N1 解码结果应为 b'Hi!'，实际 %r errs=%d msg=%r" % (data, errs, msg))
    baud, w = estimate_baud(norm, 115200)
    if w != spb:
        fails.append("case2: 最短游程应为 %d，实际 %d" % (spb, w))
    if abs(baud - 14400.0) > 1e-6:
        fails.append("case2: 波特率估算应为 14400，实际 %r" % baud)
    try:
        decode_uart(norm, 1)
        fails.append("case3: spb<2 未拒绝")
    except ValueError:
        pass
    try:
        samples_to_bits([5, 5, 5])
        fails.append("case3: 恒值采样未拒绝")
    except ValueError:
        pass
    for fn, arg in ((estimate_baud, ([1, 0, 1], 0)), (parse_hex, "abc"), (parse_hex, "")):
        try:
            fn(*arg) if isinstance(arg, tuple) else fn(arg)
            fails.append("case4: %s 未拒绝 %r" % (fn.__name__, arg))
        except (ValueError, TypeError):
            pass
    if parse_hex("01 02 ff") != [1, 2, 255]:
        fails.append("case4: parse_hex 解析失败")
    if fails:
        for line in fails:
            print("FAIL", line, file=sys.stderr)
        return 1
    print("selftest ok: 4 组断言全过（归一化+解码/波特率估算/参数拒绝/十六进制解析）")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="UART 8N1 波形解码（离线、纯标准库）")
    ap.add_argument("--hex", help="十六进制采样串，如 'f0 71 01 ...'（每项一个采样点）")
    ap.add_argument("--file", help="文本采样文件，一行一个十进制或 0x 十六进制采样点")
    ap.add_argument("--sample-rate", type=int, default=115200, help="采样率 Hz，默认 115200")
    ap.add_argument("--baud", type=int, default=9600, help="串口波特率，默认 9600")
    ap.add_argument("--threshold", type=int, default=None, help="自定义判决阈值")
    ap.add_argument("--selftest", action="store_true", help="运行内置自测")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not (a.hex or a.file):
        ap.error("必须提供 --hex 或 --file（或 --selftest）")
    try:
        if a.hex:
            samples = parse_hex(a.hex)
        else:
            with open(a.file, "r", encoding="utf-8") as fh:
                samples = [int(x, 0) for x in fh.read().split()]
        if a.baud <= 0:
            raise ValueError("--baud 必须 > 0，当前 %d" % a.baud)
        bits, thr = samples_to_bits(samples, a.threshold)
        spb = float(a.sample_rate) / float(a.baud)
        data, errs, msg = decode_uart(bits, spb)
    except (ValueError, OSError) as exc:
        print("失败：%s" % exc, file=sys.stderr)
        return 2
    print("采样点 %d，阈值 %d，每比特 %.2f 采样，帧错误 %d" % (len(samples), thr, spb, errs))
    print("解码 %d 字节：%s" % (len(data), data.decode("latin-1")))
    if msg:
        print("提示：%s" % msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
