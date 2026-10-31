---
title: "NewStar CTF 2024 / Game"
category: pwn
tags: ["NewStar CTF 2024", "Game", "pwn", "官方资料", "docs/wp/2024/week1/pwn/game.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "Game", "pwn"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/pwn/game.md"
tools: []
origin: imported_cats
origin_id: "official-ec68de50982447b5c21ea7"
origin_domain: "pwn"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "e4948a0ac253ee177ae081b53b30755b98c1551de5c3ef7f429d62eb61a35750"
origin_body_sha256: 7dfe247c91f570c412f485772b00917dcf7ffd3e201e9429ebfca70c9a0145fb
origin_title: "NewStar CTF 2024 / Game"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week1/pwn/game"
  chunk_ids: [8492, 8493]
  content_sha256: "e4948a0ac253ee177ae081b53b30755b98c1551de5c3ef7f429d62eb61a35750"
  domain: "pwn"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 0
  id: "official-ec68de50982447b5c21ea7"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/26b6ab348c5f1fcd34a60ab17b77fd3f7466b1b74e92a149dcc1bbc12878603b.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week1/pwn/game.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/pwn/game.md"
  tags: ["NewStar CTF 2024", "Game", "pwn", "官方资料", "docs/wp/2024/week1/pwn/game.md"]
  title: "NewStar CTF 2024 / Game"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / Game

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/pwn/game.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：e4948a0ac253ee177ae081b53b30755b98c1551de5c3ef7f429d62eb61a35750
> - 导入 ID：official-ec68de50982447b5c21ea7
> - 原 domain：pwn
> - 本地快照：62_官方赛事题库/objects/26b6ab348c5f1fcd34a60ab17b77fd3f7466b1b74e92a149dcc1bbc12878603b.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/pwn/game.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

import Container from '@/components/docs/Container.vue'

## Game

本题主要考查 `pwntools` 库中 `recv` 和 `send` 的使用

## 解法一

在 5 秒时间内，只能输入小于等于 10 的数，使这些数字相加大于 999.

所以手动输入就不可能了（当然也可以搞个宏什么的？）。

写 Python 脚本即可。

## 解法二

另一种解法，可以利用 `scanf` 函数的 `%d` 格式解析特性。

`scanf` 在解析 `%d` 遇到非数字的时候，会停止解析，但不会抛出异常，会直接返回目前的结果。

比如下面这个语句：

比如下面这个语句：

假设 `value` 原本是 `10`，如果输入 `1a`，那么会解析到 `1` 的输入，而忽略后面的`a`，这时候 `value` 会被变成 `1`.

如果不输入数字，直接输入 `a`，这时候，`scanf` 什么数字也解析不到，也就无法对 `value` 做修改。是的，这时候 `value` 的值没有变！并且由于这个解析的异常，会导致**输入缓冲区无法被刷新**，也就是说**下一次调用的时候，下一个 `scanf` 会从 `a` 开始解析**。

这么一想，那么我只需要输入寥寥几个字符，比如： `10a`，第一次调用 `scanf` 会解析出 `10`，并且给结果加上 `10`. 后面每次循环，`scanf` 会从剩下的 `a` 的位置进行解析，但是由于不是数字会被忽略，所以这个多出来的 `a` 就一直在！并且 `value` 的值没有变，保留上一次的 `10`. 因此，`scanf` 永远无法跳过这个 `a` 字符，最终就导致一直加 `10`，知道结果大于 `999`.
