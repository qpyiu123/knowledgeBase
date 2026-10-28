---
title: Shamir 秘密共享与多项式插值还原
category: crypto
tags: [shamir, 秘密共享, 拉格朗日插值, gf256, 门限]
signals: [题目给定 threshold 门限 t, 给了 t 个子秘密分享点, 分享点是 (x y) 坐标对, 源码里出现 random 多项式系数, 系数是素域 mod p 上的随机数, 密钥被拆成 n 份, 只给了一部分分享, 多项式次数比门限小, 常数项就是 flag]
difficulty: medium
source: "CTF-Wiki / Wikipedia Shamir's Secret Sharing / BSidesCbr 2021"
tools: [python, SageMath, gmpy2]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 题面直接写 `threshold = t`、`share = (x, y)`，给了 `t` 个或 `t+1` 个点。
- 源码里有 `poly = [secret] + [randint(0, p-1) for _ in range(t-1)]`，然后 `f(x) = eval(poly, x)`。
- 输出里一堆形如 `(1, 52864...)`、`(2, ...)` 的**有序数对**，`x` 是 1,2,3… 递增。
- 给了「服务器只有你的份额」「我们用 3 份恢复了密钥」之类的提示。
- 分享落在 GF(2^8) 上时，`x` 是 1..255、`y` 是单字节，常见于图片/文件分片题目。
- 附件是一个 `sss`/`gfshare` 生成的 json，字段名是 `shares`、`threshold`、`prime`。

## 二、原理

Shamir (t, n) 门限方案：在有限域 `GF(p)` 上随机取 `t-1` 次多项式

```
f(x) = s + a1*x + a2*x^2 + ... + a_{t-1}*x^{t-1},   (mod p)
```

秘密 `s = f(0)`。第 i 个参与方拿到 `(x_i, f(x_i))`。任意 `t` 个点可唯一确定 `f`，少于 `t` 个点则有 `p^(t-k)` 种可能，信息论上安全。

**拉格朗日插值**直接用 `t` 个点还原 `f(0)`：

```
s = Σ_{i=1..t} y_i * Π_{j≠i} (0 - x_j)/(x_i - x_j)   (mod p)
```

关键工程点：

1. **有限域阶**：`p` 通常是大素数（128/256 位），也可能是 `2^8`。在 `GF(2^8)` 上减法是 XOR、除法要查 log/exp 表或是 `pow(x, 254)`。
2. **x 坐标可能重复或被改**：CTF 常见「给了 t 个点，但其中 2 个 x 相同」，导致插值矩阵奇异，需判断并丢弃。
3. **次数陷阱**：题里 `threshold = t` 但多项式实际次数 `d ≠ t-1`。若实际次数更高，`t` 个点只能拟合出一条**低次近似**，得到的是错的 `f(0)`；此时需要更多点做「一致性校验」（用第 `t+1` 个点验证），或直接拟合实际次数。
4. **系数泄漏变体**：题目额外给了 `f(1)` 或某个系数，等于多一个约束，能解出原本信息不足的情况。

## 三、解题步骤

1. 从附件里抽取 `(x_i, y_i)` 与 `p`（`p` 常在源码里，或 `2^128`、`2^256` 这类 2 的幂——后者说明是 GF(2^k)，不能用整数模）。
2. `if p` 是素数：用 `pow(x, -1, p)` 求逆，直接套拉格朗日公式。
3. `if p == 2^8`：在 GF(2^8) 用 `ginv`（`pow(a, 254)` 或 log 表）。
4. 拿到 `s` 后转 bytes / 转 int 再解 ASCII，通常就是 flag 或 flag 的一部分。
5. 若结果是乱码：先检查是否用多了/用错了点（比如把 `x=0` 的「重分享」混进来），再检查次数是否被刻意调高。

## 四、可直接运行的脚本

```python
# Shamir 秘密共享还原：支持大素数 GF(p) 与 GF(2^8)
import random

def lagrange_at_zero(shares, p):
    """shares: [(x, y)]，返回 f(0) mod p；要求 len(shares) >= 实际次数+1。"""
    s = 0
    for i, (xi, yi) in enumerate(shares):
        num, den = 1, 1
        for j, (xj, _) in enumerate(shares):
            if i == j:
                continue
            num = num * (-xj) % p
            den = den * (xi - xj) % p
        s = (s + yi * num * pow(den, -1, p)) % p
    return s

def split(secret, t, n, p):
    coeffs = [secret] + [random.randrange(p) for _ in range(t - 1)]
    def f(x):
        acc = 0
        for c in reversed(coeffs):
            acc = (acc * x + c) % p
        return acc
    return [(i, f(i)) for i in range(1, n + 1)], coeffs

# ---- GF(2^8) 版本（x 是 1..255，y 是单字节）----
def gf_mul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        if a & 0x100:
            a ^= 0x11B
        b >>= 1
    return r

def gf_pow(a, e):
    r = 1
    while e:
        if e & 1:
            r = gf_mul(r, a)
        a = gf_mul(a, a)
        e >>= 1
    return r

def gf_div(a, b):
    return gf_mul(a, gf_pow(b, 254))

def lagrange_gf256(shares):
    s = 0
    for i, (xi, yi) in enumerate(shares):
        num, den = 1, 1
        for j, (xj, _) in enumerate(shares):
            if i == j:
                continue
            num = gf_mul(num, xj)          # -xj == xj in GF(2^8)
            den = gf_mul(den, xi ^ xj)     # 减法即 XOR
        s ^= gf_mul(yi, gf_div(num, den))
    return s

if __name__ == "__main__":
    # 1) 大素数域
    p = (1 << 127) - 1
    secret = int.from_bytes(b"flag{shamir_demo}", "big") % p
    shares, coeffs = split(secret, 3, 5, p)
    assert lagrange_at_zero(shares[:3], p) == secret
    assert lagrange_at_zero(shares[1:4], p) == secret
    print("GF(p) 还原 OK:", secret == lagrange_at_zero(shares[:3], p))

    # 2) GF(2^8)
    vals = [(1, 0x35), (2, 0x7A), (3, 0xC1)]   # 占位：换成题目给的份额
    print("GF(2^8) f(0) =", hex(lagrange_gf256(vals)))
```

校验「次数是否被偷偷调高」（用第 t+1 个点做一致性检查）：

```python
import random

def split(secret, t, n, p):
    """辅助：生成 (t, n) 门限份额，仅用于自测。"""
    coeffs = [secret] + [random.randrange(p) for _ in range(t - 1)]
    def f(x):
        acc = 0
        for c in reversed(coeffs):
            acc = (acc * x + c) % p
        return acc
    return [(i, f(i)) for i in range(1, n + 1)], coeffs

def verify_extra_point(known, extra, p):
    """known: 用来插值的 t 个点；extra: 多余的 1 个点。
    返回 True 表示次数与门限一致；False 说明题目实际次数更高或数据被污染。"""
    x, y = extra
    # 用 known 插值求出整条多项式在 x 处的值：按点插值，不用 f(0)
    val = 0
    for i, (xi, yi) in enumerate(known):
        num, den = 1, 1
        for j, (xj, _) in enumerate(known):
            if i != j:
                num = num * (x - xj) % p
                den = den * (xi - xj) % p
        val = (val + yi * num * pow(den, -1, p)) % p
    return val == y % p

if __name__ == "__main__":
    p = (1 << 127) - 1
    shares, _ = split(123456789, 3, 5, p)
    print("一致性:", verify_extra_point(shares[:3], shares[3], p))   # True
    # 反例：次数被偷偷调高到 3 次，却只按 2 次插值
    shares2, _ = split(123456789, 4, 5, p)
    print("次数被调高时的一致性:", verify_extra_point(shares2[:3], shares2[3], p))  # False
```

## 五、常见坑 / 变体

- **`p` 是 2 的幂**：`2^128` 不是素数，`pow(den, -1, p)` 会抛 `ValueError`；这说明是 GF(2^k)，必须用 `gf_*` 那一套。
- **x 从 0 开始**：有的库用 `x=0` 作为分享点，但 `f(0)` 本身就是秘密，这种题要么是 bug、要么秘密藏在别的系数里。
- **点重复/顺序被打乱**：插值公式与 `x` 顺序无关，但**不能有重复 x**；重复时先 `dict` 去重。
- **次数被调高**：`threshold=t` 但实际是 `t+1` 次，`t` 个点插出来的 `f(0)` 会「看起来也像 flag 但读不通」，务必用 `verify_extra_point` 校验。
- **负数取模**：Python 的 `% p` 对负数返回非负，直接可用；C/Go 实现里要注意补 `p`。
- **秘密是字节串**：还原出 `s` 后先 `s.to_bytes((s.bit_length()+7)//8, "big")`，别直接 `chr(s)`。
- **GF(2^8) 的乘法多项式**：默认是 `0x11B`（AES），但 GF(256) 分片工具可能用别的不可约多项式，需从源码确认。

## 六、参考来源

- [Wikipedia: Shamir's Secret Sharing](https://en.wikipedia.org/wiki/Shamir%27s_secret_sharing)
- [CTF-Wiki 密码学总览](https://ctf-wiki.org/crypto/introduction/)
- [BSidesCbr 2021 CTF Crypto Writeups（含秘密共享题）](https://jsur.in/posts/2021-04-12-bsidescbr-2021-ctf-crypto-writeups/)
