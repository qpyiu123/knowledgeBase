---
title: "NewStar CTF 2024 / 两个黄鹂鸣翠柳"
category: crypto
tags: ["NewStar CTF 2024", "两个黄鹂鸣翠柳", "crypto", "官方资料", "docs/wp/2024/week3/crypto/lianggehuangli.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "两个黄鹂鸣翠柳", "crypto"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/crypto/lianggehuangli.md"
tools: []
origin: imported_cats
origin_id: "official-43e918389aed460cc8fc72"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
origin_body_sha256: 741f2b352fde744de421715ca664719dd68222cdc58528e99a62d79960055674
origin_title: "NewStar CTF 2024 / 两个黄鹂鸣翠柳"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week3/crypto/lianggehuangli"
  chunk_ids: [8991]
  content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 1
  id: "official-43e918389aed460cc8fc72"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/59abbb9ed18569a18b0326738b162376fd44d0b2ce8de097f1511470f26afa09.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week3/crypto/lianggehuangli.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/crypto/lianggehuangli.md"
  tags: ["NewStar CTF 2024", "两个黄鹂鸣翠柳", "crypto", "官方资料", "docs/wp/2024/week3/crypto/lianggehuangli.md"]
  title: "NewStar CTF 2024 / 两个黄鹂鸣翠柳"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / 两个黄鹂鸣翠柳

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/crypto/lianggehuangli.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d
> - 导入 ID：official-43e918389aed460cc8fc72
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/59abbb9ed18569a18b0326738b162376fd44d0b2ce8de097f1511470f26afa09.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week3/crypto/lianggehuangli.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

## 两个黄鹂鸣翠柳

整体就是一个稍加变形的关联信息攻击，只是一般的关联信息攻击给出的两个方程式信息比较明确，而在本题中各掺了一点点随机性的干扰小量。

所以其实在思路上只需要依整体代换思想把它改为一般的关联信息攻击，再对被代换的「整体」进行爆破求解即可。

此外由于本题对于较大的数据求最大公因子的需求，一般的 GCD 算法难以胜任，所以需要使用 Half-GCD 算法。关于这个算法的原理可以参考下面这篇文章：

- [多项式 gcd 的正确姿势：Half-GCD 算法](https://www.cnblogs.com/whx1003/p/16217087.html)

解题脚本如下：
