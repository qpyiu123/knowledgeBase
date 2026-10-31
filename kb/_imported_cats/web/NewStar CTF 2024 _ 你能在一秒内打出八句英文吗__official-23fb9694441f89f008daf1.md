---
title: "NewStar CTF 2024 / 你能在一秒内打出八句英文吗"
category: web
tags: ["NewStar CTF 2024", "你能在一秒内打出八句英文吗", "web", "官方资料", "docs/wp/2024/week2/web/bajuyingwen.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "你能在一秒内打出八句英文吗", "web"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/web/bajuyingwen.md"
tools: []
origin: imported_cats
origin_id: "official-23fb9694441f89f008daf1"
origin_domain: "web"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
origin_body_sha256: 6c99056e2cf293c2f096c995871f594ea488f87ed5635f2328473680a685ca4e
origin_title: "NewStar CTF 2024 / 你能在一秒内打出八句英文吗"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week2/web/bajuyingwen"
  chunk_ids: [8910]
  content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
  domain: "web"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 0
  id: "official-23fb9694441f89f008daf1"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/1e942f1a389d55057e65938b9d0b6372ea85c9de8581b25d9aade78d23e65c77.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week2/web/bajuyingwen.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/web/bajuyingwen.md"
  tags: ["NewStar CTF 2024", "你能在一秒内打出八句英文吗", "web", "官方资料", "docs/wp/2024/week2/web/bajuyingwen.md"]
  title: "NewStar CTF 2024 / 你能在一秒内打出八句英文吗"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / 你能在一秒内打出八句英文吗

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/web/bajuyingwen.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d
> - 导入 ID：official-23fb9694441f89f008daf1
> - 原 domain：web
> - 本地快照：62_官方赛事题库/objects/1e942f1a389d55057e65938b9d0b6372ea85c9de8581b25d9aade78d23e65c77.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week2/web/bajuyingwen.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

## 你能在一秒内打出八句英文吗

经典脚本题，思路：先获取页面中需要输入的英文文本，再提交你获得的的文本。

这里推荐模拟 POST 请求，直接来看 EXP：

`requests` 库可以很方便的进行会话控制，`BeautifulSoup` 可以帮你快速定位文本位置。剩下就是 POST 请求 + 打印回显。

当然，解法很多，你也可以使用 `Selenium` 等库模拟浏览器操作，又或者装一些浏览器插件凭手速把文本直接复制过去再提交，随你喜欢。
