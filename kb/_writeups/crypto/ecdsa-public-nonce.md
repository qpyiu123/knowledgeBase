---
title: "ECDSA：每条签名的临时数都不同，但可以公开算出"
category: "crypto"
kind: "writeup"
tags: ["ECDSA", "已知 nonce", "P-521", "签名编码"]
signals: ["公开前缀生成 k", "r 不重复", "固定宽度 r 与 s"]
source: "密码学题解汇编 / ECDSA：公开确定性 nonce 与私钥 MD5"
origin_id: "r67-ecdsa-public-nonce"
relates_to: ["crypto/ecdsa-nonce-reuse-lattice.md", "_methods/ecdsa_nonce_reuse.md"]
verification: "公钥和 60 条签名核对通过；答案表示待确认"
---

# ECDSA：每条签名的临时数都不同，但可以公开算出

## 先看这一步

只用公开数据就能重算签名临时数 k 时，一条签名就可求私钥，不必等 r 重复。

**适用时**：知道该签名实际用的 k、消息哈希、群阶和编码；r 在群阶下可逆。

**留意**：恢复私钥后，仍要确认题目对私钥字节或文本的表示，才能选定 MD5。

## 一条签名就够

原附件把 SHA-512 用在公开前缀和消息编号上，生成临时数 `k`。ECDSA 签名满足 `s*k≡z+r*d`（模群阶），故 `d≡(s*k−z)·r⁻¹`。这里的 `s` 是签名字段，`z` 来自消息哈希。规范的确定性签名会把私钥纳入派生，不能只看到“确定性”就套这条路。

## 对齐输入字节

样本用 P-521，签名是 66 字节 `r` 紧跟 66 字节 `s`，不是带字段标记的 DER 格式。样本的消息哈希实际是 SHA-1，和派生临时数的 SHA-512 分开。哈希长于群阶位数时，取左侧相同位数。

## 怎么回验

60 条签名算出同一私钥；`dG` 与公钥相符，`kG` 的横坐标也对上每个 `r`。再用公钥核对签名等式。题面没有定私钥的序列化方式，十进制文本和固定 66 字节会产生不同 MD5。

## 配套代码

`kb/_code/r67/case_relations.py`。函数接收题目的公开数值；不会运行题目源码。

## 出处

- ECDSA：公开确定性 nonce 与私钥 MD5：汇编中的 `题目/upload-ecdsa/WP.md`。
- [RFC 6979：确定性临时数](https://www.rfc-editor.org/rfc/rfc6979#section-3.2)。
