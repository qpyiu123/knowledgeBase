---
title: "NewStar CTF 2025 / X0r"
category: reverse
tags: ["NewStar CTF 2025", "X0r", "reverse", "官方资料", "docs/wp/2025/week1/reverse/x0r.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "X0r", "reverse"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week1/reverse/x0r.md"
tools: []
origin: imported_cats
origin_id: "official-db7adfd4c657b42ded41bb"
origin_domain: "reverse"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
origin_body_sha256: 3d12dac841db9268b04fba1868a474e7817d659fd487dac6b7daab4d4080ae26
origin_title: "NewStar CTF 2025 / X0r"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/week1/reverse/x0r"
  chunk_ids: [10404, 10405]
  content_sha256: "3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761"
  domain: "reverse"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-db7adfd4c657b42ded41bb"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/9ce105b05111ed744472a788530bea64f8450d7c4fdf88a6e9ea2246e820e687.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/week1/reverse/x0r.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week1/reverse/x0r.md"
  tags: ["NewStar CTF 2025", "X0r", "reverse", "官方资料", "docs/wp/2025/week1/reverse/x0r.md"]
  title: "NewStar CTF 2025 / X0r"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / X0r

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week1/reverse/x0r.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：3505c69bd87af33f36578bb0699417dda5647a640603bba828608be30f9ca761
> - 导入 ID：official-db7adfd4c657b42ded41bb
> - 原 domain：reverse
> - 本地快照：62_官方赛事题库/objects/9ce105b05111ed744472a788530bea64f8450d7c4fdf88a6e9ea2246e820e687.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/week1/reverse/x0r.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

import Container from '@/components/docs/Container.vue'

## X0r

本题考查异或加密的逆向分析。

加密逻辑都在 `main` 函数中：

有两次加密操作，第一次是遍历字符串，根据索引对 3 取模的不同情况来进行异或，第二次是按周期异或数组，最后进行结果比较。

解密就从后往前逆回去，exp 如下：

最后得到的 flag 为 `flag{y0u_Kn0W_b4s1C_xOr}`
