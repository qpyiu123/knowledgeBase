---
title: "UCATFLAGS 2024 / LVM 0"
category: reverse
tags: ["UCATFLAGS 2024", "LVM 0", "reverse", "官方资料", "wp/re/lvm0-wp.md", "origin_tag:imported_cats"]
signals: ["UCATFLAGS 2024", "LVM 0", "reverse"]
difficulty: medium
source: "https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/re/lvm0-wp.md"
tools: []
origin: imported_cats
origin_id: "official-beb33e5d5d1ef4913493f5"
origin_domain: "reverse"
origin_family: "official_event_archive"
origin_event: "UCATFLAGS 2024"
origin_year: 2024
origin_license: "not_declared"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "4399956984e4127596e94647b1a8e42f40446d734806e572a128b019f19b2447"
origin_body_sha256: 811461a0e4ce0d253aa812cc1d1d44c7b1607da5518ac7f127d84c678325f019
origin_title: "UCATFLAGS 2024 / LVM 0"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "ucatflags2024:wp/re/lvm0"
  chunk_ids: [8181]
  content_sha256: "4399956984e4127596e94647b1a8e42f40446d734806e572a128b019f19b2447"
  domain: "reverse"
  domain_basis: "repository_path"
  event: "UCATFLAGS 2024"
  external_links_not_followed: 0
  id: "official-beb33e5d5d1ef4913493f5"
  kind: "official_wp_prose"
  language: "zh"
  license: "not_declared"
  local_path: "62_官方赛事题库/objects/9e17c72a33ed3614f9da9593f11a4c0b82935c1d4e7fdd3c372254318175c321.blob"
  official_evidence: "https://github.com/UCAS-CTF/UCATFLAGS-WP"
  original_path: "wp/re/lvm0-wp.md"
  revision: "b1e667240041738bf1361b555b162b5713be315c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/re/lvm0-wp.md"
  tags: ["UCATFLAGS 2024", "LVM 0", "reverse", "官方资料", "wp/re/lvm0-wp.md"]
  title: "UCATFLAGS 2024 / LVM 0"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# UCATFLAGS 2024 / LVM 0

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/re/lvm0-wp.md
> - 许可：not_declared
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：UCATFLAGS 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：4399956984e4127596e94647b1a8e42f40446d734806e572a128b019f19b2447
> - 导入 ID：official-beb33e5d5d1ef4913493f5
> - 原 domain：reverse
> - 本地快照：62_官方赛事题库/objects/9e17c72a33ed3614f9da9593f11a4c0b82935c1d4e7fdd3c372254318175c321.blob
> - 源修订：b1e667240041738bf1361b555b162b5713be315c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/re/lvm0-wp.md

## 解法 1

在 LVM_REPL 中输入 `.m(10)` 就会发现两位数无法被处理,
从而猜到可能存在 `11`, `12` 之类的隐藏 manual.

## 解法 2

呃, 克隆下仓库, 然后执行:

就可以得到结果了.

## 解法 3

flag 也写到了 git log 中了.
