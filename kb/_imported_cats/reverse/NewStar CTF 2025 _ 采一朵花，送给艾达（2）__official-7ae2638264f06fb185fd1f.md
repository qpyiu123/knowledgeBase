---
title: "NewStar CTF 2025 / 采一朵花，送给艾达（2）"
category: reverse
tags: ["NewStar CTF 2025", "采一朵花，送给艾达（2）", "reverse", "官方资料", "docs/wp/2025/week3/reverse/flower-2.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "采一朵花，送给艾达（2）", "reverse"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/reverse/flower-2.md"
tools: []
origin: imported_cats
origin_id: "official-7ae2638264f06fb185fd1f"
origin_domain: "reverse"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
origin_body_sha256: 3084f32e00b30153bb2484e1d0cb1fc8f88568c4a257848026701ba119582935
origin_title: "NewStar CTF 2025 / 采一朵花，送给艾达（2）"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/week3/reverse/flower-2"
  chunk_ids: [11088]
  content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
  domain: "reverse"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-7ae2638264f06fb185fd1f"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/df29666bb1698ef78205be30add84c63c9a078c8c232d51c6c5b5e3706ce2ab8.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/week3/reverse/flower-2.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/reverse/flower-2.md"
  tags: ["NewStar CTF 2025", "采一朵花，送给艾达（2）", "reverse", "官方资料", "docs/wp/2025/week3/reverse/flower-2.md"]
  title: "NewStar CTF 2025 / 采一朵花，送给艾达（2）"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / 采一朵花，送给艾达（2）

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/reverse/flower-2.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579
> - 导入 ID：official-7ae2638264f06fb185fd1f
> - 原 domain：reverse
> - 本地快照：62_官方赛事题库/objects/df29666bb1698ef78205be30add84c63c9a078c8c232d51c6c5b5e3706ce2ab8.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/reverse/flower-2.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

## 采一朵花，送给艾达（2）

程序主函数中有花：

A4位置取消定义A5位置重定义，反编译：

Keygen中有类似的花，去除后反编译：

Keygen中有类似的花，去除后反编译：

查看RC4init：

发现函数几乎是空的，没有重要逻辑，也没有jumpout，但是提示要查看汇编：

发现了call $+5和retn，符号表也给出了这里正常代码的恢复位置，将call $+5到retn的位置全部nop即可

发现和正常的RC4_KSA相比略有魔改，PRGA函数也有类似之前的两个花，去除即可：

尾部多了一个加索引，解密时前置即可

编写解密脚本：

编写解密脚本：

`flag{WO0o0O0w_So0Oo0o_m4Ny_F1oO0o0oW3R5}`
