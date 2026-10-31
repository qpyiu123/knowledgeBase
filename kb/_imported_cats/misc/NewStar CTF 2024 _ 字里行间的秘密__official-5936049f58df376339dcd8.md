---
title: "NewStar CTF 2024 / 字里行间的秘密"
category: misc
tags: ["NewStar CTF 2024", "字里行间的秘密", "misc", "官方资料", "docs/wp/2024/week2/misc/zilihangjian.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "字里行间的秘密", "misc"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/misc/zilihangjian.md"
tools: []
origin: imported_cats
origin_id: "official-5936049f58df376339dcd8"
origin_domain: "misc"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
origin_body_sha256: 5863a58c4dec970ac6d8a822e9ee6d0fe9509ef71b82db2a290b5f9c7090d187
origin_title: "NewStar CTF 2024 / 字里行间的秘密"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week2/misc/zilihangjian"
  chunk_ids: [8774]
  content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
  domain: "misc"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 1
  id: "official-5936049f58df376339dcd8"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/b57d06614f6cd30e31b57c8f5a0013b80ad4d8711519e2e140ecab20b5917ec3.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week2/misc/zilihangjian.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/misc/zilihangjian.md"
  tags: ["NewStar CTF 2024", "字里行间的秘密", "misc", "官方资料", "docs/wp/2024/week2/misc/zilihangjian.md"]
  title: "NewStar CTF 2024 / 字里行间的秘密"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / 字里行间的秘密

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/misc/zilihangjian.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d
> - 导入 ID：official-5936049f58df376339dcd8
> - 原 domain：misc
> - 本地快照：62_官方赛事题库/objects/b57d06614f6cd30e31b57c8f5a0013b80ad4d8711519e2e140ecab20b5917ec3.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/misc/zilihangjian.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

## 字里行间的秘密

题目描述为：

> 我横竖睡不着，仔细看了半夜，才从字缝里看出字来

打开附件，一个名为 flag 的 Word 文件，一个 `key.txt`.

Word 文件被加密，打开 `key.txt`，文字有明显的水印特征，放到 vim 或 VSCode 就能看出存在零宽隐写，放到[在线网站](https://www.mzy0.com/ctftools/zerowidth1/)默认参数，可以拿到 key `it_is_k3y`.

然后打开 Word 发现没有flag，但 <kbd>^ Ctrl</kbd><kbd>A</kbd> 全选发现第二行还是有内容的，将字体改为黑色就可发现 flag.
