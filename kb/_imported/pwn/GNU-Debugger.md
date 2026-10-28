---
title: "GNU Debugger"
category: pwn
tags: [NewStar CTF 2025, wp prose]
signals: [GNU Debugger]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week1/pwn/gnu-debugger.md"
tools: []
origin: imported
origin_id: official-a7e6a2491913eee8acde0b
origin_sha256: 25a4509b5a5a9d8aac7b20d26331937f972b5706f786f018b08d928b81aace03
origin_event: "NewStar CTF 2025"
origin_kind: wp_prose
license: "MIT"
updated: 2026-10-23
---
# NewStar CTF 2025 / GNU Debugger

> 来源：NewStar CTF 2025  |  类型：wp_prose  |  https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week1/pwn/gnu-debugger.md

import Container from '@/components/docs/Container.vue'

# GNU Debugger


本题考查 GDB 的的使用。

本题开始之前，你可以先参考 [0x01. Pwn 环境搭建](/learn/pwn.html) 来搭建做题环境。若已经安装好 pwndbg<span data-desc>（pwndbg 是一个集成到 GDB 调试器中的插件）</span>，这里建议使用最原始的 gdb 来完成这道题目。

进入题目附件所在目录，直接运行程序以开始，这里仅对预期解法进行说明。


输入 `run <ip> <port>` 开始游戏，其中 `ip` 和 `port` 通过开启容器得到。

:::tip 举例

首先要做的就是开启题目容器。

〔原图省略〕

nc 后面的 `8.147.132.32` 就是 IP，而 `39543` 则是端口，使用 `run 8.147.132.32 39543` 命令开始游戏。

:::

## 关卡 1：已验丁真


需要查看 r12 寄存器的值，这里有很多方法，简单列举其中两个：

1. `info r`：显示所有寄存器的值，包括 16 进制以及 10 进制
2. `p/x $r12`：`p` 指打印，`x` 指 16 进制的形式，`$` 指后面的是寄存器

〔原图省略〕

复制后使用 continue 指令 `c` 让程序继续执行，随后提交即可。

## 关卡 2：义眼丁真


这关使用 `x` 指令来查看内存，使用 `x/` 后面加上不同的参数就能用不同的形式来展示内存，这里稍微列举一些：

- `x` 按十六进制格式显示变量。
- `o` 按八进制格式显示变量。
- `s` 按字符串显示。
- `i` 显示汇编指令。

使用 `x/s 0x555555557c27` 查看对应字符串即可。

〔原图省略〕

## 关卡 3：犹豫丁真


这关需要给函数下一个断点，使用 break 指令 `b` 即可，注意使用时需要在地址前加上 `*` 来告诉 GDB 这是一个地址，使用指令：`b *0x555555555779`.

## 关卡 4：应用丁真


这关使用 `set` 指令来修改数据，同样需要在地址前加上 `*` ，使用指令 `set *0x7fffffffdd04  = 0xdeadbeef` 即可，最后使用 `c` 命令让程序继续执行就能看到 FLAG 了。
