---
title: "NewStar CTF 2024 / Herta's Study"
category: misc
tags: ["NewStar CTF 2024", "Herta's Study", "misc", "官方资料", "docs/wp/2024/week2/misc/herta.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "Herta's Study", "misc"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/misc/herta.md"
tools: []
origin: imported_cats
origin_id: "official-d7707d8cfe46aa3aabe107"
origin_domain: "misc"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "e4948a0ac253ee177ae081b53b30755b98c1551de5c3ef7f429d62eb61a35750"
origin_body_sha256: d3f088fc97de7fa845e1aaed7f17b13aa5922dcb148c52a63e36bb54581bdef6
origin_title: "NewStar CTF 2024 / Herta's Study"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week2/misc/herta"
  chunk_ids: [8720, 8721]
  content_sha256: "e4948a0ac253ee177ae081b53b30755b98c1551de5c3ef7f429d62eb61a35750"
  domain: "misc"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 0
  id: "official-d7707d8cfe46aa3aabe107"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/7f449be71dbc181f0019dfb501eba724a646a22bb44230eab973850b942ff98d.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week2/misc/herta.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/misc/herta.md"
  tags: ["NewStar CTF 2024", "Herta's Study", "misc", "官方资料", "docs/wp/2024/week2/misc/herta.md"]
  title: "NewStar CTF 2024 / Herta's Study"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / Herta's Study

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/misc/herta.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：e4948a0ac253ee177ae081b53b30755b98c1551de5c3ef7f429d62eb61a35750
> - 导入 ID：official-d7707d8cfe46aa3aabe107
> - 原 domain：misc
> - 本地快照：62_官方赛事题库/objects/7f449be71dbc181f0019dfb501eba724a646a22bb44230eab973850b942ff98d.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/misc/herta.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

import Container from '@/components/docs/Container.vue'

## Herta's Study

本题考点：PHP 混淆，流量分析

建议配合 unknown 师傅的前两道流量题食用

第七条流量是上传的 PHP 木马

第七条流量是上传的 PHP 木马

可以搜索一下 `create_funtion()` 函数，解除混淆后得到加密代码

就是 Base64 后把奇数位 ROT13

解码反过来就行（第38条，`f.txt` 里的是真 flag，另一个是假 flag）
