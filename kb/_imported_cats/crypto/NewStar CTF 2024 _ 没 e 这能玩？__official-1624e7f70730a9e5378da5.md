---
title: "NewStar CTF 2024 / 没 e 这能玩？"
category: crypto
tags: ["NewStar CTF 2024", "没 e 这能玩？", "crypto", "官方资料", "docs/wp/2024/week3/crypto/noenoplay.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "没 e 这能玩？", "crypto"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/crypto/noenoplay.md"
tools: []
origin: imported_cats
origin_id: "official-1624e7f70730a9e5378da5"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
origin_body_sha256: 9ba8088f6f741853100073fe6d85c9a8314d19c361c6b65be63cca5ae101531a
origin_title: "NewStar CTF 2024 / 没 e 这能玩？"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week3/crypto/noenoplay"
  chunk_ids: [8997]
  content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 0
  id: "official-1624e7f70730a9e5378da5"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/c9f40be2c3929fd406d84340e8ec2e67bc4ceed5bda4728f9272ae56f8a55e49.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week3/crypto/noenoplay.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/crypto/noenoplay.md"
  tags: ["NewStar CTF 2024", "没 e 这能玩？", "crypto", "官方资料", "docs/wp/2024/week3/crypto/noenoplay.md"]
  title: "NewStar CTF 2024 / 没 e 这能玩？"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / 没 e 这能玩？

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/crypto/noenoplay.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d
> - 导入 ID：official-1624e7f70730a9e5378da5
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/c9f40be2c3929fd406d84340e8ec2e67bc4ceed5bda4728f9272ae56f8a55e49.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/crypto/noenoplay.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

## 没 e 这能玩？

先解一个三元一次方程，解出 $p, q, r$

然后解 $\mathrm{hint}\equiv \mathrm{a\_big\_prime}^e \pmod 2^{512}$ 得到 $e$

最后常规 RSA 步骤得到 flag.
