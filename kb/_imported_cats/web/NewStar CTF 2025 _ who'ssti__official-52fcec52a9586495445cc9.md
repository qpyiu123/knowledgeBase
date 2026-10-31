---
title: "NewStar CTF 2025 / who'ssti"
category: web
tags: ["NewStar CTF 2025", "who'ssti", "web", "官方资料", "docs/wp/2025/week3/web/whossti.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "who'ssti", "web"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/web/whossti.md"
tools: []
origin: imported_cats
origin_id: "official-52fcec52a9586495445cc9"
origin_domain: "web"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
origin_body_sha256: 8f385bc589b958fdc26064129dafd60ac9d6d3f624ececf6ea5806e3d5fed053
origin_title: "NewStar CTF 2025 / who'ssti"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/week3/web/whossti"
  chunk_ids: [11168, 11169]
  content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
  domain: "web"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 1
  id: "official-52fcec52a9586495445cc9"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/5cabf1d347ac5cb2e3c1099fe4da808f2d111f0d5b5d3414fcbd7d34fdc2c923.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/week3/web/whossti.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/web/whossti.md"
  tags: ["NewStar CTF 2025", "who'ssti", "web", "官方资料", "docs/wp/2025/week3/web/whossti.md"]
  title: "NewStar CTF 2025 / who'ssti"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / who'ssti

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/web/whossti.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761
> - 导入 ID：official-52fcec52a9586495445cc9
> - 原 domain：web
> - 本地快照：62_官方赛事题库/objects/5cabf1d347ac5cb2e3c1099fe4da808f2d111f0d5b5d3414fcbd7d34fdc2c923.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/web/whossti.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

import Container from '@/components/docs/Container.vue'

## who'ssti

本题考验 SSTI 基本功，由于没设置过滤，搜索用例通过 `eval` 调用就行。

这里由于是 flask 环境，可以利用 `config` 或 `lipsum` 等 flask 环境内的自带模块快捷地取得全局对象。

Lipsum 是一个用于生成随机化 [Lorem Ipsum 文本](https://cn.lipsum.com/)的 Python 模块
