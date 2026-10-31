---
title: "NewStar CTF 2025 / 小 W 和小 K 的故事（最终章）"
category: web
tags: ["NewStar CTF 2025", "小 W 和小 K 的故事（最终章）", "web", "官方资料", "docs/wp/2025/week5/web/w-k-story-final.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "小 W 和小 K 的故事（最终章）", "web"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week5/web/w-k-story-final.md"
tools: []
origin: imported_cats
origin_id: "official-901500bbdce8671a2663b7"
origin_domain: "web"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
origin_body_sha256: 02122888dc0e83d1dfd26abad760f67481bd412ce3b04f338fa0e5c3316fd04a
origin_title: "NewStar CTF 2025 / 小 W 和小 K 的故事（最终章）"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/week5/web/w-k-story-final"
  chunk_ids: [11751]
  content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
  domain: "web"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-901500bbdce8671a2663b7"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/cec7376a73f3895c8f3cc14feb44f4ed77116205d2c0edca51eb17a34f8339b2.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/week5/web/w-k-story-final.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week5/web/w-k-story-final.md"
  tags: ["NewStar CTF 2025", "小 W 和小 K 的故事（最终章）", "web", "官方资料", "docs/wp/2025/week5/web/w-k-story-final.md"]
  title: "NewStar CTF 2025 / 小 W 和小 K 的故事（最终章）"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / 小 W 和小 K 的故事（最终章）

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week5/web/w-k-story-final.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579
> - 导入 ID：official-901500bbdce8671a2663b7
> - 原 domain：web
> - 本地快照：62_官方赛事题库/objects/cec7376a73f3895c8f3cc14feb44f4ed77116205d2c0edca51eb17a34f8339b2.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week5/web/w-k-story-final.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

## 初步审计

在 CTF 中遇到 NodeJS 相关题目有很多固定的起始套路，我们一般可以根据这些套路先对环境进行初步的处理。

第一步为查看环境状态，众所周知，NodeJS 后端基本上是由一个个组件作为基础支撑搭建起来的，组件漏洞或者说供应链漏洞是非常常见的漏洞类型之一，在下发的 `src` 中，存在一个名为 `package.json` 的文件，这个文件中表明了该后端服务所使用的组件以及其版本。我们可以针对性的对这些组件进行搜索，如果其格式如 `"express": "^5.1.0"`，表明会自动拉取该组件**最新**的版本，如果没有 `^`，那么就会拉取一个**精确**的版本。

在本题中，这个知识点表现在 ejs 组件和 lodash 组件拉取的并不是最新版本，我们可以上网搜索这些组件该版本下是否存在漏洞。

通过搜索可以得到两个结果，分别是 CVE-2019-10744 和 CVE-2022-29078。通过这两个 CVE，我们再来完成这道题目，就轻而易举了。

## 漏洞利用。

首先，我们可以通过 `/addUser` 路由来进行任意的原型链污染操作，然后根据 CVE-2022-29078，由于 ejs 在进行模板渲染的时候，`outputFunctionName` 成员默认为空，所以直接用原型链污染为他赋值，然后植入我们的恶意代码就可以了。

最终 payload：

然后反复访问页面即可。

然后反复访问页面即可。

由于是无回显 RCE，所以你需要反弹 shell。但是因为镜像的原因，你需要使用 nc 来进行反弹 shell，具体操作留给读者自查。
