---
title: "[Binary] 完美的代码"
category: pwn
tags: [GeekGame 2024, wp prose]
signals: ["[Binary] 完美的代码", "Rust"]
difficulty: medium
source: "https://github.com/PKU-GeekGame/geekgame-4th/blob/a21d7f7387512ec7ef77720e998d60efa16f2353/official_writeup/binary-saferustplus/README.md"
tools: []
origin: imported
origin_id: official-fd4adc2d3ab44c09f392a5
origin_sha256: b3b5b1d331f103cf264b7e92b2dc0cbd5d91a1c1778270d6263a001e2a83631b
origin_event: "GeekGame 2024"
origin_kind: wp_prose
license: "not_declared"
updated: 2026-10-23
---
# GeekGame 2024 / [Binary] 完美的代码

> 来源：GeekGame 2024  |  类型：wp_prose  |  https://github.com/PKU-GeekGame/geekgame-4th/blob/a21d7f7387512ec7ef77720e998d60efa16f2353/official_writeup/binary-saferustplus/README.md

# [Binary] 完美的代码

- 命题人：lrh2000
- 发现：400 分
- 解密：300 分

## 题目描述


**[【附件：下载题目源码（binary-saferustplus.zip）】](attachment/binary-saferustplus.zip)**

**【终端交互：连接到题目】**

## 预期解法

这题的出题思路是之前正常开发的时候突然蹦出来个段错误，十分疑惑，最后调试了下发现竟然是 Rust 编译器的问题。~~感觉可以用来注入后门，~~ 那不如先出道题吧。

### Flag 1：发现

怎么发现哪里有问题呢？首先题面暗示问题不在源代码里，但在编译之后的二进制文件里。预期解法：
 - 这题是个菜单题，但内部并没有维护复杂状态，其实本质不同的输入也就只有十几种或者最多几十种，手动全部尝试一遍就能发现异常了（如果输入离谱一点基本就段错误了）。懒得手动尝试也可以写个程序自动尝试，或者直接 fuzzing 。
 - 如果注意力惊人，也可以根据源代码猜一下问题在哪，比如定义了一堆 trait 并用了 `trait_upcasting` ，那么可能这块有问题概率比较大，然后去逆向二进制中对应模块。这个确实比较难，实际好像也没有选手是这么做出来的。

### Flag 2：解密

分析一下 Flag 1 中的段错误，可以看出是虚表错位，也就是调用 `put` 实际调用的是 `put_unchecked`，那么也就可以任意写入了。

正好栈上有个 `is_admin` 的布尔值，把它置为真，就可以任意读写内存，也可以泄漏 libc 里的地址。

不过这题 `main` 函数不会返回，所以不太好覆盖栈上的返回地址，但是堆上的虚表可以随便改。所以只要构造一个假的虚表，把里面的函数指针填成 `system`，就可以拿到 shell 或者执行 `cat ./flag2.txt` 了。

[利用程序：](sol/exp.py)


### 优秀选手解法

 - 下面的脚本可以秒出 Flag 1，参见清华大学选手 [Vursc 的 writeup](../../players_writeup/1273#binary完美的代码) （确实是“完美的解法”）：
> 完美的解法（出结果用不了一秒钟）：
>
> ```
> while
>     grep -ao '[0123]' /dev/urandom | tee in | ./run >/dev/null 2>err;
>     grep -q assert err;
> do :; done
> ```
 - 其实不利用 `is_admin` 也不调用 `system` 同样能拿 Flag 2，参见清华大学选手 [tony 的 writeup](../../players_writeup/700#完美的代码)：
> 而利用这点修改了别的`BoxedData`的data指针后，也就能任意位置读取了。
>
> [ .. ]
>
> 总之我采取了另一个方法，利用的是调用的虚函数的返回值是会打印出来的这一点，首先执行`open64(./flag2.txt, 0)`，返回值`fd`会被打印到命令行（其实不打印的话也大概率可以猜是3）。然后再调用`read(fd, buf, ...)`，当然，第三个参数是没法控制的，因为override的虚函数只有前两个参数，只好听天由命希望这个值足够大就行。事实上，确实work了，最后读取`buf`的内容就是flag2了。
