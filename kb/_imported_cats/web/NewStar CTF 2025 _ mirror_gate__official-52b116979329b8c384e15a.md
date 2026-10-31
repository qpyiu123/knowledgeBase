---
title: "NewStar CTF 2025 / mirror_gate"
category: web
tags: ["NewStar CTF 2025", "mirror_gate", "web", "官方资料", "docs/wp/2025/week3/web/mirror-gate.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "mirror_gate", "web"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/web/mirror-gate.md"
tools: []
origin: imported_cats
origin_id: "official-52b116979329b8c384e15a"
origin_domain: "web"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
origin_body_sha256: ceb47c2e5878f61d12cb88c07b42ea5e6516b9ee73ffd84a41a78c7484a275bb
origin_title: "NewStar CTF 2025 / mirror_gate"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/week3/web/mirror-gate"
  chunk_ids: [11146]
  content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
  domain: "web"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-52b116979329b8c384e15a"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/86fd89223cdf987d854f74e966a7f46f573fd35fbc276a5a2192ce27357cac90.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/week3/web/mirror-gate.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/web/mirror-gate.md"
  tags: ["NewStar CTF 2025", "mirror_gate", "web", "官方资料", "docs/wp/2025/week3/web/mirror-gate.md"]
  title: "NewStar CTF 2025 / mirror_gate"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / mirror_gate

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/web/mirror-gate.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579
> - 导入 ID：official-52b116979329b8c384e15a
> - 原 domain：web
> - 本地快照：62_官方赛事题库/objects/86fd89223cdf987d854f74e966a7f46f573fd35fbc276a5a2192ce27357cac90.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/web/mirror-gate.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

## mirror_gate

根据提示 `请设法找出他系统中的应用配置缺陷，突破上传限制。`，我们先抓一个响应包，发现存在 `Server: Apache/2.4.51 (Debian)` 头部，
猜测是 `.htaccess`（Apache 配置文件）解析问题。

## 收集信息

访问网站，<kbd>F12</kbd> 查看前端源码发现

上传 jpg 也有 hint：dirsearch

## 漏洞利用

用 dirsearch 扫描 `ip:端口/uploads`，发现 `.htaccess` 返回了 200，印证了我们的猜想。

下载 `.htaccess` 得到

这让上传的 `.webp` 文件被解析成 `php` 类型。

接下来上传 webp 一句话木马，利用解析漏洞让我们的 `.webp` 解析成 php, 从而绕过检查。再简单地绕过一下 waf 就可以，这里打法很多。
