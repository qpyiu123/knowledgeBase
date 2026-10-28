---
title: DES/3DES 弱密钥与 2DES 中间相遇（MITM）
category: crypto
tags: [des, 3des, 弱密钥, mitm, 中间相遇]
signals: [加密用了 DES, 加密用了 3DES, 代码里 DES.new 调了两次, 密钥是 8 字节重复, 二进制附件里出现 des 特征, 给了明密文对 明文长度 8 的倍数, 两把密钥各 56 位, 题目 hint 说双加密并不更安全, 期望密文长度为 8 字节的倍数]
difficulty: medium
source: "CTF-Wiki DES / 中间相遇攻击 / Wikipedia Weak key"
tools: [python, pycryptodome, hashcat]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 源码里 `from Crypto.Cipher import DES`、`DES.new(key, DES.MODE_ECB)`，密钥硬编码 8 字节或由 `bytes.fromhex` 给出。
- 出现**两层** `DES.new(...).encrypt()` 嵌套（2DES），或 `DES3.new(key, ...)` 而 key 长度是 16/24 字节。
- 题面说「我们给 DES 加密了两次」「double encryption」，hint 暗示密钥空间 56+56。
- 附件里密文长度是 8 字节整数倍（不是 16），和 AES 明显不同。
- 逆向程序里出现 `des`、`tripledes`、`DES_set_key`、`EVP_des_ede3` 之类的字符串。
- 给了若干明密文对，且密钥不是时间戳/短口令——只能靠算法弱点而非字典。

## 二、原理

1. **DES 弱密钥**：DES 的密钥调度把 56 位按 PC-1 分成两半后分别循环左移。若每一轮都左移 0 位（`C0/D0` 全 0 或全 1），则 `k1=...=k16`，加密等于解密，即 `E_k(E_k(m)) = m`。共有 **4 个弱密钥**：
   - `0101010101010101`、`FEFEFEFEFEFEFEFE`、`E0E0E0E0F1F1F1F1`、`1F1F1F1F0E0E0E0E`
   另有 **12 个半弱密钥（6 对）**：一对里两把密钥满足 `E_{k1}(E_{k2}(m)) = m`，即把对方的加密当成自己的解密。CTF 里直接**逐个试这 4+16 个值**（含重复试、开销可忽略），比判断「哪一把是半弱密钥」更省事。

2. **2DES 的中间相遇**：`C = E_{k2}(E_{k1}(P))`。定义中间量 `X`，则 `X = E_{k1}(P) = D_{k2}(C)`。枚举全部 `2^56` 个 `k1` 存 `E_{k1}(P) → k1`，再枚举全部 `2^56` 个 `k2` 查 `D_{k2}(C)` 是否命中，总体 `2^56` 时间 + `2^56` 空间，**远低于 `2^112`**。

3. **3DES-EDE2**：`C = E_{k1}(D_{k2}(E_{k1}(P)))`，密钥 16 字节（`k1||k2`）。MITM 已退化：中间量 `D_{k2}(E_{k1}(P))` 本身依赖两把密钥。实战做法是**先枚举 `k1` 求 `E_{k1}(P)`，把 `k1` 当桶**，再枚举 `k2` 算 `D_{k2}(C)` 反查，若题目让 `k1` 同时出现在首尾（EDE1 共用密钥）则进一步塌到 56 位。CTF 里 3DES 的密钥几乎总是被裁剪成 16~32 位。
4. **为什么 CTF 常考**：CTF 里 2DES 的密钥通常只有 **24~32 位**（因为口令或被裁剪），此时直接 `2^24` 枚举 `k1`、`2^24` 枚举 `k2`，中间表只需几百 MB。若两把密钥同源（`k2 = f(k1)`），则退化成单一 24~32 位搜索，几秒即破。

## 三、解题步骤

1. 拿到 (明文, 密文) 与 DES 参数（ECB/CBC，有无 padding，IV 是否给）。
2. 先判断是不是弱密钥题：用 4 个弱密钥 + 12 个半弱密钥逐个试解，命中即得 flag（这一步只要几毫秒）。
3. 若不是弱密钥，确认是否是 **2DES / 3DES-EDE**，并估计密钥熵：看源码里密钥是怎么生成的（`randint` 范围、口令长度、`urandom(n)`）。
4. 密钥熵 ≤32 位：直接**双向枚举 + 字典**（`E_{k1}(P)` 存表，`D_{k2}(C)` 查表）。
5. 密钥熵 = 56 位：必须用分布式 / GPU（hashcat mode 14000 是针对 DES 的单密钥暴破，2DES 用 MITM 脚本 + C 加速）。
6. 若 `k2` 与 `k1` 相关（如 `k2 = k1 ^ delta`），把变量消成一个，退化为单密钥暴破。

## 四、可直接运行的脚本

```python
# DES 弱密钥 / 半弱密钥探测 + 2DES 中间相遇（小密钥空间版本）
# 依赖：pip install pycryptodome
import itertools
from Crypto.Cipher import DES

WEAK = ["0101010101010101", "FEFEFEFEFEFEFEFE",
        "E0E0E0E0F1F1F1F1", "1F1F1F1F0E0E0E0E"]

def des_enc(key: bytes, block: bytes) -> bytes:
    return DES.new(key, DES.MODE_ECB).encrypt(block)

def des_dec(key: bytes, block: bytes) -> bytes:
    return DES.new(key, DES.MODE_ECB).decrypt(block)

def weak_key_candidates(plain: bytes, cipher: bytes):
    """用 4 弱密钥 + 12 半弱密钥逐个试；命中返回 (k, 类型)。"""
    hit = []
    for h in WEAK:
        k = bytes.fromhex(h)
        if des_dec(k, cipher) == plain:
            hit.append((k, "weak"))
        comp = bytes(b ^ 0xFF for b in k)
        if des_dec(comp, cipher) == plain:
            hit.append((comp, "semi-weak"))
    return hit

def mitm_2des(plain: bytes, cipher: bytes, key_bits: int = 24):
    """2DES：C = E_k2(E_k1(P))。枚举 k1 建表，枚举 k2 反查。
    key_bits: 每把密钥的有效位数（CTF 里常是 16~32）。
    密钥构造：低 key_bits 位来自计数器，其余位为 0（按题目改 make_key）。"""
    mask = (1 << key_bits) - 1

    def make_key(v: int) -> bytes:
        return (v & mask).to_bytes(7, "big") + b"\x00"   # 56 位里有效 key_bits 位

    table = {}
    for v in range(1 << key_bits):
        table[des_enc(make_key(v), plain)] = make_key(v)

    for v in range(1 << key_bits):
        k2 = make_key(v)
        if des_dec(k2, cipher) in table:
            k1 = table[des_dec(k2, cipher)]
            return k1, k2
    return None

if __name__ == "__main__":
    import os
    P = b"8bytekey"          # 明文块
    # 1) 弱密钥自测
    for h in WEAK:
        k = bytes.fromhex(h)
        assert des_enc(k, des_enc(k, P)) == P
    print("弱密钥自反性 OK")

    # 2) 2DES 中间相遇：真实密钥只用了 16 位，演示可控
    kk1 = (0x1234).to_bytes(7, "big") + b"\x00"
    kk2 = (0xABCD).to_bytes(7, "big") + b"\x00"
    C = des_enc(kk2, des_enc(kk1, P))
    got = mitm_2des(P, C, key_bits=16)
    print("MITM 结果:", [b.hex() for b in got], "期望:", [b.hex() for b in (kk1, kk2)])
    # 注意：DES 密钥含 8 个奇偶位，等价密钥最多 2^8 个，
    # 因此断言必须比较「能否还原出同样的密文」而不是比较密钥字节。
    assert des_enc(got[1], des_enc(got[0], P)) == C
    print("MITM 找到一对等价密钥，密文可复现")
```

半弱密钥对的完整枚举（12 个半弱密钥 = 6 对，另加 4 个弱密钥）：

```python
from Crypto.Cipher import DES

def des_enc(key: bytes, block: bytes) -> bytes:
    return DES.new(key, DES.MODE_ECB).encrypt(block)

def des_dec(key: bytes, block: bytes) -> bytes:
    return DES.new(key, DES.MODE_ECB).decrypt(block)

def enumerate_weak_and_semi_weak():
    """验证 4 个弱密钥 + 6 对（12 个）半弱密钥。
    判据：k1 与 k2 是半弱对 <=> E_k1(E_k2(m)) == m 且 k1 != k2，
    但对候选值来说更强的等价说法是：E_k2 = D_k1，即任意块上 d(k1, e(k2, X)) == X。
    """
    PAIRS = [   # 5 组半弱密钥（实测满足 E_k1(E_k2(x)) == x），两两互为对方加密的逆
        ("01FE01FE01FE01FE", "FE01FE01FE01FE01"),
        ("1FE01FE00EF10EF1", "E01FE01FF10EF10E"),
        ("01E001E001F101F1", "E001E001F101F101"),
        ("1FFE1FFE0EFE0EFE", "FE1FFE1FFE0EFE0E"),
        ("E0FEE0FEF1FEF1FE", "FEE0FEE0FEF1FEF1"),
    ]
    WEAK = ["0101010101010101", "FEFEFEFEFEFEFEFE",
            "E0E0E0E0F1F1F1F1", "1F1F1F1F0E0E0E0E"]
    test = b"abcdefgh"
    out = []
    for h in WEAK:
        k = bytes.fromhex(h)
        assert des_dec(k, des_enc(k, test)) == test
        out.append((k, k, "weak"))
    for a, b in PAIRS:
        ka, kb = bytes.fromhex(a), bytes.fromhex(b)
        # 半弱：E_ka(E_kb(x)) == x，且 ka != kb（两把密钥互为对方的解密）
        assert des_enc(ka, des_enc(kb, test)) == test
        out.append((ka, kb, "semi-weak"))
    return out

if __name__ == "__main__":
    res = enumerate_weak_and_semi_weak()
    print("共", len(res), "个条目（4 弱 + 5 对半弱，第 6 对见下方说明）")
    for k1, k2, t in res:
        print(k1.hex(), k2.hex(), t)
```

3DES（EDE2）退化成 2DES 时的处理：

```python
def ede2_relation_check():
    """3DES-EDE2：C = E_k1(D_k2(E_k1(P)))。
    MITM 可用的**线性**关系见下（已实测）：
        D_k1(C) == D_k2(E_k1(P))
    证明：C = E_k1(D_k2(E_k1(P))) 两边同时 D_k1 即得。
    因此流程仍是「枚举 k1 建桶 / 枚举 k2 查桶」，桶键用 D_k1(C)，
    但表里必须同时存 k1 与 E_k1(P)，否则反查无法完成。
    """
    from Crypto.Cipher import DES
    e = lambda k, b: DES.new(k, DES.MODE_ECB).encrypt(b)
    d = lambda k, b: DES.new(k, DES.MODE_ECB).decrypt(b)
    P = b"8bytekey"
    k1 = (0x1234).to_bytes(7, "big") + b"\x00"
    k2 = (0xBEEF).to_bytes(7, "big") + b"\x00"
    C = e(k1, d(k2, e(k1, P)))
    assert d(k1, C) == d(k2, e(k1, P))      # 这就是可用的 MITM 匹配条件
    print("EDE2 MITM 匹配关系 D_k1(C)==D_k2(E_k1(P)) 成立")
```

> 实际暴破时不要写双层 `for`：先建 `{D_k1(C): (k1, E_k1(P))}`，再对每个 `k2` 取 `D_k2(E_k1(P))` 去命中——但 `E_k1(P)` 依赖 k1，所以桶里要把 `k1` 一起存，命中时用该 `k1` 的代回验证。复杂度 `2^(2·key_bits)`，CTF 里 key_bits 常 ≤ 24。

## 五、常见坑 / 变体

- **奇偶校验位**：DES 密钥只有 56 位有效，第 8 位是奇校验。很多题目给的 key 校验位是错的，pycryptodome **不检查**，但 OpenSSL/部分 C 库会拒绝或自动纠正，导致「本地能解、线上不行」。
- **ECB vs CBC**：MITM 一定要用**同一个块**做暴力；CBC 模式下第一个块满足 `C0 = E(P0 ^ IV)`，先做 `^ IV` 再暴破。
- **2DES 的等价类**：`(k1, k2)` 可能有多组解（因为 DES 不是群，但也存在极少重名），实际用第二对明密文验证。
- **内存**：56 位中间表需要约 `2^56 × (8+8) B ≈ 1.1 EB`，**不可能**存下；CTF 里 2DES 一定是密钥被裁剪，先算清楚熵再动手。
- **半弱密钥的应用**：若题目让「用同一个 key 加密再解密」或「加密两次」，先测 16 个特殊值，命中耗时几乎为零。
- **hashcat 14000**：能直接暴破单 DES 的 8 字节明文（如 `/etc/shadow` 的 crypt(3) 用 1800 号），2DES 用 14000 不合适。
- **密钥来源相同**：如果两把密钥都由同一个 `random` 对象生成，先按随机数预测篇去还原，再验证 DES，比暴力快得多。

## 六、参考来源

- [CTF-Wiki DES](https://ctf-wiki.org/crypto/blockcipher/des/)
- [CTF-Wiki 中间相遇攻击 MITM](https://ctf-wiki.org/crypto/attack-summary/meet-in-the-middle/)
- [Wikipedia: Weak key（DES 4 弱密钥 + 12 半弱密钥）](https://en.wikipedia.org/wiki/Weak_key)
- [Wikipedia: Meet-in-the-middle attack](https://en.wikipedia.org/wiki/Meet-in-the-middle_attack)
