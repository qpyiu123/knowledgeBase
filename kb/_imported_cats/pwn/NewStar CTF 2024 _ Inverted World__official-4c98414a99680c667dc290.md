---
title: "NewStar CTF 2024 / Inverted World"
category: pwn
tags: ["NewStar CTF 2024", "Inverted World", "pwn", "官方资料", "docs/wp/2024/week2/pwn/inverted-world.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "Inverted World", "pwn"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/pwn/inverted-world.md"
tools: []
origin: imported_cats
origin_id: "official-4c98414a99680c667dc290"
origin_domain: "pwn"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
origin_body_sha256: 2de4c9769ebfba05908a848db107f2905c14dfdcd08b4ad1db6588de61a5f222
origin_title: "NewStar CTF 2024 / Inverted World"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week2/pwn/inverted-world"
  chunk_ids: [8807]
  content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
  domain: "pwn"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 0
  id: "official-4c98414a99680c667dc290"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/f80a4ffcccc0a425ff5fc7ad0fb8b96fab100b150c87ddca6b91355188f006c5.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week2/pwn/inverted-world.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/pwn/inverted-world.md"
  tags: ["NewStar CTF 2024", "Inverted World", "pwn", "官方资料", "docs/wp/2024/week2/pwn/inverted-world.md"]
  title: "NewStar CTF 2024 / Inverted World"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / Inverted World

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/pwn/inverted-world.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d
> - 导入 ID：official-4c98414a99680c667dc290
> - 原 domain：pwn
> - 本地快照：62_官方赛事题库/objects/f80a4ffcccc0a425ff5fc7ad0fb8b96fab100b150c87ddca6b91355188f006c5.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/pwn/inverted-world.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

## 题目分析

checksec 之后发现未开启 pie，开启了 Canary.

`main` 函数的 `read` 存在栈溢出，但是这个 `read` 函数是自定义的（源码中命名函数名为 `_read` 来实现的）。

`_read` 实现的是和正常 `read` 相反方向进行输入，我们这里输入的长度 `0x512` 明显大于 255，可以写到低地址的栈帧的东西，我们劫持位于低地址的 `_read` 函数的返回地址到 backdoor 中间的部分（因为劫持到开头过不了检测）。

反向输入 `sh` 即可执行 `system("sh")` 拿到 shell.

:::info 关于 Canary
因为是反向输入的，只要不多写东西就不会修改到 Canary，自然就不用故意绕过 Canary.
:::
