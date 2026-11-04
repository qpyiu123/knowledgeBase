---
title: 方法卡 · CyberChef 常用配方的离线复刻
category: misc
tags: [cyberchef, magic, 编码, xor爆破, wsl, ctf]
signals:
  - "队友发来 CyberChef 配方截图，本地却打不开浏览器"
  - "附件跑完 strings 只剩一串可打印字符，长度是 4 的倍数"
  - "Magic (Intensive mode) 给出多条候选路径不知选哪条"
  - "From Base64 之后接 Raw Inflate 才出现文件头"
  - "单字节 XOR 用 flag{ 作 crib 命中多个密钥"
  - "Strings 设了 min length 6、UTF-16LE 才看到线索"
difficulty: medium
source: kb/misc/cyberchef-and-tools.md, kb/misc/encoding-auto-detect.md
updated: 2026-11-03
tools: [python3, cyberchef, wsl, binwalk, file]
---
## 适用场景

拿到一段疑似编码/压缩的附件，需要反复试"From Base64 → Raw Inflate → Detect File Type"
这类链式配方，但目标机器没有浏览器、或要批量跑几十个文件。本卡把 CyberChef 最常见的
五个操作（Magic、Base64+Inflate 链、XOR Brute Force、Strings、Detect File Type）
做成可脚本化、离线、结果可复现的最小实现，用来快速筛路径，再回 CyberChef 手工精修。

## 前置条件

- Python 3.8+，无需第三方包（zlib/gzip/base64 均来自标准库）。
- 待分析文件或标准输入。
- 知道要用的 crib（已知明文前缀，如 `flag{`），否则 XOR 爆破只能盲猜。

## 步骤

1. **先 file / binwalk 定性**，已有已知文件头（PNG/ZIP/PDF/gzip）时不必再套变换链。
2. **Magic 打分**：对每个候选变换算"可打印比例×2 + 线索词×3"，只保留相对当前节点
   提升 ≥1 分的步骤，深度 4、每层保留前 3 条（beam search），避免对明文乱套 ROT47。
3. **二进制保护**：输入首部出现 NUL 或高位字节、或是已知文件头时，不再尝试
   ROT13/ROT47/URL Decode 这类字符级变换。
4. **固定配方复现**：`--recipe "From Base64 -> Raw Inflate"`，任何一步失败立刻报错，
   不静默吞掉（这一步与 CyberChef 手工点选等价）。
5. **XOR 爆破**：`--xor-brute blob.bin --crib "flag{"`，用 crib 反推单字节密钥。
6. **Strings**：默认 min length 6；UTF-16LE 垃圾里常藏明文，用 `--utf16` 再看。
7. **Detect File Type**：结果按魔数表打印（PNG/JPEG/ZIP/PDF/gzip/zlib/ELF），
   命中后直接交给对应专题卡（steg/carving）。

## 立即可用脚本

`kb/_methods/scripts/cyberchef_recipes.py`（纯标准库、离线、只读）

```
python cyberchef_recipes.py --magic --file data.txt
python cyberchef_recipes.py --auto --file data.txt
python cyberchef_recipes.py --recipe "From Base64 -> Raw Inflate" --file data.txt
python cyberchef_recipes.py --xor-brute blob.bin --crib "flag{"
python cyberchef_recipes.py --strings blob.bin --min 6 --utf16
python cyberchef_recipes.py --selftest
```

参数：

- `--file`：输入文件；省略时从标准输入读（便于管道）。
- `--magic`：逐层自动识别变换，打印路径、评分、文件类型与结果片段。
- `--auto`：在 magic 结果上补 Detect File Type（等价于 CyberChef 的
  "From Base64 → Raw Inflate → Detect File Type" 链）。
- `--recipe`：手写配方，步骤名用 `->` 分隔，未知步骤或失败步骤直接报错。
- `--xor-brute FILE` + `--crib`：单字节 XOR 爆破，命中列出 key 与明文。
- `--strings FILE --min N [--utf16]`：提取可打印串。
- `--selftest`：断言 magic 还原 base64、配方链还原 zlib、XOR crib 命中、
  未知步骤/过短串被拒绝、结果可复现且空输入不崩。

失败行为：未知配方步骤、输入文件不存在、`--min < 1`，stderr 打印 `失败：…` 返回 2；
自检通过打印 `selftest ok: …` 返回 0。

## 手工示例

```
$ python cyberchef_recipes.py --magic --file data.txt
路径：From Base64 -> Raw Inflate
评分：9.31
类型：PNG image
$ python cyberchef_recipes.py --xor-brute blob.bin --crib "flag{"
key=0x5a  b'flag{xor}'
$ python cyberchef_recipes.py --magic --file img.png
路径：(无需变换)
评分：0.91
类型：PNG image
```

## 失效场景

- 需要 CyberChef 独有算子（Fork/Subsection、AES/DES 解密、SSH 密钥解析）：
  本脚本不实现，仍需回 CyberChef。
- 多重压缩或加密后再编码（如 AES+base64）：magic 找不到路径，需要先拿到密钥。
- 评分函数只看可打印比例与线索词，可能选中"能打印但无意义"的结果，需人工比对。
- 超大文件（>10 MB）逐层爆破较慢，建议先切片定位。

## 相关文档

- `kb/misc/cyberchef-and-tools.md`：主要来源，工具矩阵与常用配方。
- `kb/misc/encoding-auto-detect.md`：编码判据表与评分思路来源。
- `kb/_methods/enc_chain_decode.md`：已有的多层级解码链方法卡（本卡偏工具复刻）。
- `kb/forensics/steganalysis-workflow.md`：拿到图片后的下一步。

## 目录与收录说明

- 卡片：`kb/_methods/cyberchef-recipes.md`；脚本：`kb/_methods/scripts/cyberchef_recipes.py`。
- 对应 backlog 项 `cyberchef-recipes`（category=misc），源文档
  `kb/misc/cyberchef-and-tools.md`、`kb/misc/encoding-auto-detect.md`。
