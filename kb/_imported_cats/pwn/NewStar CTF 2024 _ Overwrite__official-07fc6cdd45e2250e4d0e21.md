---
title: "NewStar CTF 2024 / Overwrite"
category: pwn
tags: ["NewStar CTF 2024", "Overwrite", "pwn", "官方资料", "docs/wp/2024/week1/pwn/overwrite.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "Overwrite", "pwn"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/pwn/overwrite.md"
tools: []
origin: imported_cats
origin_id: "official-07fc6cdd45e2250e4d0e21"
origin_domain: "pwn"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
origin_body_sha256: 33d3e194b3fd73d199a3a8419b7029af54f82bce56f0db9c0ae185028710c995
origin_title: "NewStar CTF 2024 / Overwrite"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week1/pwn/overwrite"
  chunk_ids: [8516]
  content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
  domain: "pwn"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 0
  id: "official-07fc6cdd45e2250e4d0e21"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/51ca840108e29341ed2d94f6ab95e79ba01e63519fba33fa788db893b7ab5367.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week1/pwn/overwrite.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/pwn/overwrite.md"
  tags: ["NewStar CTF 2024", "Overwrite", "pwn", "官方资料", "docs/wp/2024/week1/pwn/overwrite.md"]
  title: "NewStar CTF 2024 / Overwrite"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / Overwrite

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/pwn/overwrite.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d
> - 导入 ID：official-07fc6cdd45e2250e4d0e21
> - 原 domain：pwn
> - 本地快照：62_官方赛事题库/objects/51ca840108e29341ed2d94f6ab95e79ba01e63519fba33fa788db893b7ab5367.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/pwn/overwrite.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

## Overwrite

IDA 反编译查看源代码

在这个函数中，我们可以输入一个数值 `nbytes`，然后读取相应长度的数据到 `nbytes_4` 中。如果 `nptr` 中的字符串被转换为数字且大于 `114514`，程序会打印 `flag`，否则会输出钱包空的信息。

漏洞分析：

漏洞分析：

1. `nptr` 和 `nbytes_4` 之间的偏移是 0x30。如果输入大于 0x30 的正整数，程序将会通过 `exit()` 退出。
2. 观察到，`read()` 函数中使用的是 `unsigned int nbytes`，但在输入校验时 `nbytes` 是 `int` 类型，进行了有符号比较。这里产生了漏洞。

例如，`-1` 的 16 进制表示是 `0xffffffff`，对于有符号整数来说，这是一个负数；但在无符号整数中，它代表一个非常大的正整数。因此，利用这一点，输入一个负数值，可以绕过前面的大小检查，将后续输入的数据覆盖到 `nptr`，从而完成利用。
