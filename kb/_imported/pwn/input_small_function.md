---
title: "input_small_function"
category: pwn
tags: [NewStar CTF 2025, wp prose]
signals: [input_small_function, pwntools]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week2/pwn/input-small-function.md"
tools: []
origin: imported
origin_id: official-76b89c72e27af373a1b20a
origin_sha256: 7a144d46b25dc51785fefcfdbf20fd4bc56c22cd6dc2996e7603ecec86471279
origin_event: "NewStar CTF 2025"
origin_kind: wp_prose
license: "MIT"
updated: 2026-10-23
---
# NewStar CTF 2025 / input_small_function

> 来源：NewStar CTF 2025  |  类型：wp_prose  |  https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week2/pwn/input-small-function.md

import Container from '@/components/docs/Container.vue'

# input_small_function


本题考查 shellcode 的进阶利用。

这道题目是 input_function 的延续，我们把可执行文件用 IDA 打开，查看 `main` 函数：

〔原图省略〕

这一道题目仍然考查 shellcode，但是对读入字符数做出了限制，同时存在一个 `clear` 函数，我们查看一下 `clear` 函数的内容。

〔原图省略〕

看上去就只是返回了 0，但是我们看汇编代码。

〔原图省略〕

可以看到程序清空了 `rax`，`rbx`，`rcx`，`rdx`，`rdi`，`rsi`，`r8`-`r15`寄存器，因此此时程序中仅有 `rbp`，`rsp`，`rip` 三个寄存器没有被清空。

〔原图省略〕

随后程序返回 `main` 函数之后，将 shellcode 开始的地址放入 `rdx` 中，随后执行 `call rdx` 以执行 shellcode。

〔原图省略〕

由于存在 shellcode 字符数限制，因此直接使用 pwntools 生成的 shellcode 会由于长度过长而导致失败，一般情况下我们有以下的两条思路。

## 思路一：shellcode 优化

我们先考虑对 shellcode 进行优化。

首先我们写出最简单的 shellcode：


这个 shellcode 是最简单最直观的，但是汇编出来是 29 字节，长度过长，我们以这个为基础进行优化。

在 gdb 中我们可以看到，程序在进入 shellcode 之前清空了除了 `rsi` 等寄存器，因此即使我不使用 `xor rsi, rsi`，`rsi` 寄存器也是 0，因此可以直接删去这一行。

同时，由于 `rax` 也被清零，所以将 `rax` 赋值为 59，下面几行汇编指令均可以达到目的：


汇编之后的机器码如下，可以看到字符数最少的语句是 `mov al, 0x3b`，仅为 2 字节。


随后，我们需要知道，`push 寄存器`和 `pop 寄存器`的字符数均为 1，因此 `mov rdi, rsp`<span data-desc>（3 字节）</span>可写为 `push rsp ; pop rdi`<span data-desc>（2 字节）</span>，这样还能节省 1 字节。

`xor rdx, rdx` 为 3 字节，但是 `xor edx, edx` 仅为 2 字节也可以达到清空寄存器的目的。

优化完的 shellcode 如下：


> [!info]
> 将 `xor edx, edx` 写成 `cdq` 还可以再节省 1 字节的空间

最终的脚本如下：


## 思路二：构建 `read` 再次读入

其实还有种思路，既然执行 shellcode 的时候，shellcode 所处段还是可读可写可执行的状态，并且 `rdx` 中还存储着此段的地址，那么可以考虑通过 shellcode 构建一个 `read`，通过这个 `read` 再次读入 shellcode，即可绕过 `main` 函数中 `read` 对于字节大小的限制。

相当于是要分两次写入两段 shellcode，第一段 shellcode 调用 `read` 函数以读入第二段 shellcode，通过第二段 shellcode 拿到 shell
