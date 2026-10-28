---
title: 跨语言随机数预测（Java Random / PHP mt_rand / Python random）
category: crypto
tags: [随机数预测, java-random, php, mt_rand, prng]
signals: [题目用 java.util.Random, 源码里出现 nextInt 或 nextLong, 密钥来自 Random 种子, 种子是时间戳或 System.currentTimeMillis, 服务端是 PHP 且用了 mt_rand, 输出里有一串连续的随机整数, 提示 seed 与时间有关, 两次请求返回的随机数相关, 用 shuffle 打乱后输出]
difficulty: medium
source: "CTF-Wiki PRNG / Python docs random / mt_rand 逆向研究"
tools: [python, java, php, pwntools]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 附件/源码里出现 `java.util.Random`、`nextInt(bound)`、`nextLong()`、`Math.abs(rnd.nextInt())`。
- Java 侧种子是 `System.currentTimeMillis()`（毫秒）或 `new Random(seed)`，且 seed 有界。
- 服务端接口是 PHP，用了 `mt_rand()` / `rand()` / `shuffle()`，且 `mt_srand($seed)` 的种子很弱（时间、小整数）。
- 输出是一串**整数**（不是字节），例如 `[1234, 5678, ...]`，且数量 ≥ 624（Python）或 ≥ 15（PHP）。
- 题面提示「我们的 token 是用时间做种子的」「服务重启后 token 一样」。
- 用 Java/PHP 生成 AES key 或 flag 的某些位，且重复调用得到**可预测**结果。
- 同时存在多语言组件（Java 后端 + PHP 前端），需要判断是哪一方的 PRNG。

## 二、原理

1. **`java.util.Random`**：内部状态是 48 位 LCG：
   `state = (state * 0x5DEECE66D + 0xB) & ((1<<48)-1)`。
   `nextInt(bound)` 用**拒绝采样**：先 `next(31)` 得合理位，若 `bits - (bits % bound) + bound - 1 < 0` 则重抽。所以 `nextInt(1000)` 的输出并不直接等于状态的线性函数，**但可以反推**：对一个已知输出 `v = nextInt(b)`，满足 `v = bits % b` 的候选 `bits` 有约 `2^31/b` 个，可以用「线性同余 + 收集多个输出」暴力恢复状态。
   - 最简单情形：`nextInt()`（无参，输出 32 位）两个连续值就能恢复 48 位状态（`next()` 的高 32 位直接暴露，配合低位枚举）。
   - 种子是 `currentTimeMillis()`：枚举毫秒数（`now-10s .. now+10s` 约 `2^24` 个候选），对每个种子重放校验。
2. **PHP `mt_rand`**：早期 PHP（<7.1）的 `mt_rand()` 直接返回 MT19937 的输出（31 位），和 Python 的 `random` 是**同一算法但不同实现**（PHP 用 `mt_srand` 的种子映射不同，且输出截断为 31 位）。PHP 7.1+ 修了「`mt_rand` 输出可预测」的问题，但仍可通过 `mt_srand` 反推种子。
   - **恢复种子**：`mt_srand(seed)` 后前 625 个输出截断了 `>>1`（31 位），可用「暴力小种子」或 `php_mt_seed` 工具反推；种子空间小（如时间戳）时直接枚举。
   - **恢复状态**：收集 624 个连续 `mt_rand()` 输出，untemper 后得到 MT 状态；但 PHP 输出是 31 位，需要已知最高位如何处理（`mt_rand()` 返回 `>>1`，因此有 1 位未知，需用「两个相邻输出」或 `mt_rand(0, 0x7fffffff)` 变体）。
3. **Python `random`**：标准 MT19937，624 个 `getrandbits(32)` 可直接 untemper 还原状态（见已有 `random-mt19937.md`）。跨语言题的坑在于 **`randint`/`choice`/`shuffle` 会消耗额外随机数**，因此「直接抓 624 个输出」往往不够，要按调用序列重放。
4. **跨语言搬运**：把 Java 的 LCG 状态用 Python 复现，把 PHP 的 MT 输出用 Python 的 MT 实现复现，最后在目标语言里验证。

## 三、解题步骤

1. 先确认语言：看源码文件后缀（`.java` / `.php` / `.py`）、序列化格式、接口报错信息。
2. **Java**：收集 ≥ 2 个 `nextInt()` 连续输出（或足够多 `nextInt(bound)`），用 LCG 反推状态，预测后续。
3. **种子可枚举**（时间戳）：在 `[now-Δ, now+Δ]` 里暴力，对每个种子生成前几个输出，和实际输出比对。
4. **PHP**：收集 ≥ 624 个 `mt_rand()`，或已知种子范围时直接枚举；工具 `php_mt_seed` 可把「前若干输出」反推成种子。
5. 用预测出的序列生成 key / token / flag 片段，与目标交互验证。
6. 注意**跨语言调用顺序**：如果题目先 `shuffle` 再 `randint`，随机数的消耗顺序必须一一还原。

## 四、可直接运行的脚本

```python
# Java Random（48 位 LCG）状态恢复与预测；PHP mt_rand 的 31 位截断处理
MASK48 = (1 << 48) - 1
A = 0x5DEECE66D
C = 0xB

def java_next(state):
    state = (state * A + C) & MASK48
    return state, state >> 16          # next(32) 的高 32 位

def recover_java_from_nextint_vals(vals):
    """vals: 连续的 nextInt()（无参，32 位）输出 >= 2 个。
    nextInt() 返回 state>>16，低 16 位未知 -> 枚举 2^16 个低位，
    用下一个输出校验。返回值是「第一个输出对应的 state」，
    因此 predict_java(该 state, k) 得到的是 vals[1:] 的预测。"""
    v0, v1 = vals[0], vals[1]
    for low in range(1 << 16):
        s0 = (v0 << 16) | low
        if ((s0 * A + C) & MASK48) >> 16 == v1:
            return s0
    return None

def java_seed_bruteforce(outputs, seed_range, n_check=3):
    """种子可枚举（毫秒时间戳）时：对每个种子重放，比较前 n_check 个 nextInt()。"""
    for seed in seed_range:
        s = (seed ^ A) & MASK48
        ok = True
        for i in range(n_check):
            s = (s * A + C) & MASK48
            if (s >> 16) != outputs[i]:
                ok = False
                break
        if ok:
            return seed
    return None

def predict_java(state, n):
    """从已知状态预测后续 n 个 nextInt()。"""
    out = []
    for _ in range(n):
        state, _ = java_next(state)
        out.append(state >> 16)
    return out

def php_mt_rand_mask(vals_31):
    """PHP mt_rand() 返回 31 位（MT 输出 >> 1）。
    这里演示：把 31 位输出补成 32 位（最高位未知）后交给标准 untemper 需要额外约束；
    实战更常用 php_mt_seed 反推种子。此函数仅做截断一致性检查。"""
    return [v & 0x7FFFFFFF for v in vals_31]

if __name__ == "__main__":
    # 1) 构造一个 Java Random 并恢复状态
    seed = 123456789
    s = (seed ^ A) & MASK48
    outs = []
    for _ in range(4):
        s = (s * A + C) & MASK48
        outs.append(s >> 16)
    st = recover_java_from_nextint_vals(outs[:2])
    assert st is not None
    assert predict_java(st, 3) == outs[1:4]
    print("Java Random 状态恢复 OK，预测:", predict_java(st, 2))

    # 2) 种子枚举（模拟时间戳 5000 个候选）
    seed2 = 1_700_000_123
    s2 = (seed2 ^ A) & MASK48
    outs2 = []
    for _ in range(3):
        s2 = (s2 * A + C) & MASK48
        outs2.append(s2 >> 16)
    found = java_seed_bruteforce(outs2, range(1_700_000_000, 1_700_000_200), n_check=3)
    assert found == seed2
    print("Java 毫秒种子枚举 OK:", found)
```

PHP `mt_rand` 的收割与种子反推（需要先 `pip install mt19937predictor` 或自己 untemper）：

```python
# PHP mt_rand() 的 31 位输出恢复 MT 状态
def php_collect(vals_31):
    """>=625 个连续 mt_rand() 输出，按 PHP 的 31 位截断处理。
    PHP 的 MT19937 与 Python 相同，只是每个输出右移 1 位。
    补齐策略：对每个输出枚举最高位 0/1，用后续输出做一致性过滤。"""
    assert len(vals_31) >= 625, "至少需要 625 个 31 位输出"
    cands = []
    for high in (0, 1):
        full = [(v << 1) | high for v in vals_31]
        # 用「连续 624 个 untemper 后重放第 625 个」来过滤 high
        st = untemper_state(full[:624])
        if twist_once(st) == full[624]:
            cands.append(full)
    return cands

def untemper_state(y_list):
    """标准 MT19937 untemper（与已有 mt19937 篇一致）。"""
    def undo_right(y, shift):
        x = y
        for _ in range(5):
            x = y ^ (x >> shift)
        return x
    def undo_left(y, shift, mask):
        x = y
        for _ in range(5):
            x = y ^ ((x << shift) & mask)
        return x
    out = []
    for y in y_list:
        y = undo_right(y, 18)
        y = undo_left(y, 15, 0xEFC60000)
        y = undo_left(y, 7, 0x9D2C5680)
        y = undo_right(y, 11)
        out.append(y)
    return out

def twist_once(st):
    """从给定 624 个 state 算出下一个输出（简化为直接 twist 后取第一个）。"""
    n, m = 624, 397
    y = (st[0] & 0x80000000) | (st[1] & 0x7FFFFFFF)
    ny = st[m] ^ (y >> 1)
    if y & 1:
        ny ^= 0x9908B0DF
    ny &= 0xFFFFFFFF
    # temper
    y2 = ny
    y2 ^= (y2 >> 11)
    y2 ^= (y2 << 7) & 0x9D2C5680
    y2 ^= (y2 << 15) & 0xEFC60000
    y2 ^= (y2 >> 18)
    return y2 & 0xFFFFFFFF
```

## 五、常见坑 / 变体

- **`nextInt(bound)` 的拒绝采样**：`nextInt(1000)` 不是总有输出，重抽会导致序列位置偏移；用 `nextInt()`（无参）恢复状态最稳。
- **Java 的 `nextLong()`**：由两次 `next(32)` 拼成，恢复状态时按两次处理。
- **PHP 7.1 之后**：`mt_rand()` 仍可被 `php_mt_seed` 破，但 `random_int()` 是 CSPRNG，不可预测。
- **PHP 的 31 位截断**：直接拿 624 个输出 untemper 会错，必须补齐最高位或用 `mt_rand(0, 0x7fffffff)` 之类的完整宽度调用。
- **Python `shuffle`/`randint`**：会额外消耗随机数，跨语言复现时必须**逐调用**模拟而不是「按输出数量」。
- **多种子组合**：题目可能 `seed = time ^ pid`，需要枚举两维；先用「已知输出反推种子」缩小范围。
- **验证永远用重放**：预测出后续后，先用已知的几条输出确认，再提交答案。

## 六、参考来源

- [Python 官方文档：random 模块](https://docs.python.org/3/library/random.html)
- [CTF-Wiki：伪随机数题目](https://ctf-wiki.org/crypto/streamcipher/prng/problem/)
- [CTF-Wiki：MT19937 介绍](https://ctf-wiki.org/crypto/streamcipher/prng/intro/)
- [RandCrack（Python MT19937 破解库）](https://github.com/tna0y/Python-random-module-cracker)
