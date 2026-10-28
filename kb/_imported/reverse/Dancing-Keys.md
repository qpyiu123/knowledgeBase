---
title: "Dancing Keys"
category: reverse
tags: [NewStar CTF 2025, wp prose]
signals: [Dancing Keys]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week4/reverse/dancing-keys.md"
tools: []
origin: imported
origin_id: official-8bad5c781664b50999dca6
origin_sha256: f77484e6496f52b08b5a8fea373819c1c8b5aa952fe6ac27295253e00094bd24
origin_event: "NewStar CTF 2025"
origin_kind: wp_prose
license: "MIT"
updated: 2026-10-23
---
# NewStar CTF 2025 / Dancing Keys

> 来源：NewStar CTF 2025  |  类型：wp_prose  |  https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week4/reverse/dancing-keys.md

# Dancing Keys

### 分析程序逻辑

查看程序的 main 函数：


我们发现，main在开头给4个dword进行了赋值，随后在 `sub_4015EB` 中使用了这组dword，作为加密的密钥，我们查看这个函数：


发现是一个初始sum值不为0，delta为随机值的魔改TEA加密，那么之前的4个连续dword自然就是密钥了，`sub_40132B` 和 `sub_4013F3` 则是将byte与dword互相转化的函数。

但是实际动态调试时我们发现，key似乎并不是这个初始化的值，且 `sub_40132B` 和 `sub_4013F3` 不是标准的大/小端序转换，而是进行了自定义的重排：


除此之外，经过细心观察似乎还能发现，key的值貌似是会变化的，与函数上打入的断点密切相关，因此可以猜测这是某种反调试逻辑；另一方面，如果delta是随机值，则几乎大概率在其之前有一个 `srand(seed)` 来设置随机数种子，但我们查看所有的函数，发现并没有srand函数的引入，rand函数也不是粉色的库函数，我们查看rand的实现：


原来这个rand函数是一个自实现的随机函数，`dword_404060` 则是全局的随机数种子，我们查看其交叉引用（xref），发现除了rand之外，其还在一个叫 `start_routine` 的函数中被引用，查看这个函数：


可以看到，`seed` 是将 `start` 函数开始的地址一直到某个偏移量（这里是程序 `.text` 段的结尾）位置的字节带入 `sub_40128A` 中生成的，且 `start_routine` 同时还修改了 `dword_404070`（也就是密钥）的值，查看 `sub_40128A`：


这是一个自实现的简单校验函数，将程序的整个 `.text` 段的所有字节计算一个哈希，并加入了反调试逻辑。打入函数上的断点实际上改变了运行的程序在内存中的字节，因此如果断点的位置、数量等不同，每次生成的 `key` 值也会不同。

那么 `start_routine` 这个函数究竟是什么时候被调用的呢？动态调试可以发现其是在 `main` 之前被调用的。查看其 xref，有一个函数 `sub_401590` 调用了它：


这个函数创建了一个线程，使其与 `main` 同时运行。`start_routine` 中的 `sleep(1)` 用于等待 `main` 中的 key 初始化赋值。`sub_401590` 的 xref 位于 `.init_array` 段；在 ELF 文件中，该段中的函数会先于 `main` 执行，因此这就是 key 被篡改的原因。

既然存在反调试和哈希校验，还能否拿到密钥？

可以，这里有两种方法：

方法 1：在哈希生成函数中的 `ptrace` 处下断点。由于 `ptrace` 是库函数，其调用位置在 `.plt.sec` 段，在 `.text` 段上方，不在哈希函数的处理范围内，因此可以在其上打断点：


断在这里之后单步调试，或者直接运行到鼠标指针处（Run to cursor）：


在这里观察 `rax` 寄存器，其值就是 `ptrace` 返回值，为 `0xFFFFFFFFFFFFFFFF`（-1）。将其改为 `0`，即可返回正确的哈希值。

方法 2：手动求哈希。使用十六进制编辑器或 IDA 直接 dump `.text` 段，再手动编写脚本求解哈希值。该方法较繁琐，且不容易确认结果正确性，更适合作为辅助验证手段。

### 实现加密解密

得到哈希后，就可以复现并逆向程序的加密逻辑。先对 byte 与 dword 互相转换的函数进行逆向：


然后复现正向加密逻辑并编写逆向脚本（这里也包含手动求哈希的方法）：


确认输出与程序比较时的结果相同后即可解密。需要注意以下几点：

1. 需要重新计算一次哈希值，确保使用的种子一致，并且要手动调用 4 次 `rand` 来模拟修改密钥时的 `rand` 行为。

2. 注意 `sum` 值的起始值，加的不是 `轮数 * delta`，因为每轮加的是 `i * delta` 而不是 `delta`。

3. 注意每组解密时轮数需要倒序，直接正向解密是错误的，因为 `sum` 每次变化的值与轮数有关。

解密脚本：


FLAG：
