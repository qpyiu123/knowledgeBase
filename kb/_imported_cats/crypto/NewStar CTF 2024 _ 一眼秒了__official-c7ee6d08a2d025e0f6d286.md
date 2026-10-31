---
title: "NewStar CTF 2024 / 一眼秒了"
category: crypto
tags: ["NewStar CTF 2024", "一眼秒了", "crypto", "官方资料", "docs/wp/2024/week1/crypto/yiyanmiaole.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "一眼秒了", "crypto"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/crypto/yiyanmiaole.md"
tools: []
origin: imported_cats
origin_id: "official-c7ee6d08a2d025e0f6d286"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
origin_body_sha256: 24c8451d35f4179df04e98fe27b699d91d90b1edbf76f91cec1f7d0048e9b546
origin_title: "NewStar CTF 2024 / 一眼秒了"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week1/crypto/yiyanmiaole"
  chunk_ids: [8457]
  content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 4
  id: "official-c7ee6d08a2d025e0f6d286"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/2049a0132617ae9d309f2af4391aba345767265ecb77a8601a13661501f76a14.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week1/crypto/yiyanmiaole.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/crypto/yiyanmiaole.md"
  tags: ["NewStar CTF 2024", "一眼秒了", "crypto", "官方资料", "docs/wp/2024/week1/crypto/yiyanmiaole.md"]
  title: "NewStar CTF 2024 / 一眼秒了"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / 一眼秒了

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/crypto/yiyanmiaole.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d
> - 导入 ID：official-c7ee6d08a2d025e0f6d286
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/2049a0132617ae9d309f2af4391aba345767265ecb77a8601a13661501f76a14.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week1/crypto/yiyanmiaole.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

## 一眼秒了

在做题之前可以先看一下 [RSA 算法原理详解](https://blog.csdn.net/qq_36665989/article/details/123184780)、[RSA 算法原理](https://blog.csdn.net/dbs1215/article/details/48953589) 这两篇文章，或者自己找一些文章学一下这个加密算法。

拿到题目我们可以看到这个 $n$ 比较小，那么我们就可以考虑分解 $n$ 得到 $p$ 和 $q$.

推荐一个在线网站 [FactorDB](http://www.factordb.com/) 或者离线工具 [CaptfEncoder](https://www.freebuf.com/sectool/188397.html).

分解得到 $p$ 和 $q$，随后就是常规的解密流程了。
