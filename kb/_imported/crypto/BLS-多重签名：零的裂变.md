---
title: "BLS 多重签名：零的裂变"
category: crypto
tags: [NewStar CTF 2025, wp prose]
signals: [BLS 多重签名：零的裂变]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week5/crypto/bls-multisig-zero.md"
tools: []
origin: imported
origin_id: official-52ee4251ba47c83b8935b0
origin_sha256: 99c046bf0cf625bc04a04bde39b2cd3583c9ff53a41bd2dbc7b48e6179a37f7d
origin_event: "NewStar CTF 2025"
origin_kind: wp_prose
license: "MIT"
updated: 2026-10-23
---
# NewStar CTF 2025 / BLS 多重签名：零的裂变

> 来源：NewStar CTF 2025  |  类型：wp_prose  |  https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week5/crypto/bls-multisig-zero.md

# BLS 多重签名：零的裂变

这是一个关于 BLS（Boneh-Lynn-Shacham）签名系统中多重签名漏洞的题目。

### BLS 签名基础知识

1. BLS 签名基本概念

BLS 是一种基于椭圆曲线配对的数字签名方案。私钥 $sk$ 是一个随机数，公钥 $pk = sk \times G$，其中 $G$ 是椭圆曲线的生成元。签名 $\sigma = sk \times H(m)$，其中 $H(m)$ 是将消息映射到椭圆曲线上的哈希函数。

2. BLS 签名的线性特性

BLS 签名有一个重要的数学特性是线性。这意味着，公钥可以叠加，即 $pk_1 + pk_2 = (sk_1 + sk_2) \times G$；签名也可以叠加，即 $\sigma_1 + \sigma_2 = (sk_1 + sk_2) \times H(m)$。

3. 多重签名验证

在多重签名中，多个参与者共同对同一消息签名时，聚合公钥等于所有参与者的公钥之和，聚合签名等于所有参与者的签名之和，验证时检查 $e(\text{聚合公钥}, H(m)) = e(G, \text{聚合签名})$。

### 题目漏洞分析

关键漏洞：未检测零公钥攻击

题目中的关键检查：


这里要求我们提供的三个公钥的聚合结果必须等于服务器的公钥。正常情况下这很难做到，但利用 BLS 的线性特性，我们可以构造特殊的密钥对来绕过这个检查。

如果我们能找到两个私钥 $sk_1$ 和 $sk_2$，使得 $sk_1 + sk_2 = 0 \pmod{order}$。

那么对应的公钥 $pk_1 + pk_2 = (sk_1 + sk_2) \times G = 0 \times G = 零点$。

这样，如果我们构造：用户公钥 1 为 $pk_1$，用户公钥 2 为 $pk_2$，服务器公钥为 $pk_{server}$。

那么三个公钥的聚合结果为 $pk_1 + pk_2 + pk_{server} = 零点 + pk_{server} = pk_{server}$。

这样就绕过了聚合公钥的检查。

### 具体解题步骤

1. 生成攻击密钥对


这里 $x_1 + x_2 = order \equiv 0 \pmod{order}$，所以 $pk_1 + pk_2 = 零点$。

2. 注册两个公钥

分别用两个私钥对消息 `"POP"` 签名，生成证明（Proof of Possession），然后注册两个公钥。


3. 获取服务器签名


4.构造攻击获取 FLAG


完整 EXP：
