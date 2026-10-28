---
title: "[Algorithm] 随机数生成器"
category: pwn
tags: [GeekGame 2024, wp prose]
signals: [[Algorithm] 随机数生成器, Python, Go]
difficulty: medium
source: "https://github.com/PKU-GeekGame/geekgame-4th/blob/a21d7f7387512ec7ef77720e998d60efa16f2353/official_writeup/algo-randomzoo/README.md"
tools: []
origin: imported
origin_id: official-f77c49777f3b961a35b367
origin_sha256: 2b84710d6b9d59758e73b376386b2bf7cb0eb3c151ef2db7ef2cbc864af5627c
origin_event: "GeekGame 2024"
origin_kind: wp_prose
license: "not_declared"
updated: 2026-10-23
---
# GeekGame 2024 / [Algorithm] 随机数生成器

> 来源：GeekGame 2024  |  类型：wp_prose  |  https://github.com/PKU-GeekGame/geekgame-4th/blob/a21d7f7387512ec7ef77720e998d60efa16f2353/official_writeup/algo-randomzoo/README.md

# [Algorithm] 随机数生成器

- 命题人：debugger
- C++：150 分
- Python：200 分
- Go：200 分

## 题目描述


**[【附件：下载题目源码（algo-randomzoo.zip）】](attachment/algo-randomzoo.zip)**

**【终端交互：连接到第一关（C++）】**

**【终端交互：连接到第二关（Python）】**

**【终端交互：连接到第三关（Go）】**

## 预期解法
注意：本题还有其他解法，可见选手wp。此处仅给出出题人的解法。

此题给了一个程序，可以生成一串随机数，但是其中每个随机数都加上了flag的一个字节。

### C++
C++程序用了srand初始化随机数种子。因为srand的参数是32位整数，直接枚举即可。参见sol/exp1.cpp。

C++使用的LFG随机数生成器也是可以预测的，预测方法和下面Go一节类似，这里不再给出具体实现。

### Python
Python的随机数是用MT19937生成的，一个块（32 bit）的值只与它之前第 624、623、227 个块有关。我们不知道每个块的具体值，但是知道tempering之后再加上flag字节的值，所以可以枚举两个块对应的flag字节，从而得到可能的原始的块的具体值。可以尝试改变每个块的tempering之后的值，看看对预测结果有什么变化：

从这个程序的运行结果可见，改变v_623对预测结果的影响显著大于v_227，或者说其实只要知道某个块和前面第623、227个块加上flag字节并tempering后的结果，就能得到前面第623个块对应的flag字节。如果假设每个块都是可见字符，每个字符需要枚举量不超过128^3。参见sol/exp2.py。
### Go

Go里面随机数用的是64位的块，且每个块等于前面第607和第273个块的和（舍弃进位）。接着int63会把最高位加到最低位，得到63位随机数。uint32只取int63的最高32位。

设第i个uint32为`random[i]`，有`random[i-273]+random[i-607]-random[i]`为0、-1、2^32、2^32-1之一。再设`flag[i]`为flag的第i个字节（循环），则生成的数为`nums[i]=random[i]+flag[i]`，从而`(nums[i-273]+nums[i-607]-nums[i]+c)%2^32=(flag[i-273]+flag[i-607]-flag[i]+c-k)`，其中c为某个数使得`flag[i-273]+flag[i-607]-flag[i]+c`永远大于0，k为0或1。`(nums[i-273]+nums[i-607]-nums[i]+c)%2^32`是一个大约以flag长度为周期的数列，可以用auto correlation等方法找出其周期（直接试也行）。找出周期（设为n）后，可以列出`flag[(i-273)%n]+flag[(i-607)%n]-flag[i%n]`的方程组并解出flag。参见sol/exp3.py。
