---
title: 方法卡 · RSA 部分比特恢复（小范围枚举与 Coppersmith 参考）
category: crypto
tags: [方法卡, rsa, coppersmith, 小根, 格, lll, 已知高位, univariate]
signals: [已知 p 的高若干位, 已知 flag 的前缀, 明文高位已知, 低位未知, p 的高位与 flag 拼接, Coppersmith 小根, 不用 sage 的格约化, 只给 n e c 但有高位提示]
difficulty: hard
source: kb/crypto/rsa-coppersmith.md, kb/crypto/lattice-lll.md
tools: [python, sympy, SageMath]
updated: 2026-11-03
---

# 方法卡 · RSA 部分比特恢复

## 适用场景

已知 p 的高位、给了 p 的部分比特，或已知明文高位。先估计剩余未知位数，再选择小范围枚举或来源文档中的 Coppersmith 方法。

本卡脚本的命令行入口使用枚举，不执行格攻击。文件中的 LLL 与多项式构造函数保留作实验代码，尚待单独核对，实际题目优先参考来源中的 SageMath 示例。

## 前置条件

- 高位因子模式：给出 n、p >> k 与 k；未知低位最多 26 位，位数越大枚举越慢。
- 明文模式：给出 n、e、c、明文高位和未知低位数。演示采用 e=3、小未知范围。
- 低位模式：给出 p 的低位与低位数，通过候选补齐和整除验证恢复。
- 运行主体使用标准库；自检还需要 sympy 生成测试数。

## 步骤

1. 保留题目给出的 n、e、c 与泄漏定义，区分高位和低位。
2. 高位因子写成 p = (hint << k) + x，枚举 0 <= x < 2^k，逐一验证 n % p == 0。
3. 明文写成 m = (prefix << k) + x，枚举后验证 pow(m, e, n) == c。
4. 未知范围太大时，阅读 kb/crypto/rsa-coppersmith.md 中的格构造与 SageMath 用法。库内实验函数不作为这个入口的替代。
5. 保存因子相乘结果或重加密结果，确认与原题输入一致。

## 脚本

`kb/_methods/scripts/rsa_coppersmith.py`

```bash
python kb/_methods/scripts/rsa_coppersmith.py --n 221 --known-high 2 --shift-bits 3
python kb/_methods/scripts/rsa_coppersmith.py --n 221 --p-low 13 --low-bits 4
python kb/_methods/scripts/rsa_coppersmith.py --selftest
```

- `--known-high`：因子高位枚举；`--shift-bits`：未知低位个数。
- `--plain-high` 配合 `--n --e --c`：明文高位枚举。
- `--p-low --low-bits`：因子低位补齐。
- `--m` 是旧接口保留参数，当前枚举入口不使用它。
- `--json` 输出结构化结果。无匹配时列表为空；非法参数退出码为 2。

## 失效场景

- 未知位数大时枚举耗时很长，应改用来源中的 SageMath 实现。
- 泄漏定义、前缀或位数抄错时找不到结果，先核对原始题面。
- 给出的是 d 的部分比特时，不能直接作为 p 的高位输入。
- 文件中的实验格函数未完成独立验收；自检覆盖小样例和入口边界。

## 来源

- `kb/crypto/rsa-coppersmith.md`：已知 p、m 高位的识别与 SageMath 示例。
- `kb/crypto/lattice-lll.md`：格、子集和与小根的构造背景。
