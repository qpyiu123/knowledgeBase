---
title: "Pangbai 泰拉记（3）"
category: reverse
tags: [NewStar CTF 2024, wp prose]
signals: [Pangbai 泰拉记（3）]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/reverse/pangbai-terra3.md"
tools: []
origin: imported
origin_id: official-38d8aa83185d882c451890
origin_sha256: 164cb7bd88bea50504e8e7cfad9ac71e4e9369fe595cfec53d43751c64a4d42e
origin_event: "NewStar CTF 2024"
origin_kind: wp_prose
license: "MIT"
updated: 2026-10-23
---
# NewStar CTF 2024 / Pangbai 泰拉记（3）

> 来源：NewStar CTF 2024  |  类型：wp_prose  |  https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/reverse/pangbai-terra3.md

# Pangbai 泰拉记（3）

个人做所有逆向题思路：找判断，找密文，找密钥，找算法，写正向，写逆向

运行程序显示

〔原图省略〕

有 ROOT 的果子机的话可以用巨魔装，我 iPhone 7 装过了

一个 iOS 的安装包，用压缩包方式打开 ipa 文件，找到里面的可执行文件 `test`，然后对其进行反编译，全是 swift

最简单就是搜字符串，都试试

〔原图省略〕

可以搜到这些

〔原图省略〕

先看下面，这涉及到 swift 编译的知识，他的函数是动态的，这里只能显示函数名，交叉引用其他啥都没有，但是只要是 `_TtC4` 开头的基本都是在 `main` 中被调用的函数，也就是这道题用到了这些函数<span data-desc>（这个可以给直接提示）</span>，里面看到一个 RC4 和 AES，大胆猜测有用到这两个加密

〔原图省略〕

交叉引用 `input your flag` 可以到 `contentView` 中，里面可以看到好多 swiftUI 的调用函数，看到一个倒过来的 `click me`，是个小提示，提示去找这个 `string` 被绑在哪里

〔原图省略〕

被绑定在这个 button 里面，查看这个 button 里的函数

〔原图省略〕

一个倒着的 `correct` 函数和 `wrong` 函数，还有 `==` 判断，可以肯定这个肯定是关键函数

看上面，`a1` 是输入，通过 `a1` 来找几个关键函数

〔原图省略〕

我还原了一下大致的函数，着重讲一下几个难的怎么看出特征的

`set256able` 中（`rc4_init`）：

〔原图省略〕

`rc4_encrypt`：

〔原图省略〕

结尾一个异或，再顺着往前看偏移，看数据，发现与 RC4 很符合

AES:

〔原图省略〕

〔原图省略〕

一个 ECB 模式，确认是分组加密，然后结合前面，大概率是一个调用了库的 AES ECB 加密

摸清楚加密后，只剩下密文密钥，发现前面两个很奇怪的字符串还没用

〔原图省略〕

第一个密文，第二个密钥（`0x10` 刚好 16 位符合 AES 密钥长度）

〔原图省略〕

**Ans:** `flag{Sw1ft_$0_funny!}`

## 原文配图

![运行程序](../../_assets/images/179e30775f9117f2c10112abcfc17b1df1b1bd474b833fcb3a3f0d2b65515910.png)

![搜字符串](../../_assets/images/b23617a5ea19c183180afae3e753a8fea95a2b1936a678dba8dbedc3954d1f4c.png)

![妙妙字符串](../../_assets/images/4f6bcc011e0acb11cfa828bdd317c058086bacefe1677ca7979ced56dd8f1b40.png)

![猜测加密方式](../../_assets/images/aedf7ed10a4ee4582a1b4d9696db239358da47a23522154d82e3f86413e3578d.png)

![查看绑定](../../_assets/images/c3ba03ed9b2ec84974369f542bfecc61f9183e6b5146c6111fd661dfcbf1da8d.png)

![buttun 上的其他函数](../../_assets/images/42f97871b0fc47686525d7c9491de22e4930713b5bde9fbb5b5500bc089350bf.png)

![找关键函数](../../_assets/images/c49c4c7a66812313bdd743430c56d8432ef61941837c477b3d77ad94fff52dd8.png)

![RC4 初始化](../../_assets/images/ede0afa702cc0e63251609c6379da323bb70c8309a2ca7839b9630922e7abd78.png)

![RC4 加密](../../_assets/images/b9757dc13926d7da4cad6f942267840afa64db0b18f86c0bb122159c90fc4ea2.png)

![AES_1](../../_assets/images/b3014aad466ac81f43b77e7454d1364af677e1d516986010c8ead7582d09dc8a.png)

![AES_2](../../_assets/images/06eaec58e8e3f2be5644a118ce0011be596e263ef247650af0223ba2eb686ae4.png)

![两个字符串](../../_assets/images/3040a5578323a3714e61a361d4933f5078ec1a195067f57bd882df96f048b574.png)

![CyberChef](../../_assets/images/c38b93f7d40523bde0acf9695d319eae924d64146a3393765b8e710736f19541.png)
