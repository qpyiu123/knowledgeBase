"""位切片枚举 MyCode 的低位密钥。输入密文、已知密钥高位、未知位数和明文前缀。"""

# 取自《密码学题解汇编》shared/src/cryptoexp/utils/nibble_spn.py。
# 原作者 coolmoon & guaidao2，MIT 许可见同目录 LICENSE.txt。

SBOX = (9, 4, 10, 11, 13, 1, 8, 5, 6, 2, 0, 3, 12, 14, 15, 7)
INV = tuple(SBOX.index(i) for i in range(16))


def round_keys(key, rounds=10):
    keys = []
    for _ in range(rounds):
        keys.append(key)
        key ^= ((key << 1) & 0xFFFFFFFF) | (key >> 31)
    return keys


def crypt(data, key, decrypt=False):
    if type(data) is not bytes or len(data) > 8192 or len(data) % 4:
        raise ValueError("SPN 输入须为四字节分组且在容量内")
    if type(key) is not int or not 0 <= key < 2**32:
        raise ValueError("SPN 密钥须为 32 位整数")
    keys = round_keys(key)
    out = bytearray(data)
    for r in reversed(keys) if decrypt else keys:
        for i, x in enumerate(out):
            k = (r >> ((i % 4) * 8)) & 255
            if decrypt:
                x ^= k
                out[i] = INV[x & 15] | (INV[x >> 4] << 4)
            else:
                out[i] = (SBOX[x & 15] | (SBOX[x >> 4] << 4)) ^ k
    return bytes(out)


def bit_variable(bit, count):
    if count < 8:
        return sum(((i >> bit) & 1) << i for i in range(count))
    stride = 1 << bit
    if stride < 8:
        byte = sum(((i >> bit) & 1) << i for i in range(8))
        raw = bytes([byte]) * (count // 8)
    else:
        raw = (b"\0" * (stride // 8) + b"\xff" * (stride // 8)) * (
            count // (2 * stride)
        )
    return int.from_bytes(raw, "little")


def sub_planes(v, mask):
    out = [0, 0, 0, 0]
    for value, result in enumerate(SBOX):
        term = mask
        for j in range(4):
            term &= v[j] if value >> j & 1 else mask ^ v[j]
        for j in range(4):
            if result >> j & 1:
                out[j] |= term
    return out


def recover(ct, base, unknown, prefix, check=lambda: None):
    if (
        type(unknown) is not int
        or not 0 <= unknown <= 20
        or type(base) is not int
        or not 0 <= base < 2**32
        or base & ((1 << unknown) - 1)
    ):
        raise ValueError("部分密钥范围无效或未知位超过 20")
    if type(prefix) is not bytes or not 4 <= len(prefix) <= 32 or len(prefix) > len(ct):
        raise ValueError("至少需要 4 字节明确的已知明文前缀")
    if type(ct) is not bytes or not len(ct) % 4 == 0 or len(ct) > 8192:
        raise ValueError("密文不是容量内完整分组")
    count = 1 << unknown
    mask = (1 << count) - 1
    planes = [
        bit_variable(i, count) if i < unknown else mask if base >> i & 1 else 0
        for i in range(32)
    ]
    keys = []
    for _ in range(10):
        check()
        keys.append(planes)
        planes = [planes[i] ^ planes[(i - 1) % 32] for i in range(32)]
    valid = mask
    for pos in range(4):
        check()
        state = [mask if prefix[pos] >> j & 1 else 0 for j in range(8)]
        for key in keys:
            check()
            state = sub_planes(state[:4], mask) + sub_planes(state[4:], mask)
            state = [v ^ key[(pos % 4) * 8 + j] for j, v in enumerate(state)]
        for j, v in enumerate(state):
            valid &= v if ct[pos] >> j & 1 else mask ^ v
        if not valid:
            return [], dict(searched=count, first_block_matches=0)
    records = []
    matches = valid.bit_count()
    if matches > 4096:
        raise ValueError("首块命中超过 4096，未静默截断；需更强约束")
    while valid:
        check()
        lowest = valid & -valid
        k = base + lowest.bit_length() - 1
        valid ^= lowest
        raw = crypt(ct, k, True)
        if not raw.startswith(prefix):
            continue
        if crypt(raw, k) != ct:
            raise ValueError("SPN 重加密核验失败")
        records.append((k, raw))
        if len(records) > 128:
            raise ValueError("最终候选超过 128，未静默截断")
    return records, dict(
        searched=count,
        first_block_matches=matches,
        keys_verified=len(records),
        all_reencrypted=True,
        source_executed=False,
        zero_padding_ambiguous=True,
    )
