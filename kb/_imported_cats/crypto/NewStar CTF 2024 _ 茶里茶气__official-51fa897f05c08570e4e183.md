---
title: "NewStar CTF 2024 / 茶里茶气"
category: crypto
tags: ["NewStar CTF 2024", "茶里茶气", "crypto", "官方资料", "docs/wp/2024/week2/crypto/chalichaqi.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "茶里茶气", "crypto"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/crypto/chalichaqi.md"
tools: []
origin: imported_cats
origin_id: "official-51fa897f05c08570e4e183"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
origin_body_sha256: 4099826712c33d92185f27684bda2393acf17eb6527df302d8b58d09623fd19f
origin_title: "NewStar CTF 2024 / 茶里茶气"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week2/crypto/chalichaqi"
  chunk_ids: [8663]
  content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 0
  id: "official-51fa897f05c08570e4e183"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/617844e2723791fc8e967c51fd300d95b88461f4bfe78b8d7f10983f86f04043.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week2/crypto/chalichaqi.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/crypto/chalichaqi.md"
  tags: ["NewStar CTF 2024", "茶里茶气", "crypto", "官方资料", "docs/wp/2024/week2/crypto/chalichaqi.md"]
  title: "NewStar CTF 2024 / 茶里茶气"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / 茶里茶气

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/crypto/chalichaqi.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d
> - 导入 ID：official-51fa897f05c08570e4e183
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/617844e2723791fc8e967c51fd300d95b88461f4bfe78b8d7f10983f86f04043.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/crypto/chalichaqi.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

## 茶里茶气

简单的 TEA（Tiny Encryption Algorithm）加密算法

只需要逆推一下过程，然后把字符串拼接在一起转成字符即可

对于 `v2` 这个变量，先进行正推得到最终值，再倒退进行解密<span data-desc>（数量级不大，使用乘法和加法都可以）</span>

注意每一步都要取模
