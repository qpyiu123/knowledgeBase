---
title: "NewStar CTF 2025 / 小的明？题问"
category: pwn
tags: ["NewStar CTF 2025", "小的明？题问", "pwn", "官方资料", "docs/wp/2025/week3/pwn/xiaoming-question.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "小的明？题问", "pwn"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/pwn/xiaoming-question.md"
tools: []
origin: imported_cats
origin_id: "official-c86a1dc554675d1518fb97"
origin_domain: "pwn"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
origin_body_sha256: c4d7b6e866e77c17d4ca6e83cfa20858eb26850166c80c783cc577495fce0a62
origin_title: "NewStar CTF 2025 / 小的明？题问"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/week3/pwn/xiaoming-question"
  chunk_ids: [11071]
  content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
  domain: "pwn"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-c86a1dc554675d1518fb97"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/95ed0942818001bba00b12f176b34fe194ec8d591c29421b0b71d88b5d2d0faa.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/week3/pwn/xiaoming-question.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/pwn/xiaoming-question.md"
  tags: ["NewStar CTF 2025", "小的明？题问", "pwn", "官方资料", "docs/wp/2025/week3/pwn/xiaoming-question.md"]
  title: "NewStar CTF 2025 / 小的明？题问"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / 小的明？题问

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/pwn/xiaoming-question.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579
> - 导入 ID：official-c86a1dc554675d1518fb97
> - 原 domain：pwn
> - 本地快照：62_官方赛事题库/objects/95ed0942818001bba00b12f176b34fe194ec8d591c29421b0b71d88b5d2d0faa.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/pwn/xiaoming-question.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

## 分析

漏洞在下面这个地方

另外一个漏洞是在 `add` 的时候程序会把 ` ` 和 `\n` 替换成 `\0`

而 `get_flag` 用的是 `strcmp` 进行比较

只要重命名为 `root 1`，就会被替换成 `root\01`，并通过 `get_flag` 的条件，直接获得 FLAG。

本题无需编写 EXP，使用 nc 交互即可完成利用。
