"""OSINT 图片溯源与弱口令/泄露检索的离线编排：哈希指纹、候选列表、查询串构造。纯标准库。"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys

ALGOS = ("dhash", "ahash")


def _downsample(pixels, width, height, grid):
    """把 width*height 的灰度像素块降采样成 grid*grid 的均值矩阵。"""
    if width < grid or height < grid:
        raise ValueError("图像尺寸 %dx%d 小于目标网格 %d" % (width, height, grid))
    cells = []
    for gy in range(grid):
        y0 = gy * height // grid
        y1 = max(y0 + 1, (gy + 1) * height // grid)
        row = []
        for gx in range(grid):
            x0 = gx * width // grid
            x1 = max(x0 + 1, (gx + 1) * width // grid)
            total, n = 0, 0
            for y in range(y0, y1):
                base = y * width
                for x in range(x0, x1):
                    total += pixels[base + x]
                    n += 1
            row.append(total // n)
        cells.append(row)
    return cells


def dhash(pixels, width, height, bits=64):
    """差分哈希：横向相邻像素比较，差值 >0 记 1。"""
    grid = 8 if bits == 64 else 16
    cells = _downsample(pixels, width, height, grid + 1)
    value = 0
    for y in range(grid):
        for x in range(grid):
            value = value * 2 + (1 if cells[y][x] > cells[y][x + 1] else 0)
    return value


def ahash(pixels, width, height, bits=64):
    """均值哈希：与全图均值比较。"""
    grid = 8 if bits == 64 else 16
    cells = _downsample(pixels, width, height, grid)
    flat = [v for row in cells for v in row]
    mean = sum(flat) // len(flat)
    value = 0
    for v in flat:
        value = value * 2 + (1 if v > mean else 0)
    return value


def hamming(a, b):
    """两个哈希值的汉明距离（用异或后数 1）。"""
    if a < 0 or b < 0:
        raise ValueError("哈希值不能为负：%d %d" % (a, b))
    x = a ^ b
    n = 0
    while x:
        n += 1
        x = x & (x - 1)
    return n


def verdict(dist):
    """按库内经验：<10 同源，10..20 疑似，>20 基本不同。"""
    if dist < 0:
        raise ValueError("距离不能为负：%d" % dist)
    if dist < 10:
        return "同源"
    if dist <= 20:
        return "疑似同源，需人工比对称/纹理"
    return "基本不同"


def flip_lr(pixels, width, height):
    """水平镜像，用于"先翻转再算"的经验技巧。"""
    out = []
    for y in range(height):
        base = y * width
        for x in range(width - 1, -1, -1):
            out.append(pixels[base + x])
    return out


def gray_from_rgb(raw):
    """RGB 三段字节转灰度，供演示与测试使用。"""
    if len(raw) % 3:
        raise ValueError("RGB 字节流长度必须是 3 的倍数，当前 %d" % len(raw))
    out = []
    for i in range(0, len(raw), 3):
        out.append((raw[i] * 299 + raw[i + 1] * 587 + raw[i + 2] * 114) // 1000)
    return out


def sha1_hibp(password):
    """k-anonymity：只上送 SHA-1 前 5 位，这里只算本地期望值。"""
    digest = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    return "SHA1:%s" % digest, digest[:5], digest[5:]


def hash_kind(text):
    """按长度判哈希类型：32=MD5/NTLM，40=SHA1，64=SHA256。"""
    t = text.strip()
    if not t:
        raise ValueError("哈希串为空")
    for ch in t:
        if ch not in "0123456789abcdefABCDEF":
            raise ValueError("不是十六进制串：%r" % t[:20])
    if len(t) == 32:
        return "MD5 或 NTLM（32 位十六进制无法区分）"
    if len(t) == 40:
        return "SHA-1"
    if len(t) == 64:
        return "SHA-256"
    raise ValueError("长度 %d 不是常见的 32/40/64 位哈希" % len(t))


def selftest():
    fails = []
    # 3x3 灰度：中间亮、四周暗，16x16 放大后应保持"中心亮"结构
    base = [0, 0, 0, 0, 200, 0, 0, 0, 0]
    pixels = []
    for y in range(16):
        for x in range(16):
            pixels.append(base[(y // 6) * 3 + (x // 6)])
    d = dhash(pixels, 16, 16)
    a = ahash(pixels, 16, 16)
    if not (0 <= d < (1 << 64)) or not (0 <= a < (1 << 64)):
        fails.append("case1: 哈希值超出 64 位范围")
    flipped = flip_lr(pixels, 16, 16)
    if len(flipped) != len(pixels):
        fails.append("case1: 镜像后像素数变化")
    if hamming(d, d) != 0:
        fails.append("case2: 同图距离应为 0，实际 %d" % hamming(d, d))
    if hamming(d, d ^ 0b1111) != 4:
        fails.append("case2: 距离计算错误")
    pairs = [(0, "同源"), (9, "同源"), (10, "疑似同源，需人工比对称/纹理"),
             (20, "疑似同源，需人工比对称/纹理"), (21, "基本不同")]
    for dist, want in pairs:
        if verdict(dist) != want:
            fails.append("case3: verdict(%d) 期望 %s，实际 %s" % (dist, want, verdict(dist)))
    for dist in (-1,):
        try:
            verdict(dist)
            fails.append("case3: verdict 未拒绝负距离")
        except ValueError:
            pass
    if hash_kind("d41d8cd98f00b204e9800998ecf8427e") != "MD5 或 NTLM（32 位十六进制无法区分）":
        fails.append("case4: 32 位哈希判定错误")
    if hash_kind("a" * 40) != "SHA-1":
        fails.append("case4: 40 位哈希判定错误")
    for bad in ("", "zz" * 16, "abc"):
        try:
            hash_kind(bad)
            fails.append("case4: hash_kind 未拒绝 %r" % bad)
        except ValueError:
            pass
    label, prefix, suffix = sha1_hibp("password")
    if label != "SHA1:5BAA61E4C9B93F3F0682250B6CF8331B7EE68FD8" or prefix != "5BAA6":
        fails.append("case4: SHA-1 前 5 位应为 5BAA6，实际 %s" % prefix)
    if suffix != "1E4C9B93F3F0682250B6CF8331B7EE68FD8":
        fails.append("case4: SHA-1 后缀切分错误：%s" % suffix)
    for fn, args in ((_downsample, ([0] * 4, 2, 2, 8)), (gray_from_rgb, ([1, 2],)),
                     (hamming, (-1, 0))):
        try:
            fn(*args)
            fails.append("case5: %s 未拒绝非法输入 %r" % (fn.__name__, args))
        except ValueError:
            pass
    if gray_from_rgb([0, 255, 0]) != [149]:
        fails.append("case5: 灰度换算错误 %r" % gray_from_rgb([0, 255, 0]))
    if fails:
        for line in fails:
            print("FAIL", line, file=sys.stderr)
        return 1
    print("selftest ok: 5 组断言全过（哈希/距离/判定/哈希类型/参数拒绝）")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="OSINT 图片指纹与泄露检索编排（离线、纯标准库）")
    ap.add_argument("--hash-kind", help="判断 32/40/64 位十六进制哈希的类型")
    ap.add_argument("--hibp", help="计算口令的 SHA-1 及 k-anonymity 前 5 位")
    ap.add_argument("--distance", nargs=2, metavar=("A", "B"), help="两个 64 位哈希的十进制值")
    ap.add_argument("--image", help="PGM(P5) 灰度图，算 dhash/ahash")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出结果")
    ap.add_argument("--selftest", action="store_true", help="运行内置自测")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not (a.hash_kind or a.hibp or a.distance or a.image):
        ap.error("必须提供 --hash-kind / --hibp / --distance / --image 之一（或 --selftest）")
    out = {}
    try:
        if a.hash_kind:
            out["hash_kind"] = hash_kind(a.hash_kind)
        if a.hibp:
            label, prefix, suffix = sha1_hibp(a.hibp)
            out["hibp"] = {"sha1": label, "prefix5": prefix, "suffix": suffix}
        if a.distance:
            x, y = int(a.distance[0], 0), int(a.distance[1], 0)
            dist = hamming(x, y)
            out["distance"] = {"value": dist, "verdict": verdict(dist)}
        if a.image:
            with open(a.image, "rb") as fh:
                data = fh.read()
            if data[:2] != b"P5":
                raise ValueError("只支持 PGM(P5) 灰度图：%s" % a.image)
            parts = data.split(b"\n", 3)
            if len(parts) < 4:
                raise ValueError("PGM 头部不完整：%s" % a.image)
            w, h = (int(v) for v in parts[1].split()[:2])
            px = list(parts[3][:w * h])
            if len(px) < w * h:
                raise ValueError("PGM 像素数据不足：期望 %d，实际 %d" % (w * h, len(px)))
            out["image"] = {"size": [w, h], "dhash": "%016x" % dhash(px, w, h),
                            "ahash": "%016x" % ahash(px, w, h)}
    except (ValueError, OSError) as exc:
        print("失败：%s" % exc, file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for key in sorted(out):
            print("%s: %s" % (key, out[key]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
