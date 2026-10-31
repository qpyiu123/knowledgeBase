---
title: "NewStar CTF 2025 / 随机数之旅 4"
category: crypto
tags: ["NewStar CTF 2025", "随机数之旅 4", "crypto", "官方资料", "docs/wp/2025/week4/crypto/random-4.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "随机数之旅 4", "crypto"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week4/crypto/random-4.md"
tools: []
origin: imported_cats
origin_id: "official-2861c8c1e1072a991f3371"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
origin_body_sha256: ee21aca97ac9c99630be8b0168c34e1b1c76f245797321b83ae6f74b7a7b39f2
origin_title: "NewStar CTF 2025 / 随机数之旅 4"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/week4/crypto/random-4"
  chunk_ids: [11197, 11198]
  content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-2861c8c1e1072a991f3371"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/8e97e1b8ab10b743b943dd9a23a39490dab9dfbc5736acbe1c499e78ffa7202f.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/week4/crypto/random-4.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week4/crypto/random-4.md"
  tags: ["NewStar CTF 2025", "随机数之旅 4", "crypto", "官方资料", "docs/wp/2025/week4/crypto/random-4.md"]
  title: "NewStar CTF 2025 / 随机数之旅 4"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / 随机数之旅 4

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week4/crypto/random-4.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761
> - 导入 ID：official-2861c8c1e1072a991f3371
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/8e97e1b8ab10b743b943dd9a23a39490dab9dfbc5736acbe1c499e78ffa7202f.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week4/crypto/random-4.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

import Container from '@/components/docs/Container.vue'

## 随机数之旅 4

本题考查线性代数。

FLAG 被切片为 14 块，每块转为数字后得到秘密向量 $c$。
$x$ 初始为 14 个随机数字，然后按如下关系扩展 $x$ 序列：

$$x_k = (c_0*x_{k-14} + c_1*x_{k-13} + ... + c_{13}*x_{k-1}) \pmod{p}$$

题目给出了 $p$ 和 $x$ 序列的最后 28 位。

利用这 28 位可以根据递推关系列出 14 个关于 $c_i$ 的 14 元方程，求解即可。
