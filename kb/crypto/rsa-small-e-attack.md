---
title: RSA 小公钥指数攻击（小明文开方 / Coppersmith）
category: crypto
tags: [rsa, 小e, 低加密指数, k 次开方, Coppersmith]
signals: [e=3, e 很小, 公钥指数只有 3, 密文长度和 n 差不多但 e 是 3, flag 很短, 直接开三次方, m 很小, e=5 或 e=17, 没有填充]
difficulty: easy
source: "CTF-Wiki / 公开 writeup"
tools: [python, gmpy2, SageMath]
updated: 2026-11-05
---

## 一、识别信号（题面长什么样）

- `e = 3`（最常见），偶尔 `e = 5`、`e = 17`，甚至 `e = 2`。
- `n` 很大（2048 bit 以上），但 flag 明显很短（几十字节），`m < n^(1/e)`。
- 标准密文总满足 `0 <= c < n`。密文短可以作为检查开根的线索，实际用整数根的精确性判断。
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

1. 直接计算 `r, exact = iroot(c, e)`。精确时检查 `0 <= r < n`、`pow(r, e, n) == c` 和题目编码；例如 `n=11413, e=3, c=8000` 可得到 `m=20`，无需先比较 `c` 与 `n^(1/e)`。
2. 不精确时，在明确上限内枚举 `k`，检查 `c + k*n` 的整数根；记录命中的 `k`。上限外是否有解需继续检查题目条件。
3. 将候选按题目指定的字节序与编码还原，再回代加密。可打印率仅用于浏览候选。
4. 若源码明确把两段整数相乘 `m=m1*m2`，可用已知 `m1` 整除；普通字节前缀满足 `m=prefix*256^t+suffix`，应使用已知高位的方法。
5. 已知高位、未知部分足够小时，参考 Coppersmith 小根（见 `rsa-coppersmith.md`）。

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
    raise ValueError("指定 k 范围内未找到精确根，请检查上限、明文长度与填充")

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

# 只适用于题目明确采用整数相乘的构造；普通 flag 字节前缀使用已知高位方法。
print(split_plaintext(n, 3, c, b"flag{"))
```

Coppersmith（SageMath）——已知 `m` 的高位 `m0`，低 `k` 位未知：

```python
# sage 环境：known = m0 * 2^k + x，求 x
R.<x> = PolynomialRing(Zmod(n))
f = (known_high * 2^k + x)^e - c
ro = f.small_roots(X=2^k, beta=1, epsilon=0.02)   # X 需符合小根范围，留出 epsilon 的余量
print([long_to_bytes(int(known_high * 2^k + r)) for r in ro])
```

## 五、常见坑 / 变体

- `iroot` 返回 `(root, is_exact)`，别把元组直接当整数用；`gmpy2.iroot` 对负数会异常。
- `k = (m^e-c)//n`，由明文长度上限估计搜索量；`2^20` 只是示例预算。标准 `m<n`、`e=3` 时有 `k<n^2`，通常无法穷举这个理论范围。
- 标准模幂返回的 `c<n`；若输入 `c>=n`，先核对题面数据、进制和预处理方式。
- `int(flag.hex(), 16)` 与大端 `int.from_bytes(flag, 'big')` 数值相同。前导零字节要按已知原长度恢复，不随意删除。
- Coppersmith 示例需要 SageMath，需确定未知位数和根的范围；本页 Sage 片段本轮未运行。查询完整模数的小根时 `beta=1`，是否使用因子比例取决于所求问题。
- Håstad 广播攻击见 `rsa-broadcast-attack.md`；两者常被混淆：广播需要**多个不同的 n**，小 e 只需**一个 n**。

## 六、参考来源

2026-11-05 修订：原步骤中的 `c < n^(1/e)` 改为整数根精确检查；有限枚举、普通前缀与乘法构造分别说明。可运行的标准库版本见 `kb/_methods/scripts/rsa_small_e.py`，路径对照见 `kb/_reference/rsa-path-check.md`。修订前内容保存在项目 R4 备份和 Git 历史。

- [Handbook of Applied Cryptography 第 8 章，§8.2.2(ii)](https://cacr.uwaterloo.ca/hac/about/chap8.pdf)：核对低指数原理，仅链接，不附 PDF。
- [SageMath small_roots 参数](https://doc.sagemath.org/html/en/reference/polynomial_rings/sage/rings/polynomial/polynomial_modn_dense_ntl.html#sage.rings.polynomial.polynomial_modn_dense_ntl.small_roots)：核对 beta 与根范围，未运行本页 Sage 片段。
- [CTF-Wiki 公钥指数相关攻击](https://ctf-wiki.org/crypto/asymmetric/rsa/rsa_e_attack/)
- [CTF-Wiki Coppersmith 相关攻击](https://ctf-wiki.org/crypto/asymmetric/rsa/rsa_coppersmith_attack/)
- [CTF-Wiki GitHub 仓库](https://github.com/ctf-wiki/ctf-wiki)
- [CrackerCat/RSA-CTF](https://github.com/CrackerCat/RSA-CTF)
