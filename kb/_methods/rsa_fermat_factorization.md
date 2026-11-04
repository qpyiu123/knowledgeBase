---
title: 方法卡 · RSA Fermat 分解（p、q 相近）
category: crypto
tags: [方法卡, rsa, fermat, 因式分解, p q 相近, nextprime]
signals: [p 和 q 很接近, q 等于 nextprime(p), 两个素数相邻, p q 差值很小, isqrt(n) 的平方减 n 很小, n 的位数不到两个素数位长之和, 分解 n 后直接解密]
difficulty: easy
source: kb/crypto/rsa-fermat-factorization.md, kb/_imported/crypto/RSA.md
tools: [python, 内置脚本]
updated: 2026-11-03
---

# 方法卡 · RSA Fermat 分解（p、q 相近）

## 适用场景

题面源码里 `p = getPrime(512); q = nextprime(p)`，或者说明"我用了两个非常接近的质数"。另一个强信号很实用：
`n` 的二进制位长**明显短于**两个素数位长之和（乘积接近平方数时总会有几个前导位损失）。
把 `isqrt(n)^2 - n` 算出来，如果是完全平方，那就是一眼 Fermat。

## 前置条件

- 已知 `n`（解密再加 `e, c`）；`n = p*q` 两素数乘积。
- 迭代次数 ≈ `(p+q)/2 - sqrt(n) ≈ (p-q)^2 / (8*sqrt(n))`。实测经验界：`|p-q| < 2*n^(1/4)` 时几十次收敛。
- `n = p^2` 退化情形直接 `isqrt(n)` 取整。
- `p, q` 完全随机（差距和 `sqrt(n)` 同量级）时**不可用**，迭代是天文数字。

## 步骤

1. 先做"值不值得跑"的判定：打印 `a = isqrt(n)+1` 与 `a*a - n`，再打印经验界 `isqrt(isqrt(n))`，前者远小于后者才值得。
2. 从 `a` 开始递增，检查 `a^2 - n` 是否为完全平方：

   ```python
   a = isqrt(n) + 1
   while True:
       b = isqrt_exact(a*a - n)
       if b is not None and (a-b)*(a+b) == n:
           return a-b, a+b
       a += 1
   ```

3. 拿到 `p, q` 后**必须验算** `p*q == n`，再 `d = invert(e, (p-1)(q-1))` 解密。
4. 迭代超过阈值（脚本默认 10^6）直接判不适合，转 Pollard rho / yafu / 格方法，不硬跑。
5. 已知 `p+q` 的变体：不用 Fermat，直接解 `x^2 - (p+q)x + n = 0`。

## 脚本

脚本路径：`kb/_methods/scripts/rsa_fermat.py`

```powershell
# 自检：相近素数分解 + 解密、n=p^2 边界、非法输入拒绝、不适用判定、固定 seed（<1s）
.\.venv\Scripts\python.exe kb/_methods/scripts/rsa_fermat.py --selftest

# 实战：只分解
.\.venv\Scripts\python.exe kb/_methods/scripts/rsa_fermat.py --n 0x... --json

# 实战：分解后顺手解密
.\.venv\Scripts\python.exe kb/_methods/scripts/rsa_fermat.py --n 0x... --e 65537 --c 0x... --json
```

- 公开函数：`fermat(n, max_iter)` 返回 `(p, q, iterations)`；`closeness_score(n)` 给出 `a^2-n` 做前置判定；`solve(n, e, c)`。
- 参数：`--max-iter` 默认 `1000000`；给了 `--e` 就必须给 `--c`，否则 argparse 报参数不足。
- 迭代超限打印中文原因并 **exit 1**；`e` 与 `phi` 不互素时 **exit 2** 并提示换分支，绝不给乱码明文当结果。

## 失效场景

- **`p, q` 随机且等长**：迭代次数天文数字，脚本会明确报"差距太大"，不要以为调大 `max_iter` 能救。
- **`n` 含 3 个及以上相近因子**：普通 Fermat 只分解成 `(p, q)` 两块，`n = p*q*r` 需要推广的双边分解或直接 `factor()`。
- **`p ≈ k*q`（比例关系但差值不小）**：不属于 Fermat，属于"已知比例 → Coppersmith 近似"，换格方法。
- **`isqrt(n)^2 - n` 很小但 `n` 是素数**：`p*q == n` 验算会挡住，脚本不会输出伪因子。

## 相关文档

- `kb/crypto/rsa-fermat-factorization.md`（原理公式、迭代次数估计、一页速查分流函数）
- `kb/_imported/crypto/RSA.md`（p、q 不当分解的排查顺序：Fermat → Pollard p-1 → batch GCD → Coppersmith）
- `kb/_imported/crypto/RSA-複雜題目.md`（SCTF RSA1：用 yafu 分解相近素数的实战）
- 方法卡：`kb/_methods/rsa_shared_prime_attack.md`、`kb/_methods/rsa_wiener_continued_fraction.md`
