---
title: "NewStar CTF 2024 / Since you konw something"
category: crypto
tags: ["NewStar CTF 2024", "Since you konw something", "crypto", "官方资料", "docs/wp/2024/week2/crypto/since-you-know-something.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "Since you konw something", "crypto"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/crypto/since-you-know-something.md"
tools: []
origin: imported_cats
origin_id: "official-3094d3f1923e86ce57a4be"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
origin_body_sha256: be52cc8f98f6af56ba6d691dc7dba9d4b7fd3ad5559d3eafe01070ae2210c07c
origin_title: "NewStar CTF 2024 / Since you konw something"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week2/crypto/since-you-know-something"
  chunk_ids: [8685]
  content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 0
  id: "official-3094d3f1923e86ce57a4be"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/1b102da30716e04d3f4d7c5b23fdd0b029e28a840902f227b136c8687627b2e1.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week2/crypto/since-you-know-something.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/crypto/since-you-know-something.md"
  tags: ["NewStar CTF 2024", "Since you konw something", "crypto", "官方资料", "docs/wp/2024/week2/crypto/since-you-know-something.md"]
  title: "NewStar CTF 2024 / Since you konw something"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / Since you konw something

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/crypto/since-you-know-something.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d
> - 导入 ID：official-3094d3f1923e86ce57a4be
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/1b102da30716e04d3f4d7c5b23fdd0b029e28a840902f227b136c8687627b2e1.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/crypto/since-you-know-something.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

## Since you konw something

题目代码如下

又是简单的签到题，出现了上周的老朋友 `xor()`

此题注释非常重要，希望新生能够充分地利用泄露的信息，即 flag 的前一部分

这道题可以关注的地方是 flag 的格式是明确的 `flag{` 开头，结合注释，`key` 极短，直接把 `c` 和 `flag{` 异或一下看看

可以看到，`key` 的前一部分是重复的 `ns`，不难猜测 key 就是 `ns`

希望大家都能签到成功喵 ~
