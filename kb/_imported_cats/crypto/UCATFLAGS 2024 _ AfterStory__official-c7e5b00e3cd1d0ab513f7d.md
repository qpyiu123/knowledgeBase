---
title: "UCATFLAGS 2024 / AfterStory"
category: crypto
tags: ["UCATFLAGS 2024", "AfterStory", "crypto", "官方资料", "wp/crypto/AfterStory-wp.md", "origin_tag:imported_cats"]
signals: ["UCATFLAGS 2024", "AfterStory", "crypto"]
difficulty: medium
source: "https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/crypto/AfterStory-wp.md"
tools: []
origin: imported_cats
origin_id: "official-c7e5b00e3cd1d0ab513f7d"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "UCATFLAGS 2024"
origin_year: 2024
origin_license: "not_declared"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "a5370094c839d110da1e80c4052427a0754b02f43ac80fdf76ce8e7b1abb486b"
origin_body_sha256: 92d03926ba86bde80ea7c739eec72e2275508f2c244999649068bc4e3ced8b89
origin_title: "UCATFLAGS 2024 / AfterStory"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "ucatflags2024:wp/crypto/AfterStory"
  chunk_ids: [7856, 7857, 7858]
  content_sha256: "a5370094c839d110da1e80c4052427a0754b02f43ac80fdf76ce8e7b1abb486b"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "UCATFLAGS 2024"
  external_links_not_followed: 0
  id: "official-c7e5b00e3cd1d0ab513f7d"
  kind: "official_wp_prose"
  language: "zh"
  license: "not_declared"
  local_path: "62_官方赛事题库/objects/8ef71e0b5544b672f38c3604783839e2c85cafe87cfca408c18e18445237272b.blob"
  official_evidence: "https://github.com/UCAS-CTF/UCATFLAGS-WP"
  original_path: "wp/crypto/AfterStory-wp.md"
  revision: "b1e667240041738bf1361b555b162b5713be315c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/crypto/AfterStory-wp.md"
  tags: ["UCATFLAGS 2024", "AfterStory", "crypto", "官方资料", "wp/crypto/AfterStory-wp.md"]
  title: "UCATFLAGS 2024 / AfterStory"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# UCATFLAGS 2024 / AfterStory

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/crypto/AfterStory-wp.md
> - 许可：not_declared
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：UCATFLAGS 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：a5370094c839d110da1e80c4052427a0754b02f43ac80fdf76ce8e7b1abb486b
> - 导入 ID：official-c7e5b00e3cd1d0ab513f7d
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/8ef71e0b5544b672f38c3604783839e2c85cafe87cfca408c18e18445237272b.blob
> - 源修订：b1e667240041738bf1361b555b162b5713be315c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/crypto/AfterStory-wp.md

## 题目源码

`AfterStory.c`

{% raw %}
{% endraw %}

`AfterStory.h`

`AfterStory.h`

{% raw %}
{% endraw %}

## 思路分析

注意到 Flag 的格式一定以 `ucatflags{` 开头，而密钥（lfsr产生的数据）是直接异或到 Flag 上的，所以可以获得密钥的前几十位。这几十位恰好能覆盖到初始状态的位数，因此可以直接利用当前获得的前几十位往后使用给定的lfsr进行递推。

## 解题代码

`solve5.c`

{% raw %}
{% endraw %}

`solve5.h`

`solve5.h`

{% raw %}
{% endraw %}

`Makefile`

{% raw %}
{% endraw %}
