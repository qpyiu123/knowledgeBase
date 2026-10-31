---
title: "NewStar CTF 2025 / 随机数之旅 3"
category: crypto
tags: ["NewStar CTF 2025", "随机数之旅 3", "crypto", "官方资料", "docs/wp/2025/week3/crypto/random-3.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "随机数之旅 3", "crypto"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/crypto/random-3.md"
tools: []
origin: imported_cats
origin_id: "official-80cb171184e83dd7264871"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
origin_body_sha256: 5bbb9911d5c4b5f4a3c1b2c925557b5e7ef4d0a8d906e25e224338b8d4bc9522
origin_title: "NewStar CTF 2025 / 随机数之旅 3"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/week3/crypto/random-3"
  chunk_ids: [10938, 10939]
  content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-80cb171184e83dd7264871"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/36592913e386414f52baf19e253efc7a85a1b358a610ef2400057bd71b22d4e0.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/week3/crypto/random-3.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/crypto/random-3.md"
  tags: ["NewStar CTF 2025", "随机数之旅 3", "crypto", "官方资料", "docs/wp/2025/week3/crypto/random-3.md"]
  title: "NewStar CTF 2025 / 随机数之旅 3"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / 随机数之旅 3

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/crypto/random-3.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761
> - 导入 ID：official-80cb171184e83dd7264871
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/36592913e386414f52baf19e253efc7a85a1b358a610ef2400057bd71b22d4e0.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/crypto/random-3.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

import Container from '@/components/docs/Container.vue'

## 随机数之旅 3

本题考查线性代数。

FLAG 的每个字符取其 ASCII 码得到明文向量 $x$，注意这是 42 维的。
随机生成 $41\times 42$ 的模 $p$ 矩阵 $A$，计算 $b=Ax$
题目输出了 $A,b,p$，目标是恢复 $x$。

根据题目关系有：
$$A_{41\times 42}x_{42\times1}=b_{41\times1}$$
根据线代知识，这是欠定方程，它的解构成一个解空间：
$$x=x_p+tv,t\in Z_p$$
其中 $x_p$ 是特解，$v$ 是 $A$ 的右核空间的基。

用 Sage 写就是：

可以通过 `rank()` 函数查看矩阵的秩。容易得到 $A$ 的秩是 $41$，因此右核只有 1 维，即只有一个基。

方程解有多个，但 FLAG 只有一个。注意到 FLAG 中有 6 个字符已知，可以任选一个已知字符计算参数：
