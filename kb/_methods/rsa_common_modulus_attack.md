---
title: 方法卡 · RSA 共模攻击（同 n 不同 e）
category: crypto
tags: [方法卡, rsa, 共模攻击, 扩展欧几里得, 同余]
signals: [n 只有一个, 两组 e 和 c, 同一明文加密两次, gcd(e1,e2)=1]
difficulty: easy
source: kb/crypto/rsa-common-modulus-attack.md
tools: [python, 内置脚本]
updated: 2026-11-05
---

# 方法卡 · RSA 共模攻击（同 n 不同 e）

## 适用场景

题面只给**一个** `n`，却给出两组或更多 `(e_i, c_i)`，且不同 `e` 都用来加密"同一条明文"。
先确认两次加密使用同一个整数明文，再检查指数和模逆条件。

## 前置条件

- 已知 `n, e1, c1, e2, c2`（可三个以上两两组合试）。
- `gcd(e1, e2) = g`；`g=1` 时组合密文直接得到明文；`g>1` 时得到 `m^g mod n`，还需检查整数根或有限枚举条件。
- 负系数对应的密文在模 `n` 下可逆；若不可逆，先计算 `gcd(c_i,n)` 检查因子。
- 明文满足 `m < n`（RSA 的常规假设）。

## 步骤

1. 用扩展欧几里得求 `a*e1 + b*e2 = 1` 中的 `(a, b)`；负指数用模逆代替。
2. 计算 `m = c1^a * c2^b mod n`；`a` 为负时先求 `c1^-1 mod n`。
3. `g=1` 时将 `m` 按题目编码还原并回代两组密文；文本不可读时先检查编码和同明文条件。
4. `g>1` 时记组合结果为 `r=m^g mod n`。只有 `r+k*n` 为精确 `g` 次幂，且候选回代两组密文成立时才继续；枚举需指定上限。

## 立即可用脚本

脚本路径：`kb/_methods/scripts/rsa_common_modulus.py`

```powershell
# 自检（无网络、内置微型算例、<2s）
.\.venv\Scripts\python.exe kb/_methods/scripts/rsa_common_modulus.py --selftest

# 实战：直接用命令行传参
.\.venv\Scripts\python.exe kb/_methods/scripts/rsa_common_modulus.py --n 0x... --e1 2333 --c1 0x... --e2 23333 --c2 0x... --json
```

- 公开函数：`egcd(a, b)`、`common_modulus(n, e1, c1, e2, c2)`、`long_to_bytes(x)`。
- `--json` 输出 `g, recovered, m_int, m_hex, m_bytes`；`g>1` 还输出 `note`，退出码 2。此时 `m_int` 存储组合结果 `m^g mod n`。
- 自检输出形如 `selftest ok: 4/4（互素还原、负系数、不互素 g=3、逆元）`。

## 手工示例

`n = 1147 = 31 * 37`，`m = 877`，`e1 = 3, e2 = 7`（`gcd = 1`）：

```
c1 = 877^3  mod 1147 = 667
c2 = 877^7  mod 1147 = 692
扩展欧几里得 3a + 7b = 1 → a = -2, b = 1
m = (667^-1 mod 1147)^2 * 692 mod 1147 = 877
```

现场核对命令：

```powershell
.\.venv\Scripts\python.exe kb/_methods/scripts/rsa_common_modulus.py --n 1147 --e1 3 --c1 667 --e2 7 --c2 692 --json
# => {"g": 1, "recovered": true, "m_int": "877", "m_hex": "0x36d", ...}
```

注意挑 `n` 时确认 `gcd(c_i, n) = 1`——若某个密文与 `n` 不互素，等于白送一个因子
（`gcd(c, n)` 直接就是 `p`），此时更省事的是转 `rsa_shared_prime.py` 的分支。

## 失效场景

- **明文每次不同**（题面里 `m = bytes_to_long(flag + os.urandom(8))`）→ 共模关系被随机填充破坏，本方法失效，转看是否有填充 oracle 或 `rsa-small-e-attack.md`。
- **`n` 不互素**——共模攻击不需要两个 `n`，但如果你把"多个 n"的题误判成本卡 → 先跑 `rsa_shared_prime.py`，`gcd(n1, n2)` 一旦非 1 直接分解。
- **`gcd(e1,e2)=g>1`**：组合结果是 `r=m^g mod n`。检查 `r+k*n` 的精确根，枚举上限由额外明文范围确定；已知高位时再看 `kb/crypto/rsa-coppersmith.md`。
- **AES/HMAC 场景**：只要出现对称加密或签名，直接退出本卡。

## 相关文档

- `kb/crypto/rsa-common-modulus-attack.md`（原理与识别信号来源）
- `kb/crypto/rsa-broadcast-attack.md`（多 `n` 同 `e` 的孪生方法，差一个前提）
- `kb/crypto/rsa-small-e-attack.md`（单 `n`、`m^e < n` 时先试开方）
- `kb/crypto/rsa-wiener-attack.md`（`e` 特别大时的另一种"参数异常"）
- 方法卡：`kb/_methods/rsa_shared_prime_attack.md`、`kb/_methods/rsa_hastad_broadcast.md`

## 目录与收录说明

本卡直接放在 `kb/_methods/` 下、文件名不带下划线前缀，是为了同时满足两件事：
`tools/kb/parser.py` 的 `iter_md_paths` 会跳过名字以 `_` 开头的文件（脚本目录 `scripts/` 不受影响），
而这些方法卡需要在 `python tools/cli.py index` 之后能被正常检索到。
