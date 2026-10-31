---
title: "NewStar CTF 2025 / 眼熟的计算器"
category: web
tags: ["NewStar CTF 2025", "眼熟的计算器", "web", "官方资料", "docs/wp/2025/week5/web/familiar-calc.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "眼熟的计算器", "web"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week5/web/familiar-calc.md"
tools: []
origin: imported_cats
origin_id: "official-ac31cb7706c91ad582833e"
origin_domain: "web"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
origin_body_sha256: b4f2c00543cd2768efce2c35ce1d9570df9ede5ba2749648617868b510b39e8c
origin_title: "NewStar CTF 2025 / 眼熟的计算器"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/week5/web/familiar-calc"
  chunk_ids: [11740]
  content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
  domain: "web"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-ac31cb7706c91ad582833e"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/cd1986beca9539437ce3a9a31d1b6dc8089ccab4426e14d4d795e805a0ef9587.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/week5/web/familiar-calc.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week5/web/familiar-calc.md"
  tags: ["NewStar CTF 2025", "眼熟的计算器", "web", "官方资料", "docs/wp/2025/week5/web/familiar-calc.md"]
  title: "NewStar CTF 2025 / 眼熟的计算器"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / 眼熟的计算器

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week5/web/familiar-calc.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579
> - 导入 ID：official-ac31cb7706c91ad582833e
> - 原 domain：web
> - 本地快照：62_官方赛事题库/objects/cd1986beca9539437ce3a9a31d1b6dc8089ccab4426e14d4d795e805a0ef9587.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week5/web/familiar-calc.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

## 初步审计

对于 CTF 中的白盒 JAVA 题目，一般有两种出题手法，第一种是直接给一个 jar 包，另一种是给一个 tomcat 的 war 包，分别对应了两种不同的做题思路，这里只讲如何处理 jar 包的形式。

一般而言，题目给的 jar 包都是以 spring 为框架的 JAVA 后端程序，如果你安装了 IDEA，那么可以通过导入依赖的形式来简单的反编译出源码，然后进行审计。

一般而言，我们需要首先查看该程序的依赖，一般存放在 `/META-INF/maven/xxx/xxx/pom.xml` 这个文件中，通过审计这个文件我们可以完整的得知整个 jar 包的依赖和版本情况，这一点与 NodeJS 后端审计是非常相似的。

但是本题中并没有考查依赖相关的事项，我们可以直接去到源码处查看。

一般而言，源码存放在 `/BOOT-INF/classes` 文件目录下，由于是编译过后的 `.class` 文件，我们需要使用反编译器进行反编译操作，一般的 JAVA 编辑器都可以胜任这个工作。（如果你还会一点安卓的话，你也可以使用 jadx 完成上述操作）

本题的源码存在这样一个函数：

本题的源码存在这样一个函数：

我们只需要去理解这里的代码做了一个什么操作就行。

他将我们输入的 `content` 进行了黑名单的过滤，然后使用 `ScrEngineManager` 对象，使用 `js` 类型来进行处理，并且将结果输出出来。

## 漏洞利用

其实这个漏洞利用起来非常简单，无比类似于之前大家做过的 jail 题目，只是环境从 python 换到了 JAVA 而已，通过本地的尝试，我们可以给出这样一个 payload：

JAVA 中也有很多有意思的这种类型的 jail 可以出的更加有意思，期待各位未来的创造力。
