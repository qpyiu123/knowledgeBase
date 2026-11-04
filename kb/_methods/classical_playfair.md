---
title: 方法卡 · Playfair 双字母替换（棋盘重建与统计破译）
category: crypto
tags: [方法卡, 古典密码, playfair, 双字母替换, 5x5 棋盘, 单表替换, 爬山破译]
signals: [密文全是字母且长度为偶数, 字母表里没有 j 或 j 与 i 混用, 双字母组频率异常高于单字母, 题目提到 5x5 棋盘或关键词表, 明文按两位一组处理且相邻相同字母被拆开, flag 外壳被整体替换后内部仍是字母, 关键词给出一串英文单词]
difficulty: easy
source: kb/crypto/classical-cipher.md
tools: [python, 内置脚本]
updated: 2026-11-03
---

# 方法卡 · Playfair

## 适用场景

古典密码题里出现「双字母替换 + 5×5 棋盘」的特征：

- 密文长度是**偶数**，且字母表通常只有 25 个字母（`j` 与 `i` 合并）；
- 明文被两两分组后加密，`balloon` 这类双写字母会先插填充字母（`x` 或 `q`）再加密；
- 题面给了关键词（`MONARCHY`、`PLAYFAIR`）或要求"用关键词构造棋盘"；
- 单字母频率接近均匀，但**双字母组**出现明显偏斜。

## 前置条件

- 确定字母表约定：25 字母（i/j 合并）还是 26 字母（部分变体会去掉 `q`）—— 本脚本按 i/j 合并实现。
- 确定填充字母：常见 `x`，也有用 `q` 的；解密后要手动把填充字母去掉。
- 至少要知道「规则版本」：同列下移、同行右移、矩形互换列。

## 步骤

1. **规整密文**：去掉空格/标点，`j` 统一成 `i`，确认长度偶数（奇数说明丢字符或用了不同约定）。
2. **已知关键词**：直接 `encrypt/decrypt --key`；先用经典向量核对实现（`MONARCHY` + `instruments` → `GATLMCLRQXA` 前 12 位）。
3. **无关键词、有已知明文**：把 (明文库, 密文库) 按对分开喂给 `build_key_from_known`，它搜索**能同时解释所有对**的棋盘；搜不到会明确报"不相容"，不会编造键盘。
4. **什么都没有**：`--crack` 用英文一元+二元频率做随机重启爬山，密文 ≥ 60 字母才有意义；结果需要人工读一遍确认。
5. **还原 flag**：解密后去掉填充字母（`x`/`q`），再把外层 `synt{}` 之类换回 `flag{}`。

## 立即可用脚本

`kb/_methods/scripts/classical_playfair.py`（纯标准库）：

```bash
# 自检（17 组断言：经典向量、往返、重复字母填充、j 合并、已知明文重建键盘、爬山改进、非法拒绝、确定性）
python kb/_methods/scripts/classical_playfair.py --selftest

python kb/_methods/scripts/classical_playfair.py --key MONARCHY --encrypt "instruments" --json
python kb/_methods/scripts/classical_playfair.py --key MONARCHY --decrypt "GATLMZCLRQXA"
python kb/_methods/scripts/classical_playfair.py --crack "BMDXMESQ..." --seed 0
```

导出函数：`clean_key`/`grid_string`、`prepare`、`encrypt`/`decrypt`、`score`、
`hill_climb_decrypt`、`build_key_from_known`。退出码：`0` 成功、`2` 参数不足/数据非法（奇数长度、空密钥、密文太短）。

## 失效场景

1. **26 字母变体**：有的实现合并的是 `q` 而不是 `i/j`，用的是 5×5 去掉 `q` 或者 6×6 含数字；脚本固定 i/j 合并，遇到这类题会报「字母不在字母表中」或算出错误文本。
2. **填充字符不同**：明文含 `x` 或双写 `ll` 时脚本按常规插 `x`；若加密方用 `q` 填充，密文末尾会多对、解密得到带 `q` 的尾巴，需要按实际填充字符裁剪。
3. **密文奇长**：`decrypt` 直接 `ValueError`；说明源数据被我方预处理破坏（去掉了非字母但原文明文里有一个字符处于分组边界），要回到原始数据核对。
4. **已知明文对与同一棋盘不相容**：`build_key_from_known` 会抛「已知明文对与同一个 Playfair 键盘不相容」——通常是明文侧没做填充（`ll` 被拆开）或者密文对没对齐，按对重新切分即可，绝不能拿"近似键盘"当结果。
5. **爬山破译不可靠**：密文太短（< 60 字母）或语言不是英文时，`--crack` 给出的文本只是"分数最高的候选"，不保证是原文；需要用 flag 格式先验人工校验，或改用已知明文重建键盘。
6. **`j` 信息丢失**：i/j 合并后无法区分原文写的是 `i` 还是 `j`，还原 flag 时要按语义猜；如果 flag 恰好含 `j`（如 `flag{j...}`），密文里会变成 `i`，需要结合外层格式判断。
