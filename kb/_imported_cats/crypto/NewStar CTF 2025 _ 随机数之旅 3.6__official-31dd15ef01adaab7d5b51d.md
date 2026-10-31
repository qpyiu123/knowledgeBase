---
title: "NewStar CTF 2025 / 随机数之旅 3.6"
category: crypto
tags: ["NewStar CTF 2025", "随机数之旅 3.6", "crypto", "官方资料", "docs/wp/2025/extras/crypto/random-3.6.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "随机数之旅 3.6", "crypto"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/extras/crypto/random-3.6.md"
tools: []
origin: imported_cats
origin_id: "official-31dd15ef01adaab7d5b51d"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
origin_body_sha256: 9a4900e8ff3ac7834082b51c0c4e98e7dfeec66ab8cbcd5191b82f3b53ef8190
origin_title: "NewStar CTF 2025 / 随机数之旅 3.6"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/extras/crypto/random-3.6"
  chunk_ids: [10042]
  content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-31dd15ef01adaab7d5b51d"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/e7ee037cb906e342331fddeb58bb426f44f7cac91e92d1956e354a281b4568c2.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/extras/crypto/random-3.6.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/extras/crypto/random-3.6.md"
  tags: ["NewStar CTF 2025", "随机数之旅 3.6", "crypto", "官方资料", "docs/wp/2025/extras/crypto/random-3.6.md"]
  title: "NewStar CTF 2025 / 随机数之旅 3.6"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / 随机数之旅 3.6

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/extras/crypto/random-3.6.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579
> - 导入 ID：official-31dd15ef01adaab7d5b51d
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/e7ee037cb906e342331fddeb58bb426f44f7cac91e92d1956e354a281b4568c2.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/extras/crypto/random-3.6.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

## 随机数之旅 3.6

这是「随机数之旅 3」的进阶版本。这里 $m=n-6$，方程数量不足，但 FLAG 的六个已知字符 `f,l,a,g,{,}` 可以用于补充约束并求解。

预期外解法：格规约。
