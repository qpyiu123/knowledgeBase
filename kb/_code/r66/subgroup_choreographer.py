"""复做 Subgroup Choreographer：python subgroup_choreographer.py 原题.py。需要 numpy 和 pycryptodome；仅将原题源码当作文字读取。"""

import argparse
import re
from ast import literal_eval
from hashlib import sha256, shake_256
from itertools import product
from pathlib import Path

import numpy as np
from Crypto.Cipher import AES


def verify(path):
    source = path.read_text(encoding="utf-8")
    T = literal_eval(re.search(r"T = np.array\((\[\[.+?\]\])", source, re.S)[1])
    cols = [r[0] for r in T]
    rows = T[0]
    group = [[T[cols.index(i)][rows.index(j)] for j in range(16)] for i in range(16)]
    e = T[0][0]

    def cyclic(x):
        ans = [e]
        for _ in range(16):
            a = group[ans[-1]][x]
            if a == e:
                return ans
            ans.append(a)
        raise ValueError("重新编号后未找到循环周期")

    for a, b in product(map(cyclic, range(16)), repeat=2):
        if len(a) != 4 or len(b) != 4:
            continue
        inverse = [group[x][y] for x in a for y in b]
        if len(set(inverse)) == 16:
            break
    else:
        raise AssertionError("未找到坐标系")
    lookup = np.array([divmod(inverse.index(i), 4) for i in range(16)], dtype="int32")
    inv = np.array(inverse, dtype="uint8")

    def params(mapping):
        z = lookup[mapping[e]]
        out = (lookup[[mapping[a[1]], mapping[b[1]]]] - z).T % 4
        assert np.array_equal((lookup @ out.T + z) % 4, lookup[mapping])
        return out, z

    L, l = params(cols)
    R, r = params(rows)
    K = (l + r) % 4
    for i, j in product(range(16), repeat=2):
        assert np.array_equal((L @ lookup[i] + R @ lookup[j] + K) % 4, lookup[T[i][j]])

    def next_layer(A, B, C, length):
        width = len(C)
        I = np.eye(width, dtype="int32")
        powers = [I]
        for _ in range(max(length, 4)):
            powers.append((A @ powers[-1]) % 4)
        weight = [powers[length - 1]] + [
            (powers[length - 1 - i] @ B) % 4 for i in range(1, length)
        ]
        accum = (sum(powers[: length - 1]) @ C) % 4
        U = (powers[3] + A @ B) % 4
        V = (powers[2] @ B + B) % 4
        k = (U @ accum + V @ accum + (I + A + powers[2]) @ C) % 4
        UU = [U @ w % 4 for w in weight]
        VV = [V @ w % 4 for w in weight]
        X = np.zeros((length * width, length * width), dtype="int32")
        Y = np.zeros_like(X)
        for i in range(length):
            for j in range(length):
                x = (i + j) % length
                X[i * width : (i + 1) * width, x * width : (x + 1) * width] = UU[j]
                Y[i * width : (i + 1) * width, x * width : (x + 1) * width] = VV[j]
        return X, Y, np.tile(k, length)

    for length in (16, 6, 2):
        L, R, K = next_layer(L, R, K, length)

    def coords(arr):
        return lookup[arr].flatten()

    def uncoords(x):
        vals = x.reshape(-1, 2)
        return inv[4 * vals[:, 0] + vals[:, 1]].reshape(2, 6, 16)

    def apply(a, b):
        return (L @ a + R @ b + K) % 4

    def sourceval(k):
        return literal_eval(
            re.search(r"(?m)^" + k + r"\s*=\s*(.+)$", source.split("'''")[1])[1]
        )

    c, p1, p2, sig = map(coords, (sourceval(k) for k in ("c", "p1", "p2", "sig")))
    msg = sourceval("msg")
    d = np.frombuffer(shake_256(msg).digest(96), "u1")
    h = coords(np.stack([d >> 4, d & 15], 1))
    n = len(K)
    zero = np.zeros_like(R)
    A = np.block([[R, zero], [zero, R], [L, R]])
    bvec = np.r_[(p1 - L @ c - K) % 4, (sig - L @ h - K) % 4, (p2 - K) % 4]
    work = np.column_stack((A, bvec)) % 4
    i = 0
    pivots = []
    for j in range(2 * n):
        ks = np.flatnonzero(work[i:, j] % 2)
        if len(ks) == 0:
            continue
        k = i + int(ks[0])
        work[[k, i]] = work[[i, k]]
        work[i] = work[i] * int(work[i, j]) % 4
        multipliers = work[:, j].copy()
        multipliers[i] = 0
        work = (work - multipliers[:, None] * work[i]) % 4
        pivots.append(j)
        i += 1
    print("奇数主元：", len(pivots), "未知坐标：", 2 * n)
    assert len(pivots) == 2 * n
    x = work[: 2 * n, -1]
    assert np.array_equal((A @ x) % 4, bvec)
    k, q = x[:n], x[n:]
    assert np.array_equal(apply(c, k), p1)
    assert np.array_equal(apply(k, q), p2)
    assert np.array_equal(apply(h, q), sig)
    secret = {"c": uncoords(c), "k": uncoords(k), "q": uncoords(q)}
    key = sha256(str(secret).encode()).digest()
    cipher = sourceval("cipher")
    nonce = b"Choreographer"
    answer = AES.new(key, AES.MODE_CTR, nonce=nonce).decrypt(cipher)
    assert AES.new(key, AES.MODE_CTR, nonce=nonce).encrypt(answer) == cipher
    assert re.fullmatch(rb"[A-Za-z0-9_]+\{[ -~]+\}", answer)
    print("全部三组公开数组回验，答案格式通过，长度", len(answer))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path, help="赛题原 .py")
    args = parser.parse_args()
    verify(args.file)
