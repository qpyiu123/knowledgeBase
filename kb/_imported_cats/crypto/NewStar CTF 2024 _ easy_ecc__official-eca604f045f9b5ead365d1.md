---
title: "NewStar CTF 2024 / easy_ecc"
category: crypto
tags: ["NewStar CTF 2024", "easy_ecc", "crypto", "官方资料", "docs/wp/2024/week5/crypto/easy_ecc.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "easy_ecc", "crypto"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/crypto/easy_ecc.md"
tools: []
origin: imported_cats
origin_id: "official-eca604f045f9b5ead365d1"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
origin_body_sha256: 234fbf725b60b4d80cc25b997f9f5431986570a5878cca0e02fbde7d553a322e
origin_title: "NewStar CTF 2024 / easy_ecc"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week5/crypto/easy_ecc"
  chunk_ids: [9586]
  content_sha256: "687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 2
  id: "official-eca604f045f9b5ead365d1"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/d88e13ecc9c65df37d1769633a81daa79fc6c65dace18e258e51bacb5aef5e7f.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week5/crypto/easy_ecc.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/crypto/easy_ecc.md"
  tags: ["NewStar CTF 2024", "easy_ecc", "crypto", "官方资料", "docs/wp/2024/week5/crypto/easy_ecc.md"]
  title: "NewStar CTF 2024 / easy_ecc"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / easy_ecc

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/crypto/easy_ecc.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：687ddfdc3694b402f715820434f8e446bf5ed236864a3bc5e611205e528a6a5d
> - 导入 ID：official-eca604f045f9b5ead365d1
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/d88e13ecc9c65df37d1769633a81daa79fc6c65dace18e258e51bacb5aef5e7f.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week5/crypto/easy_ecc.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

## easy_ecc

由于 ECC 需要数论前置知识，这里很难一次讲解清楚，想要学习 ECC 的同学可以先补一下数论知识。但是对于这道题目不没有那么难，看一看下面两篇文章可以了：

- [ECC 椭圆曲线密码算法加密过程详解](https://blog.csdn.net/weixin_41754258/article/details/119595838)
- [ECC 椭圆曲线详解（含具体实例）](https://www.cnblogs.com/Yumeka/p/7392505.html)

涉及加密解密的所有参数都已经给出，flag 只和 $m$ 有关，而 $m$ 的解密只涉及 ECC 的基本解密流程

$$
m = c_1 - r \cdot K = c_1 - r \cdot k \cdot G = c1 - k \cdot c_2
$$

这样就得到了 $m$，$m$ 是一个点，$x$ 坐标和 $y$ 坐标分别是 `m[0]` 和 `m[1]`，flag 前半和后半分别整除 $x$ 和 $y$，然后拼接就能得到 flag

EXP：
