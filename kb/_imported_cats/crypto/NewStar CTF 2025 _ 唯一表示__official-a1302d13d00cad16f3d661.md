---
title: "NewStar CTF 2025 / 唯一表示"
category: crypto
tags: ["NewStar CTF 2025", "唯一表示", "crypto", "官方资料", "docs/wp/2025/week1/crypto/unique-repr.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "唯一表示", "crypto"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week1/crypto/unique-repr.md"
tools: []
origin: imported_cats
origin_id: "official-a1302d13d00cad16f3d661"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
origin_body_sha256: 7d3ffa74e7d9ea4c961f129e748b5aa0a447f77ec5c07e2710f326b6aa1ec6ba
origin_title: "NewStar CTF 2025 / 唯一表示"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/week1/crypto/unique-repr"
  chunk_ids: [10124, 10125]
  content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 1
  id: "official-a1302d13d00cad16f3d661"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/95fdeb0c50cd80489dd5b252701bcb1ae31ab86c95f11ca621403b1bc931d253.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/week1/crypto/unique-repr.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week1/crypto/unique-repr.md"
  tags: ["NewStar CTF 2025", "唯一表示", "crypto", "官方资料", "docs/wp/2025/week1/crypto/unique-repr.md"]
  title: "NewStar CTF 2025 / 唯一表示"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / 唯一表示

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week1/crypto/unique-repr.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761
> - 导入 ID：official-a1302d13d00cad16f3d661
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/95fdeb0c50cd80489dd5b252701bcb1ae31ab86c95f11ca621403b1bc931d253.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week1/crypto/unique-repr.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

import Container from '@/components/docs/Container.vue'

## 唯一表示

本题考查 CRT.

这里简单介绍一个函数：

`n, k = crt(primes, remainders)` 这是 [sympy 库](https://docs.sympy.org/latest/index.html)的一个用于求解线性同余方程组的函数。

> [!TIP] （一元）线性同余方程组
> （其中 $n_1,\cdots,n_k$ 两两互质）
> $$\begin{cases}x&\equiv a_1({\mathrm{mod}}\;n_1)\\x&\equiv a_2({\mathrm{mod}}\;n_2)\\&\vdots\\x&\equiv a_k({\mathrm{mod}}\;n_k)&\end{cases}$$

`primes` 就是要输入数组 `[n_1,...,n_k]` ，`remainders` 就是要输入数组 `[a_1,...,a_k]`。

`n` 是该函数返回的最小的 `x`<span data-desc>（显然方程组有一组解，这些解在模的意义下等同）</span>,`k` 就是模。

题目要求的 `flag` 转换成了整数，然后使用了 `fun()` 函数处理，得到了一个数组。容易知道该数组就是上面讲的 `remainders`，而 `primes` 已经告诉了怎么生成的。**直接复用 `crt()` 就可以求解**，再把数字转换为字节即可。

题目文件的名字是 `unik_repri`，其中 `unik` 是 unique 的谐音，`repri` 取自 representation 的开头几个音节。
