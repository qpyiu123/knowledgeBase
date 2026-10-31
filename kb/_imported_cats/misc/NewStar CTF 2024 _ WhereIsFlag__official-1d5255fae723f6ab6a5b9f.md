---
title: "NewStar CTF 2024 / WhereIsFlag"
category: misc
tags: ["NewStar CTF 2024", "WhereIsFlag", "misc", "官方资料", "docs/wp/2024/week1/misc/whereisflag.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "WhereIsFlag", "misc"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/misc/whereisflag.md"
tools: []
origin: imported_cats
origin_id: "official-1d5255fae723f6ab6a5b9f"
origin_domain: "misc"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "e4948a0ac253ee177ae081b53b30755b98c1551de5c3ef7f429d62eb61a35750"
origin_body_sha256: 3dfeae032219d99cfd75532d5b77d6c8a21b2266ce35c70b3e4cd61dc4603088
origin_title: "NewStar CTF 2024 / WhereIsFlag"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week1/misc/whereisflag"
  chunk_ids: [8486, 8487]
  content_sha256: "e4948a0ac253ee177ae081b53b30755b98c1551de5c3ef7f429d62eb61a35750"
  domain: "misc"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 0
  id: "official-1d5255fae723f6ab6a5b9f"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/b4997c0271a4800d684180dcfadda5ecd33358b372dd794701216dbd44410a51.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week1/misc/whereisflag.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/misc/whereisflag.md"
  tags: ["NewStar CTF 2024", "WhereIsFlag", "misc", "官方资料", "docs/wp/2024/week1/misc/whereisflag.md"]
  title: "NewStar CTF 2024 / WhereIsFlag"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / WhereIsFlag

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/misc/whereisflag.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：e4948a0ac253ee177ae081b53b30755b98c1551de5c3ef7f429d62eb61a35750
> - 导入 ID：official-1d5255fae723f6ab6a5b9f
> - 原 domain：misc
> - 本地快照：62_官方赛事题库/objects/b4997c0271a4800d684180dcfadda5ecd33358b372dd794701216dbd44410a51.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/misc/whereisflag.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

import Container from '@/components/docs/Container.vue'

## WhereIsFlag

在后续，大家会接触到很多拿到服务器 Shell 后找到 flag 的场景。本题主要考查了这部分知识，在各个常见位置设置了或真或假的 flag。并且介绍了 `cd` `ls` `cat` 等常用命令的基础用法。

其实这题的后端是个 Python 程序<s>（嘛，都说了是 Virtual Linux 了啦）（喜欢椰奶精心设计的雌小鬼版 Linux 吗）</s>

真正的 flag 在 `/proc/self/environ` 文件（可用于获取当前进程的环境变量）内，只要执行下面的命令就能拿到 flag.

`proc` 目录是对当前操作系统进程的虚拟映射，在许多攻击场景中都有妙用，在此不展开。
