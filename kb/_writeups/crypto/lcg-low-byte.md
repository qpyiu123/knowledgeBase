---
title: "Lunar LCG：泄漏的是完整状态，还是低 8 位？"
category: "crypto"
kind: "writeup"
tags: ["线性同余发生器", "低位密钥流"]
signals: ["已知模数", "完整状态泄漏"]
source: "本地密码题附件（第二轮编号：lcg-low-byte）"
origin_id: "r66-lcg-low-byte"
relates_to: ["crypto/lcg-predict.md"]
verification: "本机原附件回验"
---

# Lunar LCG：泄漏的是完整状态，还是低 8 位？

本地密码题。附件见 第二轮测试清单中的 `lcg-low-byte`。已回验全部 6 个状态，并恢复符合题目格式的明文。

## 先看这一步

附件泄漏了完整状态，低 8 位只用来异或明文。用三项完整状态求参数，再用余下状态检验。

**适用时**：模数已知，连续状态的第一组差值可逆。 **留意**：只有低位时，不能照搬完整状态公式。

题目的线性同余发生器每次做 `s = (a*s+b) % m`，再取 `s & 255` 与明文异或。但 `output.txt` 泄漏的是加密前的**完整状态**，而且公开了 `m`。先按完整数值求参数，不用先解截断问题。

把头三项写成两次递推，相减后有 `s2-s1 ≡ a*(s1-s0) (mod m)`。只要 `s1-s0` 在模 `m` 下可逆，就能求出 `a`，再代回求 `b`：

```python
a = (states[2] - states[1]) * pow(states[1] - states[0], -1, m) % m
b = (states[1] - a * states[0]) % m
assert all((a*x+b) % m == y for x, y in zip(states, states[1:]))
state = states[-1]
answer = bytearray()
for byte in ciphertext:
    state = (a*state+b) % m
    answer.append(byte ^ (state & 255))
```

第一字节用的是最后一项**之后**生成的状态。本题 `m` 不是 256 的倍数，所以不能把完整递推直接换成模 256；低 8 位只在产生密钥流时才取。

## 配套代码

`kb/_code/r66/crypto_round2.py`。从代码所在目录运行 `python crypto_round2.py lcg-low-byte 原附件`。依赖见脚本开头；运行后会显示核对结果。
