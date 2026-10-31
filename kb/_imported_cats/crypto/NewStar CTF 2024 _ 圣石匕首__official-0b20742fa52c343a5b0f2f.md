---
title: "NewStar CTF 2024 / 圣石匕首"
category: crypto
tags: ["NewStar CTF 2024", "圣石匕首", "crypto", "官方资料", "docs/wp/2024/week4/crypto/shengshibishou.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "圣石匕首", "crypto"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/crypto/shengshibishou.md"
tools: []
origin: imported_cats
origin_id: "official-0b20742fa52c343a5b0f2f"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
origin_body_sha256: 9fbfe204ad6d12c00ee0bf83b4fc0075b2930044669d83d8b56dbe917685b4f8
origin_title: "NewStar CTF 2024 / 圣石匕首"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week4/crypto/shengshibishou"
  chunk_ids: [9252]
  content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 3
  id: "official-0b20742fa52c343a5b0f2f"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/b745c9b9f3e2087bfc700fa51f0571156163158e74bd883f89b5bb0b7dd14b78.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week4/crypto/shengshibishou.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/crypto/shengshibishou.md"
  tags: ["NewStar CTF 2024", "圣石匕首", "crypto", "官方资料", "docs/wp/2024/week4/crypto/shengshibishou.md"]
  title: "NewStar CTF 2024 / 圣石匕首"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / 圣石匕首

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/crypto/shengshibishou.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d
> - 导入 ID：official-0b20742fa52c343a5b0f2f
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/b745c9b9f3e2087bfc700fa51f0571156163158e74bd883f89b5bb0b7dd14b78.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/crypto/shengshibishou.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

## 圣石匕首

题目给了一个 `.sage` 文件，内部语法格式为 Python，但是要求安装并且配置 [SageMath](https://mirrors.aliyun.com/sagemath/win/index.html) 的环境才能执行。可以参照[此篇文章](https://zhuanlan.zhihu.com/p/297736314)配置 SageMath 在 Jupyter 中的运行环境。若在 Arch Linux 中使用 SageMath，可以参考[这篇文章](https://shinichicun.top/posts/arch下的sage安装/)。

然后在 SageMath 环境中运行题目所给的脚本即可。
