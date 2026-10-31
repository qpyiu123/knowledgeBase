---
title: "NewStar CTF 2024 / sqlshell"
category: web
tags: ["NewStar CTF 2024", "sqlshell", "web", "官方资料", "docs/wp/2024/week5/web/sqlshell.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "sqlshell", "web"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/web/sqlshell.md"
tools: []
origin: imported_cats
origin_id: "official-a5b55392317db27a83ca55"
origin_domain: "web"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
origin_body_sha256: 6e146b7741aeacf3303581b097bd0c9690fe3738b9fe4b23565362517db9a3c6
origin_title: "NewStar CTF 2024 / sqlshell"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week5/web/sqlshell"
  chunk_ids: [10002]
  content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
  domain: "web"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 0
  id: "official-a5b55392317db27a83ca55"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/441ad85c41f56cfdd42f584b9125ac7ec04b2cd4349056aa2849dc93c1202f79.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week5/web/sqlshell.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/web/sqlshell.md"
  tags: ["NewStar CTF 2024", "sqlshell", "web", "官方资料", "docs/wp/2024/week5/web/sqlshell.md"]
  title: "NewStar CTF 2024 / sqlshell"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / sqlshell

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/web/sqlshell.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d
> - 导入 ID：official-a5b55392317db27a83ca55
> - 原 domain：web
> - 本地快照：62_官方赛事题库/objects/441ad85c41f56cfdd42f584b9125ac7ec04b2cd4349056aa2849dc93c1202f79.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/web/sqlshell.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

## sqlshell

mysql 启动时，加了选项 `--secure_file_priv=''`，这个的选项作用是允许 mysql 进行文件读写。

- 如果这个选项是 `NULL`，说明不能进行文件读写
- 如果这个选项是指定的目录，说明只能对指定目录进行文件读写
- 如果这个选项是空字符串，也就是 `''`，能对任意目录进行文件读写

程序运行时，执行了命令 `chmod 777 /var/www/html`，作用是允许该目录被所有用户写入文件。

所以思路就是通过注入 SQL 语句，进行写文件，写一个木马到网站根目录（`/var/www/html`）下即可。
