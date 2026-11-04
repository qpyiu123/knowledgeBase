"""QR 码与条码结构核查：纯标准库离线实现（不做纠错、不联网）。
用法示例：
  python qr_barcode.py --matrix m.txt                  # 0/1 文本矩阵
  python qr_barcode.py --pgm shot.pgm --modules 25     # PGM 灰度图降采样
  python qr_barcode.py --ean 9780306406157             # EAN-13 校验位
  python qr_barcode.py --code128 104,40,41,42,30,60     # Code128 校验和
  python qr_barcode.py --selftest
"""

from __future__ import annotations

import argparse
import re
import sys


MASKS = [
    lambda r, c: (r + c) % 2 == 0,
    lambda r, c: r % 2 == 0,
    lambda r, c: c % 3 == 0,
    lambda r, c: (r + c) % 3 == 0,
    lambda r, c: (r // 2 + c // 3) % 2 == 0,
    lambda r, c: (r * c) % 2 + (r * c) % 3 == 0,
    lambda r, c: ((r * c) % 2 + (r * c) % 3) % 2 == 0,
    lambda r, c: ((r + c) % 2 + (r * c) % 3) % 2 == 0,
]

PAT21 = (
    "111111111000111111111", "111111111000111111111", "111111111000111111111",
    "111111111000111111111", "111111111000111111111", "111111111000111111111",
    "111111111111111111111", "111111111000111111111", "111111111000111111111",
    "000000100000000000000", "000000100000000000000", "000000100000000000000",
    "111111111000000000000", "111111111000000000000", "111111111000000000000",
    "111111111000000000000", "111111111000000000000", "111111111000000000000",
    "111111111000000000000", "111111111000000000000", "111111111000000000000",

)


def reserved_map(size):
    """保留区总表：21x21 用规范字面量；更大尺寸按三块 9x9 + 定时 + 格式信息铺。"""
    if size == 21:
        return [bytearray(1 if ch == "1" else 0 for ch in line) for line in PAT21]
    n = size
    rows = [bytearray(n) for _ in range(n)]
    for i in range(9):
        for k in range(9):
            rows[i][k] = rows[i][n - 9 + k] = rows[n - 9 + i][k] = 1
    for i in range(n):
        rows[6][i] = rows[i][6] = 1
    for i in range(9):
        rows[8][i] = rows[i][8] = 1
        rows[8][n - 1 - i] = 1
        rows[n - 1 - i][8] = 1
    rows[8][n - 8] = 1
    return rows


def data_slots(size):
    """数据模块坐标：逐格扫描，跳过保留区与第 6 列计时图案。"""
    res = reserved_map(size)
    return [(r, c) for r in range(size) for c in range(size) if c != 6 and res[r][c] == 0]

FINDER = [(dr, dc, 1 if min(dr, dc, 6 - dr, 6 - dc) in (0, 2, 4) else 0)
          for dr in range(7) for dc in range(7)]


def finder_ok(m):
    """三处 7x7 定位图案：外环黑、次环白、中心 3x3 黑。"""
    n = len(m)
    for r0, c0 in ((0, 0), (0, n - 7), (n - 7, 0)):
        for dr, dc, want in FINDER:
            if m[r0 + dr][c0 + dc] != want:
                return False
    return True


def timing_ok(m):
    """第 6 行/列从第 8 位到倒数第 8 位黑白交替。"""
    n = len(m)
    for i in range(8, n - 8):
        want = 1 if i % 2 == 0 else 0
        if m[6][i] != want or m[i][6] != want:
            return False
    return True


def version_of(size):
    """由边长推版本号：21+4k, k=0..39。"""
    if size < 21 or (size - 21) % 4 or size > 177:
        raise ValueError("尺寸 %d 不是合法 QR 版本（应为 21+4k, k=0..39）" % size)
    return (size - 21) // 4 + 1


def parse_matrix(text):
    """把 0/1（可用 # . 空格 | 作分隔）的文本读成二维矩阵。"""
    rows = []
    for line in text.splitlines():
        line = line.strip().strip("|")
        if not line:
            continue
        cells = re.sub(r"[\s|,]+", "", line)
        if not cells or set(cells) - set("01#."):
            raise ValueError("矩阵行只能含 0/1（可用空格、|、#、. 分隔）：%r" % line[:30])
        rows.append([1 if ch in "1#" else 0 for ch in cells])
    if not rows:
        raise ValueError("矩阵为空：请给出 0/1 文本或用 --pgm 输入像素图")
    if len(set(len(r) for r in rows)) != 1:
        raise ValueError("矩阵不是等宽：各行列数 %r" % [len(x) for x in rows])
    width = len(rows[0])
    if len(rows) != width:
        raise ValueError("矩阵不是正方形：%dx%d" % (len(rows), width))
    return rows


def ean13_checksum(digits):
    """EAN-13：从左数前 12 位交替乘 1、3，校验位补足到 10 的倍数。"""
    digits = re.sub(r"\s+", "", digits)
    if not re.fullmatch(r"\d{13}", digits):
        raise ValueError("EAN-13 必须是 13 位数字，当前输入 %r" % digits[:20])
    total = 0
    for i in range(12):
        total += (ord(digits[i]) - 48) * (1 if i % 2 == 0 else 3)
    return (ord(digits[12]) - 48) == (10 - total % 10) % 10


def code128_check(codes):
    """Code128：起始符权重 1，其后第 k 位权重 k，末位为模 103 校验和。"""
    if len(codes) < 2:
        raise ValueError("Code128 至少需要起始符与校验符两个码值")
    total = codes[0]
    for pos in range(1, len(codes) - 1):
        total += pos * codes[pos]
    return codes[-1] == (total % 103)


def row_penalty(rows):
    """简化罚分：统计每行内同色连续 >=5 的段数。"""
    pen = 0
    for row in rows:
        run = 1
        for k in range(1, len(row)):
            run = run + 1 if row[k] == row[k - 1] else 1
            pen += 1 if run == 5 else 0
    return pen


def unmask(matrix):
    """试 8 种掩码，取罚分最小者，返回 (掩码号, 反掩码矩阵, 罚分)。"""
    slots = data_slots(len(matrix))
    best = None
    for mid in range(8):
        m2 = [row[:] for row in matrix]
        fn = MASKS[mid]
        for r, c in slots:
            if fn(r, c):
                m2[r][c] = 1 - m2[r][c]
        pen = row_penalty(m2)
        if best is None or pen < best[2]:
            best = (mid, m2, pen)
    return best


def extract_bits(matrix):
    """按逐行顺序取数据区比特（入参应为已反掩码矩阵）。"""
    return [matrix[r][c] for (r, c) in data_slots(len(matrix))]


def bits_to_bytes(bits):
    """8 位一字节（高位在前），不足 8 位的尾巴丢弃。"""
    return bytes(int("".join(str(x) for x in bits[i:i + 8]), 2) for i in range(0, len(bits) - 7, 8))


def format_info(matrix):
    """取格式信息 15 位（异或掩码 0b101010000010010），返回 (原始, 纠错等级, 掩码号)。"""
    coords = [(8, k) for k in range(6)] + [(8, 7), (8, 8), (7, 8), (5, 8), (4, 8), (3, 8),
                                           (2, 8), (1, 8), (0, 8)]
    bits = 0
    for r, c in coords:
        bits = bits * 2 + matrix[r][c]
    raw = bits ^ 0b101010000010010
    return raw, raw >> 13, (raw >> 10) % 8


def read_pgm(path):
    """读 PGM（P5 二进制 / P2 文本），返回 (宽, 高, 最大灰度, 像素 bytes)。"""
    with open(path, "rb") as fh:
        data = fh.read()
    magic = data[:2]
    if magic not in (b"P5", b"P2"):
        raise ValueError("只支持 PGM(P5/P2) 灰度图：%s" % path)
    if magic == b"P2":
        nums = [int(x) for x in data[2:].split()]
        w, h, maxv = nums[0], nums[1], nums[2]
        px = bytes(nums[3:3 + w * h])
    else:
        k = 2
        fields = []
        while len(fields) < 3:
            if k >= len(data):
                raise ValueError("PGM 头部不完整：%s" % path)
            if data[k:k + 1].isspace():
                k += 1
                continue
            if data[k:k + 1] == b"#":
                while k < len(data) and data[k:k + 1] != b"\n":
                    k += 1
                continue
            j = k
            while j < len(data) and not data[j:j + 1].isspace():
                j += 1
            fields.append(int(data[k:j]))
            k = j
        w, h, maxv = fields[0], fields[1], fields[2]
        px = data[k + 1:k + 1 + w * h]
    if len(px) < w * h:
        raise ValueError("PGM 像素数据不足：期望 %d 字节，实际 %d" % (w * h, len(px)))
    return w, h, maxv, px


def pgm_to_matrix(path, modules):
    """按每个模块中心点的灰度阈值降采样成 modules x modules 的 0/1 矩阵。"""
    w, h, maxv, px = read_pgm(path)
    if modules < 21:
        raise ValueError("--modules 必须 >= 21，当前 %d" % modules)
    if w % modules or h % modules:
        print("提示：图像 %dx%d 不能被 %d 整除，按比例取模块中心" % (w, h, modules), file=sys.stderr)
    rows = []
    for r in range(modules):
        y = int((r + 0.5) * h / modules)
        row = []
        for c in range(modules):
            x = int((c + 0.5) * w / modules)
            row.append(1 if px[y * w + x] * 2 <= maxv else 0)
        rows.append(row)
    return rows


def analyze_matrix(matrix):
    """结构核查 + 掩码选择 + 码字提取；不做 RS 纠错，因此只报结构与头部字节。"""
    n = len(matrix)
    ver = version_of(n)
    if not finder_ok(matrix):
        raise ValueError("未找到三个 7x7 定位图案，可能不是 QR 矩阵或已损坏")
    if not timing_ok(matrix):
        raise ValueError("定时图案（第 6 行/列黑白交替）不匹配，矩阵可能已损坏")
    mid, m2, pen = unmask(matrix)
    bits = extract_bits(m2)
    raw = bits_to_bytes(bits)
    _, ecc, mask_fmt = format_info(matrix)
    return {"version": ver, "size": n, "mask": mid, "penalty": pen, "format_ecc": ecc,
            "format_mask": mask_fmt, "data_modules": len(bits), "bytes": len(raw),
            "hex": raw[:32].hex()}


def build_demo(matrix):
    """铺出三个 7x7 定位图案与第 6 行/列定时图案，供自测与样例使用。"""
    n = len(matrix)
    for r0, c0 in ((0, 0), (0, n - 7), (n - 7, 0)):
        for dr in range(7):
            for dc in range(7):
                matrix[r0 + dr][c0 + dc] = 1 if min(dr, dc, 6 - dr, 6 - dc) in (0, 2, 4) else 0
    for i in range(8, n - 8):
        matrix[6][i] = matrix[i][6] = 1 if i % 2 == 0 else 0
    return matrix


def expect_raise(fn, arg, label, fails):
    """断言 fn(arg) 抛 ValueError，否则记一条失败。"""
    try:
        fn(arg)
    except ValueError:
        return
    fails.append("%s 未拒绝非法输入 %r" % (label, arg))


def selftest():
    fails = []
    n = 21
    demo = build_demo([[0] * n for _ in range(n)])
    slots = data_slots(n)
    fixed = 0
    for row in reserved_map(n):
        fixed += sum(1 for v in row if v == 1)
    if fixed != 249:
        fails.append("case1: 21x21 保留区应为 249 个模块，实际 %d" % fixed)
    if len(slots) != 192:
        fails.append("case1: 21x21 数据模块数应为 192，实际 %d" % len(slots))
    if len(extract_bits(demo)) != len(slots):
        fails.append("case1: extract_bits 取出的比特数与数据模块数不一致")
    if not finder_ok(demo) or not timing_ok(demo):
        fails.append("case1: 合法矩阵的定位图案或定时图案未被识别")
    elif version_of(21) != 1 or version_of(25) != 2 or version_of(177) != 40:
        fails.append("case1: 版本推导错误")
    broken = build_demo([[0] * n for _ in range(n)])
    broken[0][0] = 0
    if finder_ok(broken):
        fails.append("case2: 破坏定位图案后仍判为合法")
    broken2 = build_demo([[0] * n for _ in range(n)])
    broken2[6][9] = 1 - broken2[6][9]
    if timing_ok(broken2):
        fails.append("case2: 破坏定时图案后仍判为合法")
    for bad in (20, 22, 178):
        expect_raise(version_of, bad, "case2: version_of", fails)
    for bad in ("012X", "010\n011", "", "|  |"):
        expect_raise(parse_matrix, bad, "case3: parse_matrix", fails)
    if parse_matrix("|#01|\n|101|\n|000|") != [[1, 0, 1], [1, 0, 1], [0, 0, 0]]:
        fails.append("case3: parse_matrix 解析 0/1/#/. 错误")
    got_tiny = extract_bits([[0] * 20 for _ in range(20)])
    if len(got_tiny) != 153:
        fails.append("case4: 20x20 越界矩阵应跳过越界点并产出 153 位，实际 %d" % len(got_tiny))
    if bits_to_bytes([1] * 8) != b"\xff" or bits_to_bytes([1] * 7) != b"":
        fails.append("case4: bits_to_bytes 拼字节错误")
    if not ean13_checksum("9780306406157") or ean13_checksum("9780306406158"):
        fails.append("case5: EAN-13 校验位判定错误")
    if not ean13_checksum("6291041500213") or ean13_checksum("6291041500215"):
        fails.append("case5: EAN-13 交替权重方向错误")
    if not code128_check([104, 40, 41, 42, 30, 60]) or code128_check([104, 40, 41, 42, 30, 61]):
        fails.append("case5: Code128 校验和判定错误")
    expect_raise(ean13_checksum, "12345", "case5: ean13_checksum", fails)
    expect_raise(code128_check, [104], "case5: code128_check", fails)
    if fails:
        for line in fails:
            print("FAIL", line, file=sys.stderr)
        return 1
    print("selftest ok: 5 组断言全过（保留区/读取顺序/定位图案/参数拒绝/条码校验）")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="QR 矩阵与条码结构核查（离线、纯标准库）")
    ap.add_argument("--matrix", help="0/1 文本矩阵文件（# 与 . 也可作黑/白）")
    ap.add_argument("--text", help="直接给 0/1 矩阵文本")
    ap.add_argument("--pgm", help="PGM 灰度图路径，按 --modules 降采样")
    ap.add_argument("--modules", type=int, default=21, help="矩阵边长（21+4k），默认 21")
    ap.add_argument("--ean", help="校验 13 位 EAN-13 数字")
    ap.add_argument("--code128", help="逗号分隔的 Code128 码值，末位为校验和")
    ap.add_argument("--selftest", action="store_true", help="运行内置自测")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not (a.ean or a.code128 or a.pgm or a.text or a.matrix):
        ap.error("必须提供 --matrix / --text / --pgm / --ean / --code128 之一")
    try:
        if a.ean:
            print("%s: %s" % (a.ean, "校验通过" if ean13_checksum(a.ean) else "校验不通过"))
            return 0
        if a.code128:
            codes = [int(x) for x in a.code128.split(",")]
            print("%s: %s" % (a.code128, "校验通过" if code128_check(codes) else "校验不通过"))
            return 0
        if a.pgm:
            matrix = pgm_to_matrix(a.pgm, a.modules)
        elif a.text:
            matrix = parse_matrix(a.text)
        else:
            with open(a.matrix, "r", encoding="utf-8") as fh:
                matrix = parse_matrix(fh.read())
        info = analyze_matrix(matrix)
    except (ValueError, OSError) as exc:
        print("失败：%s" % exc, file=sys.stderr)
        return 2
    print("版本 %d，尺寸 %dx%d，掩码 %d（格式信息 %d），罚分 %d，数据模块 %d，可读字节 %d"
          % (info["version"], info["size"], info["size"], info["mask"], info["format_mask"],
             info["penalty"], info["data_modules"], info["bytes"]))
    print("演示采样字节（逐行取样，未按 QR 码字顺序解码）：%s" % info["hex"])
    return 0

if __name__ == "__main__":
    sys.exit(main())
