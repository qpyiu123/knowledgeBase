---
title: "NewStar CTF 2024 / Just one and more than two"
category: crypto
tags: ["NewStar CTF 2024", "Just one and more than two", "crypto", "官方资料", "docs/wp/2024/week2/crypto/just-one-and-more-than-two.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "Just one and more than two", "crypto"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/crypto/just-one-and-more-than-two.md"
tools: []
origin: imported_cats
origin_id: "official-dd1eafe65c6e20aa797aa0"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
origin_body_sha256: 905af64fb2d3571350d4215edd9f3636d4bd1357f49c1ae2dc0c802684a4bc3b
origin_title: "NewStar CTF 2024 / Just one and more than two"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week2/crypto/just-one-and-more-than-two"
  chunk_ids: [8675]
  content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 0
  id: "official-dd1eafe65c6e20aa797aa0"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/27dc873990bb95fdfc6586b252b3e8f4876675adb3a341102abeb54d90ab50e9.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week2/crypto/just-one-and-more-than-two.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/crypto/just-one-and-more-than-two.md"
  tags: ["NewStar CTF 2024", "Just one and more than two", "crypto", "官方资料", "docs/wp/2024/week2/crypto/just-one-and-more-than-two.md"]
  title: "NewStar CTF 2024 / Just one and more than two"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / Just one and more than two

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/crypto/just-one-and-more-than-two.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d
> - 导入 ID：official-dd1eafe65c6e20aa797aa0
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/27dc873990bb95fdfc6586b252b3e8f4876675adb3a341102abeb54d90ab50e9.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/crypto/just-one-and-more-than-two.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

## Just one and more than two

很常见的 RSA 板子题。在一般的 RSA 中，我们有

$$\varphi(n)= \varphi(p)*\varphi(q)=(p-1)(q-1)$$

如果你不知道，那就再回去温习一下 Week 1 中对于 RSA 的相关知识

针对 just one 的情况：

$$\varphi(n)=\varphi(p)=p-1$$

针对 more than two 的情况：

针对 more than two 的情况：

$$\varphi(n)=\varphi(p)*\varphi(q)*\varphi(r)=(p-1)(q-1)(r-1)$$

其他和普通 RSA 一样解即可

实际上还会有其他情况，只要大家对欧拉函数有足够的了解，这类问题一定可以迎刃而解的
