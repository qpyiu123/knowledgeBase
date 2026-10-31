---
title: "NewStar CTF 2025 / 黑盒 1"
category: crypto
tags: ["NewStar CTF 2025", "黑盒 1", "crypto", "官方资料", "docs/wp/2025/extras/crypto/blackbox-1.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "黑盒 1", "crypto"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/extras/crypto/blackbox-1.md"
tools: []
origin: imported_cats
origin_id: "official-833ed0a1ccba44cca04b92"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
origin_body_sha256: 6bb4792876f04d8bafc41e5e76ea9cc75e0e87a25bf8d750258635c1072e2573
origin_title: "NewStar CTF 2025 / 黑盒 1"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/extras/crypto/blackbox-1"
  chunk_ids: [10007]
  content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-833ed0a1ccba44cca04b92"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/95259a6b73a5742ccfd9a40cf2b9ba303ac48c5a06edf3d5430aeb3570e31335.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/extras/crypto/blackbox-1.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/extras/crypto/blackbox-1.md"
  tags: ["NewStar CTF 2025", "黑盒 1", "crypto", "官方资料", "docs/wp/2025/extras/crypto/blackbox-1.md"]
  title: "NewStar CTF 2025 / 黑盒 1"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / 黑盒 1

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/extras/crypto/blackbox-1.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579
> - 导入 ID：official-833ed0a1ccba44cca04b92
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/95259a6b73a5742ccfd9a40cf2b9ba303ac48c5a06edf3d5430aeb3570e31335.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/extras/crypto/blackbox-1.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

## 黑盒 1

首先先猜黑盒结构是 $f(X)=SXS^{-1},X\in \mathbb{GL}(n,q)$，然后你就可以通过输入初等矩阵来求解了。

如何判断黑盒结构是自同构？本题允许无限次输入 $X$ 并获取 $f(X)$，因此可以通过多次查询观察结构，再进行猜测与验证。

题目脚本：
