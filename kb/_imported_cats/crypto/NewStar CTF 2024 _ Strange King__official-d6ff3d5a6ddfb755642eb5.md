---
title: "NewStar CTF 2024 / Strange King"
category: crypto
tags: ["NewStar CTF 2024", "Strange King", "crypto", "官方资料", "docs/wp/2024/week1/crypto/strange-king.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "Strange King", "crypto"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/crypto/strange-king.md"
tools: []
origin: imported_cats
origin_id: "official-d6ff3d5a6ddfb755642eb5"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "e4948a0ac253ee177ae081b53b30755b98c1551de5c3ef7f429d62eb61a35750"
origin_body_sha256: 48508b19e1b4606820a195e33e0feb54a6c70c647c822d8408921bd75a2d5107
origin_title: "NewStar CTF 2024 / Strange King"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week1/crypto/strange-king"
  chunk_ids: [8437, 8438]
  content_sha256: "e4948a0ac253ee177ae081b53b30755b98c1551de5c3ef7f429d62eb61a35750"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 0
  id: "official-d6ff3d5a6ddfb755642eb5"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/6ac8c48a00f577d56dd5b6708115a315ca313bdfae4acbfe5c9b3f038ced6dbd.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week1/crypto/strange-king.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/crypto/strange-king.md"
  tags: ["NewStar CTF 2024", "Strange King", "crypto", "官方资料", "docs/wp/2024/week1/crypto/strange-king.md"]
  title: "NewStar CTF 2024 / Strange King"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / Strange King

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/crypto/strange-king.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：e4948a0ac253ee177ae081b53b30755b98c1551de5c3ef7f429d62eb61a35750
> - 导入 ID：official-d6ff3d5a6ddfb755642eb5
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/6ac8c48a00f577d56dd5b6708115a315ca313bdfae4acbfe5c9b3f038ced6dbd.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/crypto/strange-king.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

import Container from '@/components/docs/Container.vue'

## Strange King

题目描述如下：

> 某喜欢抽锐刻 5 的皇帝想每天进步一些，直到他娶了个模，回到原点，全部白给😅
> 这是他最后留下的讯息：`ksjr{EcxvpdErSvcDgdgEzxqjql}`，flag 包裹的是可读的明文

不难猜到是魔改的凯撒密码。题目描述中的数字 5 就是**初始偏移量**。「每天进步一些」代表**偏移量在递增**，对 26 取模后会到原点，偏移量每次增加是 26 的因子，此处是 2.

况且出题人连 `{}` 都没删掉，把 `ksjr` 和 `flag` 对照起来看也能看出来了吧！可以说是非常简单的古典密码了）

根据以上信息即可解出 flag
