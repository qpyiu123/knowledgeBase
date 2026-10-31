---
title: "NewStar CTF 2024 / Lock"
category: reverse
tags: ["NewStar CTF 2024", "Lock", "reverse", "官方资料", "docs/wp/2024/week5/reverse/lock.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "Lock", "reverse"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/reverse/lock.md"
tools: []
origin: imported_cats
origin_id: "official-4498e7785d7732ff81b513"
origin_domain: "reverse"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
origin_body_sha256: 06d7ddfd5ca6b83f8cba467b69a25d0d518a8994a9b5d63b359564dee9087d0b
origin_title: "NewStar CTF 2024 / Lock"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week5/reverse/lock"
  chunk_ids: [9890]
  content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
  domain: "reverse"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 0
  id: "official-4498e7785d7732ff81b513"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/93fae4a10f6c6317e790b7871a37522047aa411eb3f99bf44b80070238f7e800.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week5/reverse/lock.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/reverse/lock.md"
  tags: ["NewStar CTF 2024", "Lock", "reverse", "官方资料", "docs/wp/2024/week5/reverse/lock.md"]
  title: "NewStar CTF 2024 / Lock"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / Lock

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/reverse/lock.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d
> - 导入 ID：official-4498e7785d7732ff81b513
> - 原 domain：reverse
> - 本地快照：62_官方赛事题库/objects/93fae4a10f6c6317e790b7871a37522047aa411eb3f99bf44b80070238f7e800.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/reverse/lock.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

## Lock

由于程序告诉你每次输入对了多少个字符，所以可以逐位爆破。Cython 是一个把 Python 转化为 C 语言的项目，其逆向极为复杂，出题人也并不能完全掌握，所以这里不讲解。

EXP：
