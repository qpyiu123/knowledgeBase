---
title: RSA CRT 故障注入（Bellcore）与签名故障恢复 n
category: crypto
tags: [rsa, crt, 故障注入, bellcore, 签名]
signals: [服务端用 CRT 做签名, 同一消息签了两次结果不同, 给了两组合法签名和错误签名, 计算 d mod p 时不加随机延迟, 题目说硬件会偶尔出错, 签名验证失败但能 gcd 出因子, 源码里用 pow(m dp p) pow(m dq q), 给了 p q dp dq 和密文, 有个 oracle 能返回错误签名, e 很小且签名满足 0 的填充]
difficulty: medium
source: "CTF-Wiki RSA 侧信道 / Wikipedia Differential fault analysis"
tools: [python, gmpy2, SageMath]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 源码里做 CRT 签名：`s1 = pow(m, dp, p)`、`s2 = pow(m, dq, q)`，再 `crt(s1, s2)`。
- 题面提示「签名服务器偶尔会返回错误签名」「我们拔掉电源时出了点问题」——故障注入场景。
- 给了同一密文的多份签名，其中一份**验证不过**；或给了 `s` 和 `s'` 两份。
- 拿到一份「错签名」`s'` 后 `pow(s', e, n) != m`，但 `pow(s', e, n)` 与 `m` 有公共因子。
- 题目直接给了 `p, q, dp, dq, c`，但 `dp` 是「可疑的」，需要通过验证找出正确的那个。
- `e` 很小（3/65537），且源码里没有对 `m` 做随机化（无 padding）。

## 二、原理

RSA-CRT 签名流程：

```
s_p = m^{dp} mod p,   dp = d mod (p-1)
s_q = m^{dq} mod q,   dq = d mod (q-1)
s   = CRT(s_p, s_q)   mod n
```

**Bellcore 故障攻击（Boneh–DeMillo–Lipton）**：若计算过程中一个中间值出错（比如 `s_p` 被翻转一位、或 `p` 少读了 1），则得到的错误签名 `s'` 满足：

- 在 `mod p` 下正确：`s' ≡ s (mod p)`
- 在 `mod q` 下错误：`s' ≠ s (mod q)`

因此 `s'^e ≡ m (mod p)` 但 `s'^e ≢ m (mod q)`。于是

```
gcd( s'^e - m,  n ) = p
```

一步就分解 `n`。**关键在于 `m` 必须是未知签名者选定的同一明文**，所以攻击要求签名者能对「攻击者给的消息」签名，或者至少给出同一消息的两份签名。

变体：

1. **两份签名**：正确签名 `s` 与错误签名 `s'`，`gcd(s - s', n)` 直接得 `p`（更简单，不需要 `m`）。
2. **无 padding 的 `e=3` 签名**：若签名实现是 `s = m^d` 且 `m` 小，`s'` 可能满足 `s'^3` 在整数上成立（无模），此时可用「开立方 + Coppersmith」恢复。
3. **共模（同一 `n`，不同 `e`）**：与已有 common-modulus 篇重合，这里只提：两条不同 `e` 的签名配合故障可省一步。
4. **`d` 的部分比特泄露**：故障导致 `d` 泄露而 `p,q` 已知，直接恢复。

## 三、解题步骤

1. 拿 `n, e`，以及**同一消息 `m`** 的两份签名：一份正确、一份错误。
2. 先试 `g = gcd(s - s', n)`，若 `1 < g < n` → `p = g`，`q = n // p`，直接算 `d`。
3. 若拿不到正确签名，只有错误签名 `s'`：算 `g = gcd(s'^e - m, n)`，同样得因子。
4. 拿到 `p, q` 后 `d = pow(e, -1, (p-1)*(q-1))`，解密密文。
5. 若 `gcd` 结果就是 `n` 或 `1`：说明两份签名「故障模式相同」或「都是对的」，换一条消息重签。
6. 若题目给的是 `dp` 可疑：用 `m^{dp} ≡ s (mod p)` 验证每个候选 `dp`，找出真正生效的那一个。

## 四、可直接运行的脚本

```python
# Bellcore 故障攻击：从一份错误签名恢复 RSA 私钥
import math

def crt_sign(m, p, q, dp, dq):
    """标准 CRT：s = sp + p * ((sq - sp) * p^{-1} mod q)"""
    sp = pow(m, dp, p)
    sq = pow(m, dq, q)
    inv_p = pow(p, -1, q)
    s = (sp + p * ((sq - sp) * inv_p % q)) % (p * q)
    return s

def error_sign(m, p, q, dp, dq, fault="sp"):
    """模拟故障：sp 或 sq 计算时出错（这里把某个中间值翻转 1 位）。"""
    sp = pow(m, dp, p)
    sq = pow(m, dq, q)
    if fault == "sp":
        sp ^= 1 << 7
    else:
        sq ^= 1 << 7
    inv_p = pow(p, -1, q)
    s = (sp + p * ((sq - sp) * inv_p % q)) % (p * q)
    return s

def bellcore_recover_n(s_wrong, m, e, n):
    """只有错误签名时：gcd(s'^e - m, n)。"""
    g = math.gcd(pow(s_wrong, e, n) - m, n)
    if 1 < g < n:
        return g, n // g
    return None

def bellcore_from_two_signs(s_good, s_bad, n):
    """有正确签名时：gcd(s - s', n)。"""
    g = math.gcd(s_good - s_bad, n)
    if 1 < g < n:
        return g, n // g
    return None

if __name__ == "__main__":
    import sympy
    p = sympy.nextprime(10**40 + 1234567)
    q = sympy.nextprime(10**40 + 7654321)
    n = p * q
    e = 65537
    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)
    dp, dq = d % (p - 1), d % (q - 1)

    m = 0x48656C6C6F  # 攻击者控制的明文
    s_good = crt_sign(m, p, q, dp, dq)
    assert pow(s_good, e, n) == m % n, "正确签名应可验证"

    # 1) 两份签名
    s_bad = error_sign(m, p, q, dp, dq, "sp")
    assert pow(s_bad, e, n) != m % n
    res = bellcore_from_two_signs(s_good, s_bad, n)
    print("两份签名 gcd 恢复:", sorted(res) == sorted((p, q)))

    # 2) 只有错误签名
    res2 = bellcore_recover_n(s_bad, m, e, n)
    print("错误签名 gcd 恢复 n:", sorted(res2) == sorted((p, q)))

    # 恢复后解密密文
    pp, qq = res2
    assert pp * qq == n
    dd = pow(e, -1, (pp - 1) * (qq - 1))
    ct = pow(m, e, n)
    assert pow(ct, dd, n) == m % n
    print("恢复私钥并解密 OK")
```

验证「可疑 `dp`」的检查器：

```python
def check_dp_candidates(m, s, p, dp_candidates):
    """在 mod p 下验证每个候选 dp：m^{dp} ≡ s (mod p)。返回通过的全部候选。"""
    ok = []
    for dp in dp_candidates:
        if pow(m, dp, p) == s % p:
            ok.append(dp)
    return ok

def check_dq_candidates(m, s, q, dq_candidates):
    return [dq for dq in dq_candidates if pow(m, dq, q) == s % q]

if __name__ == "__main__":
    import sympy
    p = sympy.nextprime(10**20 + 11)
    e, d = 65537, None
    q = sympy.nextprime(10**20 + 33)
    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)
    dp = d % (p - 1)
    m = 1234567
    s = pow(m, dp, p)
    cands = [dp ^ 0x1000, dp, dp + 1]
    print("通过验证的 dp:", check_dp_candidates(m, s, p, cands) == [dp])
```

## 五、常见坑 / 变体

- **`m` 必须一致**：`gcd(s'^e - m, n)` 里的 `m` 是**明文整数**，不是密文、不是 hash；把 `m` 抄错一位，`gcd` 直接返回 1。
- **`s - s'` 与 `s'^e - m`**：前者不需要 `e`、不需要 `m`，只要有正确签名就优先用；后者需要 `m`。
- **两份签名「同故障」**：若 `s'` 的错误发生在 `s_q` 且两次都一样，`gcd` 可能得到 `n` 本身；应换消息重签。
- **`pow(s', e, n) - m` 为负**：Python 的 `math.gcd` 接受负数，但 C 实现的 `gcd` 可能返回负值，记得 `abs`。
- **签名前有 padding**：若实现带 PKCS#1 v1.5 填充，`m` 不是用户原文而是要还原 `EM` 编码（`00 01 FF .. 00 || H`），需要用「去掉填充后的整数」做 `gcd`。
- **`e = 3` 且无 padding**：错误签名可能满足 `s'^3 = m + k·n`，此时先试 `gcd(s'^3 - m, n)`，失败再用「先恢复 `s'` 再解密」。
- **「给了 dp 可疑」题**：优先用 `pow(m, dp, p) == s mod p` 过滤候选，不要直接信题目给的 `dp`。

## 六、参考来源

- [CTF-Wiki RSA 侧信道攻击](https://ctf-wiki.org/crypto/asymmetric/rsa/rsa_side_channel/)
- [Wikipedia: Differential fault analysis（Bellcore 攻击）](https://en.wikipedia.org/wiki/Differential_fault_analysis)
- [CTF-Wiki RSA 综合题](https://ctf-wiki.org/crypto/asymmetric/rsa/rsa_complex/)
- [Wikipedia: RSA（CRT 签名流程）](https://en.wikipedia.org/wiki/RSA_(cryptosystem))
