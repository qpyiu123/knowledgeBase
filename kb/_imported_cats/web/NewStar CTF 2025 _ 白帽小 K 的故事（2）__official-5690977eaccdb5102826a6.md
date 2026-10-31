---
title: "NewStar CTF 2025 / 白帽小 K 的故事（2）"
category: web
tags: ["NewStar CTF 2025", "白帽小 K 的故事（2）", "web", "官方资料", "docs/wp/2025/week3/web/white-k-2.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "白帽小 K 的故事（2）", "web"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/web/white-k-2.md"
tools: []
origin: imported_cats
origin_id: "official-5690977eaccdb5102826a6"
origin_domain: "web"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
origin_body_sha256: 1d2f1942b6067ff540f9565a3e39b33f6d9efefce87d31f268670b93b0c394a1
origin_title: "NewStar CTF 2025 / 白帽小 K 的故事（2）"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/week3/web/white-k-2"
  chunk_ids: [11160]
  content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
  domain: "web"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-5690977eaccdb5102826a6"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/455bd26999f09dbf5c32847f1bf86b7cc7c964275dbd1f9b9829a105d1fad3f7.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/week3/web/white-k-2.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/web/white-k-2.md"
  tags: ["NewStar CTF 2025", "白帽小 K 的故事（2）", "web", "官方资料", "docs/wp/2025/week3/web/white-k-2.md"]
  title: "NewStar CTF 2025 / 白帽小 K 的故事（2）"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / 白帽小 K 的故事（2）

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/web/white-k-2.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579
> - 导入 ID：official-5690977eaccdb5102826a6
> - 原 domain：web
> - 本地快照：62_官方赛事题库/objects/455bd26999f09dbf5c32847f1bf86b7cc7c964275dbd1f9b9829a105d1fad3f7.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week3/web/white-k-2.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

## 白帽小 K 的故事（2）

这是一道 SQL 盲注题目，跟随流程，查看 hint，给了两点提示

1. 后端查询逻辑是 `SELECT 1 from Terra.animal WHERE name = '$name'`
2. 要使用盲注

这提示我们

这提示我们

1. 可以利用 `'` 闭合达成 SQL 注入
2. 注入后响应不包含 sql 语句执行结果或原始报错

简单手动 fuzz 一下 waf，发现只过滤了空格（抓包返回 `{"status":"error","message":"Invalid characters detected"}`），我们用括号绕过就行。

我们构造 `amiya'AND(${payload})#`，由于用户 amiya 存在，`WHERE name = 'amiya'` 为真，此时 `payload` 的真假决定了表达式的返回，如果 `payload` 为真，应当返回正常登录的结果，反之，则会返回用户不存在。这就符合了**布尔盲注**的条件。

由于手动盲注耗时长，我们需要编写脚本去自动完成盲注，通常我们会使用二分搜索算法和多线程来优化盲注速度。这里给出我的解题脚本：
