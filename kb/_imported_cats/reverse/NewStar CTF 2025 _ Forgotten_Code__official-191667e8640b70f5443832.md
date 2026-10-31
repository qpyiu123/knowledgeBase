---
title: "NewStar CTF 2025 / Forgotten_Code"
category: reverse
tags: ["NewStar CTF 2025", "Forgotten_Code", "reverse", "官方资料", "docs/wp/2025/week2/reverse/forgotten-code.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "Forgotten_Code", "reverse"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week2/reverse/forgotten-code.md"
tools: []
origin: imported_cats
origin_id: "official-191667e8640b70f5443832"
origin_domain: "reverse"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
origin_body_sha256: 1dd4908fa5d78674bf9282ccd64b28aef116450cceaff6616c209d33806ffa39
origin_title: "NewStar CTF 2025 / Forgotten_Code"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/week2/reverse/forgotten-code"
  chunk_ids: [10748, 10749]
  content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
  domain: "reverse"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-191667e8640b70f5443832"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/c1600c3b4679a3532ec8cf83cf2cde058e5eb6e18e1dd3d6d30269a8df0f8d43.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/week2/reverse/forgotten-code.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week2/reverse/forgotten-code.md"
  tags: ["NewStar CTF 2025", "Forgotten_Code", "reverse", "官方资料", "docs/wp/2025/week2/reverse/forgotten-code.md"]
  title: "NewStar CTF 2025 / Forgotten_Code"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / Forgotten_Code

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week2/reverse/forgotten-code.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761
> - 导入 ID：official-191667e8640b70f5443832
> - 原 domain：reverse
> - 本地快照：62_官方赛事题库/objects/c1600c3b4679a3532ec8cf83cf2cde058e5eb6e18e1dd3d6d30269a8df0f8d43.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week2/reverse/forgotten-code.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

import Container from '@/components/docs/Container.vue'

## Forgotten_Code

本题考查简单的汇编分析，及 `.s` 文件编译成可执行文件的过程。

附件是一个 `.s` 文件。

> [!INFO] > **.s 文件是什么？**
>
> 是 GCC 编译器从 C/C++ 源代码生成的汇编源代码文件。它包含了低级指令<span data-desc>（x86 汇编）</span>，但还是可读的文本形式。GCC 的编译过程包括预处理、编译<span data-desc>（生成 .s）</span>、汇编<span data-desc>（生成 .o）</span>和链接<span data-desc>（生成可执行文件）</span>。

用 `gcc chal.s -o chal` 将 `.s` 文件汇编并链接成可执行文件 chal 后，拖入 IDA 分析。

可以看到加密过程是一个 TEA 加密，不过每次加密的前会对密钥的每一个字节异或 `0x11`。

Exploit 如下：
