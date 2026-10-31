---
title: "NewStar CTF 2025 / 独一无二"
category: crypto
tags: ["NewStar CTF 2025", "独一无二", "crypto", "官方资料", "docs/wp/2025/week4/crypto/one-and-only.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "独一无二", "crypto"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week4/crypto/one-and-only.md"
tools: []
origin: imported_cats
origin_id: "official-3f3aa2e097d8b81e0a7e93"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
origin_body_sha256: cc4adb447c92ef8978bddc7b6d8ac6756b27e6ba68f25acbe393baa801a1416d
origin_title: "NewStar CTF 2025 / 独一无二"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/week4/crypto/one-and-only"
  chunk_ids: [11193, 11194]
  content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-3f3aa2e097d8b81e0a7e93"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/08fe022e63917dc515c39309115472e5d84f5ef3e818d845f67942c9ca1aaaa2.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/week4/crypto/one-and-only.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week4/crypto/one-and-only.md"
  tags: ["NewStar CTF 2025", "独一无二", "crypto", "官方资料", "docs/wp/2025/week4/crypto/one-and-only.md"]
  title: "NewStar CTF 2025 / 独一无二"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / 独一无二

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week4/crypto/one-and-only.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761
> - 导入 ID：official-3f3aa2e097d8b81e0a7e93
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/08fe022e63917dc515c39309115472e5d84f5ef3e818d845f67942c9ca1aaaa2.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week4/crypto/one-and-only.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

import Container from '@/components/docs/Container.vue'

## 独一无二

本题考查 ECDSA。

题目关键在于复用了随机数 $k$ ，这导致你可以计算出私钥 $D$
