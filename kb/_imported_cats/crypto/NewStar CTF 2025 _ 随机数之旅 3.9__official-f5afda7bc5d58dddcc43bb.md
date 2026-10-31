---
title: "NewStar CTF 2025 / 随机数之旅 3.9"
category: crypto
tags: ["NewStar CTF 2025", "随机数之旅 3.9", "crypto", "官方资料", "docs/wp/2025/extras/crypto/random-3.9.md", "origin_tag:imported_cats"]
signals: ["NewStar CTF 2025", "随机数之旅 3.9", "crypto"]
difficulty: medium
source: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/extras/crypto/random-3.9.md"
tools: []
origin: imported_cats
origin_id: "official-f5afda7bc5d58dddcc43bb"
origin_domain: "crypto"
origin_family: "official_event_archive"
origin_event: "NewStar CTF 2025"
origin_year: 2025
origin_license: "MIT"
origin_attribution: ""
origin_verification: "official_source_not_reproduced"
origin_content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
origin_body_sha256: 9edde778e56dcb01339e4853de9b3995b12e8fc879c6302eedc2789a97d0b939
origin_title: "NewStar CTF 2025 / 随机数之旅 3.9"
origin_meta:
  asset_refs: []
  basis: "original_prose_not_runtime_verified"
  challenge_key: "newstar:docs/wp/2025/extras/crypto/random-3.9"
  chunk_ids: [10045]
  content_sha256: "46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579"
  domain: "crypto"
  domain_basis: "repository_path"
  event: "NewStar CTF 2025"
  external_links_not_followed: 0
  id: "official-f5afda7bc5d58dddcc43bb"
  kind: "official_wp_prose"
  language: "zh"
  license: "MIT"
  local_path: "62_官方赛事题库/objects/f89367b0764c4d64d74e1c971c19d32a1ca28508a8f04d3b78808a27230e690d.blob"
  official_evidence: "https://newstar.wiki/wp/2024/"
  original_path: "docs/wp/2025/extras/crypto/random-3.9.md"
  revision: "1a0f2ba21a30f950276396118b315eef0328371c"
  scope_note: "官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。"
  source_family: "official_event_archive"
  source_url: "https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/extras/crypto/random-3.9.md"
  tags: ["NewStar CTF 2025", "随机数之旅 3.9", "crypto", "官方资料", "docs/wp/2025/extras/crypto/random-3.9.md"]
  title: "NewStar CTF 2025 / 随机数之旅 3.9"
  verification_status: "official_source_not_reproduced"
  year: 2025
updated: 2026-10-31
---
# NewStar CTF 2025 / 随机数之旅 3.9

> 本文由授权中文赛事 WP 正文导入（阶段 1，仅散文，代码段未导入）。
>
> - 来源：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/extras/crypto/random-3.9.md
> - 许可：MIT
> - 署名：（未提供）
> - 文档族：official_event_archive
> - 赛事：NewStar CTF 2025
> - 年份：2025
> - 核验状态：official_source_not_reproduced
> - 正文 sha256：46be4dee7413a0e557e883b20d933f502314ccca596eac91129f31092e378579
> - 导入 ID：official-f5afda7bc5d58dddcc43bb
> - 原 domain：crypto
> - 本地快照：62_官方赛事题库/objects/f89367b0764c4d64d74e1c971c19d32a1ca28508a8f04d3b78808a27230e690d.blob
> - 源修订：1a0f2ba21a30f950276396118b315eef0328371c
> - 收录说明：官方发布来源的说明正文；代码单独索引，未运行或分析。按文件收录，不把多份文件算作多道题。图片及附件下载状态见清单；仅按路径/原题分类标方向，binary 等跨方向资料留待分类。
> - 判定依据：original_prose_not_runtime_verified

> 原文：https://github.com/pj-newstar/wiki-docs/blob/1a0f2ba21a30f950276396118b315eef0328371c/docs/wp/2025/extras/crypto/random-3.9.md

## 正文

---
titleTemplate: ":title | WriteUp - NewStar CTF 2025"
---

## 随机数之旅 3.9

$A_{500\times 30}\pmb x_{30\times 1}+\pmb e_{500\times 1}=\pmb b_{500\times 1}$
已知 $A,\pmb b$，且 $\pmb e$ 的分量只有两种取值，要求恢复 $\pmb x$。

显然有
$$\sum_{j}^{30}a_{ij}x_j +e_i=b_i$$
于是
$$(\sum_{j}^{30}a_{ij}x_j +ec[0]-b_i)(\sum_{j}^{30}a_{ij}x_j +ec[1]-b_i)=0$$
这样的二次方程共有 500 个，而未知项数量为 $30\times 31/2+30=495$，因此可以求解。
将 $x_0x_0,x_0x_1,\cdots,x_ix_j,\cdots,x_{29}x_{29},x_0,\cdots,x_{29}$ 视为独立未知量后，该问题可转化为线性方程组。

也可以考虑使用 NumPy 优化矩阵运算，但当前规模下直接求解已经足够。

意料之中的非预期：
使用线性映射 $ec[i]\rightarrow a\cdot ec[i]+b=ec^{\prime}[i]$，让 $ec^{\prime}[i]$ 足够小，然后用格方法求解。

意料之外的非预期：
中间相遇攻击
