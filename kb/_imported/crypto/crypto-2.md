---
title: "crypto"
category: crypto
tags: [网鼎杯 2024, licensed blog wp prose]
signals: [crypto]
difficulty: medium
source: "https://dexterjie.github.io/2024/10/31/%E8%B5%9B%E9%A2%98%E5%A4%8D%E7%8E%B0/%E7%BD%91%E9%BC%8E%E6%9D%AF/"
tools: []
origin: imported
origin_id: cn-blog-dexter-b5032e4d-1
origin_sha256: 094076eff1a9ac4fddfefef744bb623e98cc2e01782ec6baee4393dfd84118ea
origin_event: "网鼎杯 2024"
origin_kind: licensed_blog_wp_prose
license: "CC-BY-NC-SA-4.0"
updated: 2026-10-23
---
# 2024网鼎杯 / crypto

> 来源：网鼎杯 2024  |  类型：licensed_blog_wp_prose  |  https://dexterjie.github.io/2024/10/31/%E8%B5%9B%E9%A2%98%E5%A4%8D%E7%8E%B0/%E7%BD%91%E9%BC%8E%E6%9D%AF/

2024网鼎杯

      发表于

      2024-10-31

      更新于
      2025-10-07

      阅读次数：

    Waline：

      本文字数：
      6.6k

      阅读时长 ≈
      24 分钟

    记录2024网鼎杯Crypto部分题解

青龙组

Crypto01

task.py

和2023领航杯复赛的bd一模一样，之前有记录过，可以看我的这篇博客2023江苏省领航杯 | DexterJie’Blog

exp

这个脚本是基于人家实验的，有点乱

跑出d之后解RSA

Crypto02

task.py

首先是ECDSA签名k的复用，原理如下$$s_1 \equiv k^{-1}(z_1 + r_1d_A) \mod n$$

$$s_2 \equiv k^{-1}(z_2 + r_2d_A) \mod n$$

这里$r_1 = r_2$，所以两式相减有$$s_1 - s_2 \equiv k^{-1}(z_1-z_2) \mod n$$所以$$k \equiv (z_1-z_2)\times (s_1-s_2)^{-1} \mod n$$有了k之后根据$s\equiv k^{-1}(z + rd_A)\mod n$就可以恢复$d_A$

然后解CBC得到victory_encrypted_flag

再根据加密逻辑写一个解密代码即可，最后把大写符号改为小写符号

exp

白虎组

Crypto01

task.py

这题主要是encrypt中14轮的迭代，逐一分析

可以知道和就是单纯的置换。可以把置换用矩阵的形式表达$$P(x) =\begin{pmatrix}P_{1,1} & … & P_{1,64}\\\vdots & \ddots & \vdots \\P_{64,1} & … & P_{64,64}\end{pmatrix}\times\begin{pmatrix}x_1 & … & x_{64}\end{pmatrix}$$

这样就用矩阵的形式等效替代了原来的

同理就很简单了，用$P^{-1}$乘上$x$向量就好了

接下来分析

这里的x3其实等效于

此时中只有和两个运算。我们可以用GF(2)下的矩阵乘法表示，用GF(2)下的加法表示，那么就有$$S(x) =\begin{pmatrix}A_{1,1} & … & A_{1,64}\\\vdots & \ddots & \vdots \\A_{64,1} & … & A_{64,64}\end{pmatrix}\times\begin{pmatrix}x_1 & … & x_{64}\end{pmatrix}+\begin{pmatrix}b_1 & … & b_{64}\end{pmatrix}$$

目前为止我们已经用矩阵的形式表示了三个函数

再看加密函数

可以看作再加上一个k向量,k是key的二进制形式

一轮加密：$$ret = P^{-1}(A(Px) + b + k)$$展开有$$ret = P^{-1}APx + P^{-1}b + P^{-1}k$$记$T = P^{-1}AP$,$U = P^{-1}b$。那么14轮加密后$$ret = T^{14}x + (T^{13}+T^{12} +…+I)U + (T^{13}+T^{12} +…+I)P^{-1}k$$注意到加密的时候是把flag的每八位进行分组之后再加密。那我们可以利用flag头，再爆破一位，即可获得第一组明文(此外,密文的最后两个值是一样的，可以说明后面两组明文是填充，也可以爆破填充内容来获得另外的明密文对，都可以解得k)。那么对于上面的式子，我们只有k是未知的，可以解矩阵方程得到k$$k = (T^{13}+T^{12} +…+I)^{-1}P[ret - T^{14}x -(T^{13}+T^{12} +…+I)U]$$求得k之后再解密即可

利用flag头

爆破填充内容

Crypto02

task.py

根据p,q的生成方式(Pollard’s ρ algorithm)，可以找到博客[密码学学习笔记 之 浅析Pollard’s rho algorithm及其应用 | Van1sh的小屋](https://jayxv.github.io/2019/11/11/密码学学习笔记之浅析Pollard's rho algorithm及其应用/)

基本上算是原题，拿博客的板子打就好了

exp

朱雀组

Crypto01——unsolved

easy_MNTRU.py

Crypto02

flag.enc

给出p的高256位，爆8位coppersmith

exp

Crypto03

task.py

part1

第一部分$$n_1 = p\times (2024p + x)$$把开根号，爆破一点即可分解n1

part2

第二部分，利用下面两个式子分解n2$$n_2 = p\times q$$

$$n_{22} = p^2 + q^2$$

那么有$$p+q = \sqrt{n_{22}+ 2n_2}$$

$$p-q = \sqrt{n_{22}- 2n_2}$$

part3

经过测试

记，会发现要么，要么

那么我们就有了，这很容易就能分解出p3,q3了。

但实际的使用利用的等式是，有点奇怪

三个n都分解了之后用相关消息攻击，e为2999，比较大，用H-GCD

exp

玄武组

Crypto01——unsolved

task.sage

shares数据太大

Crypto02——unsolved

main.py

pkcs1.py

        -------------已经到底啦！-------------
