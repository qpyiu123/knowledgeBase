---
title: "不思議なscanf"
category: pwn
tags: [NewStar CTF 2024, wp prose]
signals: [不思議なscanf]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/pwn/scanf.md"
tools: []
origin: imported
origin_id: official-1d65ed20206c2055721718
origin_sha256: ae6195fd4abfd95202265808ff5d9b89e402e74230127c48725bc18e0f825d67
origin_event: "NewStar CTF 2024"
origin_kind: wp_prose
license: "MIT"
updated: 2026-10-23
---
# NewStar CTF 2024 / 不思議なscanf

> 来源：NewStar CTF 2024  |  类型：wp_prose  |  https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/pwn/scanf.md

# 不思議なscanf


程序定义了一个 int 类型的数组，并利用 for 循环用 scanf 向数组读入内容

但是 for 循环的次数是 16 次，已经超出了数组定义的范围，造成了数组越界

所以我们最终的目的就是利用这个数组越界修改 `main` 函数的返回地址

〔原图省略〕

〔原图省略〕

:::tip
`scanf` 时使用的参数 `%d`：

正常输入时，输入为范围在 $[-2^{31}, 2^{32}-1]$ 内的整数。

如果输入范围在 $[-2^{63}, 2^{63}-1]$ 内的整数，则会截断高位读取，此范围是 `long long int` 的范围。

如果输入范围在 `long long int` 范围之外，则统一将参数赋值为 $-1$（0xFFFFFFFF）。

如果输入为非数字，分为下列情况：

1. 如果输入仅有一个，则该输入无效，该值不变；
2. 如果输入有数字前缀<span data-desc>（如 `12345abcd`）</span>，则 `scanf` 仅会读取前面的数字，从第一个非数字开始，后面全部舍弃<span data-desc>（`12345`）</span>；
3. 如果输入有多个且使用一个 `scanf` 语句<span data-desc>（如 `scanf("%d, %d", &a, &b)`）</span>，输入第一个非数字后，后面的所有输入均为无效，前面的输入可以赋值；
4. 如果输入有多个且使用多个 `scanf` 语句<span data-desc>（含循环，即一个 `scanf` 中仅有一个输入）</span>，则输入非数字时，如果输入的不是 `+` 或 `-`，则后面紧跟的所有 `scanf` 均自动跳过，变为无效，不能输入。如果输入的 `+` 或 `-`，则会跳过当前输入，后面仍然可以进行输入。

—— 摘抄自：[以 Pwn 视角看待 C 函数 —— scanf](https://blog.csdn.net/qq_54218833/article/details/121308367)
:::

这里我们需要利用 `scanf` 多次输入的特性，通过输入字符 `+` 来跳过对 Canary 的修改，进而直接修改返回地址为后门地址。
