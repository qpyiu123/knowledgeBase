---
title: "NewStar CTF 2024 / 隐藏的密码"
category: web
tags: ["NewStar CTF 2024", "隐藏的密码", "web", "官方资料", "docs/wp/2024/week4/web/hidden-password.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "隐藏的密码", "web"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/web/hidden-password.md"
tools: []
origin: imported_cats
origin_id: "official-e3666a46eda94c1045ab7d"
origin_domain: "web"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
origin_body_sha256: 96a38b5056759508df94736403ec5635f1712afcef7f92f49594ac34fa1d7925
origin_title: "NewStar CTF 2024 / 隐藏的密码"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week4/web/hidden-password"
  chunk_ids: [9553]
  content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
  domain: "web"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 0
  id: "official-e3666a46eda94c1045ab7d"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/5a2cbaa4c6976b38fa033d624865ca9740a250209da76c1f45c9602112de72a9.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week4/web/hidden-password.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/web/hidden-password.md"
  tags: ["NewStar CTF 2024", "隐藏的密码", "web", "官方资料", "docs/wp/2024/week4/web/hidden-password.md"]
  title: "NewStar CTF 2024 / 隐藏的密码"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / 隐藏的密码

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/web/hidden-password.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d
> - 导入 ID：official-e3666a46eda94c1045ab7d
> - 原 domain：web
> - 本地快照：62_官方赛事题库/objects/5a2cbaa4c6976b38fa033d624865ca9740a250209da76c1f45c9602112de72a9.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/web/hidden-password.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

## 隐藏的密码

根据题目隐藏的密码可能是存在信息泄露，进行目录扫描，可以扫到 `env` 和 `jolokia` 端点，可以找到 `caef11.passwd` 属性是隐藏的

读到密码后，根据题目描述和属性的名字可得用户名为 `caef11`

通过写定时任务（计划任务）的方式，以 flag 为文件名在根目录创建新文件，通过 `ls` 查看 flag，或者反弹 shell 也可以
