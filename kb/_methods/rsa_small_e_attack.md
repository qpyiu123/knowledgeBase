---
title: 方法卡 · RSA 小公钥指数直接开方（含枚举 k）
category: crypto
tags: [方法卡, rsa, 小e, 低加密指数, 整数开根, 无填充]
signals:
  - e=3 且没有填充
  - 密文比 n 小很多
  - iroot 直接开 e 次方
  - 已知明文很短
  - 小块明文加密
  - m 很小
  - 源码里 pow(m, e, n) 直接用 flag
  - e 是 5 或 17
difficulty: easy
source: kb/crypto/rsa-small-e-attack.md, kb/crypto/rsa-broadcast-attack.md
tools: [python, 内置脚本]
updated: 2026-11-05
---

# 方法卡 · RSA 小公钥指数直接开方（含枚举 k）

## 适用场景

题面只给**一组** `(n, e, c)`，而 `e` 极小（最常见 `e = 3`，偶尔 `5`、`17`），并且能看出明文没有走 OAEP/PKCS#1 填充
（源码里直接 `pow(bytes_to_long(flag), e, n)`）。此时 `m^e` 很可能根本没有超过 `n`，密文就是明文的纯幂，
`bit_length(c)` 往往明显小于 `bit_length(n)`。

这条与"广播攻击"的分界很清楚：**小 e 只要一个 n，广播要 e 个不同 n**。

## 前置条件

- 已知 `n, e, c`；`e` 建议 `≤ 17`（`e` 大了枚举 `k` 的窗口会迅速失效）。
- 成功条件：存在 `k ≥ 0` 使 `c + k*n` 是完全 `e` 次幂，此时 `m = (c + k*n)^(1/e)`。
- 没有模约减时 `k = 0`；枚举上限由明文范围估计，`2^20` 是脚本默认预算。
- 直接开根要求 `m^e<n`；有已知高位时，可继续检查 Coppersmith 所需的未知量大小。

## 步骤

1. 直接 `iroot(c, e)`，检查精确性并回代；不使用 `c < n^(1/e)` 筛选。例：`n=11413, e=3, c=8000`，精确根为 `m=20`。
2. 不精确就枚举 `k = 0,1,2,...`，对 `c + k*n` 做整数 `e` 次开方，命中即停：

   ```python
   for k in range(max_k + 1):
       r, ok = iroot(c + k * n, e)
       if ok:
           return k, long_to_bytes(r)
   ```

3. 拿到 `m` 按题目编码转 bytes、回代加密。只有源码明确构造 `m=m1*m2` 时才按已知因子整除；普通字节前缀是移位加法关系。
4. 仍不开就检查两件事：题面是不是加了固定填充（不是纯幂）；明文是否只知高位（→ Coppersmith 小根）。
5. 输出命中的 `k`，并核对 `m<n`、`pow(m,e,n)==c`、题目格式。`k=0` 和 `k>0` 都是可检查的候选。

## 脚本

脚本路径：`kb/_methods/scripts/rsa_small_e.py`

```powershell
# 自检：直接开根、枚举 k、非法参数拒绝、有界搜索、固定 seed、iroot 边界（<1s）
.\.venv\Scripts\python.exe kb/_methods/scripts/rsa_small_e.py --selftest

# 实战：e=3，给出全部候选（按可打印率排序）
.\.venv\Scripts\python.exe kb/_methods/scripts/rsa_small_e.py --n 0x... --e 3 --c 0x... --json

# 实战：已知明文前缀 flag{，顺带筛掉干扰候选
.\.venv\Scripts\python.exe kb/_methods/scripts/rsa_small_e.py --n 0x... --e 3 --c 0x... --prefix 'flag{'
```

- 公开函数：`iroot(x, e)`、`small_e_attack(n, e, c, max_k)`、`split_plaintext(n, e, c, prefix, max_k)`。
- 参数：`--e` 必填且 `≥ 2`；`--max-k` 默认 `2^20`，大整数题可调高但要估算耗时。
- 失败时打印"未找到精确 e 次根"并 **exit 1**；参数缺失由 argparse 报中文错误并 exit 2，不给假答案。

## 失效场景

- **明文被填充**：`m = long_to_bytes(pad(flag))` 或 `m = flag + os.urandom(8)`，此时 `m` 与 `n` 同量级，`k` 涨到无法枚举。
- **`e` 不小**（如 65537）或明文超过 `n^(1/e)` 多个数量级：枚举 `k` 的复杂度按 `m^e / n` 线性爆炸，`2^20` 远不够。
- **`n` 是较小的玩具模数**：自检里的 `e=3` 若 `m^3 > n` 也会走 `k>0` 分支，容易把"平凡解"误当攻击成功，先核对 `k` 与 `m` 长度。
- **输入进制或字节序不符**：先按题目还原数据；`int(flag.hex(),16)` 本身与大端字节转整数相同。

## 手工示例

```powershell
runtime/python-portable/python.exe kb/_methods/scripts/rsa_small_e.py --n 11413 --e 3 --c 8000 --max-k 0 --json
# k=0，m_hex=14（整数 20）
runtime/python-portable/python.exe kb/_methods/scripts/rsa_small_e.py --n 11413 --e 3 --c 4174 --max-k 2 --json
# k=2，m_hex=1e（整数 30）；max-k=1 时未找到
```

这里的字节是玩具数据，不要求可打印。完整对照及来源见 `kb/_reference/rsa-path-check.md`。

## 相关文档

- `kb/crypto/rsa-small-e-attack.md`（直接开根与枚举 k 的原始写法、分段明文变体）
- `kb/crypto/rsa-broadcast-attack.md`（多组 `n` 的 Håstad，与本卡互补，已有方法卡 `kb/_methods/rsa_hastad_broadcast.md`）
- `kb/crypto/rsa-coppersmith.md`（明文只知高位时的接续）
- 方法卡：`kb/_methods/rsa_hastad_broadcast.md`、`kb/_methods/rsa_common_modulus_attack.md`
