"""按赛题给定的 32 位状态方程还原 SNOW 状态；只接收密文字、已知前缀和公开泄漏。"""

# 取自《密码学题解汇编》shared/src/cryptoexp/utils/snow_state.py。
# 原作者 coolmoon & guaidao2，MIT 许可见同目录 LICENSE.txt。

MASK = 0xFFFFFFFF
# fmt: off
SR = (
    0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B,
    0xFE, 0xD7, 0xAB, 0x76, 0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0,
    0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0, 0xB7, 0xFD, 0x93, 0x26,
    0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
    0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2,
    0xEB, 0x27, 0xB2, 0x75, 0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0,
    0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84, 0x53, 0xD1, 0x00, 0xED,
    0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
    0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F,
    0x50, 0x3C, 0x9F, 0xA8, 0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5,
    0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2, 0xCD, 0x0C, 0x13, 0xEC,
    0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
    0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14,
    0xDE, 0x5E, 0x0B, 0xDB, 0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C,
    0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79, 0xE7, 0xC8, 0x37, 0x6D,
    0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
    0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F,
    0x4B, 0xBD, 0x8B, 0x8A, 0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E,
    0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E, 0xE1, 0xF8, 0x98, 0x11,
    0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
    0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F,
    0xB0, 0x54, 0xBB, 0x16,
)
SQ = (
    0x25, 0x24, 0x73, 0x67, 0xD7, 0xAE, 0x5C, 0x30, 0xA4, 0xEE, 0x6E, 0xCB,
    0x7D, 0xB5, 0x82, 0xDB, 0xE4, 0x8E, 0x48, 0x49, 0x4F, 0x5D, 0x6A, 0x78,
    0x70, 0x88, 0xE8, 0x5F, 0x5E, 0x84, 0x65, 0xE2, 0xD8, 0xE9, 0xCC, 0xED,
    0x40, 0x2F, 0x11, 0x28, 0x57, 0xD2, 0xAC, 0xE3, 0x4A, 0x15, 0x1B, 0xB9,
    0xB2, 0x80, 0x85, 0xA6, 0x2E, 0x02, 0x47, 0x29, 0x07, 0x4B, 0x0E, 0xC1,
    0x51, 0xAA, 0x89, 0xD4, 0xCA, 0x01, 0x46, 0xB3, 0xEF, 0xDD, 0x44, 0x7B,
    0xC2, 0x7F, 0xBE, 0xC3, 0x9F, 0x20, 0x4C, 0x64, 0x83, 0xA2, 0x68, 0x42,
    0x13, 0xB4, 0x41, 0xCD, 0xBA, 0xC6, 0xBB, 0x6D, 0x4D, 0x71, 0x21, 0xF4,
    0x8D, 0xB0, 0xE5, 0x93, 0xFE, 0x8F, 0xE6, 0xCF, 0x43, 0x45, 0x31, 0x22,
    0x37, 0x36, 0x96, 0xFA, 0xBC, 0x0F, 0x08, 0x52, 0x1D, 0x55, 0x1A, 0xC5,
    0x4E, 0x23, 0x69, 0x7A, 0x92, 0xFF, 0x5B, 0x5A, 0xEB, 0x9A, 0x1C, 0xA9,
    0xD1, 0x7E, 0x0D, 0xFC, 0x50, 0x8A, 0xB6, 0x62, 0xF5, 0x0A, 0xF8, 0xDC,
    0x03, 0x3C, 0x0C, 0x39, 0xF1, 0xB8, 0xF3, 0x3D, 0xF2, 0xD5, 0x97, 0x66,
    0x81, 0x32, 0xA0, 0x00, 0x06, 0xCE, 0xF6, 0xEA, 0xB7, 0x17, 0xF7, 0x8C,
    0x79, 0xD6, 0xA7, 0xBF, 0x8B, 0x3F, 0x1F, 0x53, 0x63, 0x75, 0x35, 0x2C,
    0x60, 0xFD, 0x27, 0xD3, 0x94, 0xA5, 0x7C, 0xA1, 0x05, 0x58, 0x2D, 0xBD,
    0xD9, 0xC7, 0xAF, 0x6B, 0x54, 0x0B, 0xE0, 0x38, 0x04, 0xC8, 0x9D, 0xE7,
    0x14, 0xB1, 0x87, 0x9C, 0xDF, 0x6F, 0xF9, 0xDA, 0x2A, 0xC4, 0x59, 0x16,
    0x74, 0x91, 0xAB, 0x26, 0x61, 0x76, 0x34, 0x2B, 0xAD, 0x99, 0xFB, 0x72,
    0xEC, 0x33, 0x12, 0xDE, 0x98, 0x3B, 0xC0, 0x9B, 0x3E, 0x18, 0x10, 0x3A,
    0x56, 0xE1, 0x77, 0xC9, 0x1E, 0x9E, 0x95, 0xA3, 0x90, 0x19, 0xA8, 0x6C,
    0x09, 0xD0, 0xF0, 0x86,
)
# fmt: on


def mulx(v, c):
    return ((v << 1) ^ (c if v & 128 else 0)) & 255


def power(v, n):
    for _ in range(n):
        v = mulx(v, 0xA9)
    return v


def alpha_byte(v, exps):
    return sum(power(v, e) << (24 - 8 * i) for i, e in enumerate(exps))


MA = tuple(alpha_byte(v, (23, 245, 48, 239)) for v in range(256))
DA = tuple(alpha_byte(v, (16, 39, 6, 64)) for v in range(256))


def left(w):
    return ((w << 8) ^ MA[w >> 24]) & MASK


def right(w):
    return (w >> 8) ^ DA[w & 255]


def mix(w, c):
    a, b, d, e = [w >> j & 255 for j in (24, 16, 8, 0)]
    vals = (
        mulx(a, c) ^ b ^ d ^ mulx(e, c) ^ e,
        mulx(a, c) ^ a ^ mulx(b, c) ^ d ^ e,
        a ^ mulx(b, c) ^ b ^ mulx(d, c) ^ e,
        a ^ b ^ mulx(d, c) ^ d ^ mulx(e, c),
    )
    return sum(v << (24 - i * 8) for i, v in enumerate(vals))


def linear_inverse(fn):
    rows = [
        sum(((fn(1 << j) >> i) & 1) << j for j in range(32)) | (1 << (32 + i))
        for i in range(32)
    ]
    for j in range(32):
        pivot = next((i for i in range(j, 32) if rows[i] >> j & 1), None)
        if pivot is None:
            raise ValueError("状态线性映射不可逆")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        for i in range(32):
            if i != j and rows[i] >> j & 1:
                rows[i] ^= rows[j]
    masks = tuple(row >> 32 for row in rows)
    return lambda w: sum(((w & m).bit_count() & 1) << i for i, m in enumerate(masks))


INV_LEFT = linear_inverse(left)
INV_RIGHT = linear_inverse(right)
UNMIX = (linear_inverse(lambda w: mix(w, 0x1B)), linear_inverse(lambda w: mix(w, 0x69)))
INVS = (tuple(SR.index(i) for i in range(256)), tuple(SQ.index(i) for i in range(256)))


def box(w, kind):
    table = (SR, SQ)[kind]
    sub = sum(table[w >> j & 255] << j for j in (24, 16, 8, 0))
    return mix(sub, (0x1B, 0x69)[kind])


def inverse_box(w, kind):
    sub = UNMIX[kind](w)
    table = INVS[kind]
    return sum(table[sub >> j & 255] << j for j in (24, 16, 8, 0))


def generate(initial_s, initial_r, n, check=lambda: None):
    s = list(initial_s)
    r1, r2, r3 = initial_r
    stream = []
    states = [tuple(initial_r)]
    for i in range(n):
        check()
        stream.append(((s[i + 15] + r1) & MASK) ^ r2 ^ s[i])
        r1, r2, r3 = (r2 + (r3 ^ s[i + 5])) & MASK, box(r1, 0), box(r2, 1)
        states.append((r1, r2, r3))
        s.append(left(s[i]) ^ s[i + 2] ^ right(s[i + 11]))
    return stream, s, states


def recover(ciphertext, gift, leaks, check=lambda: None):
    if (
        type(ciphertext) not in (list, tuple)
        or not 16 <= len(ciphertext) <= 512
        or any(type(x) is not int or not 0 <= x <= MASK for x in ciphertext)
    ):
        raise ValueError("SNOW 密文须为 16..512 项 uint32")
    if type(gift) is not bytes or not 9 <= len(gift) <= len(ciphertext):
        raise ValueError("明确的已知前缀不足或越界")
    if (
        type(leaks) not in (list, tuple)
        or len(leaks) != 10
        or any(type(x) is not int or not 0 <= x <= MASK for x in leaks)
    ):
        raise ValueError("状态泄漏须为指定顺序的 10 项 uint32")
    n = len(ciphertext)
    known = {}
    edges = []
    z = [c ^ p for c, p in zip(ciphertext, gift)]

    def S(i):
        return ("s", i)

    def R(k, i):
        return ("r" + str(k), i)

    changed = False

    def put(key, value, operation, inputs=()):
        nonlocal changed
        value &= MASK
        if key in known:
            if known[key] != value:
                raise ValueError("状态关系冲突：" + operation)
            return
        known[key] = value
        changed = True
        edges.append(
            {
                "output": list(key),
                "operation": operation,
                "inputs": [list(x) for x in inputs],
            }
        )

    seed_keys = [
        R(0, 2),
        R(1, 2),
        R(2, 2),
        S(2),
        S(3),
        S(6),
        S(7),
        S(8),
        R(0, 5),
        R(0, 7),
    ]
    for key, value in zip(seed_keys, leaks):
        put(key, value, "provided leak")
    for iteration in range(4 * n + 64):
        check()
        changed = False
        for i in range(n):
            for kind in (0, 1):
                a, b = R(kind, i), R(kind + 1, i + 1)
                if a in known:
                    put(b, box(known[a], kind), "S-box forward", (a,))
                elif b in known:
                    put(a, inverse_box(known[b], kind), "S-box inverse", (b,))
            keys = [R(0, i + 1), R(1, i), R(2, i), S(i + 5)]
            missing = [j for j, k in enumerate(keys) if k not in known]
            if len(missing) == 1:
                j = missing[0]
                v = [known.get(k) for k in keys]
                value = (
                    ((v[1] + (v[2] ^ v[3])) & MASK)
                    if j == 0
                    else ((v[0] - (v[2] ^ v[3])) & MASK)
                    if j == 1
                    else (((v[0] - v[1]) & MASK) ^ v[3])
                    if j == 2
                    else (((v[0] - v[1]) & MASK) ^ v[2])
                )
                put(
                    keys[j],
                    value,
                    "FSM add/XOR inverse",
                    tuple(k for k in keys if k in known),
                )
            keys = [S(i + 16), S(i), S(i + 2), S(i + 11)]
            missing = [j for j, k in enumerate(keys) if k not in known]
            if len(missing) == 1:
                j = missing[0]
                v = [known.get(k) for k in keys]
                value = (
                    (left(v[1]) ^ v[2] ^ right(v[3]))
                    if j == 0
                    else INV_LEFT(v[0] ^ v[2] ^ right(v[3]))
                    if j == 1
                    else (v[0] ^ left(v[1]) ^ right(v[3]))
                    if j == 2
                    else INV_RIGHT(v[0] ^ left(v[1]) ^ v[2])
                )
                put(
                    keys[j],
                    value,
                    "LFSR linear inverse",
                    tuple(k for k in keys if k in known),
                )
            if i < len(z):
                keys = [S(i + 15), R(0, i), R(1, i), S(i)]
                missing = [j for j, k in enumerate(keys) if k not in known]
                if len(missing) == 1:
                    j = missing[0]
                    v = [known.get(k) for k in keys]
                    value = (
                        ((z[i] ^ v[2] ^ v[3]) - v[1]) & MASK
                        if j == 0
                        else ((z[i] ^ v[2] ^ v[3]) - v[0]) & MASK
                        if j == 1
                        else z[i] ^ v[3] ^ ((v[0] + v[1]) & MASK)
                        if j == 2
                        else z[i] ^ v[2] ^ ((v[0] + v[1]) & MASK)
                    )
                    put(
                        keys[j],
                        value,
                        "known keystream equation",
                        tuple(k for k in keys if k in known),
                    )
        if not changed:
            break
    initial = [S(i) for i in range(16)] + [R(k, 0) for k in range(3)]
    missing = [k for k in initial if k not in known]
    if missing:
        raise ValueError(
            "状态传播仍缺 " + str(len(missing)) + " 个初始字；未猜测或穷举剩余状态"
        )
    stream, all_s, all_r = generate(
        [known[S(i)] for i in range(16)], [known[R(k, 0)] for k in range(3)], n, check
    )
    for key, value in known.items():
        check()
        actual = all_s[key[1]] if key[0] == "s" else all_r[key[1]][int(key[0][1])]
        if actual != value:
            raise ValueError("独立正向重放与恢复状态冲突")
    plain = [c ^ k for c, k in zip(ciphertext, stream)]
    if any(x > 255 for x in plain):
        raise ValueError("恢复结果不满足原始单字节明文宽度")
    plain = bytes(plain)
    if not plain.startswith(gift) or any(
        (p ^ k) != c for p, k, c in zip(plain, stream, ciphertext)
    ):
        raise ValueError("已知前缀或原始密文复验失败")
    return plain, {
        "initial_lfsr": [known[S(i)] for i in range(16)],
        "initial_fsm": [known[R(k, 0)] for k in range(3)],
        "recovered_state_words": len(known),
        "propagation_passes": iteration + 1,
        "edges": edges,
        "known_prefix_verified": True,
        "all_state_relations_verified": True,
        "original_ciphertext_verified": True,
        "leaks_verified": 10,
        "key_recovered": False,
        "source_executed": False,
    }
