---
title: 方法卡 · RSA 已知私钥指数 d / φ 的倍数（直接分解 n）
category: crypto
tags: [方法卡, rsa, 已知d, 已知phi, phi倍数, 分解, 弱密钥, gcd不互素]
signals: [题目直接给了 d, 题面给了 phi 或 p-1 的倍数, e*d 减 1 是 phi 的倍数, 已知私钥指数, 给了 e 和 d 要求恢复明文, gcd(e, phi) 不等于 1, 解密结果比 n 还长说明明文被模掉]
difficulty: medium
source: kb/crypto/rsa-wiener-attack.md, kb/_imported/crypto/RSA.md
tools: [python, 内置脚本]
updated: 2026-11-03
---

# 方法卡 · RSA 已知私钥指数 d / φ 的倍数（直接分解 n）

## 适用场景

`rsa-wiener-attack.md` 里维纳攻击的当代价是「只知道 `e` 很大、`d` 很小」，而本题更省事：
**`d` 已经直接给你了**（题目输出里有 `d`，或者泄漏的是 `phi`、`phi` 的某个倍数 `k*phi`）。
这时不需要连分数，`e*d - 1` 本身就是 `φ(n)` 的倍数，用它就能把 `n` 拆开。

典型题干：

- `print(n, e, d, c)` —— 给了私钥指数；
- `hint = phi // 3` 或 `leak = (p-1)*(q-1) * 随机k` —— 给了 `φ` 的倍数；
- `e*d % (p-1) == 1` 之类的 `dp`/`d` 混用，最终也能凑出 `e*d-1`。

另一个常见伴随现象：`gcd(e, φ) != 1`（`e` 取了个非素数，比如 `e = 3` 而 `φ` 也是 3 的倍数），
此时 `d = e^{-1} mod φ` 根本不存在，必须走「先分解、再解 `m^g = c^d'`、最后开 `g` 次根」的路子。

## 前置条件

- 已知 `n`，以及 `d`（或 `φ` 的任意倍数 `kφ`，`k` 是多少不需要知道）。
- `n = p*q` 是标准两素数模数；多素数 `n` 时平方根分解技巧逐轮剥离即可，但本脚本只覆盖两素数。
- `n` 为偶数时直接返回 2，属于退化情形，不当成攻击成功。
- **明文必须小于 `n`**：`m >= n` 时 `pow(c, d, n)` 只能拿到 `m mod n`，此时要么换更大的模数，
  要么用 `m = m0 + t*n` 逐次试解（本脚本不做，见失效场景）。

## 步骤

1. 先用 `e*d - 1` 得到 `φ` 的倍数 `M`（若题面直接给 `phi`，令 `M = phi`；给的是 `k*phi` 也无所谓）。
2. 用 Miller-Rabin 的平方根技巧分解：写 `M = 2^s * t`，对确定性底数 `a = 2,3,5,7,...` 计算
   `x = a^t mod n`，在 `s-1` 次折半里不断取 `gcd(x-1, n)`，一旦得到 `1 < g < n` 就命中。
3. **先把 2-adic 部分整体剥离**再折半。直接把 `M/2, M/4, ...` 逐个当指数会漏掉一半情况
   （本脚本曾经就是这么错，导致 `a=2` 一路 `gcd == 1`）。
4. 拿到 `p, q` 后必查 `p*q == n`；再算 `φ = (p-1)(q-1)`，`g = gcd(e, φ)`。
5. `g == 1`：`d' = e^{-1} mod φ`，`m = pow(c, d', n)`，收工。
6. `g > 1`：`e2 = e/g`，`d2 = e2^{-1} mod (φ/g)`，先算 `mg = pow(c, d2, n)`，再用牛顿法开 `g` 次根；
   完全幂就直接得到 `m`，否则把 `mg` 交给上层枚举 `g` 个根。
7. 最后必须验算 `pow(m, e, n) == c`，不成立就说明材料本身有问题（`d` 不是这个 `n` 的）。

## 脚本

脚本路径：`kb/_methods/scripts/rsa_d_modulus.py`

```powershell
# 自检：已知 d 分解+解密、φ 倍数、非互素开根、非法输入拒绝、错误 d 拒绝、可复现（<1s）
.\.venv\Scripts\python.exe kb/_methods/scripts/rsa_d_modulus.py --selftest

# 实战：已知 d，分解并解密
.\.venv\Scripts\python.exe kb/_methods/scripts/rsa_d_modulus.py --n 0x... --e 65537 --c 0x... --d 0x... --json

# 实战：只有 φ 的倍数（比如 e*d-1），照样能分解
.\.venv\Scripts\python.exe kb/_methods/scripts/rsa_d_modulus.py --n 0x... --e 65537 --c 0x... --phi-multiple 0x... --json
```

- 公开函数：`factor_from_phi_multiple(n, phi_mult, tries=64)` 返回因子或 `None`；
  `decrypt_with_d(n, e, d, c)` 返回 `(p, q, m)`；`decrypt_with_phi_multiple(n, e, c, k_phi)`；
  `decrypt_non_coprime(n, e, c, phi, g)` 处理 `gcd(e, φ) > 1`；`int_root(n, k)` 返回 `(floor, 是否完全 k 次幂)`。
- 退出码：`0` 成功，`1` 数据错误（`d` 与 `n` 不匹配、无法分解），`2` 参数不足。
- 全脚本只用标准库，无第三方依赖，不联网。

## 失效场景

1. **`d` 与 `n` 不配对**（题目给了别人的 `d`，或 `n` 是多素数但只给了两素数的 `φ`）：平方根技巧扫完
   12 个底数 × 64 轮仍然拿不到因子，脚本报 `无法由 e·d-1 分解 n`。这是判据问题，不是攻击问题。
2. **明文 `m >= n`**：`pow(c, d, n)` 只会返回 `m mod n`，此前的自检就吃过这个亏（测试用 `n` 只有 65 位、
   明文 79 位，解密结果完全对不上）。务必先断言 `m < n`；否则要枚举 `m0 + t*n`。
3. **`n` 是多素数**（`n = p*q*r`）：两素数的平方根分解只走一轮，`gcd` 命中的可能是 `p` 也可能是 `p*q`，
   脚本返回的 `q'` 不一定是素数，需要递归继续分解。
4. **只有 `dp` 的低位**（而不是完整的 `d`/`dp`）时本卡不适用：`k` 一般**不整除** `e*dp_low - 1`
   （实测 `k=20322`、`e*dp_low-1=189074244`、余 `18678`），必须换 Coppersmith/格方法。
5. **Boneh-Durfee（`d < n^0.292`）** 本脚本不覆盖：纯 Python 跑不了那个维度的 LLL，需要 SageMath。
6. 题面只给 `e` 很大而没有 `d`、`φ` 的任何倍数时，先走 `rsa_wiener_continued_fraction.py` 的连分数路径。
