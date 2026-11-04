---
title: 方法卡 · Many-Time-Pad（OTP / 流密码密钥流复用）与 Crib 拖拽
category: crypto
tags: [方法卡, otp, many-time-pad, crib, xor, 流密码, ctr 复用, 异或分析]
signals: [多段密文长度接近且都是 hex/base64, 题目说密钥流重复使用或 nonce 固定, 密文两两异或后出现大量可打印字符, 源码里 key 只生成一次就循环加密多条消息, 一次性密码本被复用, CTR 模式同一 nonce 加密多条明文]
difficulty: easy
source: kb/crypto/otp-many-time-pad.md
tools: [python, 内置脚本, CyberChef]
updated: 2026-11-03
---

# 方法卡 · Many-Time-Pad 与 Crib 拖拽

## 适用场景

同一段密钥流被用于多条明文（真正的 OTP 复用、CTR 同 nonce、RC4 同 key 等），表现为：

- 给了**多段**长度接近的密文，通常是 hex / base64；
- 题目明说「key 只生成一次」「nonce 固定」「我们把 OTP 复用了」；
- 把两段密文异或后，大量字节落在可打印区间——这是密钥被消掉的直接证据；
- 明文是英文句子、JSON、flag 列表等含大量可猜字符的文本。

## 前置条件

- 密文**确实是同一密钥流**：先随机抽两段异或，看可打印率是否明显高于随机（随机约 37%，若 > 80% 基本可确定）。
- 长度不一致时先截到最短再分析（补 0 会污染异或结果）。
- 至少能猜出一个足够长的 crib（≥4 字节，如 `flag{`、`the `），或者能靠空格统计定位词边界。

## 步骤

1. `--table` 打印两两异或的可读率矩阵，确认复用假设；今日脚本里随机数据可读率约 0.41，复用数据能到 1.0。
2. 用 crib 拖拽定锚：对每段每个偏移把 `c_i[o:o+L] XOR crib` 当密钥片段去解其它段，按「全可打印率 + 英文词频 + 最长字母串」排序取最佳。
3. **人工确认锚点**：看解出来的其它段是否有成词片段；确认后把 `seg:off:text` 作为 `--anchor` 固定下来，绝不让算法覆盖人工结论。
4. 用锚点解出的连续片段当新 crib 继续拖，bootstrapping 直到没有新字节。
5. 全解后拼 key 或 flag；每个新片段都回代一段密文验算，避免把伪命中当真。
6. 无任何可猜 crib 时用空格统计（空格 XOR 字母仍是字母）给粗定位，再由人眼逐位确认。

## 立即可用脚本

`kb/_methods/scripts/otp_many_time_pad.py`（纯标准库）：

```bash
# 1) 可读率矩阵（判断是否复用）
python kb/_methods/scripts/otp_many_time_pad.py --hex <c0> <c1> <c2> --table

# 2) crib 拖拽 + 锚点（1:0:flag{ 表示第 1 段偏移 0 处明文是 flag{）
python kb/_methods/scripts/otp_many_time_pad.py --hex <c0> <c1> --cribs 'flag{' 'the ' \
    --anchor 1:0:flag{ --json

# 3) 自检（14 组断言：异或恒等、crib 定位、key 片段、锚点解密、空格统计、拒绝与确定性）
python kb/_methods/scripts/otp_many_time_pad.py --selftest
```

导出函数：`xor_table`、`crib_drag(cts, crib, min_printable)`、`recover_key_stream(cts, known)`、
`apply_key(cts, key, mask)`、`best_space_positions`、`english_score`、`solve(cts, cribs, min_printable, anchors)`。
退出码：`0` 成功、`2` 参数非法（空密文/坏 hex/坏锚点）、`1` 一个字节都没恢复。

## 失效场景

1. **密钥流并未复用**：两两可读率接近 0.4（随机水平）时一切都是噪声。今日自检里 `--table` 对复用数据给出 1.000，对随机数据给出 0.412，用这个数判断，不要凭"看起来像"。
2. **评分不可靠导致自动选错锚点**：纯可打印率在短 crib（≤4 字节）上误报率极高，真实实现里最佳命中会随加了词频/字母串权重而改变——曾出现 `flag{` 最优命中从「第 1 段偏移 0（正确）」漂移到别的偏移，因为其它段凑出的短片段字母更长。**因此脚本只把 crib 命中当作候选，最终以人眼/锚点为准**，自动结果必须回代验算。
3. **无结构明文**：二进制、压缩包、中文 UTF-8 的 OTP 复用不能靠可打印率和词频，要改用已知明文攻击（例如文件头 crib）或语言模型评分。
4. **key 循环使用**：key 比明文短时等价于 Vigenère 多密钥流，需按 key 长度分列统计，本脚本按位置线性建 key 的模型不适用。
5. **CTR counter 延续**：若每次加密 counter 接着上次递增，则只有前缀重叠部分可攻击，长度不等的段会错位；必须先按覆盖区间对齐再异或。
6. **长度补 0**：把短密文补 0 会造成"该位置密钥已知"的假象，脚本一律截到最短长度而不是补齐。
7. **伪命中叠加**：每轮 bootstrap 若不加"必须与已知 key 一致"的冲突检查，错误片段会一路传染；`solve()` 里的 `accept()` 就是这道闸。
