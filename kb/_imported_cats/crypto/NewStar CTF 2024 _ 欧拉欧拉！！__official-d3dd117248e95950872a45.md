---
title: "NewStar CTF 2024 / 欧拉欧拉！！"
category: crypto
tags: ["NewStar CTF 2024", "欧拉欧拉！！", "crypto", "官方资料", "docs/wp/2024/week4/crypto/euler.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2024", "欧拉欧拉！！", "crypto"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/crypto/euler.md"
tools: []
origin: imported_cats
origin_id: "official-d3dd117248e95950872a45"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2024"
origin_year: 2024
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "e4948a0ac253ee177ae081b53b30755b98c1551de5c3ef7f429d62eb61a35750"
origin_body_sha256: bbfa641fc3a30a5521e8d3dfd25de5e590c32aa056b647785d3ef216cd92836b
origin_title: "NewStar CTF 2024 / 欧拉欧拉！！"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2024/week4/crypto/euler"
  chunk_ids: [9239, 9240]
  content_sha256: "e4948a0ac253ee177ae081b53b30755b98c1551de5c3ef7f429d62eb61a35750"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "NewStar CTF 2024"
  external_links_not_followed: 0
  id: "official-d3dd117248e95950872a45"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/92df45f055105892767615a4a0850b67904b2ab5cb23b615d40bb5c652a9c6d5.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2024/week4/crypto/euler.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/crypto/euler.md"
  tags: ["NewStar CTF 2024", "欧拉欧拉！！", "crypto", "官方资料", "docs/wp/2024/week4/crypto/euler.md"]
  title: "NewStar CTF 2024 / 欧拉欧拉！！"
  verification_status: "official_source_not_reproduced"
  year: 2024
updated: 2026-10-31
---
# NewStar CTF 2024 / 欧拉欧拉！！

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/crypto/euler.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2024
> - 年份：2024
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：e4948a0ac253ee177ae081b53b30755b98c1551de5c3ef7f429d62eb61a35750
> - 导入 ID：official-d3dd117248e95950872a45
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/92df45f055105892767615a4a0850b67904b2ab5cb23b615d40bb5c652a9c6d5.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2024/week4/crypto/euler.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2024"
---

import Container from '@/components/docs/Container.vue'

## 欧拉欧拉！！

$p$ 和 $q$ 的生成方式独特，其中有

$$
q = x + i
$$

通过 `x = (1 << bits) - 1 ^ p` 这行代码了解到，在二进制中，$p$ 和 512 个 $1$ 异或得到 $x$，则

$$
p+x=2^{512}
$$

推导得到

$$
p+q=2^{512}+i
$$

$$
p+q=2^{512}+i
$$

$\varphi$ 分解，有

$$
\varphi = (p-1)(q-1)=n-(p+q)+1
$$

代入，得

代入，得

$$
\varphi = n - (2^{512}- 1 + i) + 1 = n - 2^{512}+2-i
$$

EXP 如下
