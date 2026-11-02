---
title: 方法卡 · RSA 低指数广播攻击（Håstad，多 n 同小 e）
category: crypto
tags: [方法卡, rsa, 广播攻击, Håstad, CRT, 小 e]
signals: [e=3, 至少 3 组密文, 多个不同 n, 同一明文发多人, e 相同且很小]
difficulty: medium
source: kb/crypto/rsa-broadcast-attack.md
tools: [python, 内置脚本]
updated: 2026-11-02
---

# 方法卡 · RSA 低指数广播攻击（Håstad，多 n 同小 e）

## 适用场景

同一条明文 `m` 被 **同一个很小的公钥指数 `e`**（常见 3、5、7）分别用 **`e` 个互不相同的模数**加密，
题面给出 `(n1, c1), (n2, c2), (n3, c3)`。故事常写成"分别发给了 Alice、Bob、Carol"。
与共模攻击的分界：**共模是 1 个 `n`、多个 `e`；广播是多个 `n`、同一个 `e`**。

## 前置条件

- 组数 `k >= e`（`e = 3` 至少要 3 组）。
- 各 `n_i` 两两互素；一旦 `gcd(n_i, n_j) != 1` 就直接转入共享素数分解，CRT 分支不必再走。
- 没有随机填充（`m` 在每次加密里完全相同）。
- 要求 `m^e < prod(n_i)`，否则 CRT 的结果要加 `k*N` 再开根。

## 步骤

1. 数一下组数是否 `>= e`，否则先去题面找漏掉的密文。
2. 两两 gcd 自检；发现共享因子就改用 gcd 分解（更快）。
3. 广义 CRT 合并 `x ≡ c_i (mod n_i)`，得到 `x = m^e mod N`。
4. 对 `x` 求整数 `e` 次根；不精确就尝试 `x + k*N`（`k` 很小）或看下一步。
5. 若题面给的是"`m` 加固定后缀再加密"，先用 `--strip-suffix-hex` 剥掉已知尾巴，再开根。

## 立即可用脚本

脚本路径：`kb/_methods/scripts/rsa_hastad_broadcast.py`

```powershell
# 自检（标准广播 / 固定后缀 / 组数不足 / 开根边界 / 广义 CRT，<2s）
.\.venv\Scripts\python.exe kb/_methods/scripts/rsa_hastad_broadcast.py --selftest

# 实战：逐组给 N:C
.\.venv\Scripts\python.exe kb/_methods/scripts/rsa_hastad_broadcast.py --e 3 --pair 0xN1:0xC1 --pair 0xN2:0xC2 --pair 0xN3:0xC3 --json

# 实战：从文件读（每行一个 N:C），并剥掉已知后缀
.\.venv\Scripts\python.exe kb/_methods/scripts/rsa_hastad_broadcast.py --e 3 --pairs pairs.txt --strip-suffix-hex 0000 --json
```

- 公开函数：`crt_generalized(residues, moduli)`、`integer_nth_root(x, e)`、`hastad(pairs, e)`、`parse_pair(text)`。
- 自检输出形如 `selftest ok: 5/5（标准广播、固定后缀、组数不足、开根边界、广义 CRT）`。
- 组数不足时脚本**明确报错退出**而不是给错答案。

## 手工示例

`e = 3`，明文 `m = 1234`，三个两两互素的模数：

```
n1 = 5972999, c1 = 1234^3 mod n1 = 3559218
n2 = 3540553, c2 = 1234^3 mod n2 = 2587814
n3 = 2753939, c3 = 1234^3 mod n3 = 894506
N = n1*n2*n3 = 58239529570451802733 > 1234^3 = 1879080904   （不溢出）
CRT 合成 x = 1234^3，integer_nth_root(x, 3) = 1234
```

现场核对命令：

```powershell
.\.venv\Scripts\python.exe kb/_methods/scripts/rsa_hastad_broadcast.py --e 3 `
  --pair 5972999:3559218 --pair 3540553:2587814 --pair 2753939:894506 --json
# => {"ok": true, "exact": true, "m_int": "1234", ...}
```

⚠️ 反例警示：若随手取 `n1 = 1147, n2 = 1517, n3 = 1763`（乘积 3e9 仍大于 `m^3`），
开根就会失败——脚本如实返回 `ok: false` 并提示"CRT 合成结果不是完全 e 次幂"。
手工造算例时务必先验证 `prod(n_i) > m^e` 且三者互素。

## 失效场景

- **组数 `< e`**：CRT 只能得到 `m^e mod 部分积`，开根无解。此路不通时看 `m` 是否特别小（直接 `c^(1/e)` 试）或换 Coppersmith。
- **每次加密带随机填充**：`m` 不同 → 广播彻底失效，本卡不适用。
- **`e` 很大（65537）**：`m^e < N` 只在 `m` 极小时成立，实际上退化为小 e 单模攻击。
- **各 `n_i` 不互素**：CRT 前提被破坏；这些题的正确打法是 `rsa_shared_prime.py`，不是本卡。
- **同一 `n` 出现多次**：那是"共模"或伪广播，先看 `e` 是否相同。

## 相关文档

- `kb/crypto/rsa-broadcast-attack.md`（原理、识别信号与坑点来源）
- `kb/crypto/rsa-common-modulus-attack.md`（对照组：单 `n` 多 `e`）
- `kb/crypto/rsa-small-e-attack.md`（单 `n`、`m` 小时的开方路线）
- `kb/crypto/rsa-coppersmith.md`（开根不精确时的接续手段）
- 方法卡：`kb/_methods/rsa_common_modulus_attack.md`、`kb/_methods/rsa_shared_prime_attack.md`

## 目录与收录说明

本卡直接放在 `kb/_methods/` 下、文件名不带下划线前缀，是为了同时满足两件事：
`tools/kb/parser.py` 的 `iter_md_paths` 会跳过名字以 `_` 开头的文件（脚本目录 `scripts/` 不受影响），
而这些方法卡需要在 `python tools/cli.py index` 之后能被正常检索到。
