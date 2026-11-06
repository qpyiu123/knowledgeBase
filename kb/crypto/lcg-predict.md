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

**先分清输出**：泄漏完整状态时用上面的公式。只泄漏低位或高位时，应按两种不同的观测方式建条件。

## 三、解题步骤

1. 判断 `m` 是否已知。未知时先做差分取 gcd。
2. 由 3 项求 `a, b`（或直接用 z3 一键求解）。
3. 验证：用求出的 `a, b, m` 重新生成序列，与已知项比对。
4. 递推预测下一项 → 得到 flag 或密钥。
5. 只有低位或高位时，先看模数关系和已知参数，再选下面的做法。

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

### 只有低位或高位时

- **低 k 位**：只有原模数 `m` 是 `2**k` 的倍数时，才可直接把整个递推化成模 `2**k` 的递推。此时能复算低位；高位不会因此出现。Lunar LCG 用低 8 位生成密钥流，但附件泄漏的是完整状态。
- **模数不是该倍数**：写成 `x_next = a*x + b - q*m`，其中 `q = (a*x+b)//m`。商可能大于 1；例如 `m=11, a=7, b=1, x=10` 时商是 6。若 `a` 和 `x` 都未知，乘积仍是非线性的。已知参数且状态空间很小，可以枚举初始状态并逐项筛选。
- **只知高位**：把每个状态写成 `x = high*2**k + low`，未知低位在 `[0, 2**k)`。已知乘数和模数、低位范围足够窄时，可把递推与误差范围一起写成格问题。每个候选至少用若干额外观测回验。

下面的小例子只适合已知参数、候选状态数量少的题：

```python
def low_candidates(observations, a, b, m, bits):
    step = 1 << bits
    for first in range(observations[0], m, step):
        state = first
        for expected in observations[1:]:
            state = (a * state + b) % m
            if state % step != expected:
                break
        else:
            yield first
```

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
