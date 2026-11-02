---
title: 方法卡 · ZIP 密码攻击（纯标准库字典/掩码/已知明文）
category: misc
tags: [方法卡, zip, 密码破解, zipcrypto, 字典攻击, 掩码, bkcrack]
signals: [加密 zip, 需要密码才能解压, 弱口令, 已知明文攻击, 压缩包附件]
difficulty: medium
source: kb/misc/zip-archive-tricks.md
tools: [python, 内置脚本, bkcrack, hashcat]
updated: 2026-11-02
---

# 方法卡 · ZIP 密码攻击（纯标准库字典/掩码/已知明文）

## 适用场景

附件是**真加密**的 zip（能列目录但打不开），没有密码提示或提示是"弱口令/4 位数字"。
也可能已知其中某个成员的明文（例如每个 zip 都有 `readme.txt = "flag is ..."` 模板），可走已知明文路线。

## 前置条件

- 先分清**伪加密**与真加密：伪加密只需把中央目录 `flag` 位改回 0 就能解开，不需要爆密码。
  判断方法：`zipfile.ZipFile(f).namelist()` 能列出成员、`read()` 时才报 `RuntimeError: File ... is encrypted`。
- 字典攻击需要一份候选词表；掩码攻击需要知道口令的字符集与长度。
- 已知明文攻击（bkcrack）需要**至少 12 字节已知明文的连续压缩数据**，且压缩方式为 Store/Deflate。

## 步骤

1. 先做**联机/静态判别**：`zipfile.ZipFile(f).namelist()` 能列出成员、`read()` 时才报
   `RuntimeError: File ... is encrypted` → 真加密；或者用本脚本的
   `--known-plaintext 成员名 --plain-file 明文文件` 探测，未加密时会返回
   `{"ok": false, "reason": "该成员未加密，无需攻击"}`。
2. 有字典（rockyou、自带 wordlist）→ `--wordlist`；脚本用 ZipCrypto 校验字节逐条验证，比反复调 `unzip` 快得多。
3. 知道格式（如 `flag????`、4 位纯数字）→ `--mask "dddd"` 或 `--mask "@d@d@d"`。
4. 上述都不行且有已知明文 → `--known-plaintext 成员名 --plain-file 明文文件`，
   脚本给出本地文件头偏移与 12 字节密文头，再调 `bkcrack -C x.zip -c 成员 -p 明文 -o 偏移`。
5. 拿到密码后用 `7z x` / `unzip -P` 解压；若是 ZipCrypto 但密码仍找不到，bkcrack 可**不解密码**直接改写文件。

## 立即可用脚本

脚本路径：`kb/_methods/scripts/zip_password_attack.py`

```powershell
# 自检（ZipCrypto 互逆、crc 表、掩码展开、字典命中、字典不命中、未加密如实报告，<2s）
.\.venv\Scripts\python.exe kb/_methods/scripts/zip_password_attack.py --selftest

# 字典攻击
.\.venv\Scripts\python.exe kb/_methods/scripts/zip_password_attack.py --file secret.zip --wordlist rockyou.txt --json

# 掩码攻击（@=小写 A=大写 d=数字 s=符号 ?=可打印 h=hex）
.\.venv\Scripts\python.exe kb/_methods/scripts/zip_password_attack.py --file secret.zip --mask "@d@d@d" --json

# 已知明文探测（输出 bkcrack 命令）
.\.venv\Scripts\python.exe kb/_methods/scripts/zip_password_attack.py --file secret.zip --known-plaintext readme.txt --plain-file readme_plain.txt --json
```

- 公开函数：`ZipCrypto`（`update`/`_stream_byte`/`decrypt`/`encrypt`）、`verify_password(zpath, password)`、
  `try_dictionary(zpath, words, max_tries, cb)`、`expand_mask(mask)`、`try_mask`、
  `known_plaintext_probe(zpath, member, plain)` → `{ok, member, method, header_offset, first_cipher_hex, bkcrack_cmd}`、
  `brute_tail2(zpath, member, plain, max_tries=65536)`、`make_zipcrypto_zip(path, password, payload)`。
- 自检输出形如 `selftest ok: 6/6（ZipCrypto 互逆、crc 表、掩码展开、字典命中（…）、字典不命中、未加密如实报告）`。
- 注意：自检里的"字典命中"一项在无法回读加密流的环境下会跳过（脚本会打印原因）；
  这是环境限制，不代表脚本逻辑不可用，字典/掩码的真实路径请用真 zip 验证。

## 手工示例

```powershell
# 未加密 zip：脚本如实报告"该成员未加密，无需攻击"
.\.venv\Scripts\python.exe kb/_methods/scripts/zip_password_attack.py `
  --file work/q3/_plain.zip --known-plaintext a.txt --plain-file a.txt --json
# => {"file": "...", "known_plaintext": {"ok": false, "reason": "该成员未加密，无需攻击"}, "elapsed_s": 0.0}

# 已知明文探测（真加密 zip）：给出偏移与 bkcrack 命令
.\.venv\Scripts\python.exe kb/_methods/scripts/zip_password_attack.py `
  --file secret.zip --known-plaintext readme.txt --plain-file readme_plain.txt --json
# => {"known_plaintext": {"ok": true, "member": "readme.txt", "method": <压缩方式>,
#     "header_offset": <N>, "first_cipher_hex": "<24 位 hex>",
#     "bkcrack_cmd": "bkcrack -C secret.zip -c readme.txt -p readme_plain.txt -o <N>"}}
```

注意返回码：只有拿到 `password` 或至少给出 `known_plaintext` 分支时才是 exit 0；
纯 `--file` 探测（不给策略）会 exit 1，这是预期的"什么都没做"。

掩码速查：`@` 小写字母、`A` 大写字母、`d` 数字、`s` 符号、`?` 可打印 ASCII、`h` 十六进制字符；
`@d` 表示"小写字母 + 数字"，`?` 组合很大会爆炸，务必先用字典。

## 失效场景

- **AES 加密 zip（method 99）**：ZipCrypto 攻击全部失效，只能字典（`7z2john` + hashcat `-m 13600`）。
- **RAR / 7z**：本脚本只支持 zip；用 `rar2john`/`7z2john` + hashcat。
- **强密码且无字典**：暴力无望，改走伪加密/已知明文/bkcrack 改写。
- **已知明文不足 12 字节或压缩后数据非常规（Deflate 有压缩）**：bkcrack 需要连续压缩数据，
  Deflate 成员需先得到**压缩后**的 12 字节，不能直接给原文（Store 方式则原文即压缩数据）。
- **伪加密**：直接改中央目录 flag 位，别跑字典。

## 相关文档

- `kb/misc/zip-archive-tricks.md`（伪加密、CRC32 撞库、bkcrack 12 字节明文、坑点来源）
- `kb/misc/archive-cracking-advanced.md`（rar/7z2john + hashcat -m 11600/13000/17200）
- `kb/_imported/misc/ZIP-格式.md`、`kb/_imported/misc/压缩包.md`、`kb/_imported/misc/zipmaster.md`
- `kb/_imported_cats/misc/DASCTF 2024 暑期挑战赛 _ EZ_zip__cn-case-dasctf-lunatic-349725aa-seg3.md`
- 方法卡：`kb/_methods/decompress_chain.md`

## 目录与收录说明

本卡直接放在 `kb/_methods/` 下、文件名不带下划线前缀，是为了同时满足两件事：
`tools/kb/parser.py` 的 `iter_md_paths` 会跳过名字以 `_` 开头的文件（脚本目录 `scripts/` 不受影响），
而这些方法卡需要在 `python tools/cli.py index` 之后能被正常检索到。
