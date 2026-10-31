---
title: "NewStar CTF 2024 / 不用谢喵"
category: crypto
tags: ["NewStar CTF 2024", "不用谢喵", "crypto", "官方资料", "docs/wp/2024/week3/crypto/buyongxiemiao.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "不用谢喵", "crypto"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/crypto/buyongxiemiao.md"
tools: []
origin: imported_cats
origin_id: "official-8c43c1139499c279fde5da"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "1cdf75b7b26a6597cb3171eb314c286cbb5e4808eb17f12bf22a62a58bc21951"
origin_body_sha256: e75e2feeae6de5f6c1bd0c9754c169fadf82821d80da61a9de90fe25d98c3545
origin_title: "NewStar CTF 2024 / 不用谢喵"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week3/crypto/buyongxiemiao"
  chunk_ids: [8973, 8974]
  content_sha256: "1cdf75b7b26a6597cb3171eb314c286cbb5e4808eb17f12bf22a62a58bc21951"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 1
  id: "official-8c43c1139499c279fde5da"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/6d2b1f2fc37fe65e0624e2fe5dd54f0669326180061e19e901cbe9587fbec17e.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week3/crypto/buyongxiemiao.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/crypto/buyongxiemiao.md"
  tags: ["NewStar CTF 2024", "不用谢喵", "crypto", "官方资料", "docs/wp/2024/week3/crypto/buyongxiemiao.md"]
  title: "NewStar CTF 2024 / 不用谢喵"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / 不用谢喵

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/crypto/buyongxiemiao.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：1cdf75b7b26a6597cb3171eb314c286cbb5e4808eb17f12bf22a62a58bc21951
> - 导入 ID：official-8c43c1139499c279fde5da
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/6d2b1f2fc37fe65e0624e2fe5dd54f0669326180061e19e901cbe9587fbec17e.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/crypto/buyongxiemiao.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

import Container from '@/components/docs/Container.vue'
import AESECBCBC from '@docs/assets/images/wp/2024/BlockCipherModesofOperation.svg?component'

## 不用谢喵

可以看之前 [Week 3 参考文档](/guide/2024/week3.html#不用谢喵) 所提供的[链接](https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation)的第一张图。

总体流程即 AES CBC 加密，AES ECB 解密。

ECB 是最简单的块密码加密模式，加密前根据加密块大小<span data-desc>（如 AES 为 128 位）</span>分成若干块，之后将每块使用相同的密钥单独加密，解密同理。

CBC 模式对于每个待加密的密码块在加密前会先与前一个密码块的密文异或然后再用加密器加密。第一个明文块与一个叫初始化向量（IV）的数据块异或。

所以这题所用方式解完密之后的信息，和明文的唯一区别就在于：有没有和前一个密码块的密文异或，这里密文都给了，IV 也给了，异或一下即可。

$$
\mathrm{part}_1 = D(c_0) \oplus IV
$$

$$
\mathrm{part}_2 = D(c_1) \oplus c_0
$$

出题人的初衷的是让大家不用 `key` 解，因为需要用到 `key` 的部分都帮大家用好了，所以不用谢。

结果居然被新生非预期了，我自己都忘记我设置的 `key` 是啥了，TA 居然能猜出来😅，下次一定要随机生成 `key`！
