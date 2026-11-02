---
title: 方法卡 · MT19937 状态还原与输出预测
category: crypto
tags: [方法卡, mt19937, untemper, prng, python-random, 状态克隆]
signals: [624 个 32 位输出, python random, getrandbits 连续调用, 预测下一个随机数, 梅森旋转]
difficulty: medium
source: kb/crypto/random-mt19937.md
tools: [python, 内置脚本]
updated: 2026-11-02
---

# 方法卡 · MT19937 状态还原与输出预测

## 适用场景

服务端用 Python `random`（或 C/JS 里的 MT19937）生成密钥、验证码、token，
题面泄漏了**足够多连续输出**；或者题目把 `random.getrandbits(32)` 的结果整批打印出来。
典型场景：先喂 624 个 32 位输出克隆状态，再预测下一次校验值/密钥。

## 前置条件

- 已知 **624 个连续且未经额外变换的 32 位输出**（这是 MT19937 的 state 大小）。
- 输出的取法必须是**整字**：`getrandbits(32)`、`randrange(2**32)`。
  `getrandbits(8)`、`randint(0, 255)` 这类只取走部分比特的调用会打乱索引，需要按调用模式重建。
- MT19937 没有因为"每次调用重新播种"被打断（若每字符都新建 `Random()` 则失效）。

## 步骤

1. 判断输出粒度：确认每次调用是否恰好消费一个 32 位字。
2. 对每个输出做 **untemper**（逆右移异或、逆左移掩码异或），得到 624 个内部状态字。
3. 用 624 个状态字重建 `random.Random` 实例（`setstate`），或直接用脚本内置的克隆逻辑。
4. 预测接下来的输出；若题目只要 `getrandbits(8)`，注意是**大端拼接**成 32 位再切。
5. 越界时 `rc.submit` 会自动 twist，直接继续 predict 即可。

## 立即可用脚本

脚本路径：`kb/_methods/scripts/mt19937_untemper.py`

```powershell
# 自检（互逆、随机字、连续流克隆、错位采样拒绝、输出不足，<3s）
.\.venv\Scripts\python.exe kb/_methods/scripts/mt19937_untemper.py --selftest

# 实战：直接给 624 个值
.\.venv\Scripts\python.exe kb/_methods/scripts/mt19937_untemper.py --outputs "2653228291,3975144315,..." --predict 2 --json

# 实战：从文件读（逗号分隔），预测后续 2 个
.\.venv\Scripts\python.exe kb/_methods/scripts/mt19937_untemper.py --outputs-file work/q3/_mt.txt --predict 2 --json
```

- 公开函数：`temper(y)`、`untemper(y)`、`unshift_right_xor_mask(value, shift, mask)`、
  `unshift_left_xor_mask(value, shift, mask)`、`try_clone(outs)`、`check_clone(...)`。
- 输出 `{predictions: [...], verify: {...}}`。
- 输出不足 624 个时明确报错退出；采样粒度不对时打印"错位采样拒绝"，不会给假预测。
- 自检输出形如 `selftest ok: 5/5（互逆、随机字、连续流克隆、错位采样拒绝、输出不足）`。

## 手工示例

Python 侧生成真值（`random.Random(1337)`）：

```python
import random
r = random.Random(1337)
outs = [r.getrandbits(32) for _ in range(624)]
# 前 8 个：
# 2653228291,3975144315,2290358181,3048911309,1571306751,2452336048,2515937522,3143464376
# 紧接着的两个输出：649703518, 3141506407
```

把 624 个值写入文件后：

```powershell
.\.venv\Scripts\python.exe kb/_methods/scripts/mt19937_untemper.py --outputs-file work/q3/_mt.txt --predict 2 --json
# => {"predictions": [649703518, 3141506407], "verify": {}}
```

预测值与真值完全一致，即状态克隆成功。

## 失效场景

- **输出少于 624 个**：状态欠定，需要借助其它信息（例如 `randrange` 的取模偏差、种子爆破）。
- **每次调用只取 8 位**（`getrandbits(8)`）：词索引被打断，必须知道调用顺序才能逐字重组；
  直接喂 624 个 8 位值会被判"错位采样拒绝"。
- **每次生成都重新 `seed()`**：状态不可延续，只能爆种子。
- **非 CPython 实现的 `random`**（如 PyPy、某些 JS 引擎的 MT 变体）：参数一致，
  但取整方式（`randrange` 的拒绝采样）可能不同，需按实现核对。
- **输出经过哈希/编码**：先还原到 32 位整数，不要直接喂十六进制字符串。

## 相关文档

- `kb/crypto/random-mt19937.md`（untemper 原理、624 的来历、坑点来源）
- `kb/crypto/lcg-predict.md`（另一类 PRNG）
- `kb/crypto/cross-language-prng-predict.md`（跨语言实现差异）
- 导入批：`kb/_imported_cats/` 下的函数级参考条目
- 方法卡：`kb/_methods/lcg_parameter_recovery.md`

## 目录与收录说明

本卡直接放在 `kb/_methods/` 下、文件名不带下划线前缀，是为了同时满足两件事：
`tools/kb/parser.py` 的 `iter_md_paths` 会跳过名字以 `_` 开头的文件（脚本目录 `scripts/` 不受影响），
而这些方法卡需要在 `python tools/cli.py index` 之后能被正常检索到。
