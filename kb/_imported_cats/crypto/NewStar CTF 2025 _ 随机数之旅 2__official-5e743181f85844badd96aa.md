---
title: "NewStar CTF 2025 / 随机数之旅 2"
category: crypto
tags: ["NewStar CTF 2025", "随机数之旅 2", "crypto", "官方资料", "docs/wp/2025/extras/crypto/random-2.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "随机数之旅 2", "crypto"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/extras/crypto/random-2.md"
tools: []
origin: imported_cats
origin_id: "official-5e743181f85844badd96aa"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
origin_body_sha256: 95b88bc0dbc915ac1690a14632c702813eb63c6fa7a7614c4efac2193ebd4587
origin_title: "NewStar CTF 2025 / 随机数之旅 2"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/extras/crypto/random-2"
  chunk_ids: [10035]
  content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-5e743181f85844badd96aa"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/aea099bfd8c2732840bae223a0678b1392d584fb8a845c2d8d706df751a04bde.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/extras/crypto/random-2.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/extras/crypto/random-2.md"
  tags: ["NewStar CTF 2025", "随机数之旅 2", "crypto", "官方资料", "docs/wp/2025/extras/crypto/random-2.md"]
  title: "NewStar CTF 2025 / 随机数之旅 2"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / 随机数之旅 2

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/extras/crypto/random-2.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579
> - 导入 ID：official-5e743181f85844badd96aa
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/aea099bfd8c2732840bae223a0678b1392d584fb8a845c2d8d706df751a04bde.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/extras/crypto/random-2.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

## 随机数之旅 2

魔改 mt19937，但 temper 段简化了：

只需要逆向 temper 段，即可恢复完整的 `self.mt`，随后再输出 11 个随机数即可解密。

下面给出用于逆向 temper 段并恢复密钥的脚本：

补充说明：为什么恢复 `self.mt` 后可以直接输出 11 个随机数解密，而不需要先跳过 114 个数？

原因如下：

`self.mti` 默认是0，当我们导入 `self.mt`（`aa.mt=mt_rec`）时，就已经帮我们过掉了。
