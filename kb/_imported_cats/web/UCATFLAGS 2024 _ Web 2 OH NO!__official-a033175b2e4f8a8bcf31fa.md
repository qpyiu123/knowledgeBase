---
title: "UCATFLAGS 2024 / Web 2 OH NO!"
category: web
tags: ["UCATFLAGS 2024", "Web 2 OH NO!", "web", "官方资料", "wp/web/ohno-wp.md", "origin_tag:imported_cats"]
signals: ["UCATFLAGS 2024", "Web 2 OH NO!", "web"]
difficulty: medium
source: "https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/web/ohno-wp.md"
tools: []
origin: imported_cats
origin_id: "official-a033175b2e4f8a8bcf31fa"
origin_domain: "web"
origin_family: "official_event_archive"
origin_event: "UCATFLAGS 2024"
origin_year: 2024
origin_license: "not_declared"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "93e008690b28ee8a1dba73189f6e27779c6bd8696d3175e1bb965f3304b49f5f"
origin_body_sha256: a683297db75a75d67db9c3fbd92d063ba17e5b936ab0075414e67de520d505b1
origin_title: "UCATFLAGS 2024 / Web 2 OH NO!"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "ucatflags2024:wp/web/ohno"
  chunk_ids: [8190]
  content_sha256: "93e008690b28ee8a1dba73189f6e27779c6bd8696d3175e1bb965f3304b49f5f"
  domain: "web"
  domain_basis: "repository_path"
  event: "UCATFLAGS 2024"
  external_links_not_followed: 3
  id: "official-a033175b2e4f8a8bcf31fa"
  kind: "official_wp_prose"
  language: "zh"
  license: "not_declared"
  local_path: "62_官方赛事题库/objects/6a6e2f2879e6431d68ae43df5ccd0e1d495076035437477dbbd803dd84e6782b.blob"
  official_evidence: "https://github.com/UCAS-CTF/UCATFLAGS-WP"
  original_path: "wp/web/ohno-wp.md"
  revision: "b1e667240041738bf1361b555b162b5713be315c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/web/ohno-wp.md"
  tags: ["UCATFLAGS 2024", "Web 2 OH NO!", "web", "官方资料", "wp/web/ohno-wp.md"]
  title: "UCATFLAGS 2024 / Web 2 OH NO!"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# UCATFLAGS 2024 / Web 2 OH NO!

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/web/ohno-wp.md
> - 许可：not_declared
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：UCATFLAGS 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：93e008690b28ee8a1dba73189f6e27779c6bd8696d3175e1bb965f3304b49f5f
> - 导入 ID：official-a033175b2e4f8a8bcf31fa
> - 原 domain：web
> - 本地快照：62_官方赛事题库/objects/6a6e2f2879e6431d68ae43df5ccd0e1d495076035437477dbbd803dd84e6782b.blob
> - 源修订：b1e667240041738bf1361b555b162b5713be315c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/web/ohno-wp.md

## 题目描述

不是，什么玩意儿？

## 题目地址

[点我](http://123.249.92.229/2/2.php)

## 题目附件

[点我](http://123.249.92.229/2/gen.py)

## 考察点

php 代码审计

## 思路

`gen.py` 给了充分的提示和解题方式。访问 [网址](http://123.249.92.229/2/2.php?input=(%22]%22^%22;%22).(%22@%22^%22,%22).(%22_%22^%22%3E%22).(%22%3C%22^%22[%22)) 即可得到 flag。

对应的 payload 为 `?input=("]"^";").("@"^",").("_"^">").("<"^"[")`。

即用异或运算来绕过禁止使用字母与数字的过滤。

即用异或运算来绕过禁止使用字母与数字的过滤。

去混淆与无效代码后的代码为：
