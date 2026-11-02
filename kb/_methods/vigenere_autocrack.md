---
title: 方法卡 · Vigenère 无密钥自动破解（IoC + 卡方）
category: crypto
tags: [方法卡, vigenere, 维吉尼亚, 古典密码, ioc, kasiski, 卡方]
signals: [字母密文无人可读, 密文长度上百, 无明显单表偏移, 出现 flag 样式但被打乱, 猜测为多表替换]
difficulty: easy
source: kb/crypto/classical-cipher.md
tools: [python, 内置脚本]
updated: 2026-11-02
---

# 方法卡 · Vigenère 无密钥自动破解（IoC + 卡方）

## 适用场景

只有密文，没有密钥；密文全是大写/小写字母，长度在几百到几千字符，
用单表 Caesar 的基础上再套一层"每个位置偏移不同"的机制。
典型题干："这是一段被 Vigenère 加密的英文"、"key 是单词"。

## 前置条件

- **明文是英文**（本脚本内置英语字母频率表）。中文、代码、数字混排会显著降低准确率。
- 密文长度建议 **≥ 500 字符**（脚本自检用 1500 字符级样本；过短的文本 IoC 波动大）。
- 密文没有被再套一层（如 A1Z26、base64）。若还有外层，先用 `enc_chain_decode.py` 剥掉。
- 字母表就是 A-Z（如果题目自定义了 alphabet，需要先映射回 A-Z）。

## 步骤

1. 取密钥长候选：对 `k = 1..max_len` 把密文按列切成 `k` 组，各组算 IoC 并取平均，
   **按 IoC 降序排列**。注意：真密钥长 `k` 的整数倍（`2k`、`3k`…）也会出峰，这是正常现象。
2. 取峰值的 `k`（若是 `3k` 这样的倍数，先除回 `k`），对每一列单独做 Caesar 卡方拟合，得到该列偏移 → 密钥字母。
3. 用还原的密钥解密，肉眼验证明文是否是英文（脚本同时给出 `plaintext` 字段）。
4. 交叉验证：`--kasiski` 打印重复三元组的间距，间距的 gcd 应能被 `k` 整除；
   也可以用 `--key-len` 指定已知密钥长。
5. 若第 2 步的 `k` 解出来是"重复模式"（如 `LEMONLEMON`），说明选成了倍数，用 `5` 重跑即可。

## 立即可用脚本

脚本路径：`kb/_methods/scripts/vigenere_autocrack.py`

```powershell
# 自检（互逆、IoC 峰值、密钥+明文还原、Kasiski、随机 IoC，<2s）
.\.venv\Scripts\python.exe kb/_methods/scripts/vigenere_autocrack.py --selftest

# 实战：只给密文文件，自动找密钥长并破解
.\.venv\Scripts\python.exe kb/_methods/scripts/vigenere_autocrack.py --cipher work/q3/_vig.txt --max-len 12 --kasiski --json

# 实战：已知密钥长 / 已知密钥
.\.venv\Scripts\python.exe kb/_methods/scripts/vigenere_autocrack.py --cipher work/q3/_vig.txt --key-len 5 --json
.\.venv\Scripts\python.exe kb/_methods/scripts/vigenere_autocrack.py --cipher "EMFZRLXNOFSGMHRRSDMPCCBHBEESGFTKZOYDEFPNDLBZNJJM" --key LEMON
```

- 公开函数：`clean(text)`、`index_of_coincidence(data)`、`key_length_by_ioc(text, max_len=20)`、
  `kasiski_candidates(text, ngram=3, top=5)`、`chi2_shift(text)`、`crack(text, key_len)`、
  `encrypt_with_key(plain, key)`、`decrypt_with_key(ct, key)`、`load_cipher(arg)`。
- 输出 `{key_len, key, plaintext}`；`--kasiski` 时先打印 Kasiski 线索。
- 自检输出形如 `selftest ok: 5/5（互逆、IoC 峰值、密钥+明文还原、Kasiski、随机 IoC）`。

## 手工示例

用本仓库 `kb/crypto/classical-cipher.md` 的前 1500 个字母作明文，密钥 `LEMON`：

```powershell
# 构造密文（脚本内函数也可直接调用：encrypt_with_key）
# 密文开头：EMFZRLXNOFSGMHRRSDMPCCBHBEESGFTKZOYDEFPNDLBZNJJM
# 密文长度：1500
.\.venv\Scripts\python.exe kb/_methods/scripts/vigenere_autocrack.py --cipher work/q3/_vig.txt --max-len 12 --json
```

实际输出（节选）：

```json
{"key_len": 10, "key": "LEMONLEMON",
 "plaintext": "TITLEATBASHCATEGORYCRYPTOTAGSSIGNALSATBASHPLAYFAIR..."}
```

⚠️ 这是本卡最重要的教训：**IoC 峰值出现在 10（= 2×5）而不是 5**，
因为密钥长 `k` 的倍数同样会让各列内部自相关。输出 `key = "LEMONLEMON"`
说明取到了倍数，把密钥长除以 2 后用 `--key-len 5` 重跑，得到正确的 `LEMON`。

## 失效场景

- **明文不是英文**（中文、代码、数字为主）：卡方模型失效，密钥会给出乱码字母。
- **密文过短**（< 200 字符）：IoC 噪声大，峰值不可靠。
- **密钥长接近密文长度**：每列只有一两个字母，统计无效。
- **题目用了自定义字母表**或先做了 Atbash/ROT：先复原字母表，再用本卡。
- **是自动密钥 Vigenère（autokey）**：密钥与明文耦合，本卡的列独立假设不成立，需要先爆破首词。

## 相关文档

- `kb/crypto/classical-cipher.md`（Caesar/Atbash/Playfair/Bacon/IoC 工具函数与坑点来源）
- `kb/crypto/otp-many-time-pad.md`（密钥不比明文短时的对照：many-time-pad 不是经典 Vigenère）
- `kb/misc/encoding-chain.md`（先剥外层编码）
- 方法卡：`kb/_methods/enc_chain_decode.md`

## 目录与收录说明

本卡直接放在 `kb/_methods/` 下、文件名不带下划线前缀，是为了同时满足两件事：
`tools/kb/parser.py` 的 `iter_md_paths` 会跳过名字以 `_` 开头的文件（脚本目录 `scripts/` 不受影响），
而这些方法卡需要在 `python tools/cli.py index` 之后能被正常检索到。
