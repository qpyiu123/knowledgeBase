---
title: "UCATFLAGS 2024 / game2"
category: reverse
tags: ["UCATFLAGS 2024", "game2", "reverse", "官方资料", "wp/re/game2-wp.md", "origin_tag:imported_cats"]
signals: ["UCATFLAGS 2024", "game2", "reverse"]
difficulty: medium
source: "https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/re/game2-wp.md"
tools: []
origin: imported_cats
origin_id: "official-5c666eccbaa9eb995ee7bf"
origin_domain: "reverse"
origin_family: "official_event_archive"
origin_event: "UCATFLAGS 2024"
origin_year: 2024
origin_license: "not_declared"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "1bb667a4cb818b3cd0fd260158e481142040833e8c30cf13d914948d979ddf06"
origin_body_sha256: 311f227f36e163186eb97ddcea34f2580ec2e094f4b08f95d38ea8494604f000
origin_title: "UCATFLAGS 2024 / game2"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "ucatflags2024:wp/re/game2"
  chunk_ids: [8162, 8163, 8164]
  content_sha256: "1bb667a4cb818b3cd0fd260158e481142040833e8c30cf13d914948d979ddf06"
  domain: "reverse"
  domain_basis: "repository_path"
  event: "UCATFLAGS 2024"
  external_links_not_followed: 0
  id: "official-5c666eccbaa9eb995ee7bf"
  kind: "official_wp_prose"
  language: "zh"
  license: "not_declared"
  local_path: "62_官方赛事题库/objects/868807a7437a586d316730d67f3ace501d4f79f3578547ed04b5b0a10c0481c2.blob"
  official_evidence: "https://github.com/UCAS-CTF/UCATFLAGS-WP"
  original_path: "wp/re/game2-wp.md"
  revision: "b1e667240041738bf1361b555b162b5713be315c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/re/game2-wp.md"
  tags: ["UCATFLAGS 2024", "game2", "reverse", "官方资料", "wp/re/game2-wp.md"]
  title: "UCATFLAGS 2024 / game2"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# UCATFLAGS 2024 / game2

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/re/game2-wp.md
> - 许可：not_declared
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：UCATFLAGS 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：1bb667a4cb818b3cd0fd260158e481142040833e8c30cf13d914948d979ddf06
> - 导入 ID：official-5c666eccbaa9eb995ee7bf
> - 原 domain：reverse
> - 本地快照：62_官方赛事题库/objects/868807a7437a586d316730d67f3ace501d4f79f3578547ed04b5b0a10c0481c2.blob
> - 源修订：b1e667240041738bf1361b555b162b5713be315c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/re/game2-wp.md

## 逆向

main函数中调用了 `FUN_004018e5`函数，该函数对输入的字符串 `local_38`进行了异或和移位运算，然后与 `local_58`进行比较，比较结果为0则输出flag

异或运算的key为 `local_27`，`local_27`的值为 `0x53414355535245`，考虑小端序，则可知 `key`为 `UCASERS`

移位运算体现在

移位运算体现在

的 `+param_3`上，`param_3`的值为 `7`，所以移位运算为 `+7`

## 解题

首先要获取预定义的字符数组 `local_58`，然后对其作逆向的移位与异或运算，得到正确输入

`solve.c`
