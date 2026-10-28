---
title: 弱 RSA 共模攻击
category: crypto
tags: [rsa, 共模攻击, 扩展欧几里得, 同余]
signals: [两组密文, e 不同, n 相同, gcd(e1,e2)=1, 同一明文加密两次, 题目给了 c1 c2 e1 e2, n 只有一个, 两个公钥共用一个模数]
difficulty: easy
source: "CTF-Wiki / XCTF"
tools: [python, gmpy2]
updated: 2026-10-22
differs_from: [crypto/rsa-broadcast-attack.md, crypto/rsa-small-e-attack.md]
relates_to: [crypto/rsa-wiener-attack.md, crypto/rsa-fermat-factorization.md]
---

## 一、识别信号（题面长什么样）

题面通常只给一组 `n`，但同时给出两组 `(e1, c1)`、`(e2, c2)`，例如：

```python
n = 1385630398927...       # 只有一个
e1, c1 = 2333, 0x8f3a...
e2, c2 = 23333, 0x99b1...
# flag 被加密了两次
```

- 两个用户/两次加密共用同一个 `n` —— 这本身就是致命缺陷。
- `e1 != e2` 且 `gcd(e1, e2) == 1`（绝大多数情况成立）。
- 有时题目会"贴心地"给 `e1=3, e2=5` 或 `e1=5, e2=17` 这种小互素指数。
- 如果 `e1`、`e2` 不互素（`gcd=g`），仍然能做：先取 `gcd` 次根，再退回开方/枚举。

## 二、原理

设同一明文 `m` 用不同指数加密：

```
c1 = m^e1 mod n
c2 = m^e2 mod n
```

由贝祖定理，存在整数 `a, b` 使 `a*e1 + b*e2 = gcd(e1, e2) = 1`，用扩展欧几里得求出。

于是：

```
c1^a * c2^b = m^(a*e1) * m^(b*e2) = m^(a*e1+b*e2) = m^1 = m  (mod n)
```

注意 `a` 或 `b` 可能为负，此时 `c^x` 要换成 `invert(c, n)^|x| mod n`。这个攻击不需要分解 `n`，也不受 `e` 大小影响，只要两个密文来自同一 `m`。

## 三、解题步骤

1. 读 `n, e1, c1, e2, c2`。
2. `g, a, b = gmpy2.gcdext(e1, e2)`（`g` 应为 1）。
3. 若 `a < 0`：`a = -a; c1 = invert(c1, n)`；`b` 同理。
4. `m = pow(c1, a, n) * pow(c2, b, n) % n`。
5. `long_to_bytes(m)`，注意有时 `m` 被加了 padding 或做了 `bytes_to_long` 的倍数变换。

## 四、可直接运行的脚本

```python
from Crypto.Util.number import long_to_bytes
from gmpy2 import gcdext, invert

def common_modulus(n, e1, c1, e2, c2):
    g, a, b = gcdext(e1, e2)
    assert g == 1, "e1,e2 不互素，需先开 g 次根"
    if a < 0:
        a, c1 = -a, invert(c1, n)
    if b < 0:
        b, c2 = -b, invert(c2, n)
    m = (pow(c1, int(a), n) * pow(c2, int(b), n)) % n
    return long_to_bytes(int(m))

# 示例（自测用，真实题目替换成题面数据）
n  = 0xC5A1D3B7F2E9A41C6D8B0E37A2F5C9D14B6E8A02D7F3C5B19E4A6D8C0F2B4E6
e1, c1 = 0x10001, 0x3A5F
e2, c2 = 0x10003, 0x7C21
print(common_modulus(n, e1, c1, e2, c2))
```

若 `gcd(e1,e2) = g > 1`：

```python
g, a, b = gcdext(e1, e2)
m_g = pow(c1, int(a if a>0 else -a) * (a>0) + 0, n)  # 见下方完整写法
# 完整：
if a < 0: a, c1 = -a, invert(c1, n)
if b < 0: b, c2 = -b, invert(c2, n)
m_g = (pow(c1, int(a), n) * pow(c2, int(b), n)) % n   # = m^g mod n
# g 很小时直接开方
from gmpy2 import iroot
for k in range(100000):
    r, ok = iroot(int(m_g + k * n), g)
    if ok:
        print(long_to_bytes(int(r)))
        break
```

## 五、常见坑 / 变体

- **负指数忘取逆**：直接 `pow(c1, a, n)` 在 Python 3.8+ 对负数会抛错或返回 0，必须先 `invert`。
- **两段明文不是同一个 `m`**：若题目把 flag 分片（`m1 = flag[:20]`、`m2 = flag[20:]`），共模攻击不成立，要换思路（如 Franklin-Reiter 相关消息攻击，需已知 `m1` 与 `m2` 的线性关系）。
- **`m^1 mod n` 但 m 有 padding**：结果末尾可能带 `\x00` 或固定前缀，`strip` 一下再找 `flag{`。
- **变体：同 n 不同 e 的"半共模"**：`e1 | e2`（如 3 和 9）时可先算 `m^3`，再对 `m^3` 的小值开立方。
- **变体：公钥服务器**：题目给一个公钥接口，让你拿多组 `(e, c)`——本质就是共模，批量取两组即可。
- 注意某些题把 `n` 写成十进制超长字符串，解析时用 `int(s)` 而不是 `int(s, 16)`。

## 六、参考来源

- [CTF-Wiki 模数相关攻击（共模攻击）](https://ctf-wiki.org/crypto/asymmetric/rsa/rsa_module_attack/)
- [CTF-Wiki GitHub 仓库](https://github.com/ctf-wiki/ctf-wiki)
- [mahaloz/ctf-wiki-en: RSA module attack](https://github.com/mahaloz/ctf-wiki-en/blob/master/docs/crypto/asymmetric/rsa/rsa_module_attack.md)
- [CrackerCat/RSA-CTF 工具集](https://github.com/CrackerCat/RSA-CTF)
- [奇安信攻防社区 CTF-RSA 总结](https://mdr.skyeye.qianxin.com/forum/share/478)
