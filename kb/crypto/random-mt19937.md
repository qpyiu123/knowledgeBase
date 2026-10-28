---
title: MT19937 随机数破译（untemper）
category: crypto
tags: [mt19937, 伪随机数, untemper, python random]
signals: [random.getrandbits, python 的 random, 624 个输出, 随机数预测, mt19937, 梅森旋转, 可以控制输入时间戳, 种子是时间戳, shuffle 打乱, randint 输出]
difficulty: medium
source: "CTF-Wiki / 公开 writeup"
tools: [python, randcrack, pwntools]
updated: 2026-10-22
relates_to: [crypto/cross-language-prng-predict.md, crypto/lcg-predict.md]
analogous_to: [crypto/lcg-predict.md]
---

## 一、识别信号（题面长什么样）

- 题面直接用 `import random; random.getrandbits(32)` 或 `random.randint`，并输出若干结果。
- 需要预测"下一次加密用的密钥"、"下一次 shuffle 结果"、"下一次 token"。
- 种子是 `time.time()` / `os.urandom` 前的常量 / 小整数 —— 可爆破。
- 关键词：seed、getrandbits、random、predict、shuffle、大概率相同。
- 变体：输出被截断（只给 `getrandbits(8)`、或 `randint` 低范围）。
- 变体：`random.shuffle` 打乱后需要恢复排列。

## 二、原理

Python 的 `random` 是 **MT19937**（Mersenne Twister），状态 624 个 32 位字。生成时按 `temper` 变换后输出：

```
y = x ^ (x >> 11)
y ^= (y << 7) & 0x9D2C5680
y ^= (y << 15) & 0xEFC60000
y ^= (y >> 18)
```

由于每个变换都是**可逆的**（右移后的 `<<` 掩码更短、左移位宽度小于 32），可从输出**反推出内部状态**（untemper）。知道任意连续 624 个 32 位输出即可完整重建状态，从而预测未来（及"回顾"过去，若状态没被 `setstate` 重置）。

- **种子爆破**：若 seed 空间小（如 `int(time.time())`），用 `Random(seed)` 重放比对。
- **截断输出**：`getrandbits(8)` 只泄漏低位 8 bit，需收集 624*4 个输出拼回 32 位（注意 MT19937 的 32 位字是**小端**拼接：先产生的 8 bit 在最左）。
- **`randint(a,b)`**：内部是 `_randbelow`，用 `getrandbits(k)` 拒绝采样，能粗略反推。

## 三、解题步骤

1. 先确认输出是 32 位完整输出（`getrandbits(32)` 或 `randbits` 一次 32）→ 直接 untemper。
2. 收集 ≥ 624 个 32 位输出，`untemper` 后 `setstate((3, tuple(state + (624,)), None))`。
3. 预测后续输出，解密/拿到 flag。
4. 若输出被截断，先升采样（凑够 624 个完整字）；若种子小则直接爆破。

## 四、可直接运行的脚本

完整脚本（不依赖第三方，直接可跑）：

```python
import random

MASK = 0xFFFFFFFF

def untemper(y):
    # 逆 y ^= y >> 18
    y ^= y >> 18
    # 逆 y ^= (y << 15) & 0xEFC60000
    y ^= (y << 15) & 0xEFC60000
    # 逆 y ^= (y << 7) & 0x9D2C5680（7 位一组迭代）
    t = y
    for _ in range(4):
        t = y ^ ((t << 7) & 0x9D2C5680)
    y = t
    # 逆 y ^= y >> 11（11 位一组迭代）
    t = y
    for _ in range(2):
        t = y ^ (t >> 11)
    y = t
    return y & MASK

def temper(x):
    y = x ^ (x >> 11)
    y ^= (y << 7) & 0x9D2C5680
    y ^= (y << 15) & 0xEFC60000
    y ^= (y >> 18)
    return y & MASK

def clone_from_outputs(outs):
    """outs: 624 个随机输出的 32 位值（来自 getrandbits(32)）"""
    assert len(outs) >= 624
    state = tuple(untemper(o) for o in outs[:624])
    r = random.Random()
    r.setstate((3, state + (624,), None))
    return r

def seed_brute(outs, start, end, bits=32):
    """爆破种子：outs 是已知输出序列（完整 32 位）"""
    for seed in range(start, end):
        r = random.Random(seed)
        if all(r.getrandbits(bits) == o for o in outs):
            return seed
    return None

# ---------- 自测 ----------
if __name__ == "__main__":
    real = random.Random(12345)
    leak = [real.getrandbits(32) for _ in range(624)]
    clone = clone_from_outputs(leak)
    print("clone next:", clone.getrandbits(32), "real next:", real.getrandbits(32))
    print("种子爆破:", seed_brute(leak[:4], 0, 100000))
```

截断输出（8 bit）恢复：

```python
def rebuild_from_bytes(byte_outputs):
    """byte_outputs: getrandbits(8) 的输出列表，长度需 >= 4*624"""
    state, cur, cnt = [], 0, 0
    for b in byte_outputs:
        cur |= b << (8 * (3 - cnt))   # 大端拼：先产生的字节在高位
        cnt += 1
        if cnt == 4:
            state.append(cur); cur, cnt = 0, 0
    return clone_from_outputs(state)
```

`randcrack` 库一句话版（最省事）：

```python
from randcrack import RandCrack
rc = RandCrack()
for _ in range(624):
    rc.submit(rng.getrandbits(32))
print(rc.predict_getrandbits(32))
```

## 五、常见坑 / 变体

- **untemper 的迭代次数**：`>> 11` 需要 2 次迭代收敛（11*2 < 32），`<< 7` 需要 4 次（7*4 < 32），次数不够会得到错误状态。
- **`getrandbits(32)` vs `randint(0, 2**32-1)`**：后者走 `_randbelow` 有拒绝采样，输出**不是**直接的 MT 输出，untemper 会失败。
- **`random.shuffle` 不消耗 1 个随机数**：每步 `_randbelow` 可能消耗多个，恢复排列比恢复状态更难，优先找能拿到原始输出的地方。
- **种子爆破**：`int(time.time())` 通常精度到秒，范围 `now-1000..now+1000` 即可；`int(time.time()*1000)` 则需要更宽。
- **Python 版本差异**：`random.randrange` 在 3.2+ 用 `_randbelow_with_getrandbits`，行为稳定；但 `random.sample` 在不同版本实现不同。
- 若题目用 `numpy.random`（numpy 也是 MT19937，但状态布局不同），要用 `numpy.random.RandomState` 的 `get_state()`/`set_state()`。

## 六、参考来源

- [CTF-Wiki 伪随机数生成器](https://ctf-wiki.org/crypto/streamcipher/prng/intro/)
- [CTF-Wiki PRNG 题目](https://ctf-wiki.org/crypto/streamcipher/prng/problem/)
- [RandCrack 库](https://github.com/tna0y/Python-random-module-cracker)
- [MT19937 原论文（Matsumoto & Nishimura）](https://www.math.sci.hiroshima-u.ac.jp/m-mat/MT/ARTICLES/mt.pdf)
