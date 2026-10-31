---
title: "GeekGame 2024 / [Web] ICS笑传之查查表"
category: web
tags: ["GeekGame 2024", "[Web] ICS笑传之查查表", "web", "官方资料", "official_writeup/web-memos/README.md", "origin_tag:imported_cats"]
signals: ["GeekGame 2024", "[Web] ICS笑传之查查表", "web"]
difficulty: medium
source: "https://github.com/PKU-GeekGame/geekgame-4th/blob/a21d7f7387512ec7ef77720e998d60efa16f2353/official_writeup/web-memos/README.md"
tools: []
origin: imported_cats
origin_id: "official-b1bc1ed4475dd843fcc30d"
origin_domain: "web"
origin_family: "official_event_archive"
origin_event: "GeekGame 2024"
origin_year: 2024
origin_license: "not_declared"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "3ca71675e732e4ebd32e7705ab6df6aec0c4dca3dd87e68d1ca5cecde8c8024d"
origin_body_sha256: 84745370704a6cb4846fda51876b4458006ec92b488c128e75f001c78abf0bc1
origin_title: "GeekGame 2024 / [Web] ICS笑传之查查表"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "geekgame2024:official_writeup/web-memos"
  chunk_ids: [7613]
  content_sha256: "3ca71675e732e4ebd32e7705ab6df6aec0c4dca3dd87e68d1ca5cecde8c8024d"
  domain: "web"
  domain_basis: "repository_path"
  event: "GeekGame 2024"
  external_links_not_followed: 3
  id: "official-b1bc1ed4475dd843fcc30d"
  kind: "official_wp_prose"
  language: "zh"
  license: "not_declared"
  local_path: "62_官方赛事题库/objects/34f3963d9a3c837f96a6282772ceaaaf7109ec161c4dca4e2f09013dccb36cca.blob"
  official_evidence: "https://github.com/PKU-GeekGame/geekgame-4th"
  original_path: "official_writeup/web-memos/README.md"
  revision: "a21d7f7387512ec7ef77720e998d60efa16f2353"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/PKU-GeekGame/geekgame-4th/blob/a21d7f7387512ec7ef77720e998d60efa16f2353/official_writeup/web-memos/README.md"
  tags: ["GeekGame 2024", "[Web] ICS笑传之查查表", "web", "官方资料", "official_writeup/web-memos/README.md"]
  title: "GeekGame 2024 / [Web] ICS笑传之查查表"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# GeekGame 2024 / [Web] ICS笑传之查查表

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/PKU-GeekGame/geekgame-4th/blob/a21d7f7387512ec7ef77720e998d60efa16f2353/official_writeup/web-memos/README.md
> - 许可：not_declared
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：GeekGame 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：3ca71675e732e4ebd32e7705ab6df6aec0c4dca3dd87e68d1ca5cecde8c8024d
> - 导入 ID：official-b1bc1ed4475dd843fcc30d
> - 原 domain：web
> - 本地快照：62_官方赛事题库/objects/34f3963d9a3c837f96a6282772ceaaaf7109ec161c4dca4e2f09013dccb36cca.blob
> - 源修订：a21d7f7387512ec7ef77720e998d60efa16f2353
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/PKU-GeekGame/geekgame-4th/blob/a21d7f7387512ec7ef77720e998d60efa16f2353/official_writeup/web-memos/README.md

## [Web] ICS笑传之查查表

- 命题人：thezzisu
- 题目分值：350 分

## 题目描述

**【网页链接：访问题目网页】**

## 预期解法

预期解是通过[Memos User Service](https://github.com/usememos/memos/blob/c3cb3770cce4771d74f2e515aa7bc4e4653c002a/server/router/api/v1/user_service.go#L223)中的逻辑缺陷来修改自己的Role为Host，这样即可通过修改密码登录到管理员账号。

然而，最新的Memos源码中，该问题并不会被触发，因为[其ORM实现的另一个问题](https://github.com/usememos/memos/blob/c3cb3770cce4771d74f2e515aa7bc4e4653c002a/store/db/sqlite/user.go#L32)导致Role字段无法更新。本题中，ORM里的设置漏洞被修复，所以上述方法可以成功提权。修改的代码如下：

然而，Memos本身对Memo的查询API也存在筛选缺陷，这个在比赛期间就被[修复](https://github.com/usememos/memos/commit/b4d72e334993c372ec1567362b8f1f75a9f77122)。所以，本题的难度大大降低，从快乐源码审计题变为了快乐源码搜索题。

感谢诸位选手为开源社区做出的贡献。
