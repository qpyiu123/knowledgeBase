---
title: 方法卡 · xorshift 伪随机数参数/状态恢复（LCG 之外的线性 PRNG）
category: crypto
tags: [方法卡, xorshift, prng, 线性同余, 状态恢复, 种子反推, 移位异或, 伪随机预测]
signals: [源码里出现 x ^= x << 13 之类移位异或, 连续输出可以预测下一项, 题目给出随机数序列要求预言下一个, seed 是毫秒时间戳或小整数, 生成器叫 xorshift/xoroshiro/rand32, 没有 MT19937 的 624 字状态, 输出都是 32 位整数]
difficulty: medium
source: kb/crypto/lcg-predict.md
tools: [python, 内置脚本]
updated: 2026-11-03
---

# 方法卡 · xorshift PRNG 恢复

## 适用场景

题目里的随机数不是 Python `random`（MT19937）也不是 LCG，而是 **xorshift 家族**：

- 源码出现 `x ^= x << 13; x ^= x >> 17; x ^= x << 5` 这类「移位后异或自身」；
- 输出是 32 位整数（或 C 的 `uint32_t`），相邻两项之间有可验证的递推关系；
- seed 往往很小（毫秒时间戳、`time(0)`、固定常量），需要"预言下一项"；
- 也可能只给一串输出，连移位参数都不给。

与 LCG 的区别：xorshift **不是** `x' = a*x+b mod m` 的形式，用 LCG 的参数恢复公式（差分取 gcd）会得到无意义的数。

## 前置条件

- 拿到至少 **2** 个连续输出才能验证一组参数；要唯一定参一般需要 3～5 个。
- 输出是**完整** 32 位字（若只给低 8 位，需先用低位约束过滤候选，见失效场景 4）。
- 每两步之间没有其它扰动（例如没有额外的 `% 1000` 截断、没有和其他源异或）。

## 步骤

1. **判族**：先试 LCG 公式，若二阶差分 gcd 得不到自洽的 `m`，转 xorshift。
2. **找参数**：源码可读时直接抄 `(a,b,c)`；不可读则对 `1..31` 的三元组枚举（`brute_shifts`），用连续输出自洽性筛选——本例 3 个输出就唯一确定了 `(7,9,13)`。
3. **验证**：把候选参数代入 `verify()`，再用 `predict()` 预测第 n+1 项，与真实下一次输出比对。
4. **反推种子**：xorshift 每步可逆，`xorshift32_unstep` 由第一项还原初始状态；若序列从种子后的第一次输出开始，还原结果就是 seed。
5. **拿到 flag**：用预测值解出后续密文/令牌；或把 seed 喂回服务端的生成函数。

## 立即可用脚本

`kb/_methods/scripts/xorshift_recovery.py`（纯标准库）：

```bash
# 自检（17 组断言：可复现、自洽性、预测、unstep 互逆、反推种子、暴力恢复参数、非法输入拒绝）
python kb/_methods/scripts/xorshift_recovery.py --selftest

# 已知参数：生成 / 预测 / 反推种子
python kb/_methods/scripts/xorshift_recovery.py --shifts 13,17,5 --seed 2463534242 --count 8 --predict 3 --recover-seed

# 参数未知：枚举移位三元组
python kb/_methods/scripts/xorshift_recovery.py --brute --outs 3579884630,1699422745,2295038862 --json
```

导出函数：`XorShift32(seed,a,b,c)`、`xorshift32_step`/`xorshift32_unstep`、`verify(outs,a,b,c)`、
`predict(outs,a,b,c,n)`、`brute_shifts(outs,max_shift)`、`recover_seed(outs,a,b,c)`。
退出码：`0` 成功、`2` 参数不足/格式非法、`1` 数据不自洽（例如给出的输出根本不来自该参数）。

## 失效场景

1. **不是 xorshift**：若输出之间不存在任何 `(a,b,c)` 自洽关系，`brute_shifts` 抛「找不到匹配参数」；此时要回到 LCG / MT19937（Python `random` 是 MT，见 `random-mt19937.md`）路线，别硬套。
2. **每一步都有额外扰动**：若生成器在 xorshift 后再 `% 1000` 或只回传高位，原始状态被不可逆截断，`verify` 会失败且参数枚举无解；只能改用截断 PRNG 的约束求解。
3. **64 位 / xoroshiro 变体**：脚本只实现 32 位、`x^=x<<a; x^=x>>b; x^=x<<c` 这一种形态；xorshift128+ / xoroshiro / 64 位版本的分支与状态数组不同，`verify` 会判为不自洽（这不代表输出有错）。
4. **只给低位**：若只看到 `x & 0xff`，`brute_shifts` 会返回**多个**候选（每个候选都可能解释观察），必须结合后续输出或截断求解再筛，不能取第一个。
5. **参数枚举范围**：`brute_shifts` 默认只扫 `1..31`；若某移位量恰好为 0（退化为两步 xorshift）或超过 31，会导致"找不到参数"的假阴性。
6. **生成器被重置**：若服务每次请求都重新 `seed(时间)`，跨请求的多项序列并不连续，`verify` 失败；必须保证样本来自**同一次初始化**。
