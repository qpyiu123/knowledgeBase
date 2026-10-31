---
title: "NewStar CTF 2024 / ez_jail"
category: misc
tags: ["NewStar CTF 2024", "ez_jail", "misc", "官方资料", "docs/wp/2024/week3/misc/ez_jail.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "ez_jail", "misc"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/misc/ez_jail.md"
tools: []
origin: imported_cats
origin_id: "official-7805bcc740d33caf99f391"
origin_domain: "misc"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "e4948a0ac253ee177ae081b53b30755b98c1551de5c3ef7f429d62eb61a35750"
origin_body_sha256: 296f3959a26914e757e06836f4bf5e4f88456fff61ad6b02bfb9a0739533e1d0
origin_title: "NewStar CTF 2024 / ez_jail"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week3/misc/ez_jail"
  chunk_ids: [9018, 9019]
  content_sha256: "e4948a0ac253ee177ae081b53b30755b98c1551de5c3ef7f429d62eb61a35750"
  domain: "misc"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 0
  id: "official-7805bcc740d33caf99f391"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/696f72882747b337e96c7e7094204d2cfeb9d275679cccd67e8d226013ca413e.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week3/misc/ez_jail.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/misc/ez_jail.md"
  tags: ["NewStar CTF 2024", "ez_jail", "misc", "官方资料", "docs/wp/2024/week3/misc/ez_jail.md"]
  title: "NewStar CTF 2024 / ez_jail"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / ez_jail

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/misc/ez_jail.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：e4948a0ac253ee177ae081b53b30755b98c1551de5c3ef7f429d62eb61a35750
> - 导入 ID：official-7805bcc740d33caf99f391
> - 原 domain：misc
> - 本地快照：62_官方赛事题库/objects/696f72882747b337e96c7e7094204d2cfeb9d275679cccd67e8d226013ca413e.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/misc/ez_jail.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

import Container from '@/components/docs/Container.vue'

## ez_jail

本题的原意是只考查 `{}` 在 C++ 里的（宏）替代运算符这个知识

只要关键词用得对，网上一搜就能搜到，但是被出题人执行坏了，测题时出现了一堆非预期。考虑了一下各个知识点的难度，感觉非预期的难度和预期解相差不大，就索性变成了一道半开放性的题目

我们观察代码的 `check` 函数

我们观察代码的 `check` 函数

这段代码看似过滤了 `#include` `#define` 等，但不知道同学们有没有意识到 `#` 后加空格就能绕过这里，也就是说可以通过宏定义来做到编译前预处理

所以 Payload 可以是这样<span data-desc>（感谢 yuro 师傅提供解法）</span>

预期解是找到 C++ 的替代运算符的相关资料，然后使用 `<% %>` 替换`{}`，Payload 如下

除此之外，还可以使用指针，把 `user_code()` 变成一个空函数。输出的话可以通过定义一个全局变量接收输出函数的返回值来实现，其 payload 如下<span data-desc>（感谢 c_lby 师傅提供解法）</span>

或者可以这样<span data-desc>（感谢 KAMIYA 选手提供解法）</span>
