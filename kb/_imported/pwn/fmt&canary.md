---
title: "fmt&canary"
category: pwn
tags: [NewStar CTF 2025, wp prose]
signals: [fmt&canary]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/pwn/fmt-canary.md"
tools: []
origin: imported
origin_id: official-7979b77716ef308ef36b53
origin_sha256: e521ae1de0f63343571ab73ad3e816f15ecbe7c4b4374f739d9906732d1a3fea
origin_event: "NewStar CTF 2025"
origin_kind: wp_prose
license: "MIT"
updated: 2026-10-23
---
# NewStar CTF 2025 / fmt&canary

> 来源：NewStar CTF 2025  |  类型：wp_prose  |  https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/pwn/fmt-canary.md

import Container from '@/components/docs/Container.vue'

# fmt&canary


本题考查格式化字符串漏洞泄露 canary 以及 ret2libc。

在开始做这道题之前，需要对 canary 有基础了解，可以参考：

- [Canary 实现原理](https://ctf-wiki.org/pwn/linux/user-mode/mitigation/canary/?h=canary)

从「实现原理」部分可以知道，canary 存放在 `ebp - 0x8` / `rbp - 0x8` 的位置。

首先使用 IDA 分析程序。

〔原图省略〕

程序提供无限次格式化字符串利用机会，第 21 行的 `read(0, s, 0x100u);` 存在溢出，因此需要先通过格式化字符串漏洞泄露 canary，最后进行 ret2libc。

按照惯例，需要像 Week 2 的「刻在栈里的秘密」那样找到 canary 所在位置对应的 `n`。打开 GDB，停在 `printf` 之前。

〔原图省略〕

可以看到 `rbp - 8` 的位置就是 canary，也可以在 GDB 中输入 `canary` 进行验证。

〔原图省略〕

这里使用 `dist <canary 所在栈地址> $rsp` 计算该位置与栈顶之间的偏移：


这样即可得到 canary 所在位置与栈顶之间的距离，最后手动加上 6 即可。泄露 canary 后，接下来需要泄露 libc。这里有两种方式：

1. 输入某个函数的 GOT 地址，配合 `%s` 泄露 GOT 内容。

例如 `%7$s` 对应的就是 `puts@got` 的地址。
〔原图省略〕

2. 直接泄露栈上残留的 `__libc_start_call_main`

〔原图省略〕

该方式与泄露 canary 的方式一致，但要计算 libc 基地址还需要额外处理。

首先在 GDB 中使用 `vmmap` 命令查看程序各段的地址和范围，其中包括 libc 基地址。栈上残留的 `__libc_start_call_main+128` 与 libc 基地址之间的偏移是固定值，因此只要泄露 `__libc_start_call_main+128`，即可计算 libc 基地址。
〔原图省略〕
该方法的前提是本地已经 patch 对应版本的 libc 和 ld。相关操作可以参考 [patchelf 的功能以及使用 patchelf 修改 rpath 以解决动态库问题](https://blog.csdn.net/Longyu_wlz/article/details/108550528)。

泄露出了 libc，最后就是溢出打 ret2libc 了。
程序中没有 `pop rdi; ret` 这个 gadget，但 libc 中通常存在。由于已经泄露 libc 基地址，因此可以在 libc 中查找所需 gadget。注意需要将 `canary` 放回 `rbp - 8` 的位置，否则会触发栈溢出检测。

下面给出 EXP：
