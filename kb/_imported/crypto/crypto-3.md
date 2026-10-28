---
title: "crypto"
category: crypto
tags: [WMCTF 2024, licensed blog wp prose]
signals: [crypto]
difficulty: medium
source: "https://dexterjie.github.io/2024/09/17/%E8%B5%9B%E9%A2%98%E5%A4%8D%E7%8E%B0/2024WMCTF/"
tools: []
origin: imported
origin_id: cn-blog-dexter-f2e567a6-1
origin_sha256: 40381c7e14453cac21bf094f87daa80a48f5422cec8b5e844d63ca93a4267d69
origin_event: "WMCTF 2024"
origin_kind: licensed_blog_wp_prose
license: "CC-BY-NC-SA-4.0"
updated: 2026-10-23
---
# 2024WMCTF / crypto

> 来源：WMCTF 2024  |  类型：licensed_blog_wp_prose  |  https://dexterjie.github.io/2024/09/17/%E8%B5%9B%E9%A2%98%E5%A4%8D%E7%8E%B0/2024WMCTF/

2024WMCTF

      发表于

      2024-09-17

      更新于
      2025-10-07

      分类于

          Wp

      阅读次数：

    Waline：

      本文字数：
      6.1k

      阅读时长 ≈
      22 分钟

    记录2024WMCTF——Crypto部分题解

K-Cessation

task.py

根据密文的值，我们可以判断出轮子中部分位置的值是相反的。比如密文第一个值是2，那么说明wheel中第一位和第二位不同

密文第4个值是3，说明wheel中第5，6位和第七位不同。根据这些约束，我们可以解方程得到wheel

exp

把所有的解都弄出来尝试解密。

flag:

FACRT

task.py

找到一篇名为Revisiting PACD-based Attacks on RSA-CRT的论文

根据论文的格实现攻击

exp

flag:

RSA

task.py

$$M = \begin{pmatrix}m & -m-p-q&-m-2p&2q-m\\m+p+q&m&2q-m&m+2p\\m+2p&m-2q&m&-m-p-q\\m-2q&-m-2p&m+p+q&m\end{pmatrix}$$

$$C = M^e$$

把M化成Jordan型，存在P矩阵使得$$P^{-1}MP = M_{jordan}$$

$$C \equiv (PM_{jordan}P^{-1})^{65537} \mod n$$

$$C \equiv PM_{jordan}^{65537}P^{-1} \mod n$$

$$CP \equiv PM_{jordan}^{65537} \mod n$$

注意到$P$长这样$$P = \begin{pmatrix}1 & 1 & 1 &1\\0 & 0 & 0 & 0\\p_{2,0} & p_{2,1} & p_{2,2} & p_{2,3}\\p_{3,0} & p_{3,1} & p_{3,2} & p_{3,3}\\\end{pmatrix}$$P矩阵下面两行都是比较复杂的式子

那可以知道$CP$这个矩阵的第二行全是0

$$CP = \begin{pmatrix}c_{0,0}&c_{0,1} &c_{0,2} & c_{0,3}\\c_{1,0}&c_{1,1} &c_{1,2} & c_{1,3}\\c_{2,0}&c_{2,1} &c_{2,2} & c_{2,3}\\c_{3,0}&c_{3,1} &c_{3,2} & c_{3,3}\\end{pmatrix}\begin{pmatrix}1 & 1 & 1 &1\\0 & 0 & 0 & 0\\p_{2,0} & p_{2,1} & p_{2,2} & p_{2,3}\\p_{3,0} & p_{3,1} & p_{3,2} & p_{3,3}\\end{pmatrix}=\begin{pmatrix}t_{0,0}&t_{0,1} &t_{0,2} & t_{0,3}\\0&0&0&0\\t_{2,0}&t_{2,1} &t_{2,2} & t_{2,3}\\t_{3,0}&t_{3,1} &t_{3,2} & t_{3,3}\\end{pmatrix}$$

利用sagemath把第二行的值打印出来

得到的值还是有点复杂

我们利用之后得到

实部:

提取出以下式子即可

虚部:

这里两个式子再利用上$p\times q =n$，用gb基可以解出m,p,q

exp

这个返回的是p，具体原因我不太理解，得到p之后解矩阵RSA即可，注意$\phi(n) = (p^2-1)(q^2-1)$
