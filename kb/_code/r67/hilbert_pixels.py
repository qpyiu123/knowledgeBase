"""按 Hilbert 顺序重排竖条像素。依赖 Pillow，默认只核对结果，不写还原图。

用法：python hilbert_pixels.py ct.png
要另存还原图时加 --output 路径，原输入保持不变。
"""

import argparse
from pathlib import Path


def hilbert_xy(side, position):
    x = y = 0
    scale = 1
    while scale < side:
        rx = (position >> 1) & 1
        ry = (position ^ rx) & 1
        if not ry:
            if rx:
                x, y = scale - 1 - x, scale - 1 - y
            x, y = y, x
        x += scale * rx
        y += scale * ry
        position >>= 2
        scale <<= 1
    return x, y


def restore_pixels(stream, side):
    """输入与输出是按行存放的 RGB 字节。"""
    if side < 1 or side & (side - 1) or len(stream) != 3 * side * side:
        raise ValueError("需要 2 的幂边长，以及恰好 side² 个 RGB 像素。")
    positions = [hilbert_xy(side, i) for i in range(side * side)]
    assert len(set(positions)) == len(positions)
    assert all(
        abs(x1 - x2) + abs(y1 - y2) == 1
        for (x1, y1), (x2, y2) in zip(positions, positions[1:])
    )
    out = bytearray(len(stream))
    offsets = [(y * side + x) * 3 for x, y in positions]
    for i, j in enumerate(offsets):
        out[j : j + 3] = stream[i * 3 : i * 3 + 3]
    assert b"".join(out[j : j + 3] for j in offsets) == stream
    return bytes(out)


def main():
    from math import isqrt

    from PIL import Image

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", type=Path, help="竖条像素 PNG")
    ap.add_argument("--output", type=Path, help="可选：另存还原图")
    args = ap.parse_args()
    with Image.open(args.input) as image:
        if image.width != 1 or image.mode != "RGB":
            ap.error("输入必须是单列 RGB 图。")
        side = isqrt(image.height)
        restored = restore_pixels(image.tobytes(), side)
    if args.output:
        if args.output.resolve() == args.input.resolve():
            ap.error("请选择不同的输出路径。")
        Image.frombytes("RGB", (side, side), restored).save(args.output)
    print(f"{side}×{side}；坐标覆盖、相邻与逆序读回均已核对。")


if __name__ == "__main__":
    main()
