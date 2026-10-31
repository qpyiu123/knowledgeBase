---
title: "NewStar CTF 2025 / calc_beta"
category: pwn
tags: ["NewStar CTF 2025", "calc_beta", "pwn", "官方资料", "docs/wp/2025/week2/pwn/calc-beta.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "calc_beta", "pwn"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week2/pwn/calc-beta.md"
tools: []
origin: imported_cats
origin_id: "official-6a8e9b9b7f7adfcbf8d5e8"
origin_domain: "pwn"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
origin_body_sha256: 08a5ec803881631052b6b6ca3cf67cbdd170093affde4fea61dd769ca711102c
origin_title: "NewStar CTF 2025 / calc_beta"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/week2/pwn/calc-beta"
  chunk_ids: [10635, 10636]
  content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
  domain: "pwn"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-6a8e9b9b7f7adfcbf8d5e8"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/5e7b8927fcf38efd511e9a7ff926776fcbeee70299b9c5bc7acbfb6a26ddc5ec.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/week2/pwn/calc-beta.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week2/pwn/calc-beta.md"
  tags: ["NewStar CTF 2025", "calc_beta", "pwn", "官方资料", "docs/wp/2025/week2/pwn/calc-beta.md"]
  title: "NewStar CTF 2025 / calc_beta"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / calc_beta

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week2/pwn/calc-beta.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761
> - 导入 ID：official-6a8e9b9b7f7adfcbf8d5e8
> - 原 domain：pwn
> - 本地快照：62_官方赛事题库/objects/5e7b8927fcf38efd511e9a7ff926776fcbeee70299b9c5bc7acbfb6a26ddc5ec.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week2/pwn/calc-beta.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

import Container from '@/components/docs/Container.vue'

## calc_beta

本题考查简单的 ret2csu 和 ret2libc 利用。

本题打法很多，除了新生要学但又不太常用的 `ret2csu`，还有很多打法。

比如说，`beta_puts()` 可以当作 `puts` 来使用，这样就可以直接泄露 libc 地址，转化成简单的 `ret2libc`。

或者说，用残留的 `rdx`，结合 `pop rdi; ret` 和 `pop rsi; ret` 以及 `write`，同样可以泄露 libc 地址，并转化成 `ret2libc`。

如上，我们可以用 `pop` 控制 `rbx rbp r12 r13 r14 r15` 六个寄存器，然后再在上面的分支里面，间接控制 `rdx`，`rsi`，`edi` 寄存器，也可以控制执行流 `call [r12+rbx*8]`。

那么用 `ret2csu` 调用 `write` 泄露 libc 地址然后打 `ret2libc` 即可。
