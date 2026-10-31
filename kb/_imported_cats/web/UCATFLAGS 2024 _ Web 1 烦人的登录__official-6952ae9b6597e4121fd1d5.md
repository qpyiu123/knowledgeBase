---
title: "UCATFLAGS 2024 / Web 1 烦人的登录"
category: web
tags: ["UCATFLAGS 2024", "Web 1 烦人的登录", "web", "官方资料", "wp/web/烦人的登录-wp.md", "origin_tag:imported_cats"]
signals: ["UCATFLAGS 2024", "Web 1 烦人的登录", "web"]
difficulty: medium
source: "https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/web/%E7%83%A6%E4%BA%BA%E7%9A%84%E7%99%BB%E5%BD%95-wp.md"
tools: []
origin: imported_cats
origin_id: "official-6952ae9b6597e4121fd1d5"
origin_domain: "web"
origin_family: "official_event_archive"
origin_event: "UCATFLAGS 2024"
origin_year: 2024
origin_license: "not_declared"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "b56dfc1f8246ed56ed0e424e6701eec75a315554b8284991ff6fac20a52142cf"
origin_body_sha256: ea04579119646b7ead9ee03aa86517c14183fc93fad1516356f5f5632db763a2
origin_title: "UCATFLAGS 2024 / Web 1 烦人的登录"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "ucatflags2024:wp/web/烦人的登录"
  chunk_ids: [8198]
  content_sha256: "b56dfc1f8246ed56ed0e424e6701eec75a315554b8284991ff6fac20a52142cf"
  domain: "web"
  domain_basis: "repository_path"
  event: "UCATFLAGS 2024"
  external_links_not_followed: 1
  id: "official-6952ae9b6597e4121fd1d5"
  kind: "official_wp_prose"
  language: "zh"
  license: "not_declared"
  local_path: "62_官方赛事题库/objects/0ae91a8cdf0cdf8c5a538858f138b0d30a99928b89415965021fb222844d1750.blob"
  official_evidence: "https://github.com/UCAS-CTF/UCATFLAGS-WP"
  original_path: "wp/web/烦人的登录-wp.md"
  revision: "b1e667240041738bf1361b555b162b5713be315c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/web/%E7%83%A6%E4%BA%BA%E7%9A%84%E7%99%BB%E5%BD%95-wp.md"
  tags: ["UCATFLAGS 2024", "Web 1 烦人的登录", "web", "官方资料", "wp/web/烦人的登录-wp.md"]
  title: "UCATFLAGS 2024 / Web 1 烦人的登录"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# UCATFLAGS 2024 / Web 1 烦人的登录

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/web/%E7%83%A6%E4%BA%BA%E7%9A%84%E7%99%BB%E5%BD%95-wp.md
> - 许可：not_declared
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：UCATFLAGS 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：b56dfc1f8246ed56ed0e424e6701eec75a315554b8284991ff6fac20a52142cf
> - 导入 ID：official-6952ae9b6597e4121fd1d5
> - 原 domain：web
> - 本地快照：62_官方赛事题库/objects/0ae91a8cdf0cdf8c5a538858f138b0d30a99928b89415965021fb222844d1750.blob
> - 源修订：b1e667240041738bf1361b555b162b5713be315c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/UCAS-CTF/UCATFLAGS-WP/blob/b1e667240041738bf1361b555b162b5713be315c/wp/web/%E7%83%A6%E4%BA%BA%E7%9A%84%E7%99%BB%E5%BD%95-wp.md

## 题目描述

这个网站的登录页面很烦人，你能绕过它吗？

## 题目地址

[点击这里](http://123.249.92.229/Ques1/)

## 前置知识

本题目不需要任何前置知识。但如果你知道有关控制台的知识则能更快的解决这个问题。

## 解题方式

1. 打开题目地址，进入登录页面。
2. 不断尝试登录，直到通过验证。

## 注意事项

1. 唯一没有给出明确提示的验证是：

2. 你可以通过控制台绕过下方的勾选框验证，其代码为：

在控制台输入 `checkedCount = 6` 即可绕过验证…… 才怪，还有 `if_opened` 要等于 `1`。
3\. 密码输入与学号输入均设置了不可复制，因此出于 "人道主义"，没有设置每次清空密码，因此建议一次性做完，不要刷新页面。
4\. 本题目的 flag 为 `UCTAFLAGS{1s_th1s_4_r3al_1nput_v4l1d4t10n?}`
5\. 密码的验证分别为：

* 长度在 `16` 到 `30` 之间。
* 有且一定是字母、数字、以及 `.#$@!^%&\*()/,<>\~\` 和 ` 字符至少三种。
* 不能有空格。
* 无连续相同字符。
* 没有递增或递减的字符。
* 没有连续的数字。
* 密码内数字的每一位相加，其和应等于密码长度。
* 只能使用学号中出现的数字。
* 密码中含有 factorio 字符串。

6. 本题验证码存在 `_SESSION` 中，所以只能老老实实的输入验证码。
7. 灵感来源于国科大平台的更改密码。

下附本题完整逻辑：
