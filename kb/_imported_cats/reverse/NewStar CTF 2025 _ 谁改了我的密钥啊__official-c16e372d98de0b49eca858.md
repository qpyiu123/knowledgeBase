---
title: "NewStar CTF 2025 / 谁改了我的密钥啊"
category: reverse
tags: ["NewStar CTF 2025", "谁改了我的密钥啊", "reverse", "官方资料", "docs/wp/2025/week3/reverse/who-changed-key.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "谁改了我的密钥啊", "reverse"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/reverse/who-changed-key.md"
tools: []
origin: imported_cats
origin_id: "official-c16e372d98de0b49eca858"
origin_domain: "reverse"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
origin_body_sha256: 45f821f24bc67cf68a7ffe39070e1a108898511da31430dc04fb3a63665647f0
origin_title: "NewStar CTF 2025 / 谁改了我的密钥啊"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/week3/reverse/who-changed-key"
  chunk_ids: [11117]
  content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
  domain: "reverse"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-c16e372d98de0b49eca858"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/be18eeaa71f748718f29e22383cd746f56390161121545130cf75f4e703ee36b.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/week3/reverse/who-changed-key.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/reverse/who-changed-key.md"
  tags: ["NewStar CTF 2025", "谁改了我的密钥啊", "reverse", "官方资料", "docs/wp/2025/week3/reverse/who-changed-key.md"]
  title: "NewStar CTF 2025 / 谁改了我的密钥啊"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / 谁改了我的密钥啊

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/reverse/who-changed-key.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579
> - 导入 ID：official-c16e372d98de0b49eca858
> - 原 domain：reverse
> - 本地快照：62_官方赛事题库/objects/be18eeaa71f748718f29e22383cd746f56390161121545130cf75f4e703ee36b.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/reverse/who-changed-key.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

## 分析

和 `Week2` 安卓一样，加密在 `so` 文件里

由于 `apk` 是 `release` 编译的，所以代码有很多优化，可能有点看不出原样。看到函数列表的 `encryptSM4` 应该也能猜到这题是考查国密 `SM4`。`MK` 其实就是密钥 `{1, 0, 0, 0, 1, 0, 0, 0, 4, 0, 0, 0, 5, 0, 0, 0}`，`mm` 和之后的那几个值是密文。

没有其他的修改，但是网上的 `SM4` 解密网站其实是解不出来的，原因出在端序转化上，注意明文和密钥传入再到加密的数据在内存中是怎么样的。
