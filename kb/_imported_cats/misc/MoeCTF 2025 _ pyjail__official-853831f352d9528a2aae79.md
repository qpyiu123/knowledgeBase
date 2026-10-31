---
title: "MoeCTF 2025 / pyjail"
category: misc
tags: ["MoeCTF 2025", "pyjail", "misc", "官方资料", "challenges/Misc/pyjail/0/README.md", "origin_tag:imported_cats"]
signals: ["MoeCTF 2025", "pyjail", "misc"]
difficulty: medium
source: "https://github.com/XDSEC/MoeCTF_2025/blob/da9e708029f4666da270064c5776ddd29c61dd6f/challenges/Misc/pyjail/0/README.md"
tools: []
origin: imported_cats
origin_id: "official-853831f352d9528a2aae79"
origin_domain: "misc"
origin_family: "official_event_archive"
origin_event: "MoeCTF 2025"
origin_year: 2025
origin_license: "not_declared"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "b386cd5d86b81ae9fbc92bdc416e3f49f35e0f9bd5ef45b0e163bca62a03512c"
origin_body_sha256: 739e5886a08732151ce210b8149de11151d97cf2dbc608405a21a6ba57ac4bf6
origin_title: "MoeCTF 2025 / pyjail"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "moectf2025:challenges/Misc/pyjail"
  chunk_ids: [8224, 8225, 8226]
  content_sha256: "b386cd5d86b81ae9fbc92bdc416e3f49f35e0f9bd5ef45b0e163bca62a03512c"
  domain: "misc"
  domain_basis: "repository_path"
  event: "MoeCTF 2025"
  external_links_not_followed: 0
  id: "official-853831f352d9528a2aae79"
  kind: "official_challenge_document"
  language: "zh"
  license: "not_declared"
  local_path: "62_官方赛事题库/objects/9e8a89f7b36abf6f2dc3100fd321f3e9c5b9a8a3c1cd96a36edd036caa78cb11.blob"
  official_evidence: "https://github.com/XDSEC/MoeCTF_2025"
  original_path: "challenges/Misc/pyjail/0/README.md"
  revision: "da9e708029f4666da270064c5776ddd29c61dd6f"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/XDSEC/MoeCTF_2025/blob/da9e708029f4666da270064c5776ddd29c61dd6f/challenges/Misc/pyjail/0/README.md"
  tags: ["MoeCTF 2025", "pyjail", "misc", "官方资料", "challenges/Misc/pyjail/0/README.md"]
  title: "MoeCTF 2025 / pyjail"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# MoeCTF 2025 / pyjail

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/XDSEC/MoeCTF_2025/blob/da9e708029f4666da270064c5776ddd29c61dd6f/challenges/Misc/pyjail/0/README.md
> - 许可：not_declared
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：MoeCTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：b386cd5d86b81ae9fbc92bdc416e3f49f35e0f9bd5ef45b0e163bca62a03512c
> - 导入 ID：official-853831f352d9528a2aae79
> - 原 domain：misc
> - 本地快照：62_官方赛事题库/objects/9e8a89f7b36abf6f2dc3100fd321f3e9c5b9a8a3c1cd96a36edd036caa78cb11.blob
> - 源修订：da9e708029f4666da270064c5776ddd29c61dd6f
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/XDSEC/MoeCTF_2025/blob/da9e708029f4666da270064c5776ddd29c61dd6f/challenges/Misc/pyjail/0/README.md

## 正文

A simple reader (所以严格来说这题不算 Pyjail)

你可以使用 netcat 或 pwntools（参考二进制漏洞审计入门指北）连接到本题和后续 Pyjail 题的环境。

关于验证码，示例：Please enter the reverse of 'GZUUAOIS' to continue: SIOAUUZG

至于 flag 的位置？你可以参考 Web 第十二章（
