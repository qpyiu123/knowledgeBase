---
title: "UCATFLAGS 2024 / game4"
category: reverse
tags: ["UCATFLAGS 2024", "game4", "reverse", "官方资料", "wp/re/game4-wp.md", "origin_tag:imported_cats"]
signals: ["UCATFLAGS 2024", "game4", "reverse"]
difficulty: medium
source: "https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/re/game4-wp.md"
tools: []
origin: imported_cats
origin_id: "official-5c4db61ce4f33fada9e120"
origin_domain: "reverse"
origin_family: "official_event_archive"
origin_event: "UCATFLAGS 2024"
origin_year: 2024
origin_license: "not_declared"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "b6519fa8d1628c706afd24586f8527b3b9abfed768843f5d0e9c4533879ade38"
origin_body_sha256: 966dd49b61f7abf3cd8376eb0e1385d8c0942fcdfe6759ed54e57deff1524c65
origin_title: "UCATFLAGS 2024 / game4"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "ucatflags2024:wp/re/game4"
  chunk_ids: [8177, 8178, 8179]
  content_sha256: "b6519fa8d1628c706afd24586f8527b3b9abfed768843f5d0e9c4533879ade38"
  domain: "reverse"
  domain_basis: "repository_path"
  event: "UCATFLAGS 2024"
  external_links_not_followed: 0
  id: "official-5c4db61ce4f33fada9e120"
  kind: "official_wp_prose"
  language: "zh"
  license: "not_declared"
  local_path: "62_官方赛事题库/objects/f2901b40b6bde7f8402bbf50c12a891119fe8bd1b2de43413cfc4b53a36cb36e.blob"
  official_evidence: "https://github.com/UCAS-CTF/UCATFLAGS-WP"
  original_path: "wp/re/game4-wp.md"
  revision: "b1e667240041738bf1361b555b162b5713be315c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/re/game4-wp.md"
  tags: ["UCATFLAGS 2024", "game4", "reverse", "官方资料", "wp/re/game4-wp.md"]
  title: "UCATFLAGS 2024 / game4"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# UCATFLAGS 2024 / game4

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/re/game4-wp.md
> - 许可：not_declared
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：UCATFLAGS 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：b6519fa8d1628c706afd24586f8527b3b9abfed768843f5d0e9c4533879ade38
> - 导入 ID：official-5c4db61ce4f33fada9e120
> - 原 domain：reverse
> - 本地快照：62_官方赛事题库/objects/f2901b40b6bde7f8402bbf50c12a891119fe8bd1b2de43413cfc4b53a36cb36e.blob
> - 源修订：b1e667240041738bf1361b555b162b5713be315c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/re/game4-wp.md

## game4

逆向分析可知其为一个迷宫，且方向移动与预输入的用户名有关（用户名前五位为 `crazy`时，上下左右移动分别对应 `w`、`s`、`a`、`d`）。

然后通过逆向分析可知 `DAT_00104020`为地图，且其为int类型为一个格点，大小为10*10。

二维数组在内存中按行存储，则可以得到以下为地图

二维数组在内存中按行存储，则可以得到以下为地图

剩下的只需走出迷宫
