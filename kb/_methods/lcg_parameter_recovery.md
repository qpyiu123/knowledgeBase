---
title: 方法卡 · LCG 参数还原与输出预测
category: crypto
tags: [方法卡, lcg, 线性同余, 参数还原, prng, 状态恢复]
signals: [题目给出一串整数输出, 生成器代码含 a*x+c, 输出连续, random 模块自实现, 状态可递推]
difficulty: medium
source: kb/crypto/lcg-predict.md
tools: [python, 内置脚本, z3]
updated: 2026-11-02
---

# 方法卡 · LCG 参数还原与输出预测

## 适用场景

题面给出**一串连续整数**（例如 `outputs = [..., ..., ...]`），源码里能看到 `state = (a * state + c) % m`，
或者只给输出、要求"预测下一个值 / 还原 flag 数字"。也用于服务端 `random` 被自实现 LCG 替换的题。

## 前置条件

- 至少 **6 个连续输出**（脚本要求 `--outputs` 里至少 6 个点，用于交叉验证 `a`、`c` 与模数候选；少于 6 个会直接报错退出）。
- 闭式推导本身 3 个点够用，但实践中多给几点才能排除 `2m / 4m` 这类模数倍数候选。
- 输出没有被截断（若是 `state >> 16` 之类的截断，需要 z3 或格方法）。
- 各输出在同一模数下递推，且中间没有额外混淆。

## 步骤

1. **恢复模数 `m`**：对相邻差分 `d_i = x_{i+1} - x_i` 求两两 `|d_i*d_{i+2} - d_{i+1}^2|` 的 gcd，
   得到 `k*m`，再试 `m` 的因子（含 `2 的幂`修正）。
2. **恢复 `a`**：`a = (x_{i+2} - x_{i+1}) * inverse(x_{i+1} - x_i, m) mod m`，多个区间交叉验证。
3. **恢复 `c`**：`c = (x_1 - a*x_0) mod m`，用后续点回代验证（脚本 `verified: true`）。
4. 递推预测后续输出；若题目给的是 `bytes`/`flag` 的数值形式，转回字节串。
5. 截断 LCG（只知道高位）转到 z3：把 `state` 建成 BitVec，约束 `state >> k == 已知值`。

## 立即可用脚本

脚本路径：`kb/_methods/scripts/lcg_parameter_recovery.py`

```powershell
# 自检（参数还原、预测、c=0 特例、输出不足、xorshift 反解，<2s）
.\.venv\Scripts\python.exe kb/_methods/scripts/lcg_parameter_recovery.py --selftest

# 实战：给一串输出（至少 6 个，逗号分隔）
.\.venv\Scripts\python.exe kb/_methods/scripts/lcg_parameter_recovery.py --outputs "191421147,783686008,169580625,365869238,1477462455,1877955876,313550989,1594206786" --predict 2 --json

# 实战：从文件读取（一行一个整数）
.\.venv\Scripts\python.exe kb/_methods/scripts/lcg_parameter_recovery.py --outputs-file outputs.txt --json
```

- 公开函数：`parse_outputs(text)`、`recover_a_c(...)`、`recover_modulus(...)`、
  `recover_modulus_with_c_zero(...)`、`recover_all(...)`、`predict(...)`、`unshift_right_xor(value, shift)`。
- 输出字段：`{modulus, multiplier, increment, seed, verified, used, next}`。
- 参数个数不足时打印 `至少需要 6 个连续输出（当前 N 个），或用 --selftest` 并 **exit 1**。
- 自检输出形如 `selftest ok: 5/5（参数还原、预测、c=0、输出不足、xorshift 反解）`。

## 手工示例

真实 GNU libc 风格参数 `m = 2^31, a = 1103515245, c = 12345`，种子 `s = 2026` 产生的前 8 个输出：

```
191421147,783686008,169580625,365869238,1477462455,1877955876,313550989,1594206786
```

现场核对命令与输出：

```powershell
.\.venv\Scripts\python.exe kb/_methods/scripts/lcg_parameter_recovery.py `
  --outputs "191421147,783686008,169580625,365869238,1477462455,1877955876,313550989,1594206786" `
  --predict 2 --json
# => {"modulus": 2147483648, "multiplier": 1103515245, "increment": 12345,
#     "seed": 191421147, "verified": true, "used": 8, "next": [542493267, 2002689936]}
```

注意 `seed` 报的是**第一个输出的前一个状态**即 `191421147` 本身（脚本把首个输出当作起点），
用它加 `--predict` 继续推演即可；`next` 的两个值就是第 9、10 个输出。

## 失效场景

- **输出不足 3 个**：闭式无解，只能借助已知源码里的 `m` 或爆破 `m`。
- **截断输出**（`state >> 16`、`state % 1000`）：本脚本的差分 gcd 方法失效，改走 z3 约束求解。
- **`m` 是 2 的幂且 `a ≡ 1 (mod 4)`**：差分法会同时给出 `2m, 4m` 等倍数，需人工按题目取值范围筛。
- **`a` 与 `m` 不互素**：`inverse` 抛 `ValueError`，此时需要更弱的求解器（如 sympy 的模线性方程）。
- **状态里加了额外扰动**（例如 `rand()` 与时间混用）：不再是纯 LCG，本卡不适用。

## 相关文档

- `kb/crypto/lcg-predict.md`（模数还原公式、截断解法来源）
- `kb/crypto/random-mt19937.md`（另一类 PRNG 的状态恢复）
- `kb/crypto/cross-language-prng-predict.md`（跨语言实现差异导致的参数偏移）
- 方法卡：`kb/_methods/mt19937_untemper.md`

## 目录与收录说明

本卡直接放在 `kb/_methods/` 下、文件名不带下划线前缀，是为了同时满足两件事：
`tools/kb/parser.py` 的 `iter_md_paths` 会跳过名字以 `_` 开头的文件（脚本目录 `scripts/` 不受影响），
而这些方法卡需要在 `python tools/cli.py index` 之后能被正常检索到。
