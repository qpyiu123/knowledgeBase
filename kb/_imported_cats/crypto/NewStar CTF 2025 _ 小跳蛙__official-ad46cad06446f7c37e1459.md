---
title: "NewStar CTF 2025 / 小跳蛙"
category: crypto
tags: ["NewStar CTF 2025", "小跳蛙", "crypto", "官方资料", "docs/wp/2025/week1/crypto/little-frog.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "小跳蛙", "crypto"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week1/crypto/little-frog.md"
tools: []
origin: imported_cats
origin_id: "official-ad46cad06446f7c37e1459"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
origin_body_sha256: bce8f5f36d1600536fe2290e21b8dbb9e670bf3a967a7957516831453fffad97
origin_title: "NewStar CTF 2025 / 小跳蛙"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/week1/crypto/little-frog"
  chunk_ids: [10104, 10105]
  content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-ad46cad06446f7c37e1459"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/c90e99fc98f1fa96c6bc471faa72b8de299af9d1f57d27f1e92f613bdb62241b.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/week1/crypto/little-frog.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week1/crypto/little-frog.md"
  tags: ["NewStar CTF 2025", "小跳蛙", "crypto", "官方资料", "docs/wp/2025/week1/crypto/little-frog.md"]
  title: "NewStar CTF 2025 / 小跳蛙"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / 小跳蛙

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week1/crypto/little-frog.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761
> - 导入 ID：official-ad46cad06446f7c37e1459
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/c90e99fc98f1fa96c6bc471faa72b8de299af9d1f57d27f1e92f613bdb62241b.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week1/crypto/little-frog.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

import Container from '@/components/docs/Container.vue'

## 小跳蛙

本题考查 GCD 及简单的数论知识。

题目脚本已经告诉我们了，每次给出一个坐标 `(x,y)`，我们需要返回最后小青蛙会停留的坐标。

1. 你可以**直接复用题目脚本的验证部分**，即 `while a!=b:` 那一块。
2. 感觉直接复用太 low 了？没事你还可以学习发现：小跳蛙跳跃的过程就是在模拟辗转相除法<span data-desc>（欧几里得算法）</span>求两个数的最大公约数！这样就好办了，我们**找一个库去使用 `gcd()` 函数**就行了。
