---
title: 线性同余随机数预测（LCG）
category: crypto
tags: [lcg, 线性同余, 随机数预测, 流密码]
signals: [线性同余, rand() 输出, 连续随机数, a b m 参数, 状态递推, 输出序列, seed 未知, 预测下一个数, 递推式 x_n = a*x + b]
difficulty: medium
source: "CTF-Wiki / 公开 writeup"
tools: [python, z3, gmpy2]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 题面给出若干连续随机输出 `x1, x2, x3, ...`，参数 `a, b, m` 部分不给。
- 提示"随机数生成器"、"伪随机"、"next"、"predict"。
- 代码里有 `x = (a * x + b) % m` 或 `random.randrange` 的重实现。
- 变体：只给 `m`，让求 `a, b` 或预测下一项。
- 变体：输出经过变换（例如只给 `x % 2^k`、只给高位），需要求解"截断 LCG"。
- 变体：`m` 未知，输出是完整值。

## 二、原理

LCG 递推：`x_{n+1} = (a*x_n + b) mod m`。

**已知 `m` 求 `a, b`**：取连续 3 项

```
x2 = a*x1 + b (mod m)
x3 = a*x2 + b (mod m)
相减: x3 - x2 = a*(x2 - x1) (mod m)
```

若 `gcd(x2-x1, m) = 1`：

```
a = (x3 - x2) * (x2 - x1)^-1 mod m
b = (x2 - a*x1) mod m
```

**已知序列求 `m`**：`m` 整除 `t_n = x_{n+1} - x_n` 任意三次差分构造出的 `g = gcd(...)`。常用构造：对 `t_i` 取

```
m | (t_{i+1}*t_{i-1} - t_i^2)    对所有 i
```

取若干这样的值的 `gcd` 即为 `m` 的倍数（常常恰好是 `m`）。

**截断 LCG**：只知 `x_i mod 2^k` 时，用 z3 求解约束或格（Lattice）恢复。

## 三、解题步骤

1. 判断 `m` 是否已知。未知时先做差分取 gcd。
2. 由 3 项求 `a, b`（或直接用 z3 一键求解）。
3. 验证：用求出的 `a, b, m` 重新生成序列，与已知项比对。
4. 递推预测下一项 → 得到 flag 或密钥。
5. 截断情形转 z3 / 格方法。

## 四、可直接运行的脚本

```python
from functools import reduce
from math import gcd

def recover_m(xs):
    """从完整输出序列恢复 m（至少 6 个值更稳）"""
    t = [xs[i+1] - xs[i] for i in range(len(xs) - 1)]
    zeros = [abs(t[i+1] * t[i-1] - t[i] * t[i]) for i in range(1, len(t) - 1)]
    g = reduce(gcd, [z for z in zeros if z != 0])
    return g

def recover_ab(xs, m):
    d1 = (xs[1] - xs[0]) % m
    d2 = (xs[2] - xs[1]) % m
    a = d2 * pow(d1, -1, m) % m
    b = (xs[1] - a * xs[0]) % m
    return a, b

def predict(xs, m, n=1):
    a, b = recover_ab(xs, m)
    for _ in range(n):
        xs.append((a * xs[-1] + b) % m)
    return xs[-n:]

# --- 自测 ---
if __name__ == "__main__":
    m = 2**31 - 1
    real_a, real_b, seed = 1103515245, 12345, 42
    seq, x = [], seed
    for _ in range(10):
        x = (real_a * x + real_b) % m
        seq.append(x)
    M = recover_m(seq)
    print("m =", M, "==", m)
    print("ab =", recover_ab(seq, m))
    print("next =", predict(seq[:10], m, 1), "真实:", (real_a * seq[-1] + real_b) % m)
```

截断 LCG（只知 `x_i` 的低 `k` 位）用 z3 —— 关键是**把 `% m` 消掉**：令 `x_{n+1} = a*x_n + b - k_n*m`，其中 `k_n ∈ {0,1}`（因为 `x` 始终在 `[0, m)`，`a*x+b < 2m` 时成立）：

```python
from z3 import Ints, Solver, sat

def solve_truncated_lcg(low_outputs, m, bits):
    """low_outputs: 只有低位可知的连续输出列表（形如 x & ((1<<bits)-1)）"""
    N = len(low_outputs)
    a, b = Ints("a b")
    xs = Ints(" ".join(f"x{i}" for i in range(N + 1)))
    ks = Ints(" ".join(f"k{i}" for i in range(N)))
    s = Solver()
    for i in range(N):
        s.add(xs[i] >= 0, xs[i] < m)
        s.add(xs[i + 1] == a * xs[i] + b - ks[i] * m)   # 线性化掉 % m
        s.add(ks[i] >= 0)                                # 不限制上界，保持线性
        s.add(xs[i] % (1 << bits) == low_outputs[i])     # 只观测低 bits
    s.add(xs[N] >= 0, xs[N] < m)
    if s.check() != sat:
        raise ValueError("无解：观测太少或 bits 太小")
    M = s.model()
    return M[a].as_long(), M[b].as_long(), [M[x].as_long() for x in xs]

if __name__ == "__main__":
    m, bits = 2**31 - 1, 8
    real_a, real_b, seed = 1103515245, 12345, 7
    x, lows = seed, []
    for _ in range(8):
        x = (real_a * x + real_b) % m
        lows.append(x % (1 << bits))
    a2, b2, xs = solve_truncated_lcg(lows, m, bits)
    print("恢复 a,b =", a2, b2)            # 与真实 a,b 同余即成功
    print("下一项 =", (a2 * xs[-1] + b2) % m)
```

高阶截断（只知高位）转成格问题，这里给出思路即可：`x_i = h_i*2^k + e_i`，`|e_i| < 2^k`，构造
`[m ... 0]` 与 `[a^i * 2^k ...]` 的格，LLL 后取短向量。SageMath 里可直接用 `Integers(m)` 上的解线性方程组。

## 五、常见坑 / 变体

- **`gcd(x2-x1, m) != 1` 时求逆失败**：需先约分，`a = d2/d1 mod m` 存在多个解（`d1` 与 `m` 的每个公因子对应一组）。
- **`m` 恢复出来可能只是 `m` 的因子**：用更多项求 gcd，或验证 `m` 是否使序列自洽、`m` 应是"最大"的那个，取 `g` 或对 `g` 做小因子拆分。
- **输出被截断**：只给 `x >> k` 或 `x & 0xff` → 转格/BitVector 求解；`z3` 对截断 LCG 效率低，需加窄化。
- **Python 的 `random`** 不是 LCG（是 MT19937），见 `random-mt19937.md`；别用 LCG 公式硬套。
- **`b` 为 0 的乘法型 LCG** / `a=1` 的加法型：公式退化，需单独处理（如 `x_{n+1} = x_n + b` 直接相减）。
- 若参数里 `m` 是 `2^k`，注意求逆须 `d1` 为奇数。

## 六、参考来源

- [CTF-Wiki 线性同余生成器](https://ctf-wiki.org/crypto/streamcipher/lcg/intro/)
- [CTF-Wiki LCG 题目](https://ctf-wiki.org/crypto/streamcipher/lcg/challenge/)
- [LCG 参数恢复（Rosiello Security）](https://en.wikipedia.org/wiki/Linear_congruential_generator)
- [CTF-Wiki GitHub](https://github.com/ctf-wiki/ctf-wiki)
