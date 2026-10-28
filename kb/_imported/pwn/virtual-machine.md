---
title: "virtual machine"
category: pwn
tags: [UCATFLAGS 2024, wp prose]
signals: [virtual machine]
difficulty: medium
source: "https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/pwn/virtual_machine-wp.md"
tools: []
origin: imported
origin_id: official-91e278a332af5979d93d38
origin_sha256: f9ac6abb6ee2d97030bd6370508df10af87982c49729fefad3130e84a62e7a60
origin_event: "UCATFLAGS 2024"
origin_kind: wp_prose
license: "not_declared"
updated: 2026-10-23
---
# UCATFLAGS 2024 / virtual machine

> 来源：UCATFLAGS 2024  |  类型：wp_prose  |  https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/pwn/virtual_machine-wp.md

# virtual machine

## 预分析

返回

没有 `canary` ，`got` 表可写，开启地址随机化保护。

运行一下


附件中还给了一个 `libc.so.6` 的动态链接库，用 `strings` 查看其版本


返回


我们可以根据这个版本信息去搭建本地环境（当然，这不是刚需，尤其是你觉得不需要调试的时候）。搭建这个环境的作用是使得各函数在 `libc` 库中的**偏移**与服务端一致。

配置本地调试环境大家可以自行查询，关键词： `glibc-all-in-one` `patchelf` 

接下来使用 `ida64` 进行分析

## 逆向程序

根据题目提示，这是一台虚拟机，也可以在ida函数界面看到一些像是汇编指令一样的函数名，如 `jmp` `call` `push` 等。

观察 `main` 函数的主体部分，发现先是调用 `exec` 函数，传入了两个字节流，下面又将我们的输入传给 `exec` 函数，所以进入这个函数查看。


`a1` 由我们上面的分析，应该是要执行的命令的字符串， `a2` 现在还不知道，可以进入 `load_text` 查看。


发现是将 `a1` copy 到 `&unk_7300` ，copy的字节数是 `a2` ，所以 `a2` 的含义应该是 `a1` 的长度，`exec` 原型应是 `exec(char* a1, uint8_t a2)` ，观察 `main` 函数，发现其实没有关于此处的漏洞。

`exec` 函数的前一部分是将一些东西初始化为0 ，主要分析后面三个函数 `load_ftable` `load_text` `exec_text`

下面是 `load_ftable` 


`load_ftable` 函数将一些函数地址写入了 `bss` 段的变量里。这些函数的功能在这里就不赘述了，主要是实现一些类似汇编指令的功能。从这些函数的分析中，我们可以看到一些被经常使用的变量，如 `r6` ，而且它自增的值似乎与**函数的参数个数**有关，可以推测其功能应该类似于 `eip` 寄存器。

`load_text` 只是进行了一个拷贝。


下面是 `exec_text` 函数

{% raw %}
{% endraw %}


`exec_text` 函数中可以发现一个经常出现的变量 `byte_7300[(unsigned __int16)r6]` ，整个函数的大体含义是根据 `byte_7300[(unsigned __int16)r6]` 的值，执行 `&sysmm[4 * (unsigned __int8)byte_7300[(unsigned __int16)r6] + 4480])` 处的函数，不同条件函数传入的参数不同。

那么这个函数指针与之前那么多函数有什么关系呢？

`&sysmm` 的类型是 `_WORD` ，所以函数指针的地址应为


其中 `sysmm` 的偏移为 `0x0000000000005100` ，与后面相加为


这便是函数指针的地址。

至于 `byte_7300` ，可以从函数 `load_text` 中看到，这是从我们的输入拷贝过来的，也就是说我们的输入决定了程序调用那个函数指针，而调用规则则由 `load_ftable` 函数进行加载。而且，这更加印证了 `r6` 相当于虚拟机的 `ip` 寄存器。

再分析这些函数调用的参数是什么。

发现与 `(unsigned __int8)byte_7300[(unsigned __int16)r6] + 4480]` 有如下对应关系（改写成c）


这里，我们其实可以结合前面的函数注意到，`ra` 实际上是一个指针数组，其内部储存着 `r0 ~ r7` 的地址。所以这里（`(&ra)[(unsigned __int8)byte_7300[(unsigned __int16)r6 + 1]]`）其实存在一个**数组越界漏洞**，即我们的输入值可以大于 `ra` 的最大索引 `7` ，从而实现一些事情。 

## 漏洞利用

首先，这个程序依据我们的输入，调用不同的函数指针，执行不同的代码，那么我们可以通过更改或向对应位置写入函数指针再通过输入调用该函数，便可实现函数的执行。

然后，我们要想利用 `libc` 中的 `system` 函数，需要泄露程序的 `libc` 基址，这就需要我们泄露 `got` 表中的值，但由于地址随机化，我们要想知道 `got` 表的地址，就需要知道程序加载的基址。显然的，`bss` 段上已经有一些已储存的函数指针，他们都指向 `text` 段，可以泄露程序基址。（使用函数`pac`，它能打印依据 `sysmm` 偏移的字节）

于是我们可以像编写汇编代码一样编写本虚拟机的代码。下面附上各函数的**指令**如下（即上面的 `one_byte` 值）：


于是，我们可以编写代码


上面代码通过循环实现了打印 `nop` 这个函数指针，这个指针减去 `ida` 中可以查看到的偏移即为程序基址


这段代码主要实现了将 `puts` 的 `plt` 表地址复制到指令 `0x2c` 所对应的内存处，即程序中变量 `puts_f_addr_r` ，再调用 `puts` 函数打印出 `putchar` 的 `got` 表，从而泄露 `libc` 基址。


这段代码现将计算得到的 `system` 函数地址写入 `0x2c` 指令所在地址，在调用该函数，实现 `getshell` 。这里同样利用了和 `payload2` 一样的**数组越界漏洞**（`ra`数组）

下面是完整exp


## 程序源码

`vm.c`

{% raw %}
{% endraw %}

`registers.c`


`registers.h`


`operator.c`


`operator.h`


`memory.c`

{% raw %}
{% endraw %}

`memory.h`


编译


编译环境

ubuntu20.04标准镜像
