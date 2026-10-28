---
title: RSA Padding Oracle 攻击（Bleichenbacher / PKCS#1 v1.5）
category: crypto
tags: [rsa, padding oracle, bleichenbacher, pkcs1, 侧信道]
signals: [padding error, 解密成功或失败的返回不同, 服务器会告诉你填充对不对, PKCS#1 v1.5, padding oracle, 密文提交后返回 decrypt error, 可以反复提交任意密文, oracle 接口]
difficulty: hard
source: "Bleichenbacher (1998) / CTF-Wiki"
tools: [python, pwntools]
updated: 2026-10-22
differs_from: [crypto/aes-cbc-byte-at-a-time.md]
---

## 一、识别信号（题面长什么样）

- 服务端对你提交的 `c` 返回"解密成功 / 解密失败"两种可区分响应（甚至只是时间差、HTTP 状态码、报错文本不同）。
- 使用 **PKCS#1 v1.5** 填充：明文 = `0x00 0x02 || PS(非零随机) || 0x00 || M`。
- 题面给了 `n, e, c` 和一个"解密后返回 OK/FAIL"的 oracle。
- 关键词："padding"、"decryption error"、"submit ciphertext"、"oracle"。
- 变体：只返回 `True/False` 的端口服务（最常见），或返回 `int(m)` 前两位。

## 二、原理

Bleichenbacher 1998 的经典结论：若攻击者能判断"解密后是否是合法 PKCS#1 v1.5 填充"，则可在多项式时间内恢复明文。

核心技巧：令 `c' = c * s^e mod n`，则 `m' = m * s mod n`。通过选择合适的 `s`，让 `m'` 落入 `[2B, 3B)` 区间（`B = 2^(8*(k-2))`），oracle 返回 True 说明 `m*s mod n ∈ [2B, 3B)`。对 `s` 二分/倍增，逐步收缩 `m` 的可能区间 `[a, b]`，最终区间缩到一个候选值。

简化实现（CTF 常用）：

1. 初始时 `m` 在 `[2B, 3B)` 里（假设首个合法密文已确认）。
2. 用倍增方式找 `s` 使 `oracle(c * s^e) == True`：每次 `s <- s * 2`，直到命中，再二分收缩。
3. 直到 `a == b`，得到 `m`。

实际 CTF 中常见另一种"**教科书 RSA 的 oracle**"：服务返回 `pow(c, d, n) % 2`（最低位），这就是 **LSB Oracle Attack**，见下方脚本 B。

## 三、解题步骤

1. 先用 `c` 原样提交，确认 oracle 返回 True（说明原始密文合法）。
2. 写交互循环，用 `s` 搜索 + 区间收缩。Python 配合 `pwntools` 处理 socket。
3. 结束时得到完整明文，`strip` 掉 PKCS 头。
4. 若是 LSB oracle，直接按位从 `m` 的奇偶恢复，约 `n.bit_length()` 次查询。
5. 若 oracle 只是"解密耗时不同"，需要统计学处理（时间攻击）。

## 四、可直接运行的脚本

脚本 A —— Bleichenbacher（结构骨架 + 二分收缩）：

```python
from Crypto.Util.number import bytes_to_long, long_to_bytes

def bleichenbacher(n, e, c, oracle, timeout=10**7):
    k = (n.bit_length() + 7) // 8
    B = 1 << (8 * (k - 2))
    # 初始合法区间
    lo, hi = 2 * B, 3 * B - 1
    # 找到第一个使 m*s mod n 落回合法区间的 s（倍增法）
    s = (n + B) // (3 * B) if n // (3 * B) > 1 else 2
    found = False
    for _ in range(timeout):
        c2 = (c * pow(s, e, n)) % n
        if oracle(c2):
            found = True
            break
        s *= 2
    if not found:
        return None
    # 二分收缩：把 [lo,hi] 映射到 m*s 的范围
    for _ in range(1000):
        for _ in range(timeout):
            c2 = (c * pow(s, e, n)) % n
            if oracle(c2):
                break
            s += 1
        new_lo = (2 * B + s - 1) // s + 1
        new_hi = (3 * B - 1) // s
        if new_lo > new_hi:
            continue
        lo, hi = max(lo, new_lo), min(hi, new_hi)
        if lo == hi:
            break
        s = (2 * B - 1) * s // (hi - lo) + 1 if hi > lo else s + 1
    return long_to_bytes(lo)

# 用法：oracle 是 lambda c: remote_decrypt_returns_ok(c)
```

脚本 B —— LSB Oracle（服务返回 `m % 2`）：

```python
from Crypto.Util.number import long_to_bytes

def lsb_oracle_attack(n, e, c, lsb_oracle):
    """lsb_oracle(int) -> 0/1，返回对解密结果奇偶性的判断"""
    lo, hi = 0, n            # 明文 m 的取值区间 [lo, hi)
    for i in range(n.bit_length()):
        c = (c * pow(2, e, n)) % n          # m -> 2m mod n
        b = lsb_oracle(c)
        mid = (lo + hi) // 2
        if b == 0:  # 2m mod n 为偶 => 没翻倍溢出，落在左半
            hi = mid
        else:
            lo = mid
    m = lo
    return long_to_bytes(m)

# ---- 本地自测 ----
from Crypto.Util.number import getPrime, inverse
p, q = getPrime(256), getPrime(256)
n, e = p * q, 65537
d = inverse(e, (p - 1) * (q - 1))
msg = int.from_bytes(b"flag{lsb_or4cle_4tt4ck}", "big")
ct = pow(msg, e, n)
print(lsb_oracle_attack(n, e, ct, lambda x: pow(x, d, n) & 1))
```

## 五、常见坑 / 变体

- **速率**：Bleichenbacher 需要数十万次查询；真实靶场通常有延迟，要么本地复现，要么放宽超时并加连接复用。
- **`s` 的搜索区间**：第一阶段的倍增步长不一定是 2，用 `s = (n + B)//(3B)` 作为初值更接近理论值。
- **区间维护要用 `Fraction` 或大整数除法**，Python 整数除法对负数向下取整，注意边界 `+1/-1`。
- 变体 **Manger 攻击**（OAEP）：oracle 只告诉你"明文是否以 0x00 开头"，适用于 OAEP。
- 变体 **时间侧信道**：`time == 0` 分支不一定真不耗时，需要取多次中位数。
- 变体：oracle 返回的是 `m` 的**前几个字节**而非整体 → 建约束表，同样可做区间收缩。
- 若服务端对同一密文有缓存/单次限制，用 `c' = c * r^e` 每次换一个等价密文来绕过。

## 六、参考来源

- [CTF-Wiki Bleichenbacher's attack](https://ctf-wiki.org/crypto/asymmetric/rsa/rsa_pkcs_attack/)
- [CTF-Wiki RSA 侧信道攻击](https://ctf-wiki.org/crypto/asymmetric/rsa/rsa_side_channel/)
- [Bleichenbacher, "Chosen Ciphertext Attacks Against Protocols Based on the RSA Encryption Standard PKCS #1"](https://link.springer.com/chapter/10.1007/BFb0055716)
- [RFC 8017 - PKCS #1 v2.2 (RSA)](https://www.rfc-editor.org/rfc/rfc8017)
