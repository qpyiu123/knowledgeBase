---
title: "RSA? cmd5!"
category: crypto
tags: [NewStar CTF 2024, wp prose]
signals: [RSA? cmd5!]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/crypto/rsa_cmd5.md"
tools: []
origin: imported
origin_id: official-d5145c5535ecefd91e094b
origin_sha256: 012b80780f39d29181ce949c996304441ff5ac185b4dd629f9019e19c8ad0fde
origin_event: "NewStar CTF 2024"
origin_kind: wp_prose
license: "MIT"
updated: 2026-10-23
---
# NewStar CTF 2024 / RSA? cmd5!

> 来源：NewStar CTF 2024  |  类型：wp_prose  |  https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/crypto/rsa_cmd5.md

import Container from '@/components/docs/Container.vue'
import { ElCollapse, ElCollapseItem } from 'element-plus'
import 'element-plus/es/components/collapse/style/css'
import 'element-plus/es/components/collapse-item/style/css'

const vProps = {
  openCollapse: []
}

# RSA? cmd5!

## 题目信息


RSA 的签名，往往是给接收方 B 确定发送方 A 的身份用的，但如果发送方用不安全的哈希算法来计算信息的信息摘要，那么有可能被中途的窃密者 C 利用而得到明文。

题目描述：

> 应该都了解 RSA 解密原理了吧？
>
> **Alice:** 你把服务器密码用 RSA 加密给我发过来吧，记得带上签名.
>
> **Bob:** 好麻烦，还要签名，算了，直接 MD5 签名一下就好了吧！


::: code-group


:::


## 解析

这里我们得到了 $c$、$s$、$n$、$e$，和平时的 RSA 不同，这里多了 $s$，让我们看看这个 $s$ 是什么


计算了 `m0` 的 MD5 为变量 `hm0`，然后将变量 `hm0` 转成整数 `hm1` 进行计算

$$
s = hm_1^{d} \mod n
$$

那么我们有 $e$，理解 RSA 解密原理

$$
\begin{gather}
e \cdot d \equiv 1 \mod \varphi \\
s^e \equiv (hm_1^{d})^e \equiv hm_1^{d \cdot e} \equiv hm_1^{1+k \cdot \varphi} \equiv hm_1 \mod n = hm_1
\end{gather}
$$

那么再结合题目名字和描述，去 [cmd5.com](https://cmd5.com) 找 `hm1` 的结果:

〔原图省略〕

$m$ 为 `adm0n12`

计算 flag


## EXP


神秘数字：
