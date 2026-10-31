---
title: "NewStar CTF 2024 / headach3"
category: web
tags: ["NewStar CTF 2024", "headach3", "web", "官方资料", "docs/wp/2024/week1/web/headach3.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "headach3", "web"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/web/headach3.md"
tools: []
origin: imported_cats
origin_id: "official-7a0b9e275253e46a09b862"
origin_domain: "web"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "e4948a0ac253ee177ae081b53b30755b98c1551de5c3ef7f429d62eb61a35750"
origin_body_sha256: 7a433d62783e55c2d89633cacecc77b9c4572f657d1a62d354a6da395992d267
origin_title: "NewStar CTF 2024 / headach3"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week1/web/headach3"
  chunk_ids: [8580, 8581]
  content_sha256: "e4948a0ac253ee177ae081b53b30755b98c1551de5c3ef7f429d62eb61a35750"
  domain: "web"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 2
  id: "official-7a0b9e275253e46a09b862"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/86b123918607b0fa58acb5e17737f7539ac6c418ebc98f3e47c9db7f3882e123.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week1/web/headach3.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/web/headach3.md"
  tags: ["NewStar CTF 2024", "headach3", "web", "官方资料", "docs/wp/2024/week1/web/headach3.md"]
  title: "NewStar CTF 2024 / headach3"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / headach3

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/web/headach3.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：e4948a0ac253ee177ae081b53b30755b98c1551de5c3ef7f429d62eb61a35750
> - 导入 ID：official-7a0b9e275253e46a09b862
> - 原 domain：web
> - 本地快照：62_官方赛事题库/objects/86b123918607b0fa58acb5e17737f7539ac6c418ebc98f3e47c9db7f3882e123.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/web/headach3.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

import Container from '@/components/docs/Container.vue'

## headach3

题目源码如下：

打开浏览器开发者工具的「网络」（Network）选项卡，刷新网页，点击第一个请求，查看响应头，可以看到 flag.

关于响应头的具体内容，参见 [HTTP 标头](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Headers)、[响应标头](https://developer.mozilla.org/en-US/docs/Glossary/Response_header)。
