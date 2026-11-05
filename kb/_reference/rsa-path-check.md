---
title: RSA 路径对照：直接开根、有限 k、共模与广播
category: crypto
kind: tutorial
tags: [RSA, 条件对照, 整数根, 共模, 广播]
signals: [精确根检查, 有限枚举k, gcd指数大于1, 普通字节前缀, 移位加法, 密文8000, 模数11413]
difficulty: easy
source: kb/crypto/rsa-small-e-attack.md, kb/crypto/rsa-common-modulus-attack.md, kb/crypto/rsa-broadcast-attack.md
tools: [python, 内置脚本]
updated: 2026-11-05
license: 项目原创说明与示例；上游论文仅链接
---

## 先按参数选路径

| 已有信息 | 先检查什么 | 结果与接续 |
| --- | --- | --- |
| 一组 `(n,e,c)`，小 e | `iroot(c,e)` 是否精确 | 精确根是 k=0 候选，回代并检查题目编码 |
| k=0 不精确，明文范围可估计 | 在指定上限内检查 `c+k*n` | 记录 k；上限之外仍需额外信息 |
| 同一 n、同一整数明文、不同 e | 求 `g=gcd(e1,e2)`，组合密文 | g=1 直接恢复；g>1 得到 `r=m^g mod n`，检查 `r+k*n` 的根 |
| 同一整数明文、同一小 e、多个 n | 先两两求 gcd，再用中国剩余定理 CRT | 标准互素路径需要 `m^e<prod(n_i)`；发现共享因子先分解 |

负指数对应的密文须可逆；若 `gcd(c,n)` 是非平凡因子，先用因子解密。有限枚举的候选都要满足 `m<n` 并回代原密文。

低指数与广播原理核对自 [HAC §8.2.2(ii)](https://cacr.uwaterloo.ca/hac/about/chap8.pdf) 和 [Boneh §4.2](https://crypto.stanford.edu/~dabo/papers/RSA-survey.pdf)。上表中的有限枚举与共模 g>1 接续是按模幂恒等式推导，并用下列项目脚本验证。

## 直接开根与有限 k 的数值例子

工作目录为项目根目录，使用项目 Python。示例只处理固定整数，不访问网络。

```python
import runpy

small = runpy.run_path('kb/_methods/scripts/rsa_small_e.py')
common = runpy.run_path('kb/_methods/scripts/rsa_common_modulus.py')
attack, iroot = small['small_e_attack'], small['iroot']
n, e = 11413, 3  # 101 * 113

assert attack(n, e, 8000, max_k=0) == [(0, b'\x14')]  # m=20
assert 8000 > iroot(n, e)[0]  # 用 c<n^(1/e) 筛选会漏掉此例
assert attack(n, e, 4174, max_k=1) == []
assert attack(n, e, 4174, max_k=2) == [(2, b'\x1e')]  # m=30
assert 30**3 == 4174 + 2*n

g, residue = common['common_modulus'](n, 3, pow(30, 3, n), 9, pow(30, 9, n))
assert (g, residue) == (3, 4174)
assert not iroot(residue, g)[1]
m, exact = iroot(residue + 2*n, g)
assert exact and m == 30
assert pow(m, 3, n) == 4174 and pow(m, 9, n) == pow(30, 9, n)
```

`4174` 没有精确立方根，有限 k=2 仍能恢复。共模卡标记的“指数互素路径不满足”只排除 g=1 的直接组合，继续阅读原文的 g>1 变体。

## 普通字节前缀与整数相乘

常见 `flag = prefix + suffix` 转为整数后满足：

```python
prefix, suffix = b'flag{', b'ab}'
m = int.from_bytes(prefix + suffix, 'big')
assert m == int.from_bytes(prefix, 'big') * 256**len(suffix) + int.from_bytes(suffix, 'big')
assert m != int.from_bytes(prefix, 'big') * int.from_bytes(suffix, 'big')
```

脚本 `split_plaintext` 只适用源码明确写出整数相乘 `m=m1*m2` 的构造；`--prefix` 用于筛选已经开出的字节候选。已知普通前缀、未知低位时查 Coppersmith 的小根条件。SageMath 片段本批未复现。

## 来源和代码

- 原理位置：`kb/crypto/rsa-small-e-attack.md` 的“二、原理”，`kb/crypto/rsa-common-modulus-attack.md` 的“二、原理”，`kb/crypto/rsa-broadcast-attack.md`。
- 完整代码：`kb/_methods/scripts/rsa_small_e.py`、`rsa_common_modulus.py`、`rsa_hastad_broadcast.py`。核心整数算法使用标准库；各脚本自检的额外依赖见代码简介。
- 本页是项目原创整理与固定例子；不附带两份论文 PDF。修订、来源核对及复现结果见项目 `docs/R4-实施记录.md`。
