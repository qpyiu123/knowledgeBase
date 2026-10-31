---
title: "NewStar CTF 2025 / Poly"
category: crypto
tags: ["NewStar CTF 2025", "Poly", "crypto", "官方资料", "docs/wp/2025/week5/crypto/poly.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "Poly", "crypto"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week5/crypto/poly.md"
tools: []
origin: imported_cats
origin_id: "official-de685ea8ffcb5ac0bd2056"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
origin_body_sha256: 9174f5df3ec12ff1a0b00a7d827405a76d0a8cb2082b70be565de36344d0d9b1
origin_title: "NewStar CTF 2025 / Poly"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/week5/crypto/poly"
  chunk_ids: [11529, 11530]
  content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-de685ea8ffcb5ac0bd2056"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/408f7df79df8930aff2f7ff8c06106202a14ffb093af1aa29d58103c8d881f39.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/week5/crypto/poly.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week5/crypto/poly.md"
  tags: ["NewStar CTF 2025", "Poly", "crypto", "官方资料", "docs/wp/2025/week5/crypto/poly.md"]
  title: "NewStar CTF 2025 / Poly"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / Poly

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week5/crypto/poly.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761
> - 导入 ID：official-de685ea8ffcb5ac0bd2056
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/408f7df79df8930aff2f7ff8c06106202a14ffb093af1aa29d58103c8d881f39.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week5/crypto/poly.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

import Container from '@/components/docs/Container.vue'

## Poly

本题考查 Groebner 基。

参考 EXP：

简单来说，groebner基可以用来求多项式的公因式。

Gröbner基 方法是从任意一个多项式理想的一组给定生成元，计算另一组性质良好的生成元，并称为该理想的Gröbner基。它能用来判定任意多项式是否属于该理想。做密码题时，则使用该基简化运算来求解我们想要的。
