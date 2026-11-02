---
title: 方法卡 · RSA 小私钥指数攻击（Wiener 连分数）
category: crypto
tags: [方法卡, rsa, wiener, 连分数, 低解密指数]
signals: [e 与 n 同量级, e 特别大, d 很小, 私钥指数小, e 位数逼近 n]
difficulty: medium
source: kb/crypto/rsa-wiener-attack.md
tools: [python, 内置脚本]
updated: 2026-11-02
---

# 方法卡 · RSA 小私钥指数攻击（Wiener 连分数）

## 适用场景

题面给出 `n, e, c`，而 `e` **大到离谱**：常见 `e` 的位数与 `n` 相当（2048 位的 `n` 配 2048 位的 `e`），
或者源码里明确写了 `d = getPrime(256)` / `d = randint(1, 2**256)`。
这是"密钥生成器偷懒造了个小 `d`"的经典痕迹。

## 前置条件

- 已知 `n, e`（密文可选）。
- 理论上要求 `d < n^(1/4)/3`；超过这个界 Wiener 必失败（不是参数调不调的问题）。
- `n = p*q` 两素数，这样 `phi ≈ n` 的近似才成立。

## 步骤

1. 先看 `e.bit_length()`：若与 `n` 同量级，Wiener 是第一选择。
2. 对 `e/n` 做连分数展开，逐项取收敛子 `k_i / d_i`（`k` 是 `ed - 1 = k*phi` 里的 `k`）。
3. 跳过 `k = 0`；要求 `(e*d - 1) % k == 0`，得 `phi = (e*d - 1) / k`。
4. 解 `x^2 - (n - phi + 1)x + n = 0`，判别式必须完全平方，才能取得整数 `p, q`。
5. 用 `pow(pow(m, e, n), d, n) == m` 验证一次，再输出明文。

## 立即可用脚本

脚本路径：`kb/_methods/scripts/rsa_wiener_continued_fraction.py`

```powershell
# 自检（小 d 还原 / 正常 d 不误报 / 连分数展开 / 整数开方，<2s）
.\.venv\Scripts\python.exe kb/_methods/scripts/rsa_wiener_continued_fraction.py --selftest

# 实战：只给 n, e
.\.venv\Scripts\python.exe kb/_methods/scripts/rsa_wiener_continued_fraction.py --n 0x... --e 0x... --json

# 实战：顺手解密
.\.venv\Scripts\python.exe kb/_methods/scripts/rsa_wiener_continued_fraction.py --n 0x... --e 0x... --c 0x... --json
```

- 公开函数：`continued_fraction(a, b)`、`convergents(cf)`、`wiener(n, e)`、`isqrt_exact(x)`。
- 输出 `{k, d, p, q, candidates}`；给 `--c` 时追加明文。
- 失败时打印 `未找到有效 d（该题不满足 d < n^0.25/3 的 Wiener 条件）` 并 **exit 1**，不会给假答案。
- 自检输出形如 `selftest ok: 4/4（小 d 还原、正常 d 不误报、连分数展开、整数开方）`。

## 手工示例

一个真实可复现的小规模算例（192 位模数，`d = 118591`，远小于 `n^0.25/3 ≈ 1.2e14`）：

```
n = 2877536400939721538905425766486182432056828402196804454457
e = 878297552974636359789188863113274084907652390439249528303
脚本输出：k = 36197, d = 118591,
          p = 70809732556863032016704010373
          q = 40637583239407737376800700709
```

现场核对命令：

```powershell
.\.venv\Scripts\python.exe kb/_methods/scripts/rsa_wiener_continued_fraction.py `
  --n 2877536400939721538905425766486182432056828402196804454457 `
  --e 878297552974636359789188863113274084907652390439249528303 --json
# => {"k": 36197, "d": 118591, "p": "...", "q": "...", "candidates": 1}
```

⚠️ 不要用 `n` 只有三四位的"玩具模数"验证本卡：此时 `n^0.25/3 < 2`，
任何正常 `d` 都超过 Wiener 界，脚本会正确地判"不满足条件"。Wiener 的适用面是"大 `n` + 相对极小的 `d`"。

## 失效场景

- **`d` 在 `n^0.25/3` 到 `n^0.292` 之间**：Wiener 失败属正常，需要扩展 Wiener / Boneh-Durfee（格方法，见 `kb/crypto/lattice-lll.md`）。
- **`n` 不是两素数乘积**（`p^r`、`p*q*r`）：判别式分支不成立，需先分解或改 `phi`。
- **`e` 只是"看起来大"**（例如十进制写成很长但实际 `e = 65537`）：先 `int()` 再取 `bit_length` 确认。
- **密文带随机填充**：`d` 就算求出也可能解不出可读明文，先检查题面加密流程。

## 相关文档

- `kb/crypto/rsa-wiener-attack.md`（定理、脚本与坑点来源）
- `kb/crypto/lattice-lll.md`（`d` 稍大时的格方法接续）
- `kb/crypto/ecdsa-nonce-reuse-lattice.md`（同属"参数太小 → 格"的思路）
- `kb/_imported/crypto/RSA-複雜題目.md`（导入批中的综合 RSA 题）
- 方法卡：`kb/_methods/rsa_common_modulus_attack.md`、`kb/_methods/rsa_shared_prime_attack.md`

## 目录与收录说明

本卡直接放在 `kb/_methods/` 下、文件名不带下划线前缀，是为了同时满足两件事：
`tools/kb/parser.py` 的 `iter_md_paths` 会跳过名字以 `_` 开头的文件（脚本目录 `scripts/` 不受影响），
而这些方法卡需要在 `python tools/cli.py index` 之后能被正常检索到。
