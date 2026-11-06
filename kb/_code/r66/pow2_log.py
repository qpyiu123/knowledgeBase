"""复做 you_raise_me_up：python pow2_log.py 原题.zip。"""

import argparse
import json
import re
from pathlib import Path
from zipfile import ZipFile


def flag_bytes(m):
    return m.to_bytes((m.bit_length() + 7) // 8, "big")


def verify(path):
    with ZipFile(path) as z:
        txt = z.read(z.namelist()[0]).decode("utf-8")
    g, c = (
        int(re.search(r"(?m)^\s*#\s*" + k + r"\s*=\s*(\d+)", txt)[1])
        for k in ("m", "c")
    )
    k = int(re.search(r"(?m)^n\s*=\s*2\s*\*\*\s*(\d+)", txt)[1])
    period, x = 1, 0
    assert g % 2 == c % 2 == 1
    for i in range(2, k + 1):
        modulus = 1 << i
        if pow(g, period, modulus) == 1:
            assert pow(g, x, modulus) == c % modulus
        else:
            if pow(g, x, modulus) != c % modulus:
                x += period
            period *= 2
            assert pow(g, x, modulus) == c % modulus
    answer = flag_bytes(x)
    assert re.fullmatch(rb"flag\{[^{}\r\n]+\}", answer)
    return {
        "modulus_bits_exponent": k,
        "base_order_power": period.bit_length() - 1,
        "power_checked": True,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path, help="赛题原 ZIP")
    args = parser.parse_args()
    print(json.dumps(verify(args.file), ensure_ascii=False))
