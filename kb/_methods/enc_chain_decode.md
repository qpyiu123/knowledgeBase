---
title: 方法卡 · 编码套娃逐层解码（base64/hex/url/转义）
category: misc
tags: [方法卡, 编码, base64, hex, url编码, 套娃, 自动解码]
signals: [一长串 base64, 只有 0-9a-f, 大量百分号, 大量反斜杠转义, 解一层还是乱码]
difficulty: easy
source: kb/misc/encoding-chain.md
tools: [python, 内置脚本, cyberchef]
updated: 2026-11-02
---

# 方法卡 · 编码套娃逐层解码（base64/hex/url/转义）

## 适用场景

题面给出一段"看起来像乱码"的字符串：或者以 `flag{` 结尾的 base64、或全是 `0-9a-f`、
或长串 `%E6%88%91`、或 `\x66\x6c`。也可能是**多层套娃**：base64 → hex → base64 → flag。

## 前置条件

- 字符串是文本形式（可复制粘贴）；二进制文件请改用 `decompress_chain.py`。
- **每一层都必须是"可逆编码"**，不是加密（不是异或、不是 Vigenère）。
- 最后一层解出来应当是可见 ASCII 或 UTF-8 文本，否则脚本会停在上一层并报告。

## 步骤

1. 先看长度与字符集：长度是 4 的倍数且含 `+/=` → base64；纯 `0-9a-f` 且偶数长度 → hex；
   大量 `%` → URL 编码；大量 `\x` / `\u` → 转义序列。
2. 让脚本**自动逐层剥离**：每解一层都做可打印性检查，解出乱码就回退，不硬解。
3. 命中 `flag{` 等停止符即停；也可 `--stop ""` 关掉停止条件，看完整链条。
4. 若第一层解出来仍是"另一种编码"，再喂一次；脚本一次跑完多层的典型是 3–6 层。
5. **rot13 需要显式开启**（`--allow-rot13`）：它会把正常英文变成乱码，自动尝试几乎必然误判。

## 立即可用脚本

脚本路径：`kb/_methods/scripts/enc_chain_decode.py`

```powershell
# 自检（单层 base64、两层 hex→base64、url 解码、%xx 二字节、\x 转义、rot13 显式开启、默认不误判英文、深度上限、原文直接命中，<2s）
.\.venv\Scripts\python.exe kb/_methods/scripts/enc_chain_decode.py --selftest

# 实战：直接给字符串
.\.venv\Scripts\python.exe kb/_methods/scripts/enc_chain_decode.py --data "NjY2YzYxNjc3YjZlNjU3Mzc0NjU2NDVmNmY2Yjdk" --json

# 实战：从文件读，允许 rot13 作为最后一层
.\.venv\Scripts\python.exe kb/_methods/scripts/enc_chain_decode.py --file work/q3/_enc.txt --allow-rot13 --json
```

- 公开函数：`decode_chain(text, max_depth=8, stop="flag{", allow_rot13=False)`
  → `{input_len, steps:[{encoding, result, binary, len}], final, stop_hit, depth}`；
  `detect_layer(text)` → `(name, bytes)`；辅助有 `_is_printable(data)`、`_utf8_salvage(raw)`、`_escape`。
- 检测器优先级：第一层 url/escape 优先；之后 `escape / url / hex / base64 / base64url / base32 / base85`。
- 自检输出形如 `selftest ok: 9/9（单层 base64、两层 hex→base64、url 解码、%xx 二字节 url、\x 转义、rot13 显式开启、默认不误判英文、深度上限、原文直接命中）`。

## 手工示例

**示例 A：单层 hex**

```powershell
.\.venv\Scripts\python.exe kb/_methods/scripts/enc_chain_decode.py --data "666c61677b74776f5f6c61796572737d" --json
# => {"encoding": "hex", "result": "flag{two_layers}", "stop_hit": "flag{", "depth": 1}
```

**示例 B：三层套娃 base64 → base64 → hex**

```powershell
.\.venv\Scripts\python.exe kb/_methods/scripts/enc_chain_decode.py --data "TmpZMll6WXhOamMzWWpabE5qVTNNemMwTmpVMk5EVm1ObVkyWWpkaw==" --json
# steps: base64 -> NjY2YzYxNjc3YjZlNjU3Mzc0NjU2NDVmNmY2Yjdk
#        base64 -> 666c61677b6e65737465645f6f6b7d
#        hex    -> flag{nested_ok}
# => final: "flag{nested_ok}", depth: 3
```

**示例 C：URL 双重编码**

```powershell
.\.venv\Scripts\python.exe kb/_methods/scripts/enc_chain_decode.py --data '%2566%256c%2561%2567%257b%2575%2572%256c%255f%256f%256b%257d' --json
# url -> "%66%6c%61%67%7b%75%72%6c%5f%6f%6b%7d"
# escape -> "flag{url_ok}"
# => final: "flag{url_ok}", depth: 2
```

⚠️ 抄字符串一定要完整：手工复制时漏掉一个字符（如 `666...` 变成 `666c116...`），
hex 层就会解出带 `:`/`]` 的怪字符，这是**输入错误**而不是脚本 bug。

## 失效场景

- **不是编码而是加密**（异或、Caesar、Vigenère、RSA）：本卡无解，转到对应方法卡。
- **二进制数据**：解出来是 `binary: true` 时会给出 hex 头部，此时改用压缩/文件分析卡。
- **第一层是 rot13**：需要 `--allow-rot13` 且只解一层（连解两次会互相抵消）。
- **自定义码表**（base64 改了字母顺序、base32 变种）：需要先还原码表再解。
- **混排**：字符串中间夹了中文/换行，按行拆开分别解。

## 相关文档

- `kb/misc/encoding-chain.md`（识别顺序、常见套娃组合、坑点来源）
- `kb/misc/encoding-auto-detect.md`（按字符集判定编码类型的规则）
- `kb/misc/cyberchef-and-tools.md`（Magic 操作与图形化对照）
- `kb/_imported_cats/misc/Python base64：编码不等于加密（reference）__fn-python-base64.md`（函数级细节）
- 方法卡：`kb/_methods/decompress_chain.md`、`kb/_methods/hash_length_extension.md`

## 目录与收录说明

本卡直接放在 `kb/_methods/` 下、文件名不带下划线前缀，是为了同时满足两件事：
`tools/kb/parser.py` 的 `iter_md_paths` 会跳过名字以 `_` 开头的文件（脚本目录 `scripts/` 不受影响），
而这些方法卡需要在 `python tools/cli.py index` 之后能被正常检索到。
