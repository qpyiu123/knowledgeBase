---
title: "UCATFLAGS 2024 / Web 3 Fake Flags"
category: web
tags: ["UCATFLAGS 2024", "Web 3 Fake Flags", "web", "官方资料", "wp/web/fakeflags-wp.md", "origin_tag:imported_cats"]
signals: ["UCATFLAGS 2024", "Web 3 Fake Flags", "web"]
difficulty: medium
source: "https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/web/fakeflags-wp.md"
tools: []
origin: imported_cats
origin_id: "official-4aec353ce00d8aa4aff471"
origin_domain: "web"
origin_family: "official_event_archive"
origin_event: "UCATFLAGS 2024"
origin_year: 2024
origin_license: "not_declared"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "be1d53f0437421f2348f7a753083cbf7af8e7019e8d1f819e252541f122e639d"
origin_body_sha256: 981fcf9c81c8a52b8df04998b940045c4223b9bda82db5bc1c5c7bb8d7ebaff4
origin_title: "UCATFLAGS 2024 / Web 3 Fake Flags"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "ucatflags2024:wp/web/fakeflags"
  chunk_ids: [8185]
  content_sha256: "be1d53f0437421f2348f7a753083cbf7af8e7019e8d1f819e252541f122e639d"
  domain: "web"
  domain_basis: "repository_path"
  event: "UCATFLAGS 2024"
  external_links_not_followed: 1
  id: "official-4aec353ce00d8aa4aff471"
  kind: "official_wp_prose"
  language: "zh"
  license: "not_declared"
  local_path: "62_官方赛事题库/objects/8e494f4d257d2bcaec6e6c8476c9109f5cdf1d2be91d51a64ce6630fcb323600.blob"
  official_evidence: "https://github.com/UCAS-CTF/UCATFLAGS-WP"
  original_path: "wp/web/fakeflags-wp.md"
  revision: "b1e667240041738bf1361b555b162b5713be315c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/web/fakeflags-wp.md"
  tags: ["UCATFLAGS 2024", "Web 3 Fake Flags", "web", "官方资料", "wp/web/fakeflags-wp.md"]
  title: "UCATFLAGS 2024 / Web 3 Fake Flags"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# UCATFLAGS 2024 / Web 3 Fake Flags

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/web/fakeflags-wp.md
> - 许可：not_declared
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：UCATFLAGS 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：be1d53f0437421f2348f7a753083cbf7af8e7019e8d1f819e252541f122e639d
> - 导入 ID：official-4aec353ce00d8aa4aff471
> - 原 domain：web
> - 本地快照：62_官方赛事题库/objects/8e494f4d257d2bcaec6e6c8476c9109f5cdf1d2be91d51a64ce6630fcb323600.blob
> - 源修订：b1e667240041738bf1361b555b162b5713be315c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/web/fakeflags-wp.md

## 题目描述

假 flag 太多，你能找到真正的 flag 吗？

## 题目地址

[点我](http://123.249.92.229/3/)

## 题目附件

无

## 考察点

代码审计，脚本编写

## 思路

答案为 UCATFLAGS{mbQ7e_1s_4w3s0m3}
在 http://123.249.92.229/3/actually_flag.php 页面。假 flag 太多，需要自己写脚本爆破。
js 中有很多误导，qwq 函数中有提示页面的真实地址。
