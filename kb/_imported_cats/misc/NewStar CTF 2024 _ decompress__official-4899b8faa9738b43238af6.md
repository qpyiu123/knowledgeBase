---
title: "NewStar CTF 2024 / decompress"
category: misc
tags: ["NewStar CTF 2024", "decompress", "misc", "官方资料", "docs/wp/2024/week1/misc/decompress.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "decompress", "misc"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/misc/decompress.md"
tools: []
origin: imported_cats
origin_id: "official-4899b8faa9738b43238af6"
origin_domain: "misc"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
origin_body_sha256: a483cc27d686ae39bedde7b1263a33fd091be42b7cb9ee18bad2a605f237e214
origin_title: "NewStar CTF 2024 / decompress"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week1/misc/decompress"
  chunk_ids: [8464]
  content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
  domain: "misc"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 0
  id: "official-4899b8faa9738b43238af6"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/5b2b2a7ac929975ebd35e1d3943caa5a2b19d38d0f38ad199e8ab82b95eba23f.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week1/misc/decompress.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/misc/decompress.md"
  tags: ["NewStar CTF 2024", "decompress", "misc", "官方资料", "docs/wp/2024/week1/misc/decompress.md"]
  title: "NewStar CTF 2024 / decompress"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / decompress

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/misc/decompress.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d
> - 导入 ID：official-4899b8faa9738b43238af6
> - 原 domain：misc
> - 本地快照：62_官方赛事题库/objects/5b2b2a7ac929975ebd35e1d3943caa5a2b19d38d0f38ad199e8ab82b95eba23f.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/misc/decompress.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

## 校内赛道

解压附件后，使用 7zip 等支持解压分卷压缩包的解压软件双击 `flag.zip.001` 解压即可。

如果你使用 010 Editor 等十六进制文件查看工具，你会发现分卷压缩包仅仅是把一整个压缩包文件按设置好的大小截断成一段段文件所以也可以使用 010 Editor 等软件手动把分卷压缩包拼起来再解压。

## 公开赛道

与校内赛道相比，多了一步爆破压缩包密码的过程。

根据给的正则表达式提示，密码是三位小写字母一位数字再加一位小写字母，共五位。爆破出来是 `xtr4m`.

出题人使用的是不知道从哪下载的 passware，爆破了两分钟就出来了。

有些同学反映自己写脚本爆破不行，出题人用的压缩软件是 7zip，可能是因为每个压缩包分卷太小，7zip 为了防止 CRC 碰撞，压缩包里没有原始的 CRC 校验导致的。这确实是没考虑到的问题。
