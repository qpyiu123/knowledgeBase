---
title: "Turtle：图像与海龟绘图实现的虚拟机"
category: reverse
tags: [wp prose translation]
signals: [Turtle：图像与海龟绘图实现的虚拟机, Python]
difficulty: medium
source: "https://github.com/google/google-ctf/blob/f683ff991cac26f7673d2f2de5ac9d226b95b847/2023/quals/rev-turtle/solution/README.md"
tools: []
origin: imported
origin_id: gctf-2023-rev-turtle
origin_sha256: 30b472994ef4c7b9fc9514c6719092c1814a9f788a9e6f5e4cc55d30a65b9981
origin_event: ""
origin_kind: wp_prose_translation
license: "Apache-2.0"
updated: 2026-10-23
---
# Turtle：图像与海龟绘图实现的虚拟机

> 来源：https://github.com/google/google-ctf/blob/f683ff991cac26f7673d2f2de5ac9d226b95b847/2023/quals/rev-turtle/solution/README.md

# Google CTF 2023 — Reverse：Turtle 题解

注意：本题解由内部测试中的题目测试者撰写。

题目给出一个使用 turtle 的 Python 脚本，类似 LOGO 语言。它先画出两张题目同时提供的 PNG 图。

可以发现程序创建了四个 turtle：

- mTurt 先画出 25×21 的矩形，大部分来自 m.png；顶部放入用户提供的 flag，以像素颜色表示。
- sTurt 在左边画一条细长的粉色线。
- rTurt 在右边画一个 3×3 点阵。
- cTurt 画出 9×86 的图 c.png。

检查代码，会发现 run 函数中有明显的分派循环。这些 turtle 似乎实际实现了一种虚拟机。仔细阅读后，可以确定各自的用途：

- mTurt 是内存，由 m.png 和候选 flag 初始化。
- sTurt 是栈，用来保存局部变量和二维返回地址。
- rTurt 读写寄存器，最后三个是条件标志，分别表示相等、小于、大于。
- cTurt 从 c.png 读取代码。

作者在 disas.py 中实现了该虚拟机的反汇编器。代码只包含若干 CALL，它们都指向图像最顶端。这意味着每隔三列就是一个独立函数，因为操作码的宽度为三个像素。

以下是 disas.py 的原始输出：

〔原文代码块 1 未收录。〕

每一列是一个独立函数，第一个是主入口。作者将伪汇编改写成更易读的形式：

〔原文代码块 2 未收录。〕

第一个函数检查 flag 中的字符是否互不相同，随后调用第二个函数，再反复调用第三个函数。

第二个函数根据 m.png 第 65 至 94 个像素中硬编码的排列，对 flag 字符进行置换。

第三个函数最长。它实现了类似二分查找的过程；每次调用都断言当前比较结果应是什么。该预期结果用 1 至 4 的数表示，同样硬编码在 m.png 中，从第 95 个像素开始。

作者编写 solve.py，使用 m.png 模拟二分查找；当硬编码比较结果表示“相等”，也就是找到目标时，保存相应字符。然后利用硬编码排列逆转 flag 缓冲区，得到正确结果。由于 turtle 中只使用花括号内的部分，还需要补上 `CTF{...}` 包装：

`CTF{iT5_E-tUr+1es/AlL.7h3;waY:d0Wn}`
