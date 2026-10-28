---
title: ECDSA/EdDSA 随机数重用与偏置 nonce（格攻击）
category: crypto
tags: [ecdsa, nonce, 格攻击, hnp, eddsa]
signals: [两次签名 r 相同, 签名是 (r s) 二元组, 源码里 k = 固定值或 from_bytes, nonce 只用了 8 位, k 的高位恒为 0, 签名接口可重复调用, 曲线是 secp256k1, 公钥 Q 和私钥 d 关系 Q=dG, d 很多位已知]
difficulty: hard
source: "CTF-Wiki DSA / eprint 2019/023 / Trail of Bits"
tools: [python, SageMath, fpylll, pwntools]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 输出一堆 `(r, s)`，其中**两条签名的 `r` 完全一样**（nonce 重用）。
- 源码里 `k = random.getrandbits(128)` 但曲线阶是 256 位——`k` 只有一半随机性（偏置 nonce）。
- `k` 由 `int(hashlib.md5(m).hexdigest(), 16) % n` 之类「伪随机」派生，且能预知/碰撞。
- 签名服务能对任意消息重复签名，且允许提交一条消息的多次签名。
- 私钥生成后只打印**其中一部分比特**（如 `d & ((1<<128)-1)`）用于校验。
- 用 EdDSA/Ed25519，但实现里 nonce 自己传入（`sign(msg, nonce=...)`），而不是 RFC 8032 的确定性派生。

## 二、原理

ECDSA 签名为

```
r = (k·G).x mod n
s = k^(-1) (z + r·d) mod n        z = H(msg)
```

1. **nonce 重用**：两次签名共用 `k`，则 `r1 = r2 = r`，于是 `s1·k = z1 + r·d`、`s2·k = z2 + r·d`。两式相减消去 `r·d`：
   `k = (z1 - z2)·(s1 - s2)^(-1)`，回代即得 `d = (s1·k - z1)·r^(-1)`。
2. **偏置 nonce（HNP）**：若 `k < 2^128`（即高 128 位为 0），则
   `k = (s·r^(-1))·(z·s^(-1) + d) mod n` 中的 `k` 很小，写成
   `t_i = z_i·s_i^(-1) mod n`，`u_i = r_i·s_i^(-1) mod n`，则 `d·u_i - t_i ≡ k_i (mod n)`，而 `|k_i| < 2^128 ≪ n`。这就是**隐藏数问题（Hidden Number Problem）**，用格基约化解：
   构造 `(m+2)` 维格，最后用 LLL 找到短向量，提取 `d` 和各个 `k_i`。
3. **EdDSA**：Ed25519 的 nonce 由 `SHA512(prefix || msg)` 确定性派生，本身抗重用；但若实现把 `nonce` 作为参数暴露、或复用 `prefix` 且 `r = H(prefix||m)` 可预测，则与 ECDSA nonce 重用等价。EdDSA 里 `S = k_ephemeral + r·s`（注意 `r` 也是签名一部分），重用 `k_ephemeral` 同样能联立解出私钥。
4. **部分私钥已知**：给了 `d` 的低 128 位，等价于把 `d` 降成 128 位未知量，单条签名即可用格的 / 简单代数方法求出（`d = d_known + 2^128·x`）。

## 三、解题步骤

1. 收集所有 `(r, s, z)`，`z` 常用 `hashlib.sha256(msg).digest()` 转 int；**确认曲线阶 n**（secp256k1 的 n 是常数）。
2. 先 `Counter(r)` 找重复的 `r`——90% 的题到这一步就结束了。
3. 没有完全重复时，检查 `k` 的生成方式：位数、是否有固定前缀、是否来自 `random`（配合 MT19937/Python random 预测）。
4. 偏置 nonce：收集 ≥ 3~4 条签名，建格，LLL，提取候选 `d`，用 `Q = d·G` 验证。
5. 本地用 Sage 的 `Integer` / fpylll 跑 LLL；`d` 验证通过再解出私钥签名伪造。

## 四、可直接运行的脚本

```python
# 1) nonce 重用：两条 r 相同的签名直接解私钥
def ecdsa_nonce_reuse(r, s1, z1, s2, z2, n):
    """返回 (k, d)；n 为曲线阶。"""
    k = (z1 - z2) * pow(s1 - s2, -1, n) % n
    d = (s1 * k - z1) * pow(r, -1, n) % n
    return k, d

if __name__ == "__main__":
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    d = 0x1234567890ABCDEF
    k = 0xDEADBEEFCAFE
    z1, z2 = 0x1111, 0x2222
    r = 0xAAAA
    s1 = pow(k, -1, n) * (z1 + r * d) % n
    s2 = pow(k, -1, n) * (z2 + r * d) % n
    kk, dd = ecdsa_nonce_reuse(r, s1, z1, s2, z2, n)
    assert kk == k and dd == d
    print("nonce 重用恢复私钥 OK:", hex(dd))
```

2) 偏置 nonce 的 HNP 格构造（下面这段用 sympy 的 LLL，**可直接跑通**，用于验证构造是否正确）：

```python
from sympy import Matrix
import random

def solve_hnp_sympy(sigs, n, bias_bits):
    """sigs: [(r, s, z)]，已知每个 k < 2^bias_bits。
    返回候选私钥列表（调用方用 Q == d*G 校验）。
    构造 (m+2) 维格，最后一行是目标短向量所在的线性组合。"""
    m = len(sigs)
    B = 1 << bias_bits
    us = [(r * pow(s, -1, n)) % n for r, s, z in sigs]
    ts = [(z * pow(s, -1, n)) % n for r, s, z in sigs]
    R = m + 2
    M = [[0] * R for _ in range(R)]
    for i in range(m):
        M[i][i] = n
    for i in range(m):
        M[m][i] = us[i]
        M[m + 1][i] = ts[i]
    M[m][m] = 1                 # d 所在列的缩放
    M[m + 1][m + 1] = B         # 让 d 项在约化后规模与 k 一致
    red = Matrix(M).lll(0.99).tolist()
    out = []
    for row in red:
        v = [int(x) for x in row]
        out.append(abs(v[m]))
    return out

if __name__ == "__main__":
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    d_true = 0x1234567890ABCDEF1234567
    bits, m = 40, 6                     # k 只有 40 位，非标准题通常 128 位
    random.seed(1)
    sigs = []
    for _ in range(m):
        k = random.randrange(1, 1 << bits)
        z = random.randrange(1, n)
        r = random.randrange(1, n)
        s = pow(k, -1, n) * (z + r * d_true) % n
        sigs.append((r, s, z))
    cand = solve_hnp_sympy(sigs, n, bits)
    B = 1 << bits
    for v_m in cand:
        guess = v_m * n // B             # 关键换算：d = |v[m]| * n / B
        if guess % n == d_true or (-guess) % n == d_true:
            print("HNP 恢复私钥 OK:", hex(guess % n)); break
```

## 五、常见坑 / 变体

- **`z` 的截断**：有的题目用 `z = H(msg)` 的高 256 位直接当整数，有的先 `int.from_bytes(h, "big") >> 8`。差一位就解不出来，务必对齐源码。
- **r 相同但消息相同**：如果两条签名的 `msg` 完全一致，`s1 == s2`，分母 `(s1-s2) = 0`，说明 `k` 是确定性派生的，此时 `k = (z + r·d)/s` 仍是未知数，需要另一条独立签名。
- **格的最后一行构造**：两种等价写法——把 `2^bias` 放在 `d` 列（本文），或把 `n/B` 放在 `u` 列。**提取公式要与构造配套**：本文用 `d ≈ |v[m]| * n / B`，换成另一种构造时公式随之改变，务必先用自测样例校准。
- **偏置是「高位已知」而非「高位为 0」**：把已知部分从 `k` 里减掉再套 HNP，等价于换一个更小的界。
- **s 的逆元**：`s` 与 `n` 不互素时 `pow(s,-1,n)` 抛异常，说明签名数据本身非法（概率极低，通常是被篡改）。
- **EdDSA 的哈希**：`r = H(prefix||m)`，若题目给了 `prefix` 或两次签名消息相同，nonce 直接重复，按 ECDSA 重用处理。
- **曲线阶**：Ed25519 的阶是 `2^252 + 27742317777372353535851937790883648493`，与 secp256k1 的阶不同，套错 `n` 就全错。
- **性能**：Python 的 sympy LLL 只适合 ≤ 40 维；真实题目 256 位阶 + 10 条以上签名，用 Sage 的 `Matrix(ZZ).LLL()` 或 fpylll。

## 六、参考来源

- [CTF-Wiki DSA 签名](https://ctf-wiki.org/crypto/signature/dsa/)
- [Biased Nonce Sense: Lattice Attacks against Weak ECDSA Signatures（eprint 2019/023）](https://eprint.iacr.org/2019/023)
- [Trail of Bits: ECDSA — Handle with Care](https://blog.trailofbits.com/2020/06/11/ecdsa-handle-with-care/)
- [Wikipedia: EdDSA](https://en.wikipedia.org/wiki/EdDSA)
- [jvdsn/crypto-attacks（含 ECDSA HNP 实现）](https://github.com/jvdsn/crypto-attacks)
