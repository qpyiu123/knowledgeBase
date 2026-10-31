---
title: "UCATFLAGS 2024 / game1"
category: reverse
tags: ["UCATFLAGS 2024", "game1", "reverse", "官方资料", "wp/re/game1-wp.md", "origin_tag:imported_cats"]
signals: ["UCATFLAGS 2024", "game1", "reverse"]
difficulty: medium
source: "https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/re/game1-wp.md"
tools: []
origin: imported_cats
origin_id: "official-85310c0ffca08b1b0c0066"
origin_domain: "reverse"
origin_family: "official_event_archive"
origin_event: "UCATFLAGS 2024"
origin_year: 2024
origin_license: "not_declared"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "55d1435c6daa6db2d181ec1091f39d19061c83524afa7d5db9d3b148ed53df4d"
origin_body_sha256: 0a2502febc84b5421aa3360df18ae0637bbcf4d7321441dc31cf12bc769882dc
origin_title: "UCATFLAGS 2024 / game1"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "ucatflags2024:wp/re/game1"
  chunk_ids: [8159, 8160, 8161]
  content_sha256: "55d1435c6daa6db2d181ec1091f39d19061c83524afa7d5db9d3b148ed53df4d"
  domain: "reverse"
  domain_basis: "repository_path"
  event: "UCATFLAGS 2024"
  external_links_not_followed: 0
  id: "official-85310c0ffca08b1b0c0066"
  kind: "official_wp_prose"
  language: "zh"
  license: "not_declared"
  local_path: "62_官方赛事题库/objects/2a03264fa2e5a014aaa5152c12436aae0c30dae28a1e15ffccd6c2d71e8b1c3c.blob"
  official_evidence: "https://github.com/UCAS-CTF/UCATFLAGS-WP"
  original_path: "wp/re/game1-wp.md"
  revision: "b1e667240041738bf1361b555b162b5713be315c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/re/game1-wp.md"
  tags: ["UCATFLAGS 2024", "game1", "reverse", "官方资料", "wp/re/game1-wp.md"]
  title: "UCATFLAGS 2024 / game1"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# UCATFLAGS 2024 / game1

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/re/game1-wp.md
> - 许可：not_declared
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：UCATFLAGS 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：55d1435c6daa6db2d181ec1091f39d19061c83524afa7d5db9d3b148ed53df4d
> - 导入 ID：official-85310c0ffca08b1b0c0066
> - 原 domain：reverse
> - 本地快照：62_官方赛事题库/objects/2a03264fa2e5a014aaa5152c12436aae0c30dae28a1e15ffccd6c2d71e8b1c3c.blob
> - 源修订：b1e667240041738bf1361b555b162b5713be315c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/re/game1-wp.md

## 逆向

可知其为一个简单的字符串比较题目，只需要将输入的字符串与 `local_38`进行比较即可

更改 `local_38`的变量类型即可看到flag

脚本：
