---
title: "NewStar CTF 2024 / AmazingGame"
category: misc
tags: ["NewStar CTF 2024", "AmazingGame", "misc", "官方资料", "docs/wp/2024/week3/misc/amazinggame.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "AmazingGame", "misc"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/misc/amazinggame.md"
tools: []
origin: imported_cats
origin_id: "official-06b2da32a9f792599b481e"
origin_domain: "misc"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
origin_body_sha256: 5b348a931f7dc5e9f715f5dcc201693436c576a991cb166c7c35aa97a5072ab5
origin_title: "NewStar CTF 2024 / AmazingGame"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week3/misc/amazinggame"
  chunk_ids: [9003]
  content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
  domain: "misc"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 0
  id: "official-06b2da32a9f792599b481e"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/06c8436a0038a518e1dff108c47157f0b8489714219aa2b37e8d430ded9902f3.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week3/misc/amazinggame.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/misc/amazinggame.md"
  tags: ["NewStar CTF 2024", "AmazingGame", "misc", "官方资料", "docs/wp/2024/week3/misc/amazinggame.md"]
  title: "NewStar CTF 2024 / AmazingGame"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / AmazingGame

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/misc/amazinggame.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d
> - 导入 ID：official-06b2da32a9f792599b481e
> - 原 domain：misc
> - 本地快照：62_官方赛事题库/objects/06c8436a0038a518e1dff108c47157f0b8489714219aa2b37e8d430ded9902f3.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/misc/amazinggame.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

## AmazingGame

安卓私有目录位于 `/data/user/0/<包名>` 下

安卓的 `shared_prefs` 一般用来存放软件配置数据

修改文件即可更改已通过的关卡数据

修改文件即可更改已通过的关卡数据

通过第一关后，关掉游戏<span data-desc>（这点很重要）</span>

ADB 链接手机执行

软件有 23 个关卡，我们把关卡解锁数改为 23

正常来说应该用 `adb push` 来修改文件，这里我们为了方便直接把 2 替换成 23

打开游戏发现关卡全部解锁，随便游玩 23 关，等游戏结束即可获得 flag
