---
title: "UCATFLAGS 2024 / mylittlepoly"
category: crypto
tags: ["UCATFLAGS 2024", "mylittlepoly", "crypto", "官方资料", "wp/crypto/mylittlepoly-wp.md", "origin_tag:imported_cats"]
signals: ["UCATFLAGS 2024", "mylittlepoly", "crypto"]
difficulty: medium
source: "https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/crypto/mylittlepoly-wp.md"
tools: []
origin: imported_cats
origin_id: "official-7171e42a94a02a4c56d0a2"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "UCATFLAGS 2024"
origin_year: 2024
origin_license: "not_declared"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "ddfe748a332b3f38c2a52c032ef7250f513af31c8c6dfee06f0fffec96c64d26"
origin_body_sha256: 41c2f61ee909dcba3190b3cab9bc9b48df904e0fa690cef504b115e2ca5e4073
origin_title: "UCATFLAGS 2024 / mylittlepoly"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "ucatflags2024:wp/crypto/mylittlepoly"
  chunk_ids: [7938]
  content_sha256: "ddfe748a332b3f38c2a52c032ef7250f513af31c8c6dfee06f0fffec96c64d26"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "UCATFLAGS 2024"
  external_links_not_followed: 0
  id: "official-7171e42a94a02a4c56d0a2"
  kind: "official_wp_prose"
  language: "zh"
  license: "not_declared"
  local_path: "62_官方赛事题库/objects/f13ce2a3ae3d9bde9014a1afcd76224c9bd54e2764e09096c9cbad116fb89255.blob"
  official_evidence: "https://github.com/UCAS-CTF/UCATFLAGS-WP"
  original_path: "wp/crypto/mylittlepoly-wp.md"
  revision: "b1e667240041738bf1361b555b162b5713be315c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/crypto/mylittlepoly-wp.md"
  tags: ["UCATFLAGS 2024", "mylittlepoly", "crypto", "官方资料", "wp/crypto/mylittlepoly-wp.md"]
  title: "UCATFLAGS 2024 / mylittlepoly"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# UCATFLAGS 2024 / mylittlepoly

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/crypto/mylittlepoly-wp.md
> - 许可：not_declared
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：UCATFLAGS 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：ddfe748a332b3f38c2a52c032ef7250f513af31c8c6dfee06f0fffec96c64d26
> - 导入 ID：official-7171e42a94a02a4c56d0a2
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/f13ce2a3ae3d9bde9014a1afcd76224c9bd54e2764e09096c9cbad116fb89255.blob
> - 源修订：b1e667240041738bf1361b555b162b5713be315c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/crypto/mylittlepoly-wp.md

## 解题思路

`calc_poly` 计算的就是以 `Names_of_MyLittlePoly` 为系数的多项式，且没有常数项。注意到这些多项式的公因子恰好是 `x`，那么就对 `MyLittlePoly` 求最大公因子即可。
