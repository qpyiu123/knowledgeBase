---
title: "NewStar CTF 2025 / FHE: 0 and 1"
category: crypto
tags: ["NewStar CTF 2025", "FHE: 0 and 1", "crypto", "官方资料", "docs/wp/2025/week2/crypto/fhe-0-1.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "FHE: 0 and 1", "crypto"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week2/crypto/fhe-0-1.md"
tools: []
origin: imported_cats
origin_id: "official-163edaa048462bcbfd01dd"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
origin_body_sha256: 0c2779eb6775c9bc98364b7d0043d7fc42879ad74806a12cf48f2d6cd8c158cf
origin_title: "NewStar CTF 2025 / FHE: 0 and 1"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/week2/crypto/fhe-0-1"
  chunk_ids: [10517, 10518]
  content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-163edaa048462bcbfd01dd"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/880e1fc4f4cdc7ad5c32c9a5dd532b689d01a18a1af2d1a1df1e58b23f9292fe.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/week2/crypto/fhe-0-1.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week2/crypto/fhe-0-1.md"
  tags: ["NewStar CTF 2025", "FHE: 0 and 1", "crypto", "官方资料", "docs/wp/2025/week2/crypto/fhe-0-1.md"]
  title: "NewStar CTF 2025 / FHE: 0 and 1"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / FHE: 0 and 1

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week2/crypto/fhe-0-1.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761
> - 导入 ID：official-163edaa048462bcbfd01dd
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/880e1fc4f4cdc7ad5c32c9a5dd532b689d01a18a1af2d1a1df1e58b23f9292fe.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week2/crypto/fhe-0-1.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

import Container from '@/components/docs/Container.vue'

## FHE: 0 and 1

本题考查同态加密的分析。

$$pk_i=r_ip+s_i$$

其中 $pk$ 是 `public_key` 的值，$r_i$ 是一个随机数，$s_i$ 是一个很小的数。

显然可以把 $s_i$ 爆破然后求最大公约数。

这样会得到 $p$ 的倍数，而先前给定了 $p$ 是 $128$ 位，除以几个小因子就可以得到 $p$。

$$c_i=b_i+n_i+l_i$$

$$c_i=b_i+n_i+l_i$$

其中 $b_i$ 是每个比特，$n_i$ 是一个偶数小噪音， $l_i$ 是 $p$ 倍数的大噪音。我们刚刚求出了 $p$，模 $p$ 就可以把 $l_i$ 去掉，再对 $2$ 取模就可以去掉 $n_i$。剩下的就是 $b_i$，拼起来就是我们要求的 flag 了。
