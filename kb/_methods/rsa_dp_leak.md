---
title: 方法卡 · RSA dp/dq 泄露（完整 dp 枚举 k、低位提示、Fermat 兜底）
category: crypto
tags: [方法卡, rsa, dp泄露, dq, 部分密钥泄露, partial_key_exposure, fermat, 解密]
signals: [题目给了 dp 或 dq, 给了 d mod (p-1), 提示里出现 dp 字样, 给了 p 的低若干位, 给 e 和 n 和密文但 d 不可求, p 与 q 非常接近]
difficulty: medium
source: kb/crypto/rsa-wiener-attack.md, kb/_imported/crypto/RSA.md
tools: [python, 内置脚本]
updated: 2026-11-03
---

# 方法卡 · RSA dp/dq 泄露（完整 dp 枚举 k、低位提示、Fermat 兜底）

## 适用场景

题面给出了私钥的"半截"：`dp = d mod (p-1)`、`dq`、`p` 的低若干位，
或者干脆只给 `n, e, c` 外加一句"p 和 q 差不多大"。

> 判定信号：出现 `dp`/`dq` 字样、给的是 `d mod (p-1)` 而不是 `d`、
> 提示位数比 n 短得多（说明只给了片段）、`n` 是两个相近素数的乘积。

## 前置条件

- 已知 `n`、`e`，以及 `dp`（完整或低位片段）。
- 由定义 `e·dp ≡ 1 (mod p-1)`，所以存在 `k < e` 使
  `e·dp - 1 = k·(p-1)`。**k 一定落在 [1, e)**，这是全部穷举的边界。
- 若已知 `dq`，把 p、q 互换后同法处理。

## 步骤

1. **完整 dp**：对 `k = 1..e-1` 逐个算 `p = (e·dp - 1)//k + 1`，要求整除，
   再用 `n % p == 0` 校验。命中即得 `p, q`，随后 `d = pow(e, -1, φ)` 解密。
   这是 `dp` 泄露题的标准解法，`e` 通常很小（3、65537），几万次循环即可。
2. **dp 只有低位**：对 `k = 1..e-1` 取
   `p_low = ((e·dp_low - 1) // k + 1) mod 2^low_bits`，只保留能整除的 k，
   然后**补齐高位**（`(hi << low_bits) | p_low`）并用 `n % cand == 0` 试除。
   注意整除只对完整 dp 严格成立，低位截断会带来高位余数，所以这是启发式，
   **必须靠试除复验**，不能拿候选当结论。
3. **低位已知的 p**：直接固定低 `low_bits` 位、枚举高位试除；位数不大时
   （≤ 2^26 量级）非常快。这就是 `_lift_and_try` 的作用。
4. **Fermat 兜底**：`p, q` 相近时 `n = a² - b²`，从 `a = isqrt(n)+1` 起
   递增找 `a² - n` 为完全平方。几万次迭代覆盖到差值很小的情形。
5. **解密**：拿到 `p, q` 后按常规 RSA 解密；若明文 < n 校验失败，
   先检查明文是否被模掉（明文必须 < n）。

## 脚本

```bash
python kb/_methods/scripts/rsa_dp_leak.py --selftest
python kb/_methods/scripts/rsa_dp_leak.py --n <n> --e 65537 --dp <dp>
python kb/_methods/scripts/rsa_dp_leak.py --n <n> --e 65537 --dp-low <dp_low> --low-bits 64
```

`recover_from_full_dp(n, e, dp, max_k=None)`、`recover_from_dp_low_bits(n, e, dp_low, low_bits)`、
`recover_by_fermat_near(n, max_iter)`、`decrypt_with_dp(n, e, dp, c)`。
退出码：0 成功、1 数据拒绝（ValueError）、2 参数不足。

## 失效场景

1. **给的是 dp 低位而不是完整 dp，且 `e` 很大**：k 的搜索空间是 `e`，
   低位枚举还要再乘上高位补齐的代价，实际上打不动；此时必须转
   Coppersmith 小根路线（见 `rsa_coppersmith` 卡），而不是暴力。
2. **`n` 可被小数分解**：先用 `n` 的小因子试除、或在线的因子库确认，
   否则 k 枚举会全部落空，看起来像"dp 公式错了"。
3. **dp 与 p 不配套**（例如题目给了 dq 却当成 dp）：所有候选都试除失败，
   函数会抛出 ValueError。此时**不要**放宽到"近似匹配"。
4. **p、q 差距大且没有 dp**：Fermat 迭代次数会爆掉，需要限制 `max_iter`
   并在超限时报错，不要静默返回错误因子。
