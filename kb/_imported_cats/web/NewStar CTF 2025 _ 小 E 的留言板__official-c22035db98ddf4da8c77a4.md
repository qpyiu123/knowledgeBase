---
title: "NewStar CTF 2025 / 小 E 的留言板"
category: web
tags: ["NewStar CTF 2025", "小 E 的留言板", "web", "官方资料", "docs/wp/2025/week4/web/e-message-board.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "小 E 的留言板", "web"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week4/web/e-message-board.md"
tools: []
origin: imported_cats
origin_id: "official-c22035db98ddf4da8c77a4"
origin_domain: "web"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
origin_body_sha256: 2e024172e61022599990d19748b5d9a764a33c1773b0c53019e4089d7b895309
origin_title: "NewStar CTF 2025 / 小 E 的留言板"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/week4/web/e-message-board"
  chunk_ids: [11396]
  content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
  domain: "web"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 1
  id: "official-c22035db98ddf4da8c77a4"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/d4c4c8f51966ad52ccd79388f9ac8979697d72304d0acdcf029088a840493485.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/week4/web/e-message-board.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week4/web/e-message-board.md"
  tags: ["NewStar CTF 2025", "小 E 的留言板", "web", "官方资料", "docs/wp/2025/week4/web/e-message-board.md"]
  title: "NewStar CTF 2025 / 小 E 的留言板"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / 小 E 的留言板

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week4/web/e-message-board.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579
> - 导入 ID：official-c22035db98ddf4da8c77a4
> - 原 domain：web
> - 本地快照：62_官方赛事题库/objects/d4c4c8f51966ad52ccd79388f9ac8979697d72304d0acdcf029088a840493485.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week4/web/e-message-board.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

## 小 E 的留言板

给了 webhook 很明显要打 XSS。

新建一个用户，随便写点什么提交，发现我们的输入以 input 标签的 value 值被注入了 html

这里上 [Cross-site scripting (XSS) cheat sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet) 找一个 input 元素的 payload 试一下，因为 bot 只是访问页面而不进行任何操作，所以我们就只能通过 `autofocus` + `onfocus` 或闭合标签后制造 `<script>` 标签，我们测试如下。

经过测试 `<` 和 `>` 被过滤，闭合标签不可行。发现 `on` 和 `focus` 也被过滤掉了，但是这里我们可以双写绕过如下：

成功弹窗，然后编写偷 cookie 的 payload，提交并报告留言。

得到 FLAG。
