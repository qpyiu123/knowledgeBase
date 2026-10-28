---
title: 古典密码（Atbash / 凯撒 / 维吉尼亚 / 仿射 / 巴利克）
category: crypto
tags: [古典密码, 凯撒, 维吉尼亚, 仿射, 巴利克]
signals: [全字母无数字, 密文看起来像乱码但只是字母, 凯撒移位, 维吉尼亚, 仿射, atbash, playfair, bacon, 只有 a-z 和括号, flag 藏在一串字母里]
difficulty: easy
source: "CTF-Wiki / 公开 writeup"
tools: [python, dcode, CyberChef]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 密文由纯字母构成，保留 `flag{}` 外层结构，内部是 `[a-zA-Z]+`。
- 形如 `synt{...}`、`synt{ebg13_pvcg}` —— flag 格式被整体替换（如 `flag`→`synt`，即 ROT13）。
- 字母频率可辨：`e`、`t`、`a` 高频 → 单表替换类。
- 双字母组（digraph）频繁、每两个字母成组 → Playfair / Bifid。
- 只有 `A`、`B` 两种字母且长度是 5 的倍数 → 培根密码。
- 变体：栅栏（rail fence）后的结果，或"键盘上下左右移一位"。

## 二、原理

| 密码 | 变换 | 破法 |
|---|---|---|
| Caesar | `c = (p + k) mod 26` | 枚举 26 个 k |
| Atbash | `c = (25 - p)` | 直接逆序映射 |
| Affine | `c = (a*p + b) mod 26`，`gcd(a,26)=1` | 枚举 12*26 组 (a,b) |
| Vigenère | `c = (p + key_i) mod 26` | 卡西斯基 / IOC 求密钥长，再逐列解 Caesar |
| Playfair | 5×5 棋盘双字母替换 | 已知明文下求棋盘，或频率 + 双字母 |
| Bacon | 5 个 A/B 编码一个字母 | 分组查表 |
| Rail Fence | 按锯齿排布再读出 | 枚举栏数 |

## 三、解题步骤

1. 去掉 `flag{}`/`synt{}` 外壳，保留纯字母部分。
2. 看是否"已知格式偏移"：`synt` 是 `flag` 的 ROT13 结果，说明全局 ROT13。
3. 统计频率与重合指数（IOC）：`IOC ≈ 0.065` → 单表；`≈ 0.038` → 多表。
4. 多表时先求密钥长度（卡西斯基 / 逐位移 IOC），再逐列解 Caesar。
5. 用脚本一次性跑完候选，挑可读的。

## 四、可直接运行的脚本

```python
import string, itertools
from collections import Counter

LOW = string.ascii_lowercase

def caesar(s, k):    return shift(s, k)
def atbash(s):       return shift(s, 0, atbash=True)

def shift(s, k, atbash=False):
    out = []
    for ch in s:
        if ch.isalpha():
            base = 'A' if ch.isupper() else 'a'
            i = ord(ch) - ord(base)
            j = (25 - i) if atbash else (i + k) % 26
            out.append(chr(ord(base) + j))
        else:
            out.append(ch)
    return "".join(out)

def affine_decrypt(s, a, b):
    inv = pow(a, -1, 26)
    return "".join(
        chr(ord('a') + (inv * ((ord(c.lower()) - 97) - b)) % 26)
        if c.isalpha() and c.islower() else c
        for c in s)

def ioc(s):
    s = [c.lower() for c in s if c.isalpha()]
    n = len(s)
    if n < 2: return 0
    cnt = Counter(s)
    return sum(v * (v - 1) for v in cnt.values()) / (n * (n - 1))

def vigenere_decrypt(s, key):
    out, ki = [], 0
    for c in s:
        if c.isalpha():
            k = ord(key[ki % len(key)].lower()) - 97
            out.append(chr((ord(c.lower()) - 97 - k) % 26 + 97))
            ki += 1
        else:
            out.append(c)
    return "".join(out)

def kasiski(s, max_key=20):
    """返回最可能的密钥长度"""
    s = "".join(c.lower() for c in s if c.isalpha())
    scores = []
    for L in range(1, max_key + 1):
        total = 0.0
        for col in range(L):
            col_s = s[col::L]
            total += ioc(col_s)
        scores.append((total / L, L))
    return max(scores)[1]

def bacon_decode(s):
    table = {"AAAAA":"a","AAAAB":"b","AAABA":"c","AAABB":"d","AABAA":"e",
             "AABAB":"f","AABBA":"g","AABBB":"h","ABAAA":"i","ABAAB":"k",
             "ABABA":"l","ABABB":"m","ABBAA":"n","ABBAB":"o","ABBBA":"p",
             "ABBBB":"q","BAAAA":"r","BAAAB":"s","BAABA":"t","BAABB":"u",
             "BABAA":"v","BABAB":"w","BABBA":"x","BABBB":"y","BBAAA":"z"}
    s = "".join(c.upper() for c in s if c.isalpha())
    return "".join(table.get(s[i:i+5], "?") for i in range(0, len(s) - 4, 5))

# --- 自测 ---
print(caesar("synt{ebg13_pvcg}", 13))            # flag{rot13_ipher} → 实际 ROT13 解
print(atbash("uozt{zgzyh}"))
print(ioc("synt{ebg13_pvcg}"))
print(kasiski("LXFOPVEFRNHR" * 5))
```

常用组合：拿到密文后一键跑全部候选

```python
def brute_force(s):
    yield "caesar", {k: caesar(s, k) for k in range(26)}
    yield "atbash", atbash(s)
    yield "affine", {f"a{a}b{b}": affine_decrypt(s, a, b)
                     for a in (1,3,5,7,9,11,15,17,19,21,23,25) for b in range(26)}
    yield "bacon", bacon_decode(s)
```

## 五、常见坑 / 变体

- **别丢掉 `{}` 与下划线**：很多脚本把所有非字母都剥掉，导致 `synt{...}` 的外壳也被加密后无法定位 flag 边界。
- `flag` → `synt` 是**固定关系**：写脚本时把 `synt` 当作"已知明文"，直接反推密钥。
- 维吉尼亚密钥长度用卡西斯基（重复段间距 gcd）或 Friedman 方法；**IOC 法**更稳但要序列够长。
- 仿射密码要求 `gcd(a, 26)==1`，只有 12 个合法 `a`，枚举很快。
- Playfair 棋盘 `i/j` 合并、Bifid 有行列双置换，很多题会混用。
- 变体：**QWE 键盘错位**（每个字母换成右手边一位）、**栅栏密码**、**摩斯**、**社会主义核心价值观编码**（不要直接用在线工具，编码顺序有坑）。
- 变体：**曲路 / 螺旋矩阵**读取，需要按维度重排。

## 六、参考来源

- [CTF-Wiki 古典密码简介](https://ctf-wiki.org/crypto/classical/introduction/)
- [CTF-Wiki 单表代换加密](https://ctf-wiki.org/crypto/classical/monoalphabetic/)
- [CTF-Wiki 多表代换加密](https://ctf-wiki.org/crypto/classical/polyalphabetic/)
- [dCode 古典密码工具箱](https://www.dcode.fr/en)
- [CyberChef](https://gchq.github.io/CyberChef/)
