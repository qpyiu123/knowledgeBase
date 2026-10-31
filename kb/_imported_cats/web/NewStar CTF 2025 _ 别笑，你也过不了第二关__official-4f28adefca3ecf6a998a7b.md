---
title: "NewStar CTF 2025 / 别笑，你也过不了第二关"
category: web
tags: ["NewStar CTF 2025", "别笑，你也过不了第二关", "web", "官方资料", "docs/wp/2025/week1/web/no-laugh.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "别笑，你也过不了第二关", "web"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week1/web/no-laugh.md"
tools: []
origin: imported_cats
origin_id: "official-4f28adefca3ecf6a998a7b"
origin_domain: "web"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
origin_body_sha256: 8573b83eda3180892a623fe63b25763aae5e9468087aa6828f5e7eea9ada21c1
origin_title: "NewStar CTF 2025 / 别笑，你也过不了第二关"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/week1/web/no-laugh"
  chunk_ids: [10488, 10489]
  content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
  domain: "web"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-4f28adefca3ecf6a998a7b"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/b693c790b407e1241fd38058fc4bb0c0eaa35016f6f86b7f7e8647927ccfa677.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/week1/web/no-laugh.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week1/web/no-laugh.md"
  tags: ["NewStar CTF 2025", "别笑，你也过不了第二关", "web", "官方资料", "docs/wp/2025/week1/web/no-laugh.md"]
  title: "NewStar CTF 2025 / 别笑，你也过不了第二关"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / 别笑，你也过不了第二关

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week1/web/no-laugh.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761
> - 导入 ID：official-4f28adefca3ecf6a998a7b
> - 原 domain：web
> - 本地快照：62_官方赛事题库/objects/b693c790b407e1241fd38058fc4bb0c0eaa35016f6f86b7f7e8647927ccfa677.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week1/web/no-laugh.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

import Container from '@/components/docs/Container.vue'

## 别笑，你也过不了第二关

本题考查前端源代码分析、HTTP 协议参数 HTTP 请求报文的发送。

先打开游戏随便玩玩，发现第二关目标分数 1000000，无法正常完成。

## 收集信息

但是这是一道 web 题，所以我们开始收集信息 <kbd>Ctrl</kbd> + <kbd>U</kbd> 打开源代码审阅，发现游戏的主要逻辑在最后的 `script` 标签中，我们找到判断通关的逻辑：

阅读代码可以知道通关时，`endLevel()` 会被调用，我们的分数被提交到 `flag.php`，服务器根据分数返回不同内容。

## 解题

法一：在浏览器控制台修改前端分数

法二：模拟POST请求

法三：通过抓包工具修改

法三：通过抓包工具修改

但是要注意

举例：
