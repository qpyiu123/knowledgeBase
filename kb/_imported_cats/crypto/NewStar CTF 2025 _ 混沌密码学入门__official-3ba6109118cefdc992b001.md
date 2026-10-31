---
title: "NewStar CTF 2025 / 混沌密码学入门"
category: crypto
tags: ["NewStar CTF 2025", "混沌密码学入门", "crypto", "官方资料", "docs/wp/2025/extras/crypto/chaos-cipher-intro.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "混沌密码学入门", "crypto"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/extras/crypto/chaos-cipher-intro.md"
tools: []
origin: imported_cats
origin_id: "official-3ba6109118cefdc992b001"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
origin_body_sha256: cc60baea1c0029bc77df573d963a41dac5d483e2195ae44f0774736c9fb20713
origin_title: "NewStar CTF 2025 / 混沌密码学入门"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/extras/crypto/chaos-cipher-intro"
  chunk_ids: [10011]
  content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-3ba6109118cefdc992b001"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/118a09cf8b2615dfd98cab45800bd9598961928259e02097bcc58195ee901d4c.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/extras/crypto/chaos-cipher-intro.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/extras/crypto/chaos-cipher-intro.md"
  tags: ["NewStar CTF 2025", "混沌密码学入门", "crypto", "官方资料", "docs/wp/2025/extras/crypto/chaos-cipher-intro.md"]
  title: "NewStar CTF 2025 / 混沌密码学入门"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / 混沌密码学入门

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/extras/crypto/chaos-cipher-intro.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579
> - 导入 ID：official-3ba6109118cefdc992b001
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/118a09cf8b2615dfd98cab45800bd9598961928259e02097bcc58195ee901d4c.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/extras/crypto/chaos-cipher-intro.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

## 混沌密码学入门

题目已经给出混沌序列和加密过程，因此按加密流程逆向恢复即可。

EXP：

解密结果：

解密结果：

> 此处原文引用了示意图，但图片文件未包含在压缩包中。

由于浮点精度、舍入和误差累积问题，Windows 与 Linux 生成的混沌序列在约 30 个数后会出现明显差异，因此不同平台的解密结果可能不同。
