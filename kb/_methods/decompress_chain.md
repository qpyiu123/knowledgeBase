---
title: 方法卡 · 多格式压缩套娃逐层解压（gzip/bz2/xz/zip/tar）
category: misc
tags: [方法卡, 压缩, gzip, bz2, xz, zip, tar, 套娃, 魔数]
signals: [文件打不开, 魔数 1f8b, BZh9, fd377a585a00, PK 头, 解压一层还是压缩包, bin 文件]
difficulty: easy
source: kb/misc/encoding-chain.md
tools: [python, 内置脚本, 7z]
updated: 2026-11-02
---

# 方法卡 · 多格式压缩套娃逐层解压（gzip/bz2/xz/zip/tar）

## 适用场景

拿到一个 `.bin` / 无扩展名文件 / `attachment`，`file` 命令显示是压缩流；
或者 `NewStar CTF decompress` 这种经典的"解压 100 层"。也可能是
gzip 里套 bz2、bz2 里套 xz 的多格式混合链。

## 前置条件

- 文件能读取（不需要密码；加密 zip 请转 `zip_password_attack.py`）。
- 每层是标准格式且**没有被截断**；截断的流脚本会报错而不是静默返回半截数据。
- zip 只取**第一个成员**（多成员需要人工挑选，用 `unzip -l` 先看清单）。

## 步骤

1. 先 `sniff(data)` 看魔数：`1f 8b` → gzip、`BZh` → bz2、`fd 37 7a 58 5a 00` → xz、
   `50 4b 03 04` → zip、tar 头偏移 257 处有 `ustar`。
2. 解一层后**再看一次魔数**，循环直到解出非压缩内容为止（`--max-depth` 默认 10）。
3. 若解出的是文本，检查是否有 `flag{`；若是文件头（PNG/JPG），转文件分析流程。
4. 层数特别多（>100）时把 `--max-depth` 提高，但注意磁盘/内存；单独一层很大时先看 `in_size`。

## 立即可用脚本

脚本路径：`kb/_methods/scripts/decompress_chain.py`

```powershell
# 自检（gzip 单层、xz→bz2→gzip、zip 取首成员、tar 取首文件、zlib 裸流、截断报错不崩、非压缩数据、深度上限，<3s）
.\.venv\Scripts\python.exe kb/_methods/scripts/decompress_chain.py --selftest

# 实战：逐层解压并把最终结果写盘
.\.venv\Scripts\python.exe kb/_methods/scripts/decompress_chain.py --file work/q3/_c.bin --out work/q3/_final.txt --json

# 实战：只想要链条信息（不写盘）
.\.venv\Scripts\python.exe kb/_methods/scripts/decompress_chain.py --file attachment.bin --max-depth 200 --json
```

- 公开函数：`sniff(data)` → `'gzip'|'bz2'|'xz'|'zip'|'tar'|'zlib'|None`；
  `decompress_layer(data, kind)`；`decompress_chain(data, max_depth=10)`
  → `{steps:[{format, member, in_size, out_size, head}], depth, final_size, final_text, final_head_hex}`。
- 自检输出形如 `selftest ok: 8/8（gzip 单层、xz→bz2→gzip、zip 取首成员、tar 取首文件、zlib 裸流、截断报错不崩、非压缩数据、深度上限）`。

## 手工示例

**示例 A：xz → bz2 → gzip 三层（构造 + 解码都已实跑）**

```powershell
.\.venv\Scripts\python.exe kb/_methods/scripts/decompress_chain.py --file work/q3/_c.bin --json
# steps:
#   xz   in_size 148 -> out_size 90   (head: BZh9...)
#   bz2  in_size  90 -> out_size 39   (head: \x1f\x8b...)
#   gzip in_size  39 -> out_size 19
# final_text: "flag{zip_chain_ok}", final_head_hex: "666c61677b7a69705f636861696e5f6f6b7d0a", depth: 3
```

**示例 B：zip 取首成员**

```powershell
.\.venv\Scripts\python.exe kb/_methods/scripts/decompress_chain.py --file work/q3/_c2.bin --json
# steps: [{"format": "zip", "member": "readme.txt", "in_size": 141, "out_size": 23, ...}]
# final_text: "flag{zip_first_member}"
```

## 失效场景

- **加密 zip / RAR / 7z**：本脚本只处理无密码流。加密 zip → `zip_password_attack.py`；
  RAR/7z → `unrar`/`7z` 或 hashcat（见 `kb/misc/archive-cracking-advanced.md`）。
- **截断/损坏的流**：脚本会抛 `ValueError: ... 数据被截断` 并退出，需要先修复（见 `kb/misc/file-repair-and-corruption.md`）。
- **zip 有多个成员**：只返回第一个，其余成员要人工 `unzip -l` 挑。
- **非标准/私有压缩**：`sniff` 返回 `None`，此时按"未知文件"处理，先看文件头 hex。
- **层数极大导致内存爆**：`--max-depth 200` 但每层解压后体积翻倍时注意资源。

## 相关文档

- `kb/misc/encoding-chain.md`（编码与压缩混合链条的识别顺序）
- `kb/misc/zip-archive-tricks.md`（zip 伪加密、CRC 撞库、bkcrack）
- `kb/misc/archive-cracking-advanced.md`（rar/7z 破解）
- `kb/misc/file-repair-and-corruption.md`（损坏流的修复）
- `kb/_imported_cats/misc/NewStar CTF 2024 _ decompress__official-4899b8faa9738b43238af6.md`（同类题原文）
- 方法卡：`kb/_methods/enc_chain_decode.md`、`kb/_methods/zip_password_attack.md`

## 目录与收录说明

本卡直接放在 `kb/_methods/` 下、文件名不带下划线前缀，是为了同时满足两件事：
`tools/kb/parser.py` 的 `iter_md_paths` 会跳过名字以 `_` 开头的文件（脚本目录 `scripts/` 不受影响），
而这些方法卡需要在 `python tools/cli.py index` 之后能被正常检索到。
