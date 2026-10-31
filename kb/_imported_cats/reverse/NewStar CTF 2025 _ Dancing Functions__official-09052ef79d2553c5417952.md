---
title: "NewStar CTF 2025 / Dancing Functions"
category: reverse
tags: ["NewStar CTF 2025", "Dancing Functions", "reverse", "官方资料", "docs/wp/2025/week3/reverse/dancing-functions.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "Dancing Functions", "reverse"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/reverse/dancing-functions.md"
tools: []
origin: imported_cats
origin_id: "official-09052ef79d2553c5417952"
origin_domain: "reverse"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
origin_body_sha256: ea724d589013e5965435ab14b331168aa56ce9213a5ebd45725d4f1324a7087a
origin_title: "NewStar CTF 2025 / Dancing Functions"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/week3/reverse/dancing-functions"
  chunk_ids: [11077]
  content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
  domain: "reverse"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-09052ef79d2553c5417952"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/6cfae94b415d9f1100f1d4db8b24dca642f7e652f0050b6b0bad66479ec3b7f4.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/week3/reverse/dancing-functions.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/reverse/dancing-functions.md"
  tags: ["NewStar CTF 2025", "Dancing Functions", "reverse", "官方资料", "docs/wp/2025/week3/reverse/dancing-functions.md"]
  title: "NewStar CTF 2025 / Dancing Functions"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / Dancing Functions

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/reverse/dancing-functions.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579
> - 导入 ID：official-09052ef79d2553c5417952
> - 原 domain：reverse
> - 本地快照：62_官方赛事题库/objects/6cfae94b415d9f1100f1d4db8b24dca642f7e652f0050b6b0bad66479ec3b7f4.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/reverse/dancing-functions.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

## Dancing Functions

主函数：

有一个长度为81的字符表，约束了输入的字符集，还有一个没什么用的打印函数

keygen是一个函数指针，静态指向一个函数：

keygen是一个函数指针，静态指向一个函数：

但keygen还有多个xref，其中有一个函数可以在main之前执行：

检测了调试器，切换了keygen到一个地址，查看这个地址：

发现无法解析，再查看这个地址的xref：

发现无法解析，再查看这个地址的xref：

可以发现其在运行过程中被xor了0xCC以进行自解密，恢复解密后的函数：

查看加密函数：

是一个类RC4函数，只不过空间只有81，编写脚本解密：

`flag{D4nc1Ng_K3yG3N_fUnct10n5_wItH_r4nD_4Nd_5Mc}`
