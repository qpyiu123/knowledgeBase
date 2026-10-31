---
title: "NewStar CTF 2024 / 扫码领取 flag"
category: misc
tags: ["NewStar CTF 2024", "扫码领取 flag", "misc", "官方资料", "docs/wp/2024/week4/misc/saoma.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "扫码领取 flag", "misc"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/misc/saoma.md"
tools: []
origin: imported_cats
origin_id: "official-2465bf2246879c0967bc67"
origin_domain: "misc"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
origin_body_sha256: 2ce18c732231d8d3b888731ae71dd3dac51e453069936ea87f63babd92bcbc68
origin_title: "NewStar CTF 2024 / 扫码领取 flag"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week4/misc/saoma"
  chunk_ids: [9289]
  content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
  domain: "misc"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 0
  id: "official-2465bf2246879c0967bc67"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/85492833977540aa746464e76cfff3611112f05f3f2a4321060cc0fe6094abbf.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week4/misc/saoma.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/misc/saoma.md"
  tags: ["NewStar CTF 2024", "扫码领取 flag", "misc", "官方资料", "docs/wp/2024/week4/misc/saoma.md"]
  title: "NewStar CTF 2024 / 扫码领取 flag"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / 扫码领取 flag

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/misc/saoma.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d
> - 导入 ID：official-2465bf2246879c0967bc67
> - 原 domain：misc
> - 本地快照：62_官方赛事题库/objects/85492833977540aa746464e76cfff3611112f05f3f2a4321060cc0fe6094abbf.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/misc/saoma.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

## 扫码领取 flag

`hint.jpg` 的图片信息（属性，详细信息）中隐藏了一句 Base64 加密的提示，解码后意为「阿兹特克文明」，则题目考点与阿兹特克码有关

四张 `flag.png` 进行 CRC 宽高修复，可以还原成四张碎片

脚本参考：

脚本参考：

根据 `F` `1` `4` `9` 的顺序可以组成一张阿兹特克码

根据提示信息，找到对应的解码网页或工具，即可解开
