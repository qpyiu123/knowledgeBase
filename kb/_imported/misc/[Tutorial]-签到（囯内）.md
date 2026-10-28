---
title: "[Tutorial] 签到（囯内）"
category: misc
tags: [GeekGame 2024, wp prose]
signals: [[Tutorial] 签到（囯内）, Python]
difficulty: medium
source: "https://github.com/PKU-GeekGame/geekgame-4th/blob/a21d7f7387512ec7ef77720e998d60efa16f2353/official_writeup/tutorial-signin/README.md"
tools: []
origin: imported
origin_id: official-0180df82bf9a6d5ccc2842
origin_sha256: 999466192cbc91289182ecfea600ba99c8b7d7b8e8534f746b9f47b1265e2374
origin_event: "GeekGame 2024"
origin_kind: wp_prose
license: "not_declared"
updated: 2026-10-23
---
# GeekGame 2024 / [Tutorial] 签到（囯内）

> 来源：GeekGame 2024  |  类型：wp_prose  |  https://github.com/PKU-GeekGame/geekgame-4th/blob/a21d7f7387512ec7ef77720e998d60efa16f2353/official_writeup/tutorial-signin/README.md

# [Tutorial] 签到（囯内）

- 命题人：xmcp
- 题目分值：100 分

## 题目描述


**[【附件：下载题目附件（tutorial-signin.zip）】](attachment/tutorial-signin.zip)**

## 预期解法

本关考验你熟练使用电脑的功夫。

下载附件的 ZIP 之后，发现 ZIP 里面有三个 ZIP，每个 ZIP 又有三个 ZIP，如此套娃得到 `3**4 == 81` 个 .txt 文件，如最外层的 README.txt 所说，只有其中一个文件里有 Flag。

假设你用 7-Zip File Manager 打开压缩包，这个软件的 GUI 并不怎么好用，但贵在响应速度很快，操作不拖泥带水。接下来让我们复习一下小学计算机课的内容：

- 按 Space 可以在文件列表里选中当前项
- 按上下方向键可以在文件列表里移动
- 按回车键可以打开选中的项
- 按退格键可以回到上一级目录
- 按 Alt+F4 可以关闭窗口

把这些操作合在一起，我们可以打出丝滑小连招，在 71 秒内遍历完所有 .txt 文件（遍历到含有 Flag 的文件为止则不需要这么长时间，具体取决于你的运气）。请看 VCR：

https://github.com/user-attachments/assets/897144b1-bb33-4d6e-bf01-5d815c4be757

Peppy 说，完成上述这些操作仅需 21pp。是不是非常简单呢？

当然，打不出来这番操作也没关系，可以 <del>打开 `sol/tutorial-signin.osz` 多练</del> 写个 Python 或者 Shell 脚本自动解压一下，然后找到 Flag。比如 `sol/exp.py`。

有一些人对今年签到题不玩 PDF 了感到遗憾，其实 PDF 并非消失了，而是 [转移到了 Web 分类](../web-copy)（x

## 花絮

题目里的以下这几条文本是我手写的：


其他文本则全都是用 GPT-4o-mini 生成的，Flag 里面的 G 开头的形容词也是 GPT-4o-mini 生成的（人工排除了一些明显不对劲的词）。

〔原图省略〕
