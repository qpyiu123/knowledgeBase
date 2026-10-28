---
title: RSA 小公钥指数攻击（小明文开方 / Coppersmith）
category: crypto
tags: [rsa, 小e, 低加密指数, k 次开方, Coppersmith]
signals: [e=3, e 很小, 公钥指数只有 3, 密文长度和 n 差不多但 e 是 3, flag 很短, 直接开三次方, m 很小, e=5 或 e=17, 没有填充]
difficulty: easy
source: "CTF-Wiki / 公开 writeup"
tools: [python, gmpy2, SageMath]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- `e = 3`（最常见），偶尔 `e = 5`、`e = 17`，甚至 `e = 2`。
- `n` 很大（2048 bit 以上），但 flag 明显很短（几十字节），`m < n^(1/e)`。
- 密文 `c` 换算成十进制后，比 `n` 小很多，甚至 `c < n`。
- 题面代码里 `m = bytes_to_long(flag)`，**没有 OAEP/PKCS 填充**，直接 `pow(m, e, n)`。
- 变体：`c = m^e mod n`，其中 `m = m0 + x`，已知 `m0` 高位（→ Coppersmith）。

## 二、原理

若 `m^e < n`，则 `m^e mod n = m^e`（没有发生模约减），直接对 `c` 开 `e` 次整数方即可：

```
m = c^(1/e)       # 整数 e 次根
```

当 `m^e >= n` 时，真实关系是 `m^e = k*n + c`。若 `k` 不大（例如 `m` 略大于 `n^(1/e)`），可以枚举 `k` 并对 `c + k*n` 开方：

```
for k in range(2**20):
    r = iroot(c + k*n, e)
    if r is exact: return r
```

这就是常说的"小公钥指数攻击 + 爆破 k"。若 `m` 未知高位但已知部分位（如 `m = prefix * 2^k + x`），则转为 Coppersmith 小根求解。

## 三、解题步骤

1. 计算 `bit_length(c)` 与 `bit_length(n)`；`c < n^(1/e)` 时直接开方。
2. 不全成立则 `for k in range(...)` 暴力 `iroot(c + k*n, e)`。
3. 若拿到 `m` 后不是可读 ASCII，检查是否 `m = long_to_bytes(padded)` 或题目做了 bytes 混排。
4. `e=3` 且 `m = m1 * m2`（分段明文相乘）时，用共模/开立方先求 `m^3`，再试 `m1*m2` 因数搜索。
5. 若 `m` 有已知高位或满足 `m < n^(1/e)` 的近似，改用 Coppersmith（见 `rsa-coppersmith.md`）。

## 四、可直接运行的脚本

```python
from Crypto.Util.number import long_to_bytes, bytes_to_long
from gmpy2 import iroot

def small_e_attack(n, e, c, max_k=1 << 20):
    # 情况 1: 没有模约减
    r, exact = iroot(c, e)
    if exact:
        return long_to_bytes(int(r))
    # 情况 2: 枚举 k
    for k in range(max_k):
        r, exact = iroot(int(c + k * n), e)
        if exact:
            return long_to_bytes(int(r))
    raise ValueError("k 太大，考虑 Coppersmith 或 m 高位已知")

# --- 自测 ---
from Crypto.Util.number import getPrime
p, q = getPrime(512), getPrime(512)
n = p * q
e = 3
flag = b"flag{sm4ll_3xp0n3nt_1s_d4ng3r0us}"
m = bytes_to_long(flag)
c = pow(m, e, n)
print(small_e_attack(n, e, c))
```

分段明文变体（`e=3`、已知 `m = m1 * m2`，其中 `m1` 是明文前缀）：

```python
from gmpy2 import iroot
from Crypto.Util.number import long_to_bytes, bytes_to_long

def split_plaintext(n, e, c, known_prefix, max_k=1 << 16):
    """c = (m1*m2)^e mod n，已知 m1 = known_prefix 的字节值"""
    m1 = bytes_to_long(known_prefix)
    for k in range(max_k):
        r, exact = iroot(int(c + k * n), e)   # 拿到 m1*m2 的整数
        if not exact:
            continue
        if int(r) % m1 == 0:
            return known_prefix + long_to_bytes(int(r) // m1)
    return None

# 用法：flag = b"flag{...}"，猜前几个字节 b"flag{" 即可
print(split_plaintext(n, 3, c, b"flag{"))
```

Coppersmith（SageMath）——已知 `m` 的高位 `m0`，低 `k` 位未知：

```python
# sage 环境：known = m0 * 2^k + x，求 x
R.<x> = PolynomialRing(Zmod(n))
f = (known_high * 2^k + x)^e - c
ro = f.small_roots(X=2^k, beta=1, epsilon=0.02)   # 要求 k <= n.bit_length()/e
print([long_to_bytes(int(known_high * 2^k + r)) for r in ro])
```

## 五、常见坑 / 变体

- `iroot` 返回 `(root, is_exact)`，别把元组直接当整数用；`gmpy2.iroot` 对负数会异常。
- `k` 的暴力范围：`m < n` 时 `k < m^e/n`，理论上界为 `n^2`（e=3），实际按 `m` 与 `n^(1/e)` 的差距估算，通常 `2^20` 足够。
- 有些题 `e=3` 但故意把 `n` 的位长调小让 `c > n`，此时公共模数攻击不成立，只能枚举 k。
- 若 `c` 开方得不到可读文本，尝试 `strip(b'\x00')`，或明文是 `int(flag.encode().hex(), 16)` 这类二次编码。
- Coppersmith 失败的常见原因：`beta` 设错（当 `modulus` 不是素数时要设 `beta` 为对应因子比例）、`X` 上界估计过大。
- Håstad 广播攻击见 `rsa-broadcast-attack.md`；两者常被混淆：广播需要**多个不同的 n**，小 e 只需**一个 n**。

## 六、参考来源

- [CTF-Wiki 公钥指数相关攻击](https://ctf-wiki.org/crypto/asymmetric/rsa/rsa_e_attack/)
- [CTF-Wiki Coppersmith 相关攻击](https://ctf-wiki.org/crypto/asymmetric/rsa/rsa_coppersmith_attack/)
- [CTF-Wiki GitHub 仓库](https://github.com/ctf-wiki/ctf-wiki)
- [CrackerCat/RSA-CTF](https://github.com/CrackerCat/RSA-CTF)
