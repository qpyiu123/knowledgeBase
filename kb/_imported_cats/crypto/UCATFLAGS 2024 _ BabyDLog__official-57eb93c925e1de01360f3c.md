---
title: "UCATFLAGS 2024 / BabyDLog"
category: crypto
tags: ["UCATFLAGS 2024", "BabyDLog", "crypto", "官方资料", "wp/crypto/BabyDLog-wp.md", "origin_tag:imported_cats"]
signals: ["UCATFLAGS 2024", "BabyDLog", "crypto"]
difficulty: medium
source: "https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/crypto/BabyDLog-wp.md"
tools: []
origin: imported_cats
origin_id: "official-57eb93c925e1de01360f3c"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "UCATFLAGS 2024"
origin_year: 2024
origin_license: "not_declared"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "762c48dc417a04eed91762435574113fbf6acfa8f4e49b65c8e7b543c05794db"
origin_body_sha256: c64acd57165d86830506d1e0fe825d0eefa7e6a3ce45a64bd9e5667713b6bd9c
origin_title: "UCATFLAGS 2024 / BabyDLog"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "ucatflags2024:wp/crypto/BabyDLog"
  chunk_ids: [7867, 7868]
  content_sha256: "762c48dc417a04eed91762435574113fbf6acfa8f4e49b65c8e7b543c05794db"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "UCATFLAGS 2024"
  external_links_not_followed: 1
  id: "official-57eb93c925e1de01360f3c"
  kind: "official_wp_prose"
  language: "zh"
  license: "not_declared"
  local_path: "62_官方赛事题库/objects/cc64e4d55d4ca6368a25339065145e0e7c2707a018b99d89de396eaccfd93707.blob"
  official_evidence: "https://github.com/UCAS-CTF/UCATFLAGS-WP"
  original_path: "wp/crypto/BabyDLog-wp.md"
  revision: "b1e667240041738bf1361b555b162b5713be315c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/crypto/BabyDLog-wp.md"
  tags: ["UCATFLAGS 2024", "BabyDLog", "crypto", "官方资料", "wp/crypto/BabyDLog-wp.md"]
  title: "UCATFLAGS 2024 / BabyDLog"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# UCATFLAGS 2024 / BabyDLog

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/crypto/BabyDLog-wp.md
> - 许可：not_declared
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：UCATFLAGS 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：762c48dc417a04eed91762435574113fbf6acfa8f4e49b65c8e7b543c05794db
> - 导入 ID：official-57eb93c925e1de01360f3c
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/cc64e4d55d4ca6368a25339065145e0e7c2707a018b99d89de396eaccfd93707.blob
> - 源修订：b1e667240041738bf1361b555b162b5713be315c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/crypto/BabyDLog-wp.md

## 解题思路

典型的 **Pohlig-Hellman** 算法：

1. 找到 $p-1$ 的因数分解，记为 $p = p_1^{e_1} \cdots p_k^{e_k}$
2. P-H算法的原理可参考 [这里](https://www.ruanx.net/pohlig-hellman/)
3. 因为限制了 `flag` 的大小，所以其实我们不必要把 `flag` 对每个 $p_i^{e_i}$ 的模数求出来就可以做 CRT。

## 备注

这题出拐了，，，
- 模数出长了
- 原根能够被求出来
- 本来想的是直接dlp不能全求出来，结果还是出拐了，选一部分小素数还是能求出来
