---
title: "UCATFLAGS 2024 / game5"
category: misc
tags: ["UCATFLAGS 2024", "game5", "misc", "官方资料", "wp/misc/game5-wp.md", "origin_tag:imported_cats"]
signals: ["UCATFLAGS 2024", "game5", "misc"]
difficulty: medium
source: "https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/misc/game5-wp.md"
tools: []
origin: imported_cats
origin_id: "official-bc21d95f3063eabf30745f"
origin_domain: "misc"
origin_family: "official_event_archive"
origin_event: "UCATFLAGS 2024"
origin_year: 2024
origin_license: "not_declared"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "9275583e763966a2f6c58e1f3c56a38514ac1452de47dc1a7b63a9a81889036f"
origin_body_sha256: ef748b09b0599f7b9ffecd47a8d97539abf3afabecc48468cc4f7e5655b0038f
origin_title: "UCATFLAGS 2024 / game5"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "ucatflags2024:wp/misc/game5"
  chunk_ids: [7939, 7940, 7941]
  content_sha256: "9275583e763966a2f6c58e1f3c56a38514ac1452de47dc1a7b63a9a81889036f"
  domain: "misc"
  domain_basis: "repository_path"
  event: "UCATFLAGS 2024"
  external_links_not_followed: 0
  id: "official-bc21d95f3063eabf30745f"
  kind: "official_wp_prose"
  language: "zh"
  license: "not_declared"
  local_path: "62_官方赛事题库/objects/76c777ad3fa008c0565ab059ba996c74993db037049ecebda71787c3f7d20bce.blob"
  official_evidence: "https://github.com/UCAS-CTF/UCATFLAGS-WP"
  original_path: "wp/misc/game5-wp.md"
  revision: "b1e667240041738bf1361b555b162b5713be315c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/misc/game5-wp.md"
  tags: ["UCATFLAGS 2024", "game5", "misc", "官方资料", "wp/misc/game5-wp.md"]
  title: "UCATFLAGS 2024 / game5"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# UCATFLAGS 2024 / game5

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/misc/game5-wp.md
> - 许可：not_declared
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：UCATFLAGS 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：9275583e763966a2f6c58e1f3c56a38514ac1452de47dc1a7b63a9a81889036f
> - 导入 ID：official-bc21d95f3063eabf30745f
> - 原 domain：misc
> - 本地快照：62_官方赛事题库/objects/76c777ad3fa008c0565ab059ba996c74993db037049ecebda71787c3f7d20bce.blob
> - 源修订：b1e667240041738bf1361b555b162b5713be315c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/misc/game5-wp.md

## 正文

此题为前四道game的flag的解密与拼接

`ucatflags{B_tH1s_Is_jUsT_plAin_TExT_5oS/5L2g5Zyo5Zu956e}`

`5os/5l2g5zyo5zu956e`

`5os/5l2g5zyo5zu956e`

`ucatflags{A_DEcRypt_IT_t0_CCHHAARRRRRRRR_0e7d2707326c6b33157e1109216c252d0a6d2300}`

使用game2的解密方式解密 `0e7d2707326c6b33157e1109216c252d0a6d2300`

`ucatflags{S_a_pReTTy_keY_beh1nD_tHe_f0g_~l1FaOMIUf0%B57}m68h_Yg3ytQJ2(^p}`

使用steghide提取ucas.jpg中的压缩包

解压缩从ucas.jpg中提取的压缩包（密码为 `~l1FaOMIUf0%B57}m68h_Yg3ytQJ2(^p}`）

`ucatflags{E_tHe_f1na1_chaLLenge_1s_uNLoCked_oCd6K6u55qE6Ieq5bex}`

`oCd6K6u55qE6Ieq5bex`

四段拼接，使用base64解码得到flag
