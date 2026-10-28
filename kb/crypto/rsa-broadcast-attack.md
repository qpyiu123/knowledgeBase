---
title: RSA 低加密指数广播攻击（Håstad）
category: crypto
tags: [rsa, 广播攻击, Håstad, CRT, 小e]
signals: [多组密文, 多个 n, e 相同且很小, e=3, 同一明文发给多个人, 三个密文, 不同的模数, 同一个 flag 加密多次, 广播]
difficulty: medium
source: "CTF-Wiki / 公开 writeup"
tools: [python, gmpy2, SageMath]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 给出 `e = 3`（或 5、7），以及 **至少 `e` 组** `(n_i, c_i)`，即 `n1, c1, n2, c2, n3, c3`。
- 题面故事："Alice、Bob、Carol 用各自的 RSA 公钥加密了同一条消息"。
- 多个 `n` 互不相同，但 `e` 全都一样且很小。
- 变体：给了 `n` 列表和 `c` 列表（`ns = [...]`、`cs = [...]`）。
- 变体：同一人用不同 `e`、不同 `n` 加密同一明文（广义 Håstad，需要 Coppersmith）。

## 二、原理

同一条明文 `m`，在 `e` 个不同模数下：

```
c_i = m^e mod n_i ,  i = 1..e
```

由**中国剩余定理**，在这 `e` 个 `n_i` 互素的前提下，可求出唯一解：

```
x ≡ c_i (mod n_i)   →   x = m^e  (mod N),  N = n1*n2*...*ne
```

由于 `m < min(n_i)`，有 `m^e < N`（`N` 远大于 `m^e`），所以 CRT 解出来的 `x` **就等于** `m^e`（不发生溢出），直接开 `e` 次整数根即得 `m`。

关键在于：`e` 组密文缺一不可。若只有 `e-1` 组，则 `x = m^e mod (n1..n_{e-1})`，只能得到关于 `m^e` 的部分信息。

## 三、解题步骤

1. 确认 `len(cs) >= e` 且各 `n` 两两互素（`gcd` 检查；若不互素，直接分解，见坑点）。
2. 用 CRT 合并出 `x = m^e mod N`。
3. `m = iroot(x, e)`，`long_to_bytes`。
4. 若开根不精确 → 说明 `m^e` 超过了 `N` 或 `m` 高位已知，需要 Coppersmith 版本。

## 四、可直接运行的脚本

```python
from Crypto.Util.number import long_to_bytes
from gmpy2 import iroot, gcd
from functools import reduce

def crt(residues, moduli):
    x = 0
    M = reduce(lambda a, b: a * b, moduli, 1)
    for r, n in zip(residues, moduli):
        Mi = M // n
        x += r * Mi * pow(Mi, -1, n)
    return x % M

def hastad(ns, cs, e):
    assert len(ns) >= e, "密文组数不足 e"
    for i in range(len(ns)):
        for j in range(i + 1, len(ns)):
            if gcd(ns[i], ns[j]) != 1:
                raise ValueError("n_i 不互素，先走 gcd 分解分支")
    x = crt(cs[:e], ns[:e])
    m, exact = iroot(x, e)
    assert exact, "开方不精确：需要 Coppersmith 变体"
    return long_to_bytes(int(m))

# --- 自测 ---
from Crypto.Util.number import getPrime, bytes_to_long
flag = b"flag{H4stad_br0adcast_att4ck}"
m = bytes_to_long(flag)
e = 3
ns, cs = [], []
for _ in range(e):
    while True:
        p, q = getPrime(512), getPrime(512)
        n = p * q
        if n > m ** e:            # 保证 m < n
            break
    ns.append(n); cs.append(pow(m, e, n))
print(hastad(ns, cs, e))
```

同一明文不同 `e` 的广义 Håstad（SageMath，需要 `e_i` 互素且 `m` 的位数满足条件）：

```python
# sage: 已知 e1,e2,e3 与对应 (n_i, c_i)，用 CRT + Coppersmith
# 典型形式：c_i = (m*2^k + r_i)^e mod n_i，共同未知为 m
R.<x> = PolynomialRing(Zmod(N_crt))
f = prod([(x * 2**k + Integer(r_i))^e_i for ...]) - X_crt
print(f.monic().small_roots(X=2**k, beta=1))
```

## 五、常见坑 / 变体

- **组数不够**：只有 2 组 `e=3` 的密文无法开方，可以考虑"小明文 + k 枚举"，或找隐藏的第三组。
- **`n_i` 不互素**：`p = gcd(n_i, n_j)` 直接分解两个模数 —— 这是另一种送分攻击（gcd 分解），同样值得单列检查。
- **`m` 被加了随机填充**：每次 `m` 不同 → Håstad 失效，要检查题面 `m = bytes_to_long(flag + os.urandom(8))` 之类。
- **开方不精确**：先 `x + k*N` 尝试（`k` 很小），或换 Coppersmith。
- **模数是素数**：`n_i` 是素数时 `phi` 就是 `n_i-1`，题目可能实际上考的是"共模"或"小 e"，别被冲昏头。
- 与 `rsa-small-e-attack.md` 区分：广播需要**多个 `n`**，小 e 只要**一个 `n`**。

## 六、参考来源

- [CTF-Wiki 模数相关攻击（低加密指数广播攻击）](https://ctf-wiki.org/crypto/asymmetric/rsa/rsa_module_attack/)
- [CTF-Wiki 公钥指数相关攻击](https://ctf-wiki.org/crypto/asymmetric/rsa/rsa_e_attack/)
- [CTF-Wiki GitHub](https://github.com/ctf-wiki/ctf-wiki)
