---
title: "NewStar CTF 2025 / SageMath 使用指南"
category: crypto
tags: ["NewStar CTF 2025", "SageMath 使用指南", "crypto", "官方资料", "docs/wp/2025/week1/crypto/sagemath-guide.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "SageMath 使用指南", "crypto"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week1/crypto/sagemath-guide.md"
tools: []
origin: imported_cats
origin_id: "official-d36e83d4f1d84a3d177d81"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
origin_body_sha256: 0fa38ffc867fdc2a0ebb2fc7154546c6b233993e8ee0a51db40562efced3732b
origin_title: "NewStar CTF 2025 / SageMath 使用指南"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/week1/crypto/sagemath-guide"
  chunk_ids: [10120, 10121]
  content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 1
  id: "official-d36e83d4f1d84a3d177d81"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/a08d4915b01c78dab4639487b50a67eb69227569349be71f4cb66f33f5469dfa.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/week1/crypto/sagemath-guide.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week1/crypto/sagemath-guide.md"
  tags: ["NewStar CTF 2025", "SageMath 使用指南", "crypto", "官方资料", "docs/wp/2025/week1/crypto/sagemath-guide.md"]
  title: "NewStar CTF 2025 / SageMath 使用指南"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / SageMath 使用指南

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week1/crypto/sagemath-guide.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761
> - 导入 ID：official-d36e83d4f1d84a3d177d81
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/a08d4915b01c78dab4639487b50a67eb69227569349be71f4cb66f33f5469dfa.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week1/crypto/sagemath-guide.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

import Container from '@/components/docs/Container.vue'

## SageMath 使用指南

安装 [sagemath](https://www.sagemath.org/)，运行程序即可。

题目文件引用了许多群，并计算它们的阶，然后相乘得到一个大数作为 `key`。
