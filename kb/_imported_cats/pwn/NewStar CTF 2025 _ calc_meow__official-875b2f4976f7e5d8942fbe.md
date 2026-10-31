---
title: "NewStar CTF 2025 / calc_meow"
category: pwn
tags: ["NewStar CTF 2025", "calc_meow", "pwn", "官方资料", "docs/wp/2025/week3/pwn/calc-meow.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "calc_meow", "pwn"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/pwn/calc-meow.md"
tools: []
origin: imported_cats
origin_id: "official-875b2f4976f7e5d8942fbe"
origin_domain: "pwn"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
origin_body_sha256: 801e756d2f9b57261ad660fc1a0f481f97ce1d86736ac32defbeb498ea3fe9fa
origin_title: "NewStar CTF 2025 / calc_meow"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/week3/pwn/calc-meow"
  chunk_ids: [11032]
  content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
  domain: "pwn"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-875b2f4976f7e5d8942fbe"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/df57ba7ad6ca7a909a9dfd22280b551ca6789a0a05fbdaaf8bc7c01d3efad0ae.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/week3/pwn/calc-meow.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/pwn/calc-meow.md"
  tags: ["NewStar CTF 2025", "calc_meow", "pwn", "官方资料", "docs/wp/2025/week3/pwn/calc-meow.md"]
  title: "NewStar CTF 2025 / calc_meow"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / calc_meow

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/pwn/calc-meow.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579
> - 导入 ID：official-875b2f4976f7e5d8942fbe
> - 原 domain：pwn
> - 本地快照：62_官方赛事题库/objects/df57ba7ad6ca7a909a9dfd22280b551ca6789a0a05fbdaaf8bc7c01d3efad0ae.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/pwn/calc-meow.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

## 分析

由于本体的限制不够严格，导致有一个简单的非预期。

| `rsp - 8x` |         `retaddr`          |
| :--------: | :------------------------: |
|   `rsp`    | `numbers[] / main函数栈顶` |
|    ...     |            ...             |
|   `rbp`    |       `main函数栈底`       |

本题开启了 `pie`，因此你没法像 `calc_beta` 那样直接编辑 ROP 链

但是 `retaddr` 是 `pie` 里面的地址，结合 `calc` 里面的功能，实际上我们拿到了一个任意执行 `elf` 内指令的原语。

而且由于 `elf` 里面有 `pop rdi; ret;` 导致本题可以直接通过 `pop rdi; func@got; ret; puts@plt;` 的办法直接拿到 libc 地址

拿到 libc 地址后，本题就变成了简单的 `ret2libc`，简单构造 ROP 链就可以拿到 shell

最终 EXP 如下：
