---
title: "NewStar CTF 2025 / 随机数之旅 1"
category: crypto
tags: ["NewStar CTF 2025", "随机数之旅 1", "crypto", "官方资料", "docs/wp/2025/week1/crypto/random-1.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "随机数之旅 1", "crypto"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week1/crypto/random-1.md"
tools: []
origin: imported_cats
origin_id: "official-d4a3f3cc1f4cea775a6d6b"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
origin_body_sha256: e2b4c4a7c99aa205ab7fce67d8295c6fd839f42379eb83f7fd9b207f60884970
origin_title: "NewStar CTF 2025 / 随机数之旅 1"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/week1/crypto/random-1"
  chunk_ids: [10109, 10110]
  content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-d4a3f3cc1f4cea775a6d6b"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/c74ebfa41ae7599233f2f05357282f8060bbc26c2296e560e62210b81abf098b.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/week1/crypto/random-1.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week1/crypto/random-1.md"
  tags: ["NewStar CTF 2025", "随机数之旅 1", "crypto", "官方资料", "docs/wp/2025/week1/crypto/random-1.md"]
  title: "NewStar CTF 2025 / 随机数之旅 1"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / 随机数之旅 1

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week1/crypto/random-1.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761
> - 导入 ID：official-d4a3f3cc1f4cea775a6d6b
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/c74ebfa41ae7599233f2f05357282f8060bbc26c2296e560e62210b81abf098b.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week1/crypto/random-1.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

import Container from '@/components/docs/Container.vue'

## 随机数之旅 1

题考查 LCG 流密码。

`flag` 转为整数 `b`，容易知道题目给出了关系式：

$$X_{i+1}=aX_i+b\;\;\pmod{p}$$

$a,p$ 已知，同时给了连续 $5$ 个 $X_i$ ，很容易计算出以下结果。

$$b=X_{i+1}-aX_{i}\;\;\pmod{p}$$

题目文件的名字是 `random_jerni1`，其中 `jerni` 是 journey 的谐音。
