---
title: "[Binary] 大整数类"
category: pwn
tags: [GeekGame 2024, wp prose]
signals: [[Binary] 大整数类, SageMath]
difficulty: medium
source: "https://github.com/PKU-GeekGame/geekgame-4th/blob/a21d7f7387512ec7ef77720e998d60efa16f2353/official_writeup/binary-bigint/README.md"
tools: []
origin: imported
origin_id: official-42edc64b1dee3c0d6446d0
origin_sha256: 774ee8a6af28ac07c66e9a233b3138d1b4e32f19e93e37b6773c22cd357d1941
origin_event: "GeekGame 2024"
origin_kind: wp_prose
license: "not_declared"
updated: 2026-10-23
---
# GeekGame 2024 / [Binary] 大整数类

> 来源：GeekGame 2024  |  类型：wp_prose  |  https://github.com/PKU-GeekGame/geekgame-4th/blob/a21d7f7387512ec7ef77720e998d60efa16f2353/official_writeup/binary-bigint/README.md

# [Binary] 大整数类

- 命题人：debugger
- Flag 1：350 分
- Flag 2：300 分

## 题目描述


**[【附件：下载题目附件（binary-bigint.zip）】](attachment/binary-bigint.zip)**

**[【附件：下载带符号的题目附件（binary-bigint-new.zip）】](attachment/binary-bigint-new.zip)**

## 预期解法

此题是一个用Pascal写的大整数模板，实际上是用从网上随便找的一个版本简单改写得到的。

预期需要选手完成以下步骤：
* 找到主函数（通过搜索字符串即可知道主函数）。
* 知道字符串的存储格式（第一个字节表示长度）。
* 因为没有符号，选手需要区分哪个函数是内置的库函数，哪个是真正用来处理字符串的函数。
* 知道了处理字符串的函数之后，分析出哪个是大整数比较、加法、减法、乘法的函数，以及字符串转大整数的过程。注意没有用于判断相等的函数，而是用x<=y且y<=x来判断x和y是否相等。
* 还原出程序的大整数操作。

Flag 1会把输入的flag拆成3个部分，然后每个部分转成整数都调用一个函数，三个调用都返回true则返回Flag正确。而checkflag1函数会计算一个大整数的三次函数，三次方程有三个根，选手需要把系数提取出来，然后有众多工具（SageMath、sympy、Mathematica均可）可以得到方程的根。

Flag 2会把flag转成整数后自乘16次再和flag相乘，每步操作后都和一个常数m取余，最后把结果和另一个常数v比较。这里实现了一个RSA。使用<a target="_blank" rel="noopener noreferrer" href="https://github.com/RsaCtfTool/RsaCtfTool">RsaCtfTool</a>可以把m分解。此后还原回flag是显然的。

本题旧版本还有一个Flag 3（后来因为flag太多而且程序也无法给出反馈删了），输入flag后会计算flag^2+m，然后直接退出。实际上m可以分解成两个素数k+flag和k-flag的积，如果你输入的flag是正确的计算出来的结果会是平方数，但是这个模板没有开平方根的功能。这也是Fermat分解方法的原理：当两个素数大小接近时，你可以先找到比m大的最小平方数，然后减去m，如果得到的是平方数，那么m是两个平方数的差，因此可以分解。
