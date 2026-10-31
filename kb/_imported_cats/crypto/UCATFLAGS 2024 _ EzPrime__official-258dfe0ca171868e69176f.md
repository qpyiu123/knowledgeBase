---
title: "UCATFLAGS 2024 / EzPrime"
category: crypto
tags: ["UCATFLAGS 2024", "EzPrime", "crypto", "官方资料", "wp/crypto/EzPrime-wp.md", "origin_tag:imported_cats"]
signals: ["UCATFLAGS 2024", "EzPrime", "crypto"]
difficulty: medium
source: "https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/crypto/EzPrime-wp.md"
tools: []
origin: imported_cats
origin_id: "official-258dfe0ca171868e69176f"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "UCATFLAGS 2024"
origin_year: 2024
origin_license: "not_declared"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "b1f36c96bdcd0792a299b8bed3d993d770e940aa5abdd57d52ec3bf77e7b342f"
origin_body_sha256: d0e1a1102fb34987d843baf5fa8aca4399dbd7b2944799f7ff00219398bae408
origin_title: "UCATFLAGS 2024 / EzPrime"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "ucatflags2024:wp/crypto/EzPrime"
  chunk_ids: [7870]
  content_sha256: "b1f36c96bdcd0792a299b8bed3d993d770e940aa5abdd57d52ec3bf77e7b342f"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "UCATFLAGS 2024"
  external_links_not_followed: 0
  id: "official-258dfe0ca171868e69176f"
  kind: "official_wp_prose"
  language: "zh"
  license: "not_declared"
  local_path: "62_官方赛事题库/objects/8f91a91b311f12d202a5d0370a10efb30e2b144aa5dcd3e78632dfe4f7759165.blob"
  official_evidence: "https://github.com/UCAS-CTF/UCATFLAGS-WP"
  original_path: "wp/crypto/EzPrime-wp.md"
  revision: "b1e667240041738bf1361b555b162b5713be315c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/crypto/EzPrime-wp.md"
  tags: ["UCATFLAGS 2024", "EzPrime", "crypto", "官方资料", "wp/crypto/EzPrime-wp.md"]
  title: "UCATFLAGS 2024 / EzPrime"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# UCATFLAGS 2024 / EzPrime

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/crypto/EzPrime-wp.md
> - 许可：not_declared
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：UCATFLAGS 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：b1f36c96bdcd0792a299b8bed3d993d770e940aa5abdd57d52ec3bf77e7b342f
> - 导入 ID：official-258dfe0ca171868e69176f
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/8f91a91b311f12d202a5d0370a10efb30e2b144aa5dcd3e78632dfe4f7759165.blob
> - 源修订：b1e667240041738bf1361b555b162b5713be315c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/crypto/EzPrime-wp.md

## 解题思路

知道 `n = p * q`，从而我们只要知道 `p + q` 就可以解出 `p` 和 `q` 了。注意到 `hint` 只是抹去了 `p + q` 的末尾，因此只要遍历 `p + q` 的所有可能取值，尝试解出 `p` 和 `q` ，判断是否满足 `n = p * q` 即可。
