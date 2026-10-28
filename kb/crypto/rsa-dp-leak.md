---
title: RSA dp 泄露攻击
category: crypto
tags: [rsa, dp 泄露, 私钥泄露, 模运算]
signals: [给了 dp, 题目吐出 dp, dq 或 dp, e d p q 部分已知, 只知道 dp, private key partial, dp dq 泄漏, 给了 p 和 dp, 给了 dp 和 n]
difficulty: easy
source: "CTF-Wiki / 公开 writeup"
tools: [python, gmpy2, SageMath]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 题面直接给 `dp = d % (p-1)`（有时还配 `dq`、`p`、`e`、`c`）。
- 常见形式：`dp = pow(d, 1, p-1)`、`print(dp)`，且**没有给 `p` 和 `q`**。
- 变体：给了 `dp` 和 `dq`，让恢复 `n` 或 `p`。
- 变体：题目说明"服务器只告诉你 dp"，且 `e` 比较小（如 65537）。
- 变体：给了 `d` 的高位（`d >> 200`）—— 那是 `partial key exposure`，不在这里，见 `rsa-coppersmith.md`。

## 二、原理

`dp ≡ d mod (p-1)`，而 `e*d ≡ 1 mod (p-1)(q-1)`。因此：

```
e*dp ≡ 1  (mod p-1)
→ e*dp - 1 = k*(p-1),  k ∈ [1, e-1]
→ p = (e*dp - 1)/k + 1
```

`k` 的取值范围只是 `1..e-1`（因为 `d < φ`，`dp < p-1`，推出 `e*dp - 1 < e*(p-1)`）。对每个 `k` 计算候选 `p`，验证 `n % p == 0` 即可。

**若 `n` 未知**：`n = k'*(p-1)*... ` 不可用，但可以反过来：已知 `p = (e*dp-1)/k + 1` 后，若还给了 `n` 就能验；若 `n` 是题目给的"新模数"，可先试着分解。

若 `e` 很大导致 `k` 空间大，用**同余法**更高效：

```
p = (e*dp - 1) / k + 1，等价于 e*dp ≡ 1 (mod p-1)
```

## 三、解题步骤

1. 拿到 `n, e, c, dp`。
2. `for k in range(1, e): p = (e*dp - 1)//k + 1`；`if n % p == 0` → 命中。
3. `q = n // p`，`d = invert(e, (p-1)*(q-1))`，解密。
4. 只给 `dp, dq` 且 `n` 未知时：用 `edp-1 = k(p-1)` 和 `edq-1 = l(q-1)` 联立，或直接 `gcd` 相关量。常见做法是构造 `n` 的近似。
5. 若 `e` 极大（如 128 bit），改为对 `k` 做 `gcd` 加速或用 Sage 的 `Integer` 大整数运算。

## 四、可直接运行的脚本

```python
from Crypto.Util.number import long_to_bytes, inverse
import gmpy2, tqdm

def dp_leak(n, e, dp):
    for k in range(1, e):
        if (e * dp - 1) % k:
            continue
        p = (e * dp - 1) // k + 1
        if p > 1 and n % p == 0:
            return p, n // p
    return None

def solve(n, e, c, dp):
    p, q = dp_leak(n, e, dp)
    assert p * q == n
    d = inverse(e, (p - 1) * (q - 1))
    return long_to_bytes(pow(c, d, n))

# --- 自测 ---
from Crypto.Util.number import getPrime
p, q = getPrime(512), getPrime(512)
n, e = p * q, 65537
d = inverse(e, (p - 1) * (q - 1))
dp = d % (p - 1)
m = int.from_bytes(b"flag{dp_l34k_4tt4ck}", "big")
c = pow(m, e, n)
print(solve(n, e, c, dp))
```

只给 `dp` 和 `dq`、`n` 未知（利用 `n = p*q` 与 `dp,dq` 关系简化）：

只给 `p` 和 `dp`、`q` 未知但给了 `n`：

```python
# n = p*q，p 已知，q 直接除；dp 的意义只在于验证
q = n // p
assert p * q == n
assert (e * dp - 1) % (p - 1) == 0      # 验证 dp 合法性
d = inverse(e, (p - 1) * (q - 1))
print(long_to_bytes(pow(c, d, n)))
```

`e` 很大（如 1024 bit）时不要暴力 `k`，改用下面两种手法：

```python
# 手法 A：gcd 抓公因子（dp、dq 同时泄露出错时会命中）
g = gmpy2.gcd(e * dp - 1, n)
if g not in (1, n):
    print("p =", g)

# 手法 B：枚举 dp 的商 k 太慢 → 转成求同余式的解
#   e*dp - 1 = k*(p-1)  <=>  p = (e*dp-1)/k + 1
#   对 k 二分：p 随 k 单调下降，用 p <= sqrt(n) 先夹到候选区间再逐个验
lo, hi = 1, e
while lo < hi:
    mid = (lo + hi) // 2
    p = (e * dp - 1) // mid + 1
    if p > int(n ** 0.5):
        hi = mid            # k 太小 → p 太大 → 增大 k
    else:
        lo = mid + 1
# 在 lo 附近几十个 k 里逐个 n % p 验证
for k in range(max(1, lo - 64), lo + 64):
    p = (e * dp - 1) // k + 1
    if p > 1 and n % p == 0:
        print("p =", p); break
```

## 五、常见坑 / 变体

- `k` 的范围是 `1..e-1`，`e=65537` 时遍历很快；`e` 是 128 bit 时不要暴力，改用 `gmpy2` 的 `is_square` 或 `Sage` 的 `nth_root`/格方法。
- `dp` 有时是 `d mod p` 而不是 `d mod (p-1)`（题目命名随意），两者算法相同（`p-1` 换成 `p`），但要相应调整 `k` 上界。
- 若 `n % p != 0` 对所有 `k` 成立：检查 `dp` 是否被加了干扰/截断（如只给 `dp` 的高位，此时需要 Coppersmith）。
- 只有 `dq` 时同理，`q = (e*dq-1)/k + 1`。
- 给了 `p` 和 `dp` 但没给 `q`：直接 `q = n // p`。
- 注意 `(p-1)` 与 `(q-1)` 的 `phi` 与 `lambda = lcm(p-1,q-1)` 区别：用 `phi` 解出的 `d` 可能不是"原 `d`"，但解密同样正确。

## 六、参考来源

- [CTF-Wiki 私钥 d 相关攻击](https://ctf-wiki.org/crypto/asymmetric/rsa/d_attacks/rsa_d_attack/)
- [CTF-Wiki RSA 侧信道攻击](https://ctf-wiki.org/crypto/asymmetric/rsa/rsa_side_channel/)
- [CTF-Wiki GitHub](https://github.com/ctf-wiki/ctf-wiki)
- [奇安信攻防社区 CTF-RSA 总结](https://mdr.skyeye.qianxin.com/forum/share/478)
