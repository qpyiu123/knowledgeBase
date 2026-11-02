---
title: 方法卡 · 多份 RSA 公钥的共享素数爆破（gcd 分解）
category: crypto
tags: [方法卡, rsa, 共享素数, gcd, 模数分解]
signals: [多个 n, 同一 p 或 q, rc4/key.pem 多份公钥, gcd 直接分解, 批量公钥]
difficulty: easy
source: kb/crypto/rsa-common-modulus-attack.md
tools: [python, 内置脚本]
updated: 2026-11-02
---

# 方法卡 · 多份 RSA 公钥的共享素数爆破（gcd 分解）

## 适用场景

题目给了**两份以上**公钥（`public1.pem`、`public2.pem`…，或一个 `n` 的列表），
它们来自同一个"密钥生成器"或有共同的设计缺陷，于是某两份 `n` 共享了一个素因子。
只要 `gcd(n_i, n_j) != 1`，两个模数可以**同时分解**，私钥当场得到——不需要任何密码学计算。

## 前置条件

- 至少 2 个模数 `n_i`（越多越好，`k` 个模数需要 `k(k-1)/2` 次 gcd）。
- 每个 `n_i` 对应的 `e_i` 与密文 `c_i`（只有公钥时也能先分解，密文可稍后解）。
- 模数形如 `n_i = p * q`（两素数）；若是 `p^2`/`p*q*r`，见失效场景。

## 步骤

1. 把文件里所有 `Modulus:` / `n = ...` 摘成一行一个整数（十进或 `0x` 前缀）。
2. 两两 `math.gcd`；一旦 `g != 1`，令 `p = g`、`q = n_i // p`，分解成立。
3. 由 `p, q` 得 `phi = (p-1)(q-1)`，`d = inverse(e, phi)`，`m = pow(c, d, n)`。
4. 对每个"未被分解"的模数，继续和分解出的 `p` 做 gcd，常能连锁分解整批。
5. 反查是否有人为构造的小公因子（`gcd(n, 3)` 之类），顺手一测。

## 立即可用脚本

脚本路径：`kb/_methods/scripts/rsa_shared_prime.py`

```powershell
# 自检（内置 3 组共享素数算例，<2s）
.\.venv\Scripts\python.exe kb/_methods/scripts/rsa_shared_prime.py --selftest

# 实战：命令行直接给模数
.\.venv\Scripts\python.exe kb/_methods/scripts/rsa_shared_prime.py --n 0x... --n 0x... --e 65537 --json

# 实战：从文件读（每行一个十进制或 0x，`#` 开头为注释）
.\.venv\Scripts\python.exe kb/_methods/scripts/rsa_shared_prime.py --n-file mods.txt --e 65537 --json
```

- 公开函数：`pairwise_gcd(ns)`、`factor_via_shared(ns)`、`recover_d(n, e, p, q)`、`parse_int_line(line)`。
- 自检输出形如 `selftest ok: 5/5（3 组共享素数、分解解密、无关 n 不误报、行解析）`。
- 失败时脚本"如实报告不误报"：`gcd = 1` 的模数不会被硬掰成能分解。

## 手工示例

```
n1 = 31 * 37 = 1147
n2 = 37 * 43 = 1591
gcd(1147, 1591) = 37 → p = 37
q1 = 1147 / 37 = 31，q2 = 1591 / 37 = 43
n1 得 phi = 30 * 36 = 1080，d = 65537^-1 mod 1080 = 233，m = c^233 mod 1147
```

现场核对命令：

```powershell
.\.venv\Scripts\python.exe kb/_methods/scripts/rsa_shared_prime.py --n 1147 --n 1591 --e 65537 --json
```

## 失效场景

- **所有 `n` 两两互素**：脚本会报"未发现共享素数"，别硬跑，转 `rsa_fermat_factorization` 或 `rsa-small-e-attack`。
- **`n = p^2` 或 `p*q*r`**：`gcd` 只能挖出一个因子；`p^2` 用 `isqrt(n)` 检验，多素数用 `sympy.factorint` 或先找 `p*q` 小块。
- **`n` 是素数（教科书题误用）**：`phi = n-1`，不需要 gcd；先 `isprime` 判定，避免绕远路。
- **模数是压缩/加密后的 blob**：先解包再谈分解，别把 `PK\x03\x04` 喂给 gcd。

## 相关文档

- `kb/crypto/rsa-common-modulus-attack.md`（"模数相关攻击"母篇，共模与本卡的入口）
- `kb/crypto/rsa-fermat-factorization.md`（`p, q` 相邻时另一条分解路径）
- `kb/_imported/crypto/RSA.md`、`kb/_imported/crypto/RSA-複雜題目.md`（导入批 RSA 题库，含多公钥例题）
- 方法卡：`kb/_methods/rsa_common_modulus_attack.md`、`kb/_methods/rsa_hastad_broadcast.md`

## 目录与收录说明

本卡直接放在 `kb/_methods/` 下、文件名不带下划线前缀，是为了同时满足两件事：
`tools/kb/parser.py` 的 `iter_md_paths` 会跳过名字以 `_` 开头的文件（脚本目录 `scripts/` 不受影响），
而这些方法卡需要在 `python tools/cli.py index` 之后能被正常检索到。
