---
title: "GeekGame 2024 / [Algorithm] 打破复杂度（misc）"
category: misc
tags: ["GeekGame 2024", "[Algorithm] 打破复杂度", "cases", "官方资料", "official_writeup/algo-complexity/README.md", "origin_tag:imported_cats"]
signals: ["GeekGame 2024", "[Algorithm] 打破复杂度", "cases"]
difficulty: medium
source: "https://github.com/PKU-GeekGame/geekgame-4th/blob/a21d7f7387512ec7ef77720e998d60efa16f2353/official_writeup/algo-complexity/README.md"
tools: []
origin: imported_cats
origin_id: "official-680b56af336103632c4560"
origin_domain: "cases"
origin_family: "official_event_archive"
origin_event: "GeekGame 2024"
origin_year: 2024
origin_license: "not_declared"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "b14c52c5c79f2912306317a52353be4d653819e4e22d4ce01b8ebbccab963a79"
origin_body_sha256: c0e5a9ca9b99dc4dc3f5f255b7718cc8b2ef8fd774187ade8971bcd64ddfd4ac
origin_title: "GeekGame 2024 / [Algorithm] 打破复杂度（misc）"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "geekgame2024:official_writeup/algo-complexity"
  chunk_ids: [7260]
  content_sha256: "b14c52c5c79f2912306317a52353be4d653819e4e22d4ce01b8ebbccab963a79"
  domain: "cases"
  domain_basis: "unclassified_not_inferred_from_code"
  event: "GeekGame 2024"
  external_links_not_followed: 2
  id: "official-680b56af336103632c4560"
  kind: "official_wp_prose"
  language: "zh"
  license: "not_declared"
  local_path: "62_官方赛事题库/objects/034a29bb9c5b359af55011de9a6f283e1f2eb8a6b119afb9f87ebc5d0a5c32c9.blob"
  official_evidence: "https://github.com/PKU-GeekGame/geekgame-4th"
  original_path: "official_writeup/algo-complexity/README.md"
  revision: "a21d7f7387512ec7ef77720e998d60efa16f2353"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/PKU-GeekGame/geekgame-4th/blob/a21d7f7387512ec7ef77720e998d60efa16f2353/official_writeup/algo-complexity/README.md"
  tags: ["GeekGame 2024", "[Algorithm] 打破复杂度", "cases", "官方资料", "official_writeup/algo-complexity/README.md"]
  title: "GeekGame 2024 / [Algorithm] 打破复杂度"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# GeekGame 2024 / [Algorithm] 打破复杂度（misc）

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/PKU-GeekGame/geekgame-4th/blob/a21d7f7387512ec7ef77720e998d60efa16f2353/official_writeup/algo-complexity/README.md
> - 许可：not_declared
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：GeekGame 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：b14c52c5c79f2912306317a52353be4d653819e4e22d4ce01b8ebbccab963a79
> - 导入 ID：official-680b56af336103632c4560
> - 原 domain：cases
> - 本地快照：62_官方赛事题库/objects/034a29bb9c5b359af55011de9a6f283e1f2eb8a6b119afb9f87ebc5d0a5c32c9.blob
> - 源修订：a21d7f7387512ec7ef77720e998d60efa16f2353
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/PKU-GeekGame/geekgame-4th/blob/a21d7f7387512ec7ef77720e998d60efa16f2353/official_writeup/algo-complexity/README.md

## [Algorithm] 打破复杂度

- 命题人：Yasar
- 关于SPFA—它死了：200 分
- Dinic并非万能：200 分

## 题目描述

**【网页链接：访问题目网页】**

## 预期解法

本题并没有想要为难选手，在目标设置上较为宽松。~~下次有机会可以出个 KoH 让大家卷（bushi~~

## 算法分析

~~众所周知，“有问题，上知乎”。~~

- SPFA：[https://www.zhihu.com/question/292283275](https://www.zhihu.com/question/292283275)
- Dinic：[https://www.zhihu.com/question/266149721](https://www.zhihu.com/question/266149721)

SPFA 算法和 Dinic 算法都使用基于队列实现的 BFS 来作为每轮更新的依据。
这种更新方式假设了经过的边数越少的路径为较优路径，在大多数图中这种方式都能显著降低更新的轮数。
但是只需要打破这一点，让更新轮数增加，就能让两个算法逼近理论上的最坏时间复杂度。

出题人的做法对 SPFA 构造网格图，对 Dinic 则构造多轮的二分图完全匹配。
