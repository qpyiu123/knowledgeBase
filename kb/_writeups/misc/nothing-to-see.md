---
title: "Nothing to See：压缩包藏在 PNG 结束块之后"
category: "misc"
kind: "writeup"
tags: ["PNG 尾部附加", "ZIP", "文本元数据"]
signals: ["IEND", "tEXt", "Title"]
source: "https://github.com/TJCSec/tjctf-2023-challenges/tree/main/forensics/nothing-to-see"
origin_id: "r66-nothing-to-see"
relates_to: ["misc/zip-archive-tricks.md"]
verification: "本机原附件回验"
---

# Nothing to See：压缩包藏在 PNG 结束块之后

TJCTF 2023 · 杂项 · [赛事目录](https://github.com/TJCSec/tjctf-2023-challenges/tree/main/forensics/nothing-to-see)。本机用原图里的线索解开压缩包，读取了 39 字节的答案文件。

## 先看这一步

沿块长度读到 IEND，再检查后面的 ZIP。密码在外层图像 Title 字段，用完整字段值读取并核对 CRC。

**适用时**：能按块读到 PNG 结尾，后面的字节可独立当作 ZIP。 **留意**：不要只搜索文件里的 IEND 字符串。

先按 PNG 块的长度读到 `IEND`（结束块），不要只搜索字符串的位置。每块是长度、类型、内容和校验值；结束块的校验值之后，才是附加数据的起点。

这份文件的偏移 14751 开始是一段 228 字节的 ZIP。把这段数据独立交给 ZIP 读取器，目录里只有 `flag.txt`，加密位已设置。

密码线索还在外层图像：`tEXt`（文本元数据块）里有一项 `Title`。取分隔用的空字节之后的完整字段值，包括下划线，不要只取其中一半。用它读取内层文件，ZIP 的 CRC 校验通过，答案格式也正确。

遇到类似题时，优先查外层图像里留下的文字和元数据，再考虑其他密码来源。

## 配套代码

`kb/_code/r66/misc_samples.py`。从代码所在目录运行 `python misc_samples.py nothing-to-see 原附件`。依赖见脚本开头；运行后会显示核对结果。
