---
title: "Smile 盒"
category: crypto
tags: [NewStar CTF 2025, wp prose]
signals: [Smile 盒]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week5/crypto/smile-box.md"
tools: []
origin: imported
origin_id: official-fe10a8ad699fb033225642
origin_sha256: 4695b81d1d60dad594ddf1c6c63c6e8f2e32a4ff3ac5fa1707dde1a3cf7e520b
origin_event: "NewStar CTF 2025"
origin_kind: wp_prose
license: "MIT"
updated: 2026-10-23
---
# NewStar CTF 2025 / Smile 盒

> 来源：NewStar CTF 2025  |  类型：wp_prose  |  https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week5/crypto/smile-box.md

import Container from '@/components/docs/Container.vue'

# Smile 盒


本题考查差分攻击。

其实容易知道加密过程是 2 轮 CipherFour

> 此处原文引用了示意图，但图片文件未包含在压缩包中。

其中每条线代表一个比特，左边是高位。
加密过程：16 比特明文与轮密钥 `key0` 异或，分为 4 块 4 比特，分块过 4-4 S 盒，然后进行比特拉线（也就是 P 置换，见下文）操作。再与轮密钥 `key1` 异或，分块过 S 盒，与轮密钥 `key2` 异或，输出密文。
可以无限次输入明文来获取密文。如果猜中 `key2`（16 bit），即可得到 FLAG。
注意，我们知道过 S 盒（`p=[self.S[i] for i in p]`）和 P 置换（`permute_bits(self, x)`）的过程。也就是说我们可以逆 S 盒和 P 置换。

然后就可以找差分了。这里差分定义为 $\Delta x=x_1\oplus x_2$ .

为什么要找差分？因为我们知道，加密过程中，与轮密钥异或不影响差分（$(m_1\oplus k_1)\oplus (m_2\oplus k_1)=m_1\oplus m_2$），P 置换是线性的，不影响差分（你自己验证），影响差分的只有 S 盒。如果我们能够通过研究 S 盒找到一个**高概率的差分**，就可以利用这个差分去攻击了。

怎么攻击呢？
让我们关注加密的最后一步：
`c = S(p) ^ key2`
其中`p`是进入最后一轮 S 盒之前的 16 位中间值。
我们可以将这个等式拆分为 4 个独立的 4 bit ：
`c_i = S(p_i) ^ key2_i`
(其中`i`= 0, 1, 2, 3)。然后，通过 S 盒的逆运算`S_`，我们可以恢复出`p_i`：
`p_i = S_(c_i ^ key2_i)`
现在，我们选择一对明文`(m1, m2)`，它们具有特定的差分`dm = m1 ^ m2`。这对明文经过加密后得到一对密文`(c1, c2)`。
对于密钥`key2_i`的每一个可能猜测`k`(0-15)，我们都可以计算出一对可能的`p`值：
`p_1_i = S_(c1_i ^ k)`
`p_2_i = S_(c2_i ^ k)`
然后计算它们的差分`dp = p_1_i ^ p_2_i`。
而我们刚刚说要找的**高概率差分**，就是能对于特定的输入差分`dm`，在密码内部某个特定位置（比如 S 盒输入前）的差分`dp`会以一个很高的概率等于某个特定值。
之后如果`dp`等于我们期望的**高概率差分**，就为这个密钥猜测`k`投上一票。
在处理了大量明文对后，获得票数最高的那个密钥猜测`k`，就是最有可能的正确密钥的 4 bit。

接下来演示一下怎么找我们想要的包含高概率差分的差分路径：
首先先查差分分布表。


> 此处原文引用了示意图，但图片文件未包含在压缩包中。

发现高概率差分：`0xb->0xc:8/16` ; `0xf->0x3:8/16`
（也就是： `0b1011 -> 0b1100` ; `0b1111 -> 0b0011` ）
然后搓路径：

> 此处原文引用了示意图，但图片文件未包含在压缩包中。

可以看出我们找到了一条 `0x00b0 -> 0x00c0 -> 0x2000/0x0200` 的路径，其中差分 `0x2` 过S盒会有5种可能的输出差分（L），
所以我们在选取密文时要事先筛一遍。

我们以 `key2` 高 4 bit 为例讲讲怎么攻击：
选择差分为 `0x00b0` 的明文对 `m1,m2` 输入，然后获取密文 `c1,c2`，筛选密文差分高 4 bit 在 L 里面的。使用筛后的密文（当然我们只需要取高4 bit就可以了）猜 `key2` 高4 bit：直接爆破 `0->15`，检验 `S_(c1^key) ^ S_(c2^key)==0x2`，如果通过则给可能的记上一票。最后选择票数最高的。

一个仅供参考的脚本：
