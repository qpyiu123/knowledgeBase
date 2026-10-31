---
title: "NewStar CTF 2024 / Sign in"
category: pwn
tags: ["NewStar CTF 2024", "Sign in", "pwn", "官方资料", "docs/wp/2024/week4/pwn/signin.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "Sign in", "pwn"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/pwn/signin.md"
tools: []
origin: imported_cats
origin_id: "official-a6b25a32c101c74caf3787"
origin_domain: "pwn"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
origin_body_sha256: 938e54018a608981fe9c569f9eae7b91cfc17638cb556a729f41280ce66a2be4
origin_title: "NewStar CTF 2024 / Sign in"
origin_meta:
  asset_refs: [{"downloaded_bytes": 50123, "kind": "image", "local_path": "62_官方赛事题库/objects/00b56f34107204554e95ddab2c9567607567c61da743932f5a465d884d513e12.blob", "owner_id": "official-a6b25a32c101c74caf3787", "policy": "reference_only_no_execution", "relative_path": "docs/assets/images/wp/2024/week4/signin_1.png", "sha256": "00b56f34107204554e95ddab2c9567607567c61da743932f5a465d884d513e12", "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week4/signin_1.png"}]
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week4/pwn/signin"
  chunk_ids: [9417]
  content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
  domain: "pwn"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 0
  id: "official-a6b25a32c101c74caf3787"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/c114cb773126d1f128ffc9a078f3022f784e57183b653f5a0ca09cff810d7933.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week4/pwn/signin.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/pwn/signin.md"
  tags: ["NewStar CTF 2024", "Sign in", "pwn", "官方资料", "docs/wp/2024/week4/pwn/signin.md"]
  title: "NewStar CTF 2024 / Sign in"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / Sign in

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/pwn/signin.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d
> - 导入 ID：official-a6b25a32c101c74caf3787
> - 原 domain：pwn
> - 本地快照：62_官方赛事题库/objects/c114cb773126d1f128ffc9a078f3022f784e57183b653f5a0ca09cff810d7933.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified
> - 附件引用：[{"owner_id": "official-a6b25a32c101c74caf3787", "relative_path": "docs/assets/images/wp/2024/week4/signin_1.png", "local_path": "62_官方赛事题库/objects/00b56f34107204554e95ddab2c9567607567c61da743932f5a465d884d513e12.blob", "downloaded_bytes": 50123, "source_url": "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/assets/images/wp/2024/week4/signin_1.png", "sha256": "00b56f34107204554e95ddab2c9567607567c61da743932f5a465d884d513e12", "kind": "image", "policy": "reference_only_no_execution"}]

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/pwn/signin.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

## Sign in

用 C++ 写的一个简单小游戏，参考了 fgo 里的职阶克制，得分达到 1145 即可胜利

我们发现，程序有存档读档的功能，于是「精通单机」的我们可以想到用 SL 大法来达成目标

具体实施就是**输了就读档，赢了就存档**
